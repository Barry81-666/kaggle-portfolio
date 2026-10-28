# SAP v1.2: public label tables only; outputs contain no study identifiers.
source("R/common.R")
source("R/20_labels.R")
library(data.table)
library(jsonlite)
dest <- external_data_dir()
approval <- require_sap_approval(dest)
stopifnot(approval$sap_commit == "968c2a9cdb3be5978bbeed5128bad8ba843985f9")
started <- Sys.time()
set.seed(2026102802)
out <- "../../results/rsna-knee-public"
dir.create(out, recursive=TRUE, showWarnings=FALSE)
manifest <- fread("datasets.csv")[cohort_role == "primary_candidate"]
source_names <- c("Dread", "Steven", "Pilkwang", "Yunus", "Lixin")
stopifnot(nrow(manifest)==5L)
tables <- lapply(seq_len(5), function(j) {
  p <- file.path(dest, gsub("/", "__", manifest$dataset[j]), manifest$filename[j])
  x <- fread(p); check_label_schema(x)
  manifest[j, `:=`(sha256=sha256(p), bytes=file.size(p))]
  x
})
ids <- Reduce(intersect, lapply(tables, function(x) x$StudyInstanceUID))
tables <- lapply(tables, function(x) x[match(ids, StudyInstanceUID)])
stopifnot(all(vapply(tables, function(x) identical(x$StudyInstanceUID, ids), logical(1))))
fwrite(manifest[, .(dataset,filename,version,license,source_url,sha256,bytes)], file.path(out,"source_files.csv"))

make_labels <- function(threshold=.5, unknown=NA_real_, pilkwang_verdict=TRUE) {
  a <- array(NA_real_, c(length(ids),5,12), dimnames=list(NULL,source_names,findings))
  for(j in seq_len(5)) for(f in seq_along(findings)) {
    v <- tables[[j]][[findings[f]]]
    z <- as.numeric(v >= threshold)
    if(j==2) z[!is.na(v) & v==.5] <- unknown
    if(j==4) z[!is.na(v) & v %in% c(.05,.5)] <- unknown
    if(j==3) {
      verdict <- tables[[j]][[paste0(findings[f],"__verdict")]]
      stopifnot(all(is.na(verdict) | verdict %in% c("YES","NO","UNK")))
      if(pilkwang_verdict) z <- ifelse(verdict=="YES",1,ifelse(verdict=="NO",0,unknown))
      else z[verdict=="UNK" & !is.na(verdict)] <- unknown
    }
    a[,j,f] <- z
  }
  a
}

labels <- make_labels()
patterns <- lapply(seq_along(findings), function(f) pattern_table(labels[,,f]))
point <- lapply(patterns, function(p) weighted_stats(p$y,p$count))
B <- 2000L
draws <- lapply(point,function(x) matrix(NA_real_,B,length(x),dimnames=list(NULL,names(x))))
for(b in seq_len(B)) {
  idx<-sample.int(length(ids),length(ids),replace=TRUE)
  for(f in seq_along(findings)) {
    p<-patterns[[f]]
    draws[[f]][b,]<-weighted_stats(p$y,tabulate(p$code[idx],length(p$count)))
  }
  if(b%%250==0) message("B descriptive joint bootstrap: ",b,"/",B)
}
interval<-rbindlist(lapply(seq_along(findings),function(f) {
  rbindlist(lapply(seq_along(point[[f]]),function(k) {
    z<-draws[[f]][,k];n<-sum(is.finite(z)); parts<-strsplit(names(point[[f]])[k],"|",fixed=TRUE)[[1]]
    ci<-if(n>=.8*B) quantile(z,c(.025,.975),na.rm=TRUE,names=FALSE) else c(NA,NA)
    data.table(finding=findings[f],metric=parts[1],source_a=parts[2],source_b=if(length(parts)>2)parts[3] else "",
      estimate=point[[f]][k],lower=ci[1],upper=ci[2],bootstrap_valid=n,bootstrap_attempted=B)
  }))
}))
fwrite(interval,file.path(out,"T4_agreement.csv"),na="")
denominators<-rbindlist(lapply(seq_along(findings),function(f) {
  y<-labels[,,f];d<-majority_disagreements(y)
  rbindlist(lapply(seq_len(5),function(j) data.table(finding=findings[f],source=source_names[j],cohort_n=length(ids),
    known_n=sum(!is.na(y[,j])),positive_n=sum(y[,j]==1,na.rm=TRUE),complete_case_n=sum(complete.cases(y)),
    majority_comparable_n=sum(!is.na(d[,j])),majority_disagreements=sum(d[,j],na.rm=TRUE))))
}))
fwrite(denominators,file.path(out,"T4_denominators.csv"))
pair_n<-rbindlist(lapply(seq_along(findings),function(f) rbindlist(lapply(seq_len(ncol(pairs)),function(k) {
  y<-labels[,,f];d<-majority_disagreements(y);i<-pairs[1,k];j<-pairs[2,k]
  data.table(finding=findings[f],source_a=source_names[i],source_b=source_names[j],
    pair_known_n=sum(complete.cases(y[,c(i,j)])),disagreement_pair_n=sum(complete.cases(d[,c(i,j)])))
}))))
fwrite(pair_n,file.path(out,"T4_pair_denominators.csv"))
variants<-list(threshold_03=make_labels(.3,pilkwang_verdict=FALSE),threshold_07=make_labels(.7,pilkwang_verdict=FALSE),
 unknown_negative=make_labels(unknown=0),unknown_positive=make_labels(unknown=1))
sensitivity<-rbindlist(lapply(names(variants),function(v) rbindlist(lapply(seq_along(findings),function(f) {
  p<-pattern_table(variants[[v]][,,f]);s<-weighted_stats(p$y,p$count)
  data.table(variant=v,finding=findings[f],statistic=names(s),estimate=as.numeric(s))
}))))
fwrite(sensitivity,file.path(out,"T4_sensitivity.csv"),na="")
saveRDS(list(labels=labels,source_names=source_names,findings=findings),file.path(dest,"aligned-primary-labels.rds"))
write_json(list(sap_commit=approval$sap_commit,cohort_n=length(ids),sources=5,findings=12,
 seed=2026102802,bootstrap_replicates=B,elapsed_minutes=as.numeric(difftime(Sys.time(),started,units="mins")),
 completed_utc=format(Sys.time(),tz="UTC",usetz=TRUE),unit="study; patient clustering unavailable",
 missing_rule="SAP v1.2; source-specific undocumented codes not invented"),file.path(out,"labels-run.json"),auto_unbox=TRUE,pretty=TRUE)
message("B descriptive analysis complete; cohort n=",length(ids))
