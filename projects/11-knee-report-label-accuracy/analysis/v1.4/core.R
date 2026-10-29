# SAP v1.4: pure functions plus guards; sourcing this file does not read labels.
library(data.table)
library(jsonlite)
source("../R/common.R")
source("../R/20_labels.R")
seed32 <- function(x) as.integer(x %% 2147483647)
out_dir <- "../../results/v1.4"
guard <- function() {
  repo <- normalizePath("../../../..")
  manifest <- fromJSON("freeze-manifest.json")
  stopifnot(manifest$freeze_commit == "0053954a94baec9545e6f2e0c88fe43438456d3b")
  for (p in names(manifest$files)) {
    expected <- manifest$files[[p]]
    editorial <- manifest$editorial_updates[[p]]
    if (!is.null(editorial)) expected <- editorial$sha256
    stopifnot(identical(sha256(file.path(repo,p)), expected))
  }
  raw <- external_data_dir("../../../..")
  work <- Sys.getenv("RSNA_V14_WORK")
  stopifnot(nzchar(work))
  dir.create(work,recursive=TRUE,showWarnings=FALSE)
  work <- normalizePath(work)
  stopifnot(work != raw, work != repo, !startsWith(work,paste0(repo,"/")))
  dir.create(out_dir,recursive=TRUE,showWarnings=FALSE)
  list(raw=raw,work=work,freeze=manifest$freeze_commit)
}
verdict_map <- function(v) {
  if(any(!is.na(v) & !v %in% c("YES","NO","UNK"))) stop("Unexpected verdict")
  ifelse(v=="YES",1,ifelse(v=="NO",0,NA_real_))
}
yunus_map <- function(x, moderate=FALSE) {
  eq <- function(z) !is.na(x) & abs(x-z)<=1e-8
  code0 <- eq(0); mild <- eq(.25); mod <- eq(.55)
  severe <- !is.na(x) & x>=.90 & x<=1
  unknown <- eq(.05) | eq(.50) | is.na(x)
  undocumented <- !(code0 | mild | mod | severe | unknown)
  y <- rep(NA_real_,length(x)); y[code0] <- 0
  y[mild] <- if(moderate) 0 else 1
  y[mod | severe] <- 1
  list(y=y,undocumented=undocumented,unknown=unknown)
}
lcm_allowed <- function(n_sources) n_sources>=3L
read_inputs <- function(ctx) {
  manifest <- fread("../../results/source_files.csv")
  stopifnot(nrow(manifest)==5)
  tables <- lapply(seq_len(5),function(j) {
    p <- file.path(ctx$raw,gsub("/","__",manifest$dataset[j]),manifest$filename[j])
    stopifnot(sha256(p)==manifest$sha256[j],file.size(p)==manifest$bytes[j])
    x <- fread(p);check_label_schema(x);x
  })
  ids <- Reduce(intersect,lapply(tables,function(x) x$StudyInstanceUID))
  stopifnot(length(ids)==4349)
  tables <- lapply(tables,function(x) x[match(ids,StudyInstanceUID)])
  stopifnot(all(vapply(tables,function(x) identical(x$StudyInstanceUID,ids),logical(1))))
  old <- array(NA_real_,c(length(ids),5,12),dimnames=list(NULL,source_names,findings))
  for(j in 1:5) for(f in 1:12) {
    x <- tables[[j]][[findings[f]]];z <- as.numeric(x>=.5)
    if(j==2) z[!is.na(x)&x==.5] <- NA_real_
    if(j==4) z[!is.na(x)&x %in% c(.05,.5)] <- NA_real_
    if(j==3) z <- verdict_map(tables[[j]][[paste0(findings[f],"__verdict")]])
    old[,j,f] <- z
  }
  # Return IDs only in memory for release leakage checks, never output them.
  list(tables=tables,ids=ids,old=old,source_manifest=manifest)
}
pair_stats <- function(a,b) {
  use <- !is.na(a)&!is.na(b);a<-a[use];b<-b[use]
  if(!length(a)) return(setNames(rep(NA_real_,5),c("agreement","kappa","discordance","positive_Pilkwang","positive_Yunus")))
  po <- mean(a==b);pa<-mean(a);pb<-mean(b);pe<-pa*pb+(1-pa)*(1-pb)
  c(agreement=po,kappa=if(pe<1) (po-pe)/(1-pe) else NA_real_,discordance=1-po,
    positive_Pilkwang=pa,positive_Yunus=pb)
}
bin_patterns <- t(vapply(0:31,function(z) (z %/% 2^(0:4)) %% 2,numeric(5)))
colnames(bin_patterns) <- source_names
vote <- function(labels) {
  g1 <- rowMeans(labels[,c(2,3,5),drop=FALSE]);g2<-rowMeans(labels[,c(1,4),drop=FALSE])
  major <- as.integer(rowSums(labels)>=3)
  g1_label <- as.integer(g1>=2/3)
  definite <- g2 %in% c(0,1)
  keep <- definite & g1_label==g2
  stopifnot(all(major[keep]==g1_label[keep]),all(major[keep]==g2[keep]))
  list(major=major,keep=keep,g1=g1,g2=g2,g2_tie=!definite,
       group_disagree=definite & g1_label!=g2,common=g1_label)
}
pattern_votes <- vote(bin_patterns)
pattern_counts <- function(y) tabulate(1+as.integer(y %*% 2^(0:4)),nbins=32)
calibrate <- function(p,s) {
  g1<-pattern_votes$g1;g2<-pattern_votes$g2
  pi0<-sum(p*(g1+g2)/2);raw_pi<-pi0*s$prevalence_multiplier
  pi<-max(.02,min(.98,raw_pi));z<-s$truth_group1_weight*g1+(1-s$truth_group1_weight)*g2
  alpha <- uniroot(function(a) sum(p*plogis(a+s$truth_slope*(z-.5)))-pi,
                   c(-100,100),tol=1e-12)$root
  q<-plogis(alpha+s$truth_slope*(z-.5))
  pit_bounds <- function(g) {
    lo<-hi<-matrix(0,32,2)
    for(y in 0:1) {
      w<-p*if(y==1) q else (1-q);w<-w/sum(w)
      for(v in sort(unique(g))) {
        lo[g==v,y+1]<-sum(w[g<v]);hi[g==v,y+1]<-sum(w[g<=v])
      }
      stopifnot(abs(sum(w)-1)<1e-10,all(hi+1e-12>=lo),max(hi)<=1+1e-10)
    }
    list(lo=lo,hi=hi)
  }
  list(p=p,q=q,pi=pi,pi0=pi0,raw_pi=raw_pi,alpha=alpha,
       bounded=abs(raw_pi-pi)>1e-12,bounds=list(pit_bounds(g1),pit_bounds(g2)))
}
draw_scores <- function(n,cal,s) {
  ix<-sample.int(32,n,replace=TRUE,prob=cal$p);y<-rbinom(n,1,cal$q[ix])
  residual <- function(group) {
    b<-cal$bounds[[group]];index<-cbind(ix,y+1)
    u<-b$lo[index]+runif(n)*(b$hi[index]-b$lo[index])
    qnorm(pmax(1e-12,pmin(1-1e-12,u)))
  }
  za<-residual(if(s$orientation=="original") 1 else 2)
  zb<-residual(if(s$orientation=="original") 2 else 1)
  a<-sqrt(2)*qnorm(s$auc_a)*y+sqrt(s$inheritance)*za+sqrt(1-s$inheritance)*rnorm(n)
  b<-sqrt(2)*qnorm(s$auc_b)*y+sqrt(s$inheritance)*zb+sqrt(1-s$inheritance)*rnorm(n)
  keep<-pattern_votes$keep[ix];ref<-pattern_votes$major[ix]
  stopifnot(all(ref[keep]==pattern_votes$common[ix][keep]))
  list(y=y,a=a,b=b,keep=keep,ref=ref,ix=ix)
}
auc_from_rank <- function(r,y) {
  n1<-as.numeric(sum(y==1));n0<-length(y)-n1
  if(n1==0 || n0==0) return(NA_real_)
  (sum(r[y==1])-n1*(n1+1)/2)/(n1*n0)
}
both_auc <- function(score,ref,y) {
  r<-rank(score,ties.method="average")
  c(reference=auc_from_rank(r,ref),truth=auc_from_rank(r,y))
}
ordering <- function(delta) ifelse(!is.finite(delta),NA_integer_,ifelse(abs(delta)<=1e-12,0L,ifelse(delta>0,1L,-1L)))
simulation_rep <- function(n,cal,s) {
  d<-draw_scores(n,cal,s);k<-d$keep
  full_a<-both_auc(d$a,d$ref,d$y);full_b<-both_auc(d$b,d$ref,d$y)
  filt_a<-both_auc(d$a[k],d$ref[k],d$y[k]);filt_b<-both_auc(d$b[k],d$ref[k],d$y[k])
  c(retained_n=sum(k),g2_tie_n=sum(pattern_votes$g2_tie[d$ix]),
    group_disagree_n=sum(pattern_votes$group_disagree[d$ix]),
    retained_truth_prevalence=if(any(k)) mean(d$y[k]) else NA_real_,
    full_a_ref=unname(full_a[1]),full_b_ref=unname(full_b[1]),full_a_truth=unname(full_a[2]),full_b_truth=unname(full_b[2]),
    filtered_a_ref=unname(filt_a[1]),filtered_b_ref=unname(filt_b[1]),filtered_a_truth=unname(filt_a[2]),filtered_b_truth=unname(filt_b[2]))
}
mc_summary <- function(x) {
  x<-x[is.finite(x)];n<-length(x)
  c(estimate=if(n) mean(x) else NA_real_,mcse=if(n>1) sd(x)/sqrt(n) else NA_real_,valid=n)
}
prob_summary <- function(x) {
  x<-x[!is.na(x)];n<-length(x);p<-if(n) mean(x) else NA_real_
  c(estimate=p,mcse=if(n) sqrt(p*(1-p)/n) else NA_real_,valid=n)
}
write_run <- function(name,started,extra=list()) {
  write_json(c(list(freeze_commit="0053954a94baec9545e6f2e0c88fe43438456d3b",
    started_utc=format(started,tz="UTC",usetz=TRUE),completed_utc=format(Sys.time(),tz="UTC",usetz=TRUE),
    elapsed_minutes=as.numeric(difftime(Sys.time(),started,units="mins")),r_version=R.version.string),extra),
    file.path(out_dir,name),pretty=TRUE,auto_unbox=TRUE,na="null")
}
