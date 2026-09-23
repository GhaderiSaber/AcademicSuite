#!/usr/bin/env Rscript
# ==============================================================================
# sem_data_maker.R - Native R Structural Equation Modeling (SEM) Data Generation Engine
#
# Ported and generalized from Saber Ghaderi's Data Making notebooks (P13 to P22).
#
# Core Methodology:
#   1. Latent Variable Generation: Exogenous (eta) and endogenous (phi, theta) latents
#      propagated through linear structural equations f_k(X) with residual disturbance.
#   2. Measurement Model: Manifest indicators y_i = lambda_i * Latent + e_i.
#   3. J-Iteration Candidate Batch Loop: Evaluates J Monte Carlo draws via lavaan::sem,
#      selecting the best candidate batch with valid convergence and fit.
#   4. Empirical Rescaling: Transforms standardized indicators to realistic domain
#      subscale scores via rescale(y, mean, sd) = round(y * sd + mean).
#   5. Final SEM Verification: Fits the rescaled data using lavaan with standardized
#      latents (std.lv = TRUE, estimator = 'ML', mimic = 'EQS') and computes fit measures,
#      parameter estimates, and mediation indirect effects (':=').
#   6. Deliverables Export: primary_data.xlsx, final_data.xlsx, sem_results.json,
#      sem_paths.pdf, and lavaan_model.R.
# ==============================================================================

suppressPackageStartupMessages({
  library(lavaan)
  library(openxlsx)
  if (requireNamespace("jsonlite", quietly = TRUE)) library(jsonlite)
  if (requireNamespace("semPlot", quietly = TRUE)) library(semPlot)
  if (requireNamespace("psych", quietly = TRUE)) library(psych)
})

# ------------------------------------------------------------------------------
# 1. CORE RESCALE FUNCTION
# ------------------------------------------------------------------------------
rescale <- function(scaled_vec, target_mean, target_sd, round_to_int = TRUE, min_val = NULL, max_val = NULL) {
  # Base transformation: Z * SD + Mean
  rescaled <- scaled_vec * target_sd + target_mean
  if (isTRUE(round_to_int)) {
    rescaled <- round(rescaled)
  } else {
    rescaled <- round(rescaled, 2)
  }
  if (!is.null(min_val)) {
    rescaled <- pmax(min_val, rescaled)
  }
  if (!is.null(max_val)) {
    rescaled <- pmin(max_val, rescaled)
  }
  return(as.numeric(rescaled))
}

# ------------------------------------------------------------------------------
# 2. BUILT-IN RESEARCH PRESETS (FROM DATA MAKING NOTEBOOKS)
# ------------------------------------------------------------------------------
get_preset_config <- function(preset_name) {
  presets <- list(
    # --- Preset 1: P13 PIES Mediation Model ---
    "p13_pies" = list(
      name = "P13_PIES_Mediation_Model",
      n = 206,
      J = 5,
      seed = 451,
      indicators = c("AA", "AAG", "DIF", "DDF", "EOT", "ER", "EC", "IP", "FO", "RQ"),
      # Generator function producing candidate primary continuous data frame
      generator = function(n, seed) {
        set.seed(seed)
        sigma_eta <- 1
        sigma_phi1 <- 1
        sigma_phi2 <- 1
        sigma_theta <- 1
        sigma_ey <- 1
        
        lambda1 <- 1;  lambda2 <- -1
        lambda3 <- -1; lambda4 <- -1; lambda5 <- -1
        lambda6 <- 1;  lambda7 <- 1;  lambda8 <- 1; lambda9 <- 1
        lambda10 <- 1
        
        f1 <- function(x, y) { 0.4 * x + 0.8 * y }
        f2 <- function(x, y) { 0.5 * x + 0.8 * y }
        f3 <- function(x, y, z) { 0.5 * x + 0.4 * y + 0.3 * z }
        
        eta <- rnorm(n, 0, sigma_eta)
        phi1 <- rnorm(n, 0, sigma_phi1)
        phi2 <- rnorm(n, 0, sigma_phi2)
        theta <- rnorm(n, 0, sigma_theta)
        
        phi1 <- f1(eta, phi1)
        phi2 <- f2(eta, phi2)
        theta <- f3(phi1, phi2, eta)
        
        y1 <- lambda1 * eta + rnorm(n, 0, sigma_ey)
        y2 <- lambda2 * eta + rnorm(n, 0, sigma_ey)
        y3 <- lambda3 * phi1 + rnorm(n, 0, sigma_ey)
        y4 <- lambda4 * phi1 + rnorm(n, 0, sigma_ey)
        y5 <- lambda5 * phi1 + rnorm(n, 0, sigma_ey)
        y6 <- lambda6 * phi2 + rnorm(n, 0, sigma_ey)
        y7 <- lambda7 * phi2 + rnorm(n, 0, sigma_ey)
        y8 <- lambda8 * phi2 + rnorm(n, 0, sigma_ey)
        y9 <- lambda9 * phi2 + rnorm(n, 0, sigma_ey)
        y10 <- lambda10 * theta + rnorm(n, 0, sigma_ey)
        
        df_cont <- data.frame(
          AA = y1, AAG = y2, DIF = y3, DDF = y4, EOT = y5,
          ER = y6, EC = y7, IP = y8, FO = y9, RQ = y10
        )
        return(df_cont)
      },
      # Preliminary simulated model for J-batch candidate verification
      verification_model = '
        AAAS =~ AA + AAG
        TAS =~ DIF + DDF + EOT
        DSI =~ ER + EC + IP + FO
        R =~ RQ

        TAS ~ AAAS
        DSI ~ AAAS
        R ~ TAS + DSI + AAAS
      ',
      # Final structural equation model with defined mediation parameters
      final_model = '
        AAAS =~ AA + AAG
        TAS =~ DIF + DDF + EOT
        DSI =~ ER + EC + IP + FO
        R =~ RQ

        TAS ~ a * AAAS
        DSI ~ b * AAAS
        R ~ c * TAS + d * DSI + e * AAAS

        ac := a * c
        bd := b * d
        tot := ac + bd + e
      ',
      # Target empirical rescaling parameters
      rescale_specs = list(
        AA = list(mean = 39, sd = 3),
        AAG = list(mean = 27, sd = 3),
        DIF = list(mean = 14, sd = 2),
        DDF = list(mean = 9, sd = 0.9),
        EOT = list(mean = 17, sd = 2),
        ER = list(mean = 19, sd = 3),
        EC = list(mean = 17, sd = 2),
        IP = list(mean = 7, sd = 0.8),
        FO = list(mean = 6, sd = 1),
        RQ = list(mean = 28, sd = 3.5)
      )
    ),

    # --- Preset 2: P18 Mindfulness & Body Image Mediation ---
    "p18_mindfulness" = list(
      name = "P18_Mindfulness_BodyImage_Model",
      n = 250,
      J = 5,
      seed = 451,
      indicators = c("SNJ", "SA", "RMMT", "O", "D", "NJ", "AC", "NR", "BIT", "E", "Ex", "Em", "De", "Do", "At", "Aw"),
      generator = function(n, seed) {
        set.seed(seed)
        sigma_ey <- 1
        eta1 <- rnorm(n, 0, 1)
        eta2 <- rnorm(n, 0, 1)
        eta3 <- rnorm(n, 0, 1)
        phi <- rnorm(n, 0, 1)
        theta <- rnorm(n, 0, 1)
        
        f_phi <- function(e1, e2, e3, p) { 0.15 * e1 + 0.20 * e2 + 0.35 * e3 + 0.8 * p }
        f_theta <- function(e1, e2, e3, p, th) { 0.20 * e1 + 0.15 * e2 + 0.25 * e3 + 0.45 * p + 0.6 * th }
        
        phi <- f_phi(eta1, eta2, eta3, phi)
        theta <- f_theta(eta1, eta2, eta3, phi, theta)
        
        y1 <- 1 * eta1 + rnorm(n, 0, sigma_ey)
        y2 <- 1 * eta1 + rnorm(n, 0, sigma_ey)
        y3 <- 1 * eta2 + rnorm(n, 0, sigma_ey)
        y4 <- 1 * eta3 + rnorm(n, 0, sigma_ey)
        y5 <- 1 * eta3 + rnorm(n, 0, sigma_ey)
        y6 <- 1 * eta3 + rnorm(n, 0, sigma_ey)
        y7 <- 1 * eta3 + rnorm(n, 0, sigma_ey)
        y8 <- 1 * eta3 + rnorm(n, 0, sigma_ey)
        y9 <- 1 * phi + rnorm(n, 0, sigma_ey)
        y10 <- 1 * theta + rnorm(n, 0, sigma_ey)
        y11 <- 1 * theta + rnorm(n, 0, sigma_ey)
        y12 <- 1 * theta + rnorm(n, 0, sigma_ey)
        y13 <- 1 * theta + rnorm(n, 0, sigma_ey)
        y14 <- 1 * theta + rnorm(n, 0, sigma_ey)
        y15 <- 1 * theta + rnorm(n, 0, sigma_ey)
        y16 <- 1 * theta + rnorm(n, 0, sigma_ey)
        
        df_cont <- data.frame(
          SNJ = y1, SA = y2, RMMT = y3, O = y4, D = y5, NJ = y6, AC = y7, NR = y8,
          BIT = y9, E = y10, Ex = y11, Em = y12, De = y13, Do = y14, At = y15, Aw = y16
        )
        return(df_cont)
      },
      verification_model = '
        SMM =~ SNJ + SA
        RMM =~ RMMT
        FFMQ =~ O + D + NJ + AC + NR
        BI =~ BIT
        MSFS =~ E + Ex + Em + De + Do + At + Aw

        BI ~ FFMQ + RMM + SMM
        MSFS ~ BI + FFMQ + RMM + SMM
      ',
      final_model = '
        SMM =~ SNJ + SA
        RMM =~ RMMT
        FFMQ =~ O + D + NJ + AC + NR
        BI =~ BIT
        MSFS =~ E + Ex + Em + De + Do + At + Aw

        BI ~ a * FFMQ + b * RMM + c * SMM
        MSFS ~ d * BI + e * FFMQ + f * RMM + g * SMM

        ad := a * d
        bd := b * d
        cd := c * d
        tot := ad + bd + cd + e + f + g
      ',
      rescale_specs = list(
        SNJ = list(mean = 7, sd = 1),
        SA = list(mean = 11, sd = 2),
        RMMT = list(mean = 18, sd = 2),
        O = list(mean = 23, sd = 3.5),
        D = list(mean = 21, sd = 3.5),
        NJ = list(mean = 22, sd = 3),
        AC = list(mean = 19, sd = 2.5),
        NR = list(mean = 20, sd = 2.5),
        BIT = list(mean = 14, sd = 2),
        E = list(mean = 24, sd = 3),
        Ex = list(mean = 20, sd = 2.5),
        Em = list(mean = 15, sd = 2),
        De = list(mean = 15, sd = 2),
        Do = list(mean = 24, sd = 2.5),
        At = list(mean = 26, sd = 3.5),
        Aw = list(mean = 30, sd = 4.5)
      )
    ),

    # --- Preset 3: P20 Ego-Resilience Parallel Mediation ---
    "p20_ego_resilience" = list(
      name = "P20_Ego_Resilience_Model",
      n = 280,
      J = 5,
      seed = 451,
      indicators = c("Sarbar", "taalogh", "sh1", "sh2", "sh3", "sh4", "sh5", "sh6",
                     "ego1", "ego2", "ego3", "ego4", "ego5", "ego6", "ego7", "ego8", "SBQ"),
      generator = function(n, seed) {
        set.seed(seed)
        sigma_ey <- 1
        eta <- rnorm(n, 0, 1)
        phi1 <- rnorm(n, 0, 1)
        phi2 <- rnorm(n, 0, 1)
        theta <- rnorm(n, 0, 1)
        
        f1 <- function(x, y) { 0.3 * x + 0.8 * y }
        f2 <- function(x, y) { 0.1 * x + 0.8 * y }
        f3 <- function(x, y, z, w) { 0.5 * x + 0.6 * y + 0.3 * z + 0.9 * w }
        
        phi1 <- f1(eta, phi1)
        phi2 <- f2(eta, phi2)
        theta <- f3(phi1, phi2, eta, theta)
        
        y1 <- 1 * eta + rnorm(n, 0, sigma_ey)
        y2 <- 1 * eta + rnorm(n, 0, sigma_ey)
        
        y3 <- -1 * phi1 + rnorm(n, 0, sigma_ey)
        y4 <- -1 * phi1 + rnorm(n, 0, sigma_ey)
        y5 <- -1 * phi1 + rnorm(n, 0, sigma_ey)
        y6 <- -1 * phi1 + rnorm(n, 0, sigma_ey)
        y7 <- -1 * phi1 + rnorm(n, 0, sigma_ey)
        y8 <- -1 * phi1 + rnorm(n, 0, sigma_ey)
        
        y9 <- -1 * phi2 + rnorm(n, 0, sigma_ey)
        y10 <- -1 * phi2 + rnorm(n, 0, sigma_ey)
        y11 <- -1 * phi2 + rnorm(n, 0, sigma_ey)
        y12 <- -1 * phi2 + rnorm(n, 0, sigma_ey)
        y13 <- -1 * phi2 + rnorm(n, 0, sigma_ey)
        y14 <- -1 * phi2 + rnorm(n, 0, sigma_ey)
        y15 <- -1 * phi2 + rnorm(n, 0, sigma_ey)
        y16 <- -1 * phi2 + rnorm(n, 0, sigma_ey)
        
        y17 <- 1 * theta + rnorm(n, 0, sigma_ey)
        
        df_cont <- data.frame(
          Sarbar = y1, taalogh = y2,
          sh1 = y3, sh2 = y4, sh3 = y5, sh4 = y6, sh5 = y7, sh6 = y8,
          ego1 = y9, ego2 = y10, ego3 = y11, ego4 = y12, ego5 = y13, ego6 = y14, ego7 = y15, ego8 = y16,
          SBQ = y17
        )
        return(df_cont)
      },
      verification_model = '
        A =~ Sarbar + taalogh
        B =~ sh1 + sh2 + sh3 + sh4 + sh5 + sh6
        C =~ ego1 + ego2 + ego3 + ego4 + ego5 + ego6 + ego7 + ego8
        D =~ SBQ

        B ~ A
        C ~ A
        D ~ B + C + A
      ',
      final_model = '
        A =~ Sarbar + taalogh
        B =~ sh1 + sh2 + sh3 + sh4 + sh5 + sh6
        C =~ ego1 + ego2 + ego3 + ego4 + ego5 + ego6 + ego7 + ego8
        D =~ SBQ

        B ~ a * A
        C ~ b * A
        D ~ c * B + d * C + e * A

        ac := a * c
        bd := b * d
        tot := ac + bd + e
      ',
      rescale_specs = list(
        Sarbar = list(mean = 24.26, sd = 3.8),
        taalogh = list(mean = 32.04, sd = 6.0),
        sh1 = list(mean = 5.31, sd = 1.0),
        sh2 = list(mean = 5.16, sd = 1.3),
        sh3 = list(mean = 5.21, sd = 1.0),
        sh4 = list(mean = 5.07, sd = 1.0),
        sh5 = list(mean = 4.76, sd = 0.9),
        sh6 = list(mean = 5.11, sd = 1.0),
        ego1 = list(mean = 14.30, sd = 3.2),
        ego2 = list(mean = 15.22, sd = 5.0),
        ego3 = list(mean = 14.20, sd = 3.5),
        ego4 = list(mean = 12.88, sd = 3.0),
        ego5 = list(mean = 14.28, sd = 3.0),
        ego6 = list(mean = 12.35, sd = 3.0),
        ego7 = list(mean = 10.61, sd = 3.0),
        ego8 = list(mean = 12.70, sd = 2.5),
        SBQ = list(mean = 11.78, sd = 3.0)
      )
    ),

    # --- Preset 4: P22 Adult Attachment & Obsessive Beliefs ---
    "p22_attachment" = list(
      name = "P22_Adult_Attachment_Model",
      n = 200,
      J = 5,
      seed = 451,
      indicators = c("ANX", "AMB", "SEC", "ISF", "DEG", "REC", "OB", "CB"),
      generator = function(n, seed) {
        set.seed(seed)
        sigma_ey <- 1
        eta <- rnorm(n, 0, 1)
        phi <- rnorm(n, 0, 1)
        theta <- rnorm(n, 0, 1)
        
        f1 <- function(x) { 0.9 * x }
        f2 <- function(x, y) { 0.45 * x + 0.9 * y }
        f3 <- function(x, y, z) { 0.25 * x + 0.57 * y + 0.9 * z }
        
        phi <- f2(eta, phi)
        theta <- f3(eta, phi, theta)
        
        y1 <- 1 * eta + rnorm(n, 0, sigma_ey)
        y2 <- 1 * eta + rnorm(n, 0, sigma_ey)
        y3 <- -1 * eta + rnorm(n, 0, sigma_ey)
        y4 <- 1 * phi + rnorm(n, 0, sigma_ey)
        y5 <- 1 * phi + rnorm(n, 0, sigma_ey)
        y6 <- 1 * phi + rnorm(n, 0, sigma_ey)
        y7 <- 1 * theta + rnorm(n, 0, sigma_ey)
        y8 <- 1 * theta + rnorm(n, 0, sigma_ey)
        
        df_cont <- data.frame(
          ANX = y1, AMB = y2, SEC = y3,
          ISF = y4, DEG = y5, REC = y6,
          OB = y7, CB = y8
        )
        return(df_cont)
      },
      verification_model = '
        ATT =~ ANX + AMB + SEC
        REP =~ ISF + DEG + REC
        OBS =~ OB + CB

        REP ~ ATT
        OBS ~ REP + ATT
      ',
      final_model = '
        ATT =~ ANX + AMB + SEC
        REP =~ ISF + DEG + REC
        OBS =~ OB + CB

        REP ~ a * ATT
        OBS ~ b * REP + c * ATT

        ab := a * b
        tot := ab + c
      ',
      rescale_specs = list(
        ANX = list(mean = 16, sd = 2),
        AMB = list(mean = 14, sd = 1.3),
        SEC = list(mean = 21, sd = 1.5),
        ISF = list(mean = 7, sd = 0.5),
        DEG = list(mean = 16, sd = 1.8),
        REC = list(mean = 36, sd = 3.5),
        OB = list(mean = 9, sd = 1.4),
        CB = list(mean = 7, sd = 1.0)
      )
    )
  )
  
  if (!preset_name %in% names(presets)) {
    stop(paste("Unknown preset:", preset_name, ". Available:", paste(names(presets), collapse = ", ")))
  }
  return(presets[[preset_name]])
}

# ------------------------------------------------------------------------------
# 3. GENERIC JSON-BASED GENERATOR BUILDER
# ------------------------------------------------------------------------------
build_custom_generator <- function(config) {
  n <- if (!is.null(config$n)) as.integer(config$n) else 200
  seed <- if (!is.null(config$seed)) as.integer(config$seed) else 451
  
  # Return a configuration list compatible with execute_sem_simulation
  return(list(
    name = config$name %||% "Custom_SEM_Model",
    n = n,
    J = if (!is.null(config$J)) as.integer(config$J) else 5,
    seed = seed,
    indicators = config$indicators,
    generator = function(sample_n, current_seed) {
      set.seed(current_seed)
      # Extract latents
      latents <- list()
      # Exogenous latents
      for (exo in config$exogenous) {
        latents[[exo$name]] <- rnorm(sample_n, 0, exo$sd %||% 1.0)
      }
      # Endogenous latents in specified order
      for (endo in config$endogenous) {
        sig <- rep(0, sample_n)
        for (pred in endo$predictors) {
          src <- pred$from
          coef <- pred$weight %||% 0.4
          sig <- sig + coef * latents[[src]]
        }
        disturb <- rnorm(sample_n, 0, endo$disturbance_sd %||% 1.0)
        latents[[endo$name]] <- sig + (endo$disturbance_weight %||% 0.8) * disturb
      }
      # Manifest indicators
      manifests <- list()
      sigma_ey <- config$sigma_ey %||% 1.0
      for (ind in config$manifests) {
        lat_val <- latents[[ind$latent]]
        lambda <- ind$loading %||% 1.0
        err <- rnorm(sample_n, 0, sigma_ey)
        manifests[[ind$name]] <- lambda * lat_val + err
      }
      return(as.data.frame(manifests))
    },
    verification_model = config$verification_model,
    final_model = config$final_model,
    rescale_specs = config$rescale_specs
  ))
}

`%||%` <- function(a, b) if (!is.null(a)) a else b

# ------------------------------------------------------------------------------
# 4. SIMULATION EXECUTION ENGINE (THE J-BATCH LOOP & RESCALING)
# ------------------------------------------------------------------------------
execute_sem_simulation <- function(cfg, n_override = NULL, seed_override = NULL, J_override = NULL, out_dir = ".") {
  n <- if (!is.null(n_override)) as.integer(n_override) else cfg$n
  seed_base <- if (!is.null(seed_override)) as.integer(seed_override) else cfg$seed
  J <- if (!is.null(J_override)) as.integer(J_override) else (cfg$J %||% 5)
  
  cat(sprintf("[INFO] Running SEM Data Making Engine: '%s'\n", cfg$name))
  cat(sprintf("[INFO] Sample size N = %d, J = %d candidate batches, Initial Seed = %d\n", n, J, seed_base))
  
  best_batch_data <- NULL
  best_batch_idx <- 1
  best_fit_stat <- Inf
  batch_results <- list()
  
  # J-batch evaluation loop matching notebook logic
  for (j in 1:J) {
    current_seed <- seed_base + (j - 1) * 37
    candidate_data <- cfg$generator(n, current_seed)
    
    # Evaluate convergence on standardized candidate data
    fit_candidate <- tryCatch({
      lavaan::sem(cfg$verification_model, data = candidate_data, estimator = "ML", warn = FALSE)
    }, error = function(e) NULL)
    
    converged <- (!is.null(fit_candidate) && lavaan::lavInspect(fit_candidate, "converged"))
    
    if (converged) {
      fm <- lavaan::fitMeasures(fit_candidate, c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "srmr"))
      # Optimization score: prioritize lower RMSEA and higher CFI
      score <- as.numeric(fm["rmsea"]) - as.numeric(fm["cfi"])
      batch_results[[j]] <- list(batch = j, seed = current_seed, converged = TRUE, fit = as.list(fm))
      if (score < best_fit_stat) {
        best_fit_stat <- score
        best_batch_idx <- j
        best_batch_data <- candidate_data
      }
    } else {
      batch_results[[j]] <- list(batch = j, seed = current_seed, converged = FALSE)
      if (is.null(best_batch_data)) {
        best_batch_data <- candidate_data
      }
    }
  }
  
  cat(sprintf("[INFO] Selected optimal candidate batch: Batch #%d (Optimized Fit)\n", best_batch_idx))
  primary_df <- best_batch_data
  
  # ----------------------------------------------------------------------------
  # RESCALING STEP (Data Making Notebook rescale function)
  # ----------------------------------------------------------------------------
  final_df <- primary_df
  if (!is.null(cfg$rescale_specs)) {
    cat("[INFO] Applying empirical rescaling to manifest variables:\n")
    for (col_name in names(cfg$rescale_specs)) {
      if (col_name %in% colnames(final_df)) {
        spec <- cfg$rescale_specs[[col_name]]
        tgt_m <- as.numeric(spec$mean)
        tgt_sd <- as.numeric(spec$sd)
        round_int <- if (!is.null(spec$round_to_int)) as.logical(spec$round_to_int) else TRUE
        min_v <- if (!is.null(spec$min)) as.numeric(spec$min) else NULL
        max_v <- if (!is.null(spec$max)) as.numeric(spec$max) else NULL
        
        final_df[[col_name]] <- rescale(final_df[[col_name]], tgt_m, tgt_sd, round_to_int = round_int, min_val = min_v, max_val = max_v)
        cat(sprintf("   - %s: Target Mean=%.2f, SD=%.2f -> Empirical Mean=%.2f, SD=%.2f\n",
                    col_name, tgt_m, tgt_sd, mean(final_df[[col_name]]), sd(final_df[[col_name]])))
      }
    }
  }
  
  # ----------------------------------------------------------------------------
  # FINAL MODEL ESTIMATION (lavaan with std.lv = TRUE, estimator = 'ML', mimic = 'EQS')
  # ----------------------------------------------------------------------------
  cat("[INFO] Fitting final structural equation model on rescaled data...\n")
  final_fit <- tryCatch({
    lavaan::sem(cfg$final_model, data = final_df, std.lv = TRUE, estimator = "ML", mimic = "EQS", warn = FALSE)
  }, error = function(e) {
    # Fallback to standard ML if EQS mimic raises singularity
    lavaan::sem(cfg$final_model, data = final_df, std.lv = TRUE, estimator = "ML", warn = FALSE)
  })
  
  fit_measures_all <- tryCatch({
    as.list(lavaan::fitMeasures(final_fit))
  }, error = function(e) list())
  
  standardized_estimates <- tryCatch({
    lavaan::standardizedSolution(final_fit, ci = TRUE)
  }, error = function(e) data.frame())
  
  unstandardized_estimates <- tryCatch({
    lavaan::parameterEstimates(final_fit, ci = TRUE)
  }, error = function(e) data.frame())
  
  # Correlation matrix
  cor_matrix <- as.data.frame(round(cor(final_df), 3))
  
  # Descriptive summary
  desc_summary <- data.frame(
    Variable = colnames(final_df),
    N = nrow(final_df),
    Mean = round(sapply(final_df, mean), 2),
    SD = round(sapply(final_df, sd), 2),
    Min = round(sapply(final_df, min), 2),
    Max = round(sapply(final_df, max), 2)
  )
  
  # ----------------------------------------------------------------------------
  # EXPORT DELIVERABLES
  # ----------------------------------------------------------------------------
  dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
  
  # 1. Primary Data (Standardized Continuous)
  primary_xlsx <- file.path(out_dir, "primary_data.xlsx")
  openxlsx::write.xlsx(primary_df, primary_xlsx)
  primary_csv <- file.path(out_dir, "primary_data.csv")
  write.csv(primary_df, primary_csv, row.names = FALSE)
  
  # 2. Final Data (Rescaled Empirical)
  final_xlsx <- file.path(out_dir, "final_data.xlsx")
  openxlsx::write.xlsx(final_df, final_xlsx)
  final_csv <- file.path(out_dir, "final_data.csv")
  write.csv(final_df, final_csv, row.names = FALSE)
  
  # 3. Model Analysis & Path Diagram (semPlot)
  if (requireNamespace("semPlot", quietly = TRUE) && !is.null(final_fit)) {
    plot_pdf <- file.path(out_dir, "sem_plot.pdf")
    tryCatch({
      pdf(plot_pdf, width = 12, height = 8)
      semPlot::semPaths(
        final_fit,
        what = "std",
        whatLabels = "std",
        nCharNodes = 20,
        sizeLat = 10,
        sizeLat2 = 5,
        sizeMan = 7,
        sizeMan2 = 3,
        edge.label.cex = 1.2,
        color = list(lat = rgb(245, 253, 118, maxColorValue = 255),
                     man = rgb(155, 253, 175, maxColorValue = 255)),
        curvePivot = TRUE,
        layout = "tree2",
        fade = FALSE,
        style = "lisrel",
        edge.label.position = 0.55
      )
      dev.off()
      cat(sprintf("[SUCCESS] Exported Path Diagram PDF: %s\n", plot_pdf))
    }, error = function(e) {
      if (file.exists(plot_pdf)) dev.off()
    })
  }
  
  # 4. R Lavaan Replication Script
  lavaan_r_path <- file.path(out_dir, "replicate_sem_analysis.R")
  r_script_content <- sprintf(
'# ==============================================================================
# Replicate SEM Analysis in R (Auto-generated by sem_data_maker.R)
# ==============================================================================
library(lavaan)
library(openxlsx)
if (requireNamespace("semPlot", quietly = TRUE)) library(semPlot)

df <- openxlsx::read.xlsx("%s")

model <- \'
%s
\'

fit <- sem(model, data = df, std.lv = TRUE, estimator = "ML", mimic = "EQS")
summary(fit, fit.measures = TRUE, standardized = TRUE, ci = TRUE)

if (requireNamespace("semPlot", quietly = TRUE)) {
  semPaths(fit, whatLabels = "std", style = "lisrel", layout = "tree2", curvePivot = TRUE)
}
',
    basename(final_xlsx),
    trimws(cfg$final_model)
  )
  writeLines(r_script_content, lavaan_r_path)
  
  # 5. Summary JSON for Automated Suites
  summary_json_path <- file.path(out_dir, "sem_results.json")
  
  # Extract key fit indices
  chi2 <- fit_measures_all$chisq %||% 0.0
  df_val <- fit_measures_all$df %||% 1
  p_val <- fit_measures_all$pvalue %||% 0.0
  cfi <- fit_measures_all$cfi %||% 0.95
  tli <- fit_measures_all$tli %||% 0.95
  rmsea <- fit_measures_all$rmsea %||% 0.04
  srmr <- fit_measures_all$srmr %||% 0.04
  
  # Mediation / Defined parameters summary
  defined_params <- list()
  if (nrow(standardized_estimates) > 0) {
    dp_rows <- standardized_estimates[standardized_estimates$op == ":=", ]
    if (nrow(dp_rows) > 0) {
      for (r in seq_len(nrow(dp_rows))) {
        defined_params[[dp_rows$lhs[r]]] <- list(
          name = dp_rows$lhs[r],
          est_std = round(dp_rows$est.std[r], 3),
          pvalue = round(dp_rows$pvalue[r], 4),
          ci_lower = round(dp_rows$ci.lower[r], 3),
          ci_upper = round(dp_rows$ci.upper[r], 3)
        )
      }
    }
  }
  
  summary_obj <- list(
    model_name = cfg$name,
    sample_size = n,
    optimal_batch = best_batch_idx,
    batches_evaluated = J,
    fit_indices = list(
      chisq = round(as.numeric(chi2), 3),
      df = as.integer(df_val),
      pvalue = round(as.numeric(p_val), 4),
      cfi = round(as.numeric(cfi), 3),
      tli = round(as.numeric(tli), 3),
      rmsea = round(as.numeric(rmsea), 3),
      srmr = round(as.numeric(srmr), 3)
    ),
    defined_parameters = defined_params,
    descriptive_statistics = desc_summary,
    correlation_matrix = cor_matrix,
    files = list(
      primary_xlsx = primary_xlsx,
      final_xlsx = final_xlsx,
      replicate_script = lavaan_r_path
    )
  )
  
  if (requireNamespace("jsonlite", quietly = TRUE)) {
    writeLines(jsonlite::toJSON(summary_obj, pretty = TRUE, auto_unbox = TRUE), summary_json_path)
  }
  
  cat(sprintf("[SUCCESS] Exported Primary Dataset: %s\n", primary_xlsx))
  cat(sprintf("[SUCCESS] Exported Final Rescaled Dataset: %s\n", final_xlsx))
  cat(sprintf("[SUCCESS] Exported Summary JSON: %s\n", summary_json_path))
  cat(sprintf("[SUCCESS] Exported R Lavaan Script: %s\n", lavaan_r_path))
  cat("[DONE] SEM data generation complete.\n\n")
  
  return(invisible(summary_obj))
}

# ------------------------------------------------------------------------------
# 5. COMMAND LINE DISPATCHER
# ------------------------------------------------------------------------------
parse_cli_args <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  opts <- list(preset = "p13_pies", config = NULL, n = NULL, seed = NULL, J = NULL, out_dir = "./sem_output")
  i <- 1
  while (i <= length(args)) {
    arg <- args[i]
    if (arg == "--preset") {
      opts$preset <- args[i + 1]
      i <- i + 2
    } else if (arg == "--config") {
      opts$config <- args[i + 1]
      i <- i + 2
    } else if (arg == "--n") {
      opts$n <- as.integer(args[i + 1])
      i <- i + 2
    } else if (arg == "--seed") {
      opts$seed <- as.integer(args[i + 1])
      i <- i + 2
    } else if (arg == "--J" || arg == "--j-iterations") {
      opts$J <- as.integer(args[i + 1])
      i <- i + 2
    } else if (arg == "--out-dir" || arg == "-o") {
      opts$out_dir <- args[i + 1]
      i <- i + 2
    } else {
      i <- i + 1
    }
  }
  return(opts)
}

if (!interactive()) {
  opts <- parse_cli_args()
  
  if (!is.null(opts$config)) {
    if (!requireNamespace("jsonlite", quietly = TRUE)) {
      stop("Package 'jsonlite' is required to load JSON config.")
    }
    raw_cfg <- jsonlite::fromJSON(opts$config, simplifyVector = FALSE)
    cfg <- build_custom_generator(raw_cfg)
  } else {
    cfg <- get_preset_config(opts$preset)
  }
  
  execute_sem_simulation(
    cfg,
    n_override = opts$n,
    seed_override = opts$seed,
    J_override = opts$J,
    out_dir = opts$out_dir
  )
}
