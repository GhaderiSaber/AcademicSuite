#!/usr/bin/env Rscript
# -*- coding: utf-8 -*-
# ==============================================================================
# Deterministic Confirmatory Factor Analysis (CFA) Execution Script
# Engine: R / lavaan
# Output: cfa_results.json
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
  cat("Usage: Rscript run_cfa.R <data_file.csv> <cfa_syntax.txt> <output_results.json>\n")
  quit(status = 1)
}

data_file <- args[1]
syntax_file <- args[2]
output_file <- args[3]

data <- read.csv(data_file)
syntax <- paste(readLines(syntax_file), collapse = "\n")

fit <- lavaan::cfa(model = syntax, data = data, std.lv = TRUE, estimator = "MLR")

# Extract factor loadings
std_solution <- standardizedSolution(fit)
loadings <- std_solution[std_solution$op == "=~", c("lhs", "rhs", "est.std", "se", "z", "pvalue")]

fit_m <- fitMeasures(fit, c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "srmr"))

results <- list(
  engine = "R / lavaan CFA",
  sample_size = nobs(fit),
  fit_measures = list(
    chi2 = round(as.numeric(fit_m["chisq"]), 3),
    df = as.numeric(fit_m["df"]),
    cfi = round(as.numeric(fit_m["cfi"]), 3),
    tli = round(as.numeric(fit_m["tli"]), 3),
    rmsea = round(as.numeric(fit_m["rmsea"]), 3),
    srmr = round(as.numeric(fit_m["srmr"]), 3)
  ),
  factor_loadings = loadings,
  converged = lavInspect(fit, "converged")
)

write_json(results, output_file, pretty = TRUE, auto_unbox = TRUE)
cat(sprintf("CFA calculation complete. Output saved to: %s\n", output_file))
