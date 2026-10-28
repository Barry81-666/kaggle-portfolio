# Shared controls. Run entry scripts from analysis/rsna-knee-public.
findings <- c("ACL", "MCL", "Medial Meniscus", "Lateral Meniscus", "Medial OA",
              "Lateral OA", "PF OA", "Effusion", "Synovitis", "Baker's",
              "Contusion", "Fracture")

external_data_dir <- function(repo_root = "../..") {
  path <- Sys.getenv("RSNA_PUBLIC_DATA")
  if (!nzchar(path)) stop("Set RSNA_PUBLIC_DATA to a directory outside the repository.")
  dir.create(path, recursive = TRUE, showWarnings = FALSE)
  path <- normalizePath(path, mustWork = TRUE)
  repo <- normalizePath(repo_root, mustWork = TRUE)
  if (path == repo || startsWith(path, paste0(repo, "/"))) {
    stop("Raw inputs must be outside the repository.")
  }
  path
}

require_sap_approval <- function(path) {
  f <- file.path(path, "sap-approval.json")
  if (!file.exists(f)) stop("SAP approval has not been recorded. See DECISIONS.md.")
  a <- jsonlite::fromJSON(f)
  if (!identical(a$approved, TRUE) || !grepl("^[a-f0-9]{40}$", a$sap_commit) ||
      !nzchar(a$approved_on)) stop("Invalid SAP approval record.")
  invisible(a)
}

check_label_schema <- function(x) {
  extras <- c(paste0(findings, "__conf"), paste0(findings, "__verdict"))
  allowed <- c("StudyInstanceUID", findings, extras, "n_sources")
  if (length(setdiff(names(x), allowed))) stop("Unexpected columns: retain no file; review schema.")
  if (!all(c("StudyInstanceUID", findings) %in% names(x))) stop("Missing ID or finding.")
  ids <- x[["StudyInstanceUID"]]
  if (anyNA(ids) || any(!nzchar(as.character(ids))) || anyDuplicated(ids)) stop("Invalid study identifiers.")
  for (nm in findings) {
    z <- x[[nm]]
    if (!is.numeric(z) || any(!is.na(z) & (!is.finite(z) | z < 0 | z > 1))) stop("Invalid score column.")
  }
  invisible(TRUE)
}

sha256 <- function(path) {
  cmd <- Sys.which("shasum")
  if (!nzchar(cmd)) stop("A SHA-256 utility is required (shasum).")
  sub(" .*", "", system2(cmd, c("-a", "256", shQuote(path)), stdout = TRUE)[1])
}
