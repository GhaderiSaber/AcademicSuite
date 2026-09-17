#!/usr/bin/env Rscript
# -*- coding: utf-8 -*-
# ==============================================================================
# Deterministic Structural Equation Modeling (SEM) Execution Script
# Engine: R / lavaan
# Output: sem_results.json
# ==============================================================================

suppressPackageStartupMessages({
  if (!requireNamespace("lavaan", quietly = TRUE)) {
    stop("lavaan package is required. Install via install.packages('lavaan')")
  }
  if (!requireNamespace("jsonlite", quietly = TRUE)) {
    stop("jsonlite package is required. Install via install.packages('jsonlite')")
  }
})

library(lavaan)
library(jsonlite)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3) {
  cat("Usage: Rscript run_sem.R <data_file.csv> <model_syntax.txt> <output_results.json>\n")
  quit(status = 1)
}

data_file <- args[1]
model_file <- args[2]
output_file <- args[3]

# 1. Ingest Data
data <- read.csv(data_file)

# 2. Ingest Model Syntax
model_syntax <- paste(readLines(model_file), collapse = "\n")

# 3. Fit SEM Model (Full Information Maximum Likelihood or ML)
fit <- lavaan::sem(model = model_syntax, data = data, missing = "fiml", estimator = "MLR")

# 4. Extract 11 Goodness-of-Fit Indices
fit_measures <- fitMeasures(fit, c(
  "chisq", "df", "pvalue", "cfi", "tli", "ifi", "nfi", "gfi", "agfi", "rmsea", "rmsea.ci.lower", "rmsea.ci.upper", "srmr"
))

# 5. Extract Standardized Structural Paths
par_estimates <- standardizedSolution(fit)
structural_paths <- par_estimates[par_estimates$op == "~", c("lhs", "op", "rhs", "est.std", "se", "z", "pvalue")]

# 6. Format Structured Results
results <- list(
  engine = "R / lavaan (MLR robust estimation)",
  sample_size = nobs(fit),
  fit_indices = list(
    chi2 = round(as.numeric(fit_measures["chisq"]), 3),
    df = as.numeric(fit_measures["df"]),
    chi2_df = round(as.numeric(fit_measures["chisq"]) / as.numeric(fit_measures["df"]), 2),
    p_value = round(as.numeric(fit_measures["pvalue"]), 4),
    cfi = round(as.numeric(fit_measures["cfi"]), 3),
    tli = round(as.numeric(fit_measures["tli"]), 3),
    ifi = round(as.numeric(fit_measures["ifi"]), 3),
    nfi = round(as.numeric(fit_measures["nfi"]), 3),
    gfi = round(as.numeric(fit_measures["gfi"]), 3),
    agfi = round(as.numeric(fit_measures["agfi"]), 3),
    rmsea = round(as.numeric(fit_measures["rmsea"]), 3),
    rmsea_90_ci = c(round(as.numeric(fit_measures["rmsea.ci.lower"]), 3), round(as.numeric(fit_measures["rmsea.ci.upper"]), 3)),
    srmr = round(as.numeric(fit_measures["srmr"]), 3),
    hu_bentler_evaluation = ifelse(
      fit_measures["cfi"] >= 0.95 && fit_measures["tli"] >= 0.95 && fit_measures["rmsea"] <= 0.06 && fit_measures["srmr"] <= 0.08,
      "EXCELLENT_FIT",
      ifelse(fit_measures["cfi"] >= 0.90 && fit_measures["rmsea"] <= 0.08, "ACCEPTABLE_FIT", "POOR_FIT")
    )
  ),
  structural_paths = structural_paths,
  status = ifelse(lavInspect(fit, "converged"), "SEM_CONVERGED", "SEM_NOT_CONVERGED")
)

# 7. Export JSON Checkpoint
write_json(results, output_file, pretty = TRUE, auto_unbox = TRUE)
cat(sprintf("SEM calculation complete. Structured results exported to: %s\n", output_file))
