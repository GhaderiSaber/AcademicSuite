#!/usr/bin/env Rscript
# -*- coding: utf-8 -*-
# ==============================================================================
# Deterministic Bootstrap Mediation Script (PROCESS Model 4)
# Engine: R / boot & lavaan
# Output: mediation_results.json
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
if (length(args) < 4) {
  cat("Usage: Rscript run_mediation.R <data.csv> <X> <M> <Y> [output.json] [n_boot]\n")
  quit(status = 1)
}

data_file <- args[1]
iv <- args[2]
med <- args[3]
dv <- args[4]
output_file <- ifelse(length(args) >= 5, args[5], "mediation_results.json")
n_boot <- ifelse(length(args) >= 6, as.numeric(args[6]), 5000)

data <- read.csv(data_file)

# Lavaan model syntax for mediation with labeled paths
model <- sprintf("
  %s ~ a * %s
  %s ~ b * %s + cp * %s
  ab := a * b
  total := cp + (a * b)
", med, iv, dv, med, iv)

# Fit model with 5,000 bootstrap resamples
fit <- lavaan::sem(model = model, data = data, se = "bootstrap", bootstrap = n_boot)

# Extract parameter estimates and bootstrap BCa confidence intervals
ci <- parameterEstimates(fit, boot.ci.type = "bca.simple", level = 0.95)

get_param <- function(target) {
  row <- ci[ci$label == target, ]
  list(est = round(row$est, 3), se = round(row$se, 3), z = round(row$z, 3), p = round(row$pvalue, 4), ci_lower = round(row$ci.lower, 3), ci_upper = round(row$ci.upper, 3))
}

indirect <- get_param("ab")
direct <- get_param("cp")
total <- get_param("total")

results <- list(
  engine = "R / lavaan Bootstrap Mediation (5,000 resamples)",
  iv = iv,
  mediator = med,
  dv = dv,
  sample_size = nobs(fit),
  bootstrap_resamples = n_boot,
  indirect_effect = list(
    estimate = indirect$est,
    bca_95_ci = c(indirect$ci_lower, indirect$ci_upper),
    significant = (indirect$ci_lower * indirect$ci_upper > 0)
  ),
  direct_effect = direct$est,
  total_effect = total$est,
  status = ifelse(indirect$ci_lower * indirect$ci_upper > 0, "MEDIATION_SIGNIFICANT", "MEDIATION_NON_SIGNIFICANT")
)

write_json(results, output_file, pretty = TRUE, auto_unbox = TRUE)
cat(sprintf("Mediation calculation complete. Output saved to: %s\n", output_file))
