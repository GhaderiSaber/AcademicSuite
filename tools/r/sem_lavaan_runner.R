#!/usr/bin/env Rscript
# -*- coding: utf-8 -*-
# sem_lavaan_runner.R — Deterministic R Runner for Structural Equation Modeling (lavaan)

suppressPackageStartupMessages({
  if (requireNamespace("lavaan", quietly = TRUE)) {
    library(lavaan)
  }
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3) {
  cat("Usage: Rscript sem_lavaan_runner.R <data.csv> <model_syntax.txt> <output.json>\n")
  quit(status = 0)
}

data_file <- args[1]
model_file <- args[2]
output_file <- args[3]

cat(sprintf("[R-LAVAAN] Ingesting dataset: %s\n", data_file))
cat(sprintf("[R-LAVAAN] Model specification: %s\n", model_file))
cat(sprintf("[R-LAVAAN] Output destination: %s\n", output_file))
