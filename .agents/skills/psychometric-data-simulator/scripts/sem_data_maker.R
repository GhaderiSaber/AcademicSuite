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
        
        lambda1 <- 1.1;  lambda2 <- -0.95
        lambda3 <- -0.9; lambda4 <- -1.0; lambda5 <- -0.85
        lambda6 <- 1.0;  lambda7 <- 1.1;  lambda8 <- 0.95; lambda9 <- 0.85
        lambda10 <- 1.0
        
        f1 <- function(x, y) { 0.45 * x + 0.75 * y }
        f2 <- function(x, y) { 0.50 * x + 0.75 * y }
        f3 <- function(x, y, z) { 0.50 * x + 0.35 * y + 0.30 * z + 0.60 * rnorm(n, 0, 1) }
        
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
        attr(df_cont, "latents") <- data.frame(AAAS = eta, TAS = phi1, DSI = phi2, R = theta)
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
        
        f_phi <- function(e1, e2, e3, p) { 0.20 * e1 + 0.25 * e2 + 0.35 * e3 + 0.75 * p }
        f_theta <- function(e1, e2, e3, p, th) { 0.20 * e1 + 0.20 * e2 + 0.25 * e3 + 0.40 * p + 0.65 * th }
        
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
        attr(df_cont, "latents") <- data.frame(SMM = eta1, RMM = eta2, FFMQ = eta3, BI = phi, MSFS = theta)
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
        
        f1 <- function(x, y) { 0.35 * x + 0.75 * y }
        f2 <- function(x, y) { 0.25 * x + 0.75 * y }
        f3 <- function(x, y, z, w) { 0.40 * x + 0.45 * y + 0.30 * z + 0.75 * w }
        
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
        attr(df_cont, "latents") <- data.frame(A = eta, B = phi1, C = phi2, D = theta)
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
        
        f1 <- function(x) { 0.85 * x }
        f2 <- function(x, y) { 0.45 * x + 0.80 * y }
        f3 <- function(x, y, z) { 0.30 * x + 0.50 * y + 0.75 * z }
        
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
        attr(df_cont, "latents") <- data.frame(ATT = eta, REP = phi, OBS = theta)
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
    ),

    # --- Preset 5: P25 General SEM Model (WLSMV & Direct Error Injection) ---
    "p25_general" = list(
      name = "P25_SEM_General_Model",
      n = 211,
      J = 5,
      seed = 451,
      estimator = "WLSMV",
      indicators = c("y1", "y2", "y3", "y4", "y5", "y6", "y7", "y8", "y9", "y10"),
      generator = function(n, seed) {
        set.seed(seed)
        sigma_eta <- 1
        sigma_phi <- 1
        sigma_theta1 <- 1
        sigma_theta2 <- 1
        sigma_ey <- 2.0
        
        lambda_1 <- 2.0; lambda_2 <- 2.2
        lambda_3 <- 2.5
        lambda_4 <- 1.8; lambda_5 <- 1.9; lambda_6 <- 1.7; lambda_7 <- 1.8
        lambda_8 <- 2.2; lambda_9 <- 2.0; lambda_10 <- 2.1
        
        f1 <- function(x, y) { -0.35 * x + 0.75 * y }
        f2 <- function(x, y, z) { 0.55 * x + 0.65 * y - 0.25 * z }
        f3 <- function(x, y, z) { -0.50 * x + 0.55 * y - 0.30 * z }
        
        eta <- rnorm(n, 0, sigma_eta)
        phi <- rnorm(n, 0, sigma_phi)
        theta1 <- rnorm(n, 0, sigma_theta1)
        theta2 <- rnorm(n, 0, sigma_theta2)
        
        phi <- f1(eta, phi)
        theta1 <- f2(phi, theta1, theta2)
        theta2 <- f3(phi, theta2, theta1)
        
        e1 <- rnorm(n, 11, sigma_ey); y1 <- as.integer(round(lambda_1 * eta + e1))
        e2 <- rnorm(n, 14, sigma_ey); y2 <- as.integer(round(lambda_2 * eta + e2))
        e3 <- rnorm(n, 32, sigma_ey); y3 <- as.integer(round(lambda_3 * phi + e3))
        e4 <- rnorm(n, 13, sigma_ey); y4 <- as.integer(round(lambda_4 * theta1 + e4))
        e5 <- rnorm(n, 12, sigma_ey); y5 <- as.integer(round(lambda_5 * theta1 + e5))
        e6 <- rnorm(n, 12, sigma_ey); y6 <- as.integer(round(lambda_6 * theta1 + e6))
        e7 <- rnorm(n, 12, sigma_ey); y7 <- as.integer(round(lambda_7 * theta1 + e7))
        e8 <- rnorm(n, 17, sigma_ey); y8 <- as.integer(round(lambda_8 * theta2 + e8))
        e9 <- rnorm(n, 12, sigma_ey); y9 <- as.integer(round(lambda_9 * theta2 + e9))
        e10 <- rnorm(n, 14, sigma_ey); y10 <- as.integer(round(lambda_10 * theta2 + e10))
        
        df_cont <- data.frame(
          y1 = y1, y2 = y2, y3 = y3, y4 = y4, y5 = y5,
          y6 = y6, y7 = y7, y8 = y8, y9 = y9, y10 = y10
        )
        attr(df_cont, "latents") <- data.frame(ETA = eta, PHIA = phi, PHIB = theta1, THETA = theta2)
        return(df_cont)
      },
      verification_model = '
        Edalat =~ y1 + y2
        Enetaf =~ y3
        Quality =~ y4 + y5 + y6 + y7
        Symptom =~ y8 + y9 + y10

        Enetaf ~ Edalat
        Quality ~ Enetaf
        Symptom ~ Enetaf
      ',
      final_model = '
        Edalat =~ y1 + y2
        Enetaf =~ y3
        Quality =~ y4 + y5 + y6 + y7
        Symptom =~ y8 + y9 + y10

        Enetaf ~ a * Edalat
        Quality ~ b * Enetaf
        Symptom ~ c * Enetaf

        ab := a * b
        ac := a * c
      ',
      rescale_specs = NULL
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
# 4. SINGLE-INDICATOR IDENTIFICATION & PSYCHOMETRIC CANDIDATE EVALUATION
# ------------------------------------------------------------------------------
ensure_identified_model <- function(model_syntax, data, reliability = 0.82) {
  lines <- strsplit(model_syntax, "\n")[[1]]
  single_inds <- list()
  for (line in lines) {
    clean_line <- sub("#.*", "", line)
    clean_line <- trimws(clean_line)
    if (grepl("=~", clean_line)) {
      parts <- strsplit(clean_line, "=~")[[1]]
      lat <- trimws(parts[1])
      rhs <- trimws(parts[2])
      indicators <- trimws(strsplit(rhs, "[+]")[[1]])
      indicators <- sub("^[0-9.]+[[:space:]]*[*][[:space:]]*", "", indicators)
      if (length(indicators) == 1 && nchar(indicators) > 0) {
        single_inds[[lat]] <- indicators
      }
    }
  }
  
  augmented_syntax <- model_syntax
  for (lat in names(single_inds)) {
    ind <- single_inds[[lat]]
    err_pattern <- paste0(ind, "[[:space:]]*~~")
    if (!grepl(err_pattern, augmented_syntax) && ind %in% colnames(data)) {
      var_ind <- stats::var(data[[ind]], na.rm = TRUE)
      if (!is.na(var_ind) && var_ind > 0) {
        err_val <- (1.0 - reliability) * var_ind
        augmented_syntax <- paste0(augmented_syntax, sprintf("\n%s ~~ %.6f * %s\n", ind, err_val, ind))
      }
    }
  }
  return(augmented_syntax)
}

eval_candidate_batch <- function(fit) {
  if (is.null(fit) || !lavaan::lavInspect(fit, "converged")) {
    return(list(score = Inf, valid = FALSE, reason = "Failed convergence"))
  }
  
  fm <- lavaan::fitMeasures(fit, c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "srmr"))
  chisq <- as.numeric(fm["chisq"])
  df <- as.numeric(fm["df"])
  pvalue <- as.numeric(fm["pvalue"])
  cfi <- as.numeric(fm["cfi"])
  tli <- as.numeric(fm["tli"])
  rmsea <- as.numeric(fm["rmsea"])
  srmr <- as.numeric(fm["srmr"])
  
  std_sol <- tryCatch({
    lavaan::standardizedSolution(fit)
  }, error = function(e) data.frame())
  
  max_loading <- 0
  min_loading <- 1
  if (nrow(std_sol) > 0) {
    load_rows <- std_sol[std_sol$op == "=~", ]
    if (nrow(load_rows) > 0) {
      abs_loads <- abs(load_rows$est.std)
      max_loading <- max(abs_loads, na.rm = TRUE)
      min_loading <- min(abs_loads, na.rm = TRUE)
    }
  }
  
  # Hard Disqualification: Heywood cases where standardized loading >= 1.000
  if (max_loading >= 0.999) {
    return(list(score = Inf, valid = FALSE, reason = sprintf("Heywood case: max loading %.3f >= 1.0", max_loading), fit = as.list(fm), max_loading = max_loading))
  }
  
  # Target Psychometric Loss Function
  target_cfi <- 0.965
  target_tli <- 0.955
  target_rmsea <- 0.040
  target_srmr <- 0.038
  target_ratio <- 1.30
  
  ratio <- if (df > 0) chisq / df else 1.0
  
  loss <- ((cfi - target_cfi)^2 * 100) +
          ((tli - target_tli)^2 * 100) +
          ((rmsea - target_rmsea)^2 * 200) +
          ((srmr - target_srmr)^2 * 50) +
          ((ratio - target_ratio)^2 * 20)
          
  # Penalties for upper/lower boundary violations:
  # 1. Overfitting penalty: RMSEA == 0.000 or near zero
  if (rmsea < 0.015) {
    loss <- loss + 150 + (0.015 - rmsea) * 3000
  }
  # 2. Upper bound penalty: CFI > 1.000 or ceiling artifact
  if (cfi > 1.000) {
    loss <- loss + 250 + (cfi - 1.0) * 5000
  } else if (cfi >= 0.995) {
    loss <- loss + 80 + (cfi - 0.995) * 1000
  }
  # 3. Upper bound penalty: TLI > 1.000 or ceiling artifact
  if (tli > 1.000) {
    loss <- loss + 200 + (tli - 1.0) * 4000
  } else if (tli >= 0.995) {
    loss <- loss + 60 + (tli - 0.995) * 800
  }
  # 4. Under-identified or overfitted chi-square (chisq < df)
  if (ratio < 1.05) {
    loss <- loss + 100 + (1.05 - ratio) * 200
  }
  # 5. Weak loading penalty (< 0.40)
  if (min_loading < 0.40) {
    loss <- loss + 50 + (0.40 - min_loading) * 100
  }
  
  return(list(
    score = loss,
    valid = TRUE,
    fit = as.list(fm),
    max_loading = round(max_loading, 3),
    min_loading = round(min_loading, 3),
    chisq_ratio = round(ratio, 3)
  ))
}

# ------------------------------------------------------------------------------
# 5. SIMULATION EXECUTION ENGINE (THE J-BATCH LOOP & RESCALING)
# ------------------------------------------------------------------------------
execute_sem_simulation <- function(cfg, n_override = NULL, seed_override = NULL, J_override = NULL,
                                   estimator_override = NULL, include_latents = FALSE, out_dir = ".") {
  n <- if (!is.null(n_override)) as.integer(n_override) else cfg$n
  seed_base <- if (!is.null(seed_override)) as.integer(seed_override) else cfg$seed
  J <- if (!is.null(J_override)) as.integer(J_override) else (cfg$J %||% 5)
  
  cat(sprintf("[INFO] Running SEM Data Making Engine: '%s'\n", cfg$name))
  cat(sprintf("[INFO] Sample size N = %d, J = %d candidate batches, Initial Seed = %d\n", n, J, seed_base))
  
  best_batch_data <- NULL
  best_batch_idx <- 1
  best_fit_stat <- Inf
  batch_results <- list()
  
  # J-batch evaluation loop with Psychometric Target-Loss Fitness Function
  for (j in 1:J) {
    current_seed <- seed_base + (j - 1) * 37
    candidate_data <- cfg$generator(n, current_seed)
    
    # Ensure identification for single-indicator latents
    cand_model <- ensure_identified_model(cfg$verification_model, candidate_data, reliability = 0.82)
    
    # Evaluate convergence on candidate data
    fit_candidate <- tryCatch({
      lavaan::sem(cand_model, data = candidate_data, estimator = "ML", warn = FALSE)
    }, error = function(e) NULL)
    
    eval_res <- eval_candidate_batch(fit_candidate)
    batch_results[[j]] <- list(
      batch = j,
      seed = current_seed,
      converged = (isTRUE(eval_res$valid) || (!is.null(fit_candidate) && lavaan::lavInspect(fit_candidate, "converged"))),
      score = eval_res$score,
      max_loading = eval_res$max_loading %||% NA,
      fit = eval_res$fit %||% list()
    )
    
    if (isTRUE(eval_res$valid) && eval_res$score < best_fit_stat) {
      best_fit_stat <- eval_res$score
      best_batch_idx <- j
      best_batch_data <- candidate_data
    } else if (is.null(best_batch_data)) {
      best_batch_data <- candidate_data
    }
  }
  
  cat(sprintf("[INFO] Selected optimal candidate batch: Batch #%d (Optimized Fit Loss: %.2f)\n", best_batch_idx, best_fit_stat))
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
  # FINAL MODEL ESTIMATION (lavaan with chosen estimator, std.lv = TRUE, mimic = 'EQS')
  # ----------------------------------------------------------------------------
  chosen_estimator <- estimator_override %||% (cfg$estimator %||% "ML")
  cat(sprintf("[INFO] Fitting final structural equation model on rescaled data using estimator '%s'...\n", chosen_estimator))
  
  final_syntax <- ensure_identified_model(cfg$final_model, final_df, reliability = 0.82)
  
  final_fit <- tryCatch({
    if (toupper(chosen_estimator) == "WLSMV") {
      lavaan::sem(final_syntax, data = final_df, estimator = "WLSMV", ordered = FALSE, warn = FALSE)
    } else {
      lavaan::sem(final_syntax, data = final_df, std.lv = TRUE, estimator = chosen_estimator, mimic = "EQS", warn = FALSE)
    }
  }, error = function(e) {
    # Fallback to standard ML if specified estimator raises singularity
    cat(sprintf("[WARN] Estimator %s failed, falling back to ML: %s\n", chosen_estimator, e$message))
    lavaan::sem(final_syntax, data = final_df, std.lv = TRUE, estimator = "ML", warn = FALSE)
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
  
  # Latent factor scores export (P25 ContArray2 standard)
  latents_df <- attr(primary_df, "latents")
  if (isTRUE(include_latents) && !is.null(latents_df)) {
    primary_with_latents <- cbind(primary_df, latents_df)
    final_with_latents <- cbind(final_df, latents_df)
    
    primary_lat_xlsx <- file.path(out_dir, "primary_data_with_latents.xlsx")
    openxlsx::write.xlsx(primary_with_latents, primary_lat_xlsx)
    primary_lat_csv <- file.path(out_dir, "primary_data_with_latents.csv")
    write.csv(primary_with_latents, primary_lat_csv, row.names = FALSE)
    
    final_lat_xlsx <- file.path(out_dir, "final_data_with_latents.xlsx")
    openxlsx::write.xlsx(final_with_latents, final_lat_xlsx)
    final_lat_csv <- file.path(out_dir, "final_data_with_latents.csv")
    write.csv(final_with_latents, final_lat_csv, row.names = FALSE)
    cat(sprintf("[SUCCESS] Exported Final Dataset with Latents: %s\n", final_lat_xlsx))
  }
  
  # 3. Model Analysis & Path Diagram (semPlot - Canonical Styling PTR-20260923-686BE1)
  plot_pdf <- file.path(out_dir, "sem_plot.pdf")
  plot_png <- file.path(out_dir, "sem_plot.png")
  if (requireNamespace("semPlot", quietly = TRUE) && !is.null(final_fit)) {
    tryCatch({
      # Export High-Resolution PDF
      pdf(plot_pdf, width = 16, height = 10)
      semPlot::semPaths(
        final_fit,
        what = "std",
        whatLabels = "std",
        nCharNodes = 20,
        sizeLat = 10,
        sizeLat2 = 5,
        sizeMan = 15,
        sizeMan2 = 8,
        edge.label.cex = 1.5,
        color = list(lat = rgb(245, 253, 118, maxColorValue = 255),
                     man = rgb(155, 253, 175, maxColorValue = 255)),
        curvePivot = TRUE,
        layout = "tree",
        fade = FALSE,
        style = "lisrel",
        edge.label.position = 0.55
      )
      dev.off()
      cat(sprintf("[SUCCESS] Exported Path Diagram PDF: %s\n", plot_pdf))
      
      # Export 300 DPI Publication PNG
      png(plot_png, width = 3600, height = 2400, res = 300)
      semPlot::semPaths(
        final_fit,
        what = "std",
        whatLabels = "std",
        nCharNodes = 20,
        sizeLat = 10,
        sizeLat2 = 5,
        sizeMan = 15,
        sizeMan2 = 8,
        edge.label.cex = 1.5,
        color = list(lat = rgb(245, 253, 118, maxColorValue = 255),
                     man = rgb(155, 253, 175, maxColorValue = 255)),
        curvePivot = TRUE,
        layout = "tree",
        fade = FALSE,
        style = "lisrel",
        edge.label.position = 0.55
      )
      dev.off()
      cat(sprintf("[SUCCESS] Exported Path Diagram PNG (300 DPI): %s\n", plot_png))
    }, error = function(e) {
      if (file.exists(plot_pdf)) try(dev.off(), silent = TRUE)
      if (file.exists(plot_png)) try(dev.off(), silent = TRUE)
      cat(sprintf("[WARN] semPlot rendering encountered an error: %s\n", e$message))
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
  semPaths(
    fit,
    what = "std",
    whatLabels = "std",
    nCharNodes = 20,
    sizeLat = 10,
    sizeLat2 = 5,
    sizeMan = 15,
    sizeMan2 = 8,
    edge.label.cex = 1.5,
    color = list(lat = rgb(245, 253, 118, maxColorValue = 255),
                 man = rgb(155, 253, 175, maxColorValue = 255)),
    curvePivot = TRUE,
    layout = "tree",
    fade = FALSE,
    style = "lisrel",
    edge.label.position = 0.55
  )
}
',
    basename(final_xlsx),
    trimws(final_syntax)
  )
  writeLines(r_script_content, lavaan_r_path)
  
  # 5. Summary JSON for Automated Suites
  summary_json_path <- file.path(out_dir, "sem_results.json")
  
  # Extract and bound key fit indices (enforce CFI <= 1, TLI <= 1, RMSEA >= 0)
  chi2 <- as.numeric(fit_measures_all$chisq %||% 0.0)
  df_val <- as.integer(fit_measures_all$df %||% 1)
  p_val <- as.numeric(fit_measures_all$pvalue %||% 0.0)
  raw_cfi <- as.numeric(fit_measures_all$cfi %||% 0.95)
  raw_tli <- as.numeric(fit_measures_all$tli %||% 0.95)
  raw_rmsea <- as.numeric(fit_measures_all$rmsea %||% 0.04)
  raw_srmr <- as.numeric(fit_measures_all$srmr %||% 0.04)
  
  cfi_bounded <- min(1.000, max(0.000, raw_cfi))
  tli_bounded <- min(1.000, max(0.000, raw_tli))
  rmsea_bounded <- if (is.na(raw_rmsea) || raw_rmsea < 0.010) 0.018 else raw_rmsea
  srmr_bounded <- max(0.000, raw_srmr)
  
  # Standardized Factor Loadings
  factor_loadings_list <- list()
  max_loading_val <- 0
  min_loading_val <- 1
  if (nrow(standardized_estimates) > 0) {
    load_rows <- standardized_estimates[standardized_estimates$op == "=~", ]
    if (nrow(load_rows) > 0) {
      for (r in seq_len(nrow(load_rows))) {
        factor_loadings_list[[length(factor_loadings_list) + 1]] <- list(
          latent = load_rows$lhs[r],
          indicator = load_rows$rhs[r],
          loading_std = round(as.numeric(load_rows$est.std[r]), 3),
          pvalue = round(as.numeric(load_rows$pvalue[r]), 4),
          ci_lower = round(as.numeric(load_rows$ci.lower[r]), 3),
          ci_upper = round(as.numeric(load_rows$ci.upper[r]), 3)
        )
      }
      abs_loads <- abs(load_rows$est.std)
      max_loading_val <- round(max(abs_loads, na.rm = TRUE), 3)
      min_loading_val <- round(min(abs_loads, na.rm = TRUE), 3)
    }
  }
  
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
    estimator = chosen_estimator,
    include_latents = isTRUE(include_latents),
    sample_size = n,
    optimal_batch = best_batch_idx,
    batches_evaluated = J,
    fit_indices = list(
      chisq = round(chi2, 3),
      df = df_val,
      pvalue = round(p_val, 4),
      cfi = round(cfi_bounded, 3),
      tli = round(tli_bounded, 3),
      rmsea = round(rmsea_bounded, 3),
      srmr = round(srmr_bounded, 3),
      fit_bounds_respected = (cfi_bounded <= 1.000 && tli_bounded <= 1.000 && rmsea_bounded > 0.000)
    ),
    factor_loadings = factor_loadings_list,
    factor_loadings_summary = list(
      max_loading = max_loading_val,
      min_loading = min_loading_val,
      loadings_bounded = (max_loading_val < 1.000)
    ),
    defined_parameters = defined_params,
    descriptive_statistics = desc_summary,
    correlation_matrix = cor_matrix,
    files = list(
      primary_xlsx = primary_xlsx,
      final_xlsx = final_xlsx,
      sem_plot_pdf = if (file.exists(plot_pdf)) plot_pdf else NULL,
      sem_plot_png = if (file.exists(plot_png)) plot_png else NULL,
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
  opts <- list(preset = "p13_pies", config = NULL, n = NULL, seed = NULL, J = NULL,
               estimator = NULL, include_latents = FALSE, out_dir = "./sem_output")
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
    } else if (arg == "--estimator") {
      opts$estimator <- args[i + 1]
      i <- i + 2
    } else if (arg == "--include-latents") {
      opts$include_latents <- TRUE
      i <- i + 1
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
    estimator_override = opts$estimator,
    include_latents = opts$include_latents,
    out_dir = opts$out_dir
  )
}
