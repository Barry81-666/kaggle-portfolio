# Post-hoc expert-sample interval sensitivity. Original T7 outputs are untouched.
library(data.table)
source("R/common.R");source("R/31_paired_simulation.R");source("R/33_interval_methods.R")
started<-proc.time()[3];raw<-external_data_dir();approval<-require_sap_approval(raw)
out<-"../results";set.seed(2026102902)
R<-4000L;n<-58L;truth<-.90;B<-1999L
methods<-c("bootstrap_399","bootstrap_1999","delong_normal","delong_logit")
intervals<-array(NA_real_,c(R,4,2),dimnames=list(NULL,methods,c("lower","upper")))
estimate<-rep(NA_real_,R);npos<-integer(R);degenerate<-logical(R)
for(r in seq_len(R)) {
  y<-rbinom(n,1,.15);score<-sqrt(2)*qnorm(truth)*y+rnorm(n);npos[r]<-sum(y)
  estimate[r]<-auc_rank(y,score)
  w<-rmultinom(B,n,rep(1/n,n));draw<-weighted_auc(y,score,w)
  for(j in 1:2) {
    z<-draw[seq_len(c(399L,B)[j])]
    if(mean(is.finite(z))>=.8)intervals[r,j,]<-quantile(z,c(.025,.975),na.rm=TRUE,names=FALSE)
  }
  intervals[r,3:4,]<-delong_intervals(y,score)
  d<-delong_single(y,score);degenerate[r]<-is.finite(d[2])&&d[2]==0
}
valid<-is.finite(intervals[,,1])&is.finite(intervals[,,2])
covered<-valid&intervals[,,1]<=truth&intervals[,,2]>=truth
covered[is.na(covered)]<-FALSE
res<-rbindlist(lapply(1:4,function(j) {
  ok<-valid[,j];hit<-covered[,j];width<-intervals[ok,j,2]-intervals[ok,j,1]
  p<-mean(hit[ok]);joint<-mean(hit);delta<-as.numeric(hit)-as.numeric(covered[,1]);failure<-mean(!ok)
  data.table(method=methods[j],n=n,prevalence=.15,true_auc=truth,replicates=R,intervals_valid=sum(ok),
    coverage=p,coverage_mcse=sqrt(p*(1-p)/sum(ok)),successful_coverage=joint,successful_coverage_mcse=sd(as.numeric(hit))/sqrt(R),
    interval_failure_rate=failure,failure_mcse=sqrt(failure*(1-failure)/R),mean_width=mean(width),width_mcse=sd(width)/sqrt(sum(ok)),
    paired_success_difference=mean(delta),paired_difference_mcse=sd(delta)/sqrt(R))
}))
fwrite(res,file.path(out,"T8_interval_sensitivity.csv"))
fwrite(data.table(replicates=R,n=n,mean_positives=mean(npos),positive_q025=unname(quantile(npos,.025)),positive_median=median(npos),positive_q975=unname(quantile(npos,.975)),
  fewer_than_two_positives=sum(npos<2),boundary_auc=sum(estimate %in% c(0,1),na.rm=TRUE),zero_delong_variance=sum(degenerate),
  mean_auc=mean(estimate,na.rm=TRUE),bias=mean(estimate-truth,na.rm=TRUE),bias_mcse=sd(estimate,na.rm=TRUE)/sqrt(sum(is.finite(estimate)))),file.path(out,"T8_sample_diagnostics.csv"))
saveRDS(list(intervals=intervals,estimate=estimate,npositives=npos),file.path(raw,"posthoc-intervals.rds"))
jsonlite::write_json(list(analysis="post-hoc v1.3",primary_sap_commit=approval$sap_commit,seed=2026102902,replicates=R,
  bootstrap_max=B,nested_bootstrap_prefix=399,elapsed_minutes=unname((proc.time()[3]-started)/60),executed_on=as.character(Sys.Date())),file.path(out,"intervals-run.json"),auto_unbox=TRUE,pretty=TRUE)
print(res)
