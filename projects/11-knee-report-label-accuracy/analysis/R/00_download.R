# Read-only, public dataset acquisition. Never uses Kaggle credentials.
source("R/common.R")
library(curl)
library(jsonlite)
library(data.table)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1L || !args %in% c("--metadata", "--labels")) {
  stop("Usage: Rscript R/00_download.R --metadata | --labels")
}
dest <- external_data_dir()
manifest <- fread("datasets.csv")
get_file <- function(url, file, timeout = 120) {
  part <- paste0(file, ".part")
  h <- new_handle(timeout = timeout, connecttimeout = 20, failonerror = TRUE)
  # curl_download does not load large tables into R memory.
  curl_download(url, part, quiet = TRUE, handle = h)
  if (!file.rename(part, file)) stop("Could not finalize download.")
}
if (args == "--metadata") {
  refs <- manifest[cohort_role == "primary_candidate", dataset]
  for (ref in refs) {
    for (kind in c("view", "list")) {
      u <- paste0("https://www.kaggle.com/api/v1/datasets/", kind, "/", ref)
      if (kind == "list") u <- paste0(u, "?pageSize=200")
      f <- file.path(dest, paste0(gsub("/", "__", ref), "-", kind, ".json"))
      get_file(u, f)
      x <- fromJSON(f, simplifyVector = FALSE)
      if (kind == "list" && isTRUE(x$hasNextPageToken)) stop("File list is paginated: audit before download.")
    }
  }
  message("Public metadata saved outside the repository; no statistical analysis performed.")
}
if (args == "--labels") {
  receipts <- list()
  for (i in which(manifest$download_allowed & manifest$cohort_role == "primary_candidate")) {
    m <- manifest[i]
    if (!m$license %in% c("CC0: Public Domain")) stop("License requires a new review.")
    dir <- file.path(dest, gsub("/", "__", m$dataset))
    dir.create(dir, showWarnings = FALSE)
    f <- file.path(dir, m$filename)
    u <- paste0("https://www.kaggle.com/api/v1/datasets/download/", m$dataset, "/",
                URLencode(m$filename, reserved = TRUE), "?datasetVersionNumber=", m$version)
    get_file(u, f)
    ok <- tryCatch({ check_label_schema(fread(f)); TRUE }, error = function(e) FALSE)
    if (!ok) { unlink(f); stop("Label file failed schema allowlist; removed locally.") }
    receipts[[length(receipts) + 1L]] <- data.table(dataset=m$dataset, version=m$version,
      filename=m$filename, sha256=sha256(f), retrieved_at=format(Sys.time(), tz="UTC"))
  }
  fwrite(rbindlist(receipts), file.path(dest, "download-receipts.csv"))
}
