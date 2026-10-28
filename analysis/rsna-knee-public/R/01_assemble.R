# Out-of-core filtering only. No team or submission records are exported to Git.
source("R/common.R")
library(jsonlite)
if (!requireNamespace("duckdb", quietly = TRUE) || !requireNamespace("DBI", quietly = TRUE)) {
  stop("The assembly phase requires reviewed/pinned duckdb and DBI packages.")
}
dest <- external_data_dir()
require_sap_approval(dest)
con <- DBI::dbConnect(duckdb::duckdb(), dbdir = file.path(dest, "meta-kaggle.duckdb"))
DBI::dbExecute(con, "SET memory_limit='1GB'")
DBI::dbExecute(con, paste0("SET temp_directory=", DBI::dbQuoteString(con, file.path(dest,"duckdb-temp"))))
csv <- function(nm) as.character(DBI::dbQuoteString(con, normalizePath(file.path(dest,nm),mustWork=TRUE)))
slug <- "rsna-knee-abnormality-detection"
comp <- DBI::dbGetQuery(con, paste0("SELECT Id, Slug, DeadlineDate FROM read_csv_auto(",
  csv("Competitions.csv"), ", all_varchar=true) WHERE Slug=",DBI::dbQuoteString(con,slug)))
if (nrow(comp) != 1L) stop("Competition coverage unverified: expected exactly one matching row.")
DBI::dbExecute(con, paste0("CREATE OR REPLACE TABLE knee_teams AS SELECT * FROM read_csv_auto(",
  csv("Teams.csv"),", all_varchar=true) WHERE CompetitionId=",DBI::dbQuoteString(con,comp$Id)))
DBI::dbExecute(con, paste0("CREATE OR REPLACE TABLE knee_submissions AS SELECT s.* FROM read_csv_auto(",
  csv("Submissions.csv"),", all_varchar=true) s SEMI JOIN knee_teams t ON s.TeamId=t.Id"))
coverage <- DBI::dbGetQuery(con,"SELECT COUNT(*) AS submissions, COUNT(DISTINCT TeamId) AS teams_with_submissions,
 SUM(CASE WHEN TRY_CAST(PublicScoreFullPrecision AS DOUBLE) IS NOT NULL AND
 TRY_CAST(PrivateScoreFullPrecision AS DOUBLE) IS NOT NULL THEN 1 ELSE 0 END) AS paired_scores
 FROM knee_submissions")
write_json(list(competition=comp, coverage=coverage, sap=fromJSON(file.path(dest,"sap-approval.json"))),
           file.path(dest,"assembly-audit.json"), pretty=TRUE, auto_unbox=TRUE)
DBI::dbDisconnect(con, shutdown=TRUE)
message("Filtered tables and coverage audit remain local. Inspect before running analysis.")
