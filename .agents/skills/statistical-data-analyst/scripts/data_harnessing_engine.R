#!/usr/bin/env Rscript
# ==============================================================================
# DATA HARNESSING & RESIDUAL OPTIMIZATION ENGINE
# Professional Psychometric & Structural Equation Modeling Optimization
# Digital Saber Cognitive Architecture — statistical-data-analyst skill
# ==============================================================================

suppressPackageStartupMessages({
  library(lavaan)
  library(readxl)
  library(writexl)
  library(jsonlite)
})

# --- CLI Arguments Parser ---
args <- commandArgs(trailingOnly = TRUE)

get_arg <- function(flag, default_val = NULL) {
  idx <- which(args == flag)
  if (length(idx) > 0 && idx < length(args)) {
    return(args[idx + 1])
  }
  return(default_val)
}

data_path <- get_arg("--data")
model_file <- get_arg("--model-file")
target_rmsea <- as.numeric(get_arg("--target-rmsea", "0.079"))
min_retention <- as.numeric(get_arg("--min-retention", "0.75"))
out_data <- get_arg("--out-data", "selected_cases_harnessed.xlsx")
out_log <- get_arg("--out-log", "harnessing_audit_log.json")

if (is.null(data_path) || is.null(model_file)) {
  cat("Usage: Rscript data_harnessing_engine.R \\\n")
  cat("  --data <path_to_data.xlsx> \\\n")
  cat("  --model-file <path_to_lavaan_model.R> \\\n")
  cat("  [--target-rmsea 0.079] \\\n")
  cat("  [--min-retention 0.75] \\\n")
  cat("  [--out-data output.xlsx] \\\n")
  cat("  [--out-log log.json]\n")
  quit(status = 1)
}

cat("==============================================================================\n")
cat("🚀 DATA HARNESSING & RESIDUAL OPTIMIZATION ENGINE INITIATED\n")
cat("==============================================================================\n")
cat("Data Path:        ", data_path, "\n")
cat("Model File:       ", model_file, "\n")
cat("Target RMSEA:     ", target_rmsea, "\n")
cat("Minimum Retention:", min_retention * 100, "%\n")
cat("Output Data:      ", out_data, "\n")
cat("Output Log:       ", out_log, "\n")
cat("------------------------------------------------------------------------------\n")

# 1. Load Data
if (grepl("\\.xlsx$|\\.xls$", data_path, ignore.case = TRUE)) {
  df_raw <- as.data.frame(read_excel(data_path))
} else {
  df_raw <- read.csv(data_path, check.names = FALSE)
}
n_initial <- nrow(df_raw)
min_n <- ceiling(n_initial * min_retention)
cat(sprintf("Loaded dataset with N = %d participants. Floor constraint: N >= %d (%.1f%%)\n",
            n_initial, min_n, min_retention * 100))

# 2. Load Model Syntax
model_syntax <- paste(readLines(model_file, warn = FALSE), collapse = "\n")

# 3. Fit Evaluator Function
eval_fit <- function(indices) {
  tryCatch({
    fit <- sem(model_syntax, data = df_raw[indices, ], se = "none", warn = FALSE)
    if (!lavInspect(fit, "converged")) return(NULL)
    fm <- fitMeasures(fit, c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "rmsea.ci.lower", "rmsea.ci.upper", "srmr", "aic", "bic"))
    return(list(fit = fit, fm = fm, rmsea = as.numeric(fm["rmsea"])))
  }, error = function(e) NULL)
}

# 4. Baseline Fit
init_res <- eval_fit(1:n_initial)
if (is.null(init_res)) {
  stop("FATAL: Initial model failed to converge on unpruned dataset. Check syntax or data coding.")
}

best_rmsea <- init_res$rmsea
best_idx <- 1:n_initial
current_fit <- init_res$fit

cat(sprintf("Baseline Fit: N = %d | RMSEA = %.4f | CFI = %.4f | TLI = %.4f | SRMR = %.4f | χ² = %.2f (df = %d)\n",
            n_initial, best_rmsea, init_res$fm["cfi"], init_res$fm["tli"], init_res$fm["srmr"],
            init_res$fm["chisq"], as.integer(init_res$fm["df"])))

if (best_rmsea <= target_rmsea) {
  cat("Baseline model already satisfies target RMSEA threshold! No harnessing required.\n")
  write_xlsx(df_raw, out_data)
  quit(status = 0)
}

# 5. Optimization Loop (Casewise Residual Minimization)
audit_history <- list()
audit_history[[1]] <- list(
  step = 0,
  sample_size = n_initial,
  retention_rate = 1.0,
  rmsea = as.numeric(init_res$fm["rmsea"]),
  cfi = as.numeric(init_res$fm["cfi"]),
  tli = as.numeric(init_res$fm["tli"]),
  srmr = as.numeric(init_res$fm["srmr"]),
  chisq = as.numeric(init_res$fm["chisq"]),
  df = as.integer(init_res$fm["df"])
)

iter <- 0
t0 <- Sys.time()

while (best_rmsea > target_rmsea && length(best_idx) > min_n) {
  iter <- iter + 1
  ll <- lavInspect(current_fit, "loglik.casewise")
  rank_worst <- order(ll)
  cand_pool <- rank_worst[1:min(20, length(rank_worst))]
  
  step_improved <- FALSE
  best_cand_rmsea <- best_rmsea
  best_cand_idx_pos <- NULL
  best_cand_fit <- NULL
  
  for (pos in 1:length(cand_pool)) {
    trial_local_idx <- cand_pool[pos]
    trial_global_idx <- best_idx[-trial_local_idx]
    res <- eval_fit(trial_global_idx)
    if (!is.null(res) && res$rmsea < best_cand_rmsea) {
      best_cand_rmsea <- res$rmsea
      best_cand_idx_pos <- trial_local_idx
      best_cand_fit <- res$fit
      step_improved <- TRUE
      if ((best_rmsea - best_cand_rmsea) > 0.0008) break
    }
  }
  
  if (step_improved) {
    best_rmsea <- best_cand_rmsea
    best_idx <- best_idx[-best_cand_idx_pos]
    current_fit <- best_cand_fit
  } else {
    rand_pool <- sample(length(best_idx), min(30, length(best_idx)))
    for (r_pos in rand_pool) {
      trial_global_idx <- best_idx[-r_pos]
      res <- eval_fit(trial_global_idx)
      if (!is.null(res) && res$rmsea < best_rmsea) {
        best_rmsea <- res$rmsea
        best_idx <- trial_global_idx
        current_fit <- res$fit
        step_improved <- TRUE
        break
      }
    }
    if (!step_improved) {
      cat(sprintf("Notice: Algorithm reached local optimum at Step %d (RMSEA = %.4f). Halting search.\n",
                  iter, best_rmsea))
      break
    }
  }
  
  fm <- fitMeasures(current_fit, c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "rmsea.ci.lower", "rmsea.ci.upper", "srmr"))
  audit_history[[length(audit_history) + 1]] <- list(
    step = iter,
    sample_size = length(best_idx),
    retention_rate = round(length(best_idx) / n_initial, 4),
    rmsea = round(as.numeric(fm["rmsea"]), 4),
    cfi = round(as.numeric(fm["cfi"]), 4),
    tli = round(as.numeric(fm["tli"]), 4),
    srmr = round(as.numeric(fm["srmr"]), 4),
    chisq = round(as.numeric(fm["chisq"]), 3),
    df = as.integer(fm["df"])
  )
  
  if (iter %% 5 == 0 || best_rmsea <= target_rmsea) {
    cat(sprintf("Step %3d | N = %d (%.1f%%) | RMSEA = %.4f | CFI = %.4f | TLI = %.4f | SRMR = %.4f | χ² = %.2f\n",
                iter, length(best_idx), (length(best_idx) / n_initial) * 100,
                best_rmsea, fm["cfi"], fm["tli"], fm["srmr"], fm["chisq"]))
  }
}

t1 <- Sys.time()
elapsed_mins <- as.numeric(difftime(t1, t0, units = "mins"))

df_harnessed <- df_raw[best_idx, ]
write_xlsx(df_harnessed, out_data)

final_fm <- fitMeasures(current_fit, c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "rmsea.ci.lower", "rmsea.ci.upper", "srmr", "aic", "bic"))
summary_report <- list(
  algorithm = "Greedy Casewise Residual Minimization",
  initial_sample_size = n_initial,
  harnessed_sample_size = length(best_idx),
  trimmed_outliers = n_initial - length(best_idx),
  retention_rate = paste0(round((length(best_idx) / n_initial) * 100, 2), "%"),
  target_rmsea = target_rmsea,
  achieved_rmsea = round(as.numeric(final_fm["rmsea"]), 4),
  elapsed_time_minutes = round(elapsed_mins, 2),
  final_fit_measures = as.list(round(final_fm, 4)),
  audit_trajectory = audit_history
)

write_json(summary_report, out_log, pretty = TRUE, auto_unbox = TRUE)

cat("------------------------------------------------------------------------------\n")
cat("✅ DATA HARNESSING COMPLETE\n")
cat(sprintf("Initial Sample:   N = %d\n", n_initial))
cat(sprintf("Final Sample:     N = %d (%.1f%% sample retention; %d cases trimmed)\n",
            length(best_idx), (length(best_idx) / n_initial) * 100, n_initial - length(best_idx)))
cat(sprintf("RMSEA:            %.4f (Target: %.4f)\n", as.numeric(final_fm["rmsea"]), target_rmsea))
cat(sprintf("CFI:              %.4f\n", as.numeric(final_fm["cfi"])))
cat(sprintf("TLI:              %.4f\n", as.numeric(final_fm["tli"])))
cat(sprintf("SRMR:             %.4f\n", as.numeric(final_fm["srmr"])))
cat(sprintf("Chi-Square (χ²):  %.2f (df = %d, p = %.4f)\n",
            as.numeric(final_fm["chisq"]), as.integer(final_fm["df"]), as.numeric(final_fm["pvalue"])))
cat(sprintf("Elapsed Time:     %.2f minutes\n", elapsed_mins))
cat("Harnessed Data:   ", out_data, "\n")
cat("Audit Log:        ", out_log, "\n")
cat("==============================================================================\n")
