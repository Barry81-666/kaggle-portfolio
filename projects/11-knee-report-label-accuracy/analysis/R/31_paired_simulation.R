source("R/30_simulation.R")
simulate_pair <- function(n,prevalence=.15,auc=c(.90,.91),sensitivity=.85,specificity=.85,rho=0,score_correlation=.8) {
  stopifnot(abs(rho)<sqrt(score_correlation),length(auc)==2)
  y<-rbinom(n,1,prevalence);common<-rnorm(n)
  za<-sqrt(score_correlation)*common+sqrt(1-score_correlation)*rnorm(n)
  zb<-sqrt(score_correlation)*common+sqrt(1-score_correlation)*rnorm(n)
  u<-(rho/sqrt(score_correlation))*common+sqrt(1-rho^2/score_correlation)*rnorm(n)
  label<-as.integer(u>qnorm(1-ifelse(y==1,sensitivity,1-specificity)))
  list(y=y,score=cbind(sqrt(2)*qnorm(auc[1])*y+za,sqrt(2)*qnorm(auc[2])*y+zb),label=label)
}
weighted_auc <- function(y,score,weights) {
  stopifnot(length(y)==length(score),nrow(weights)==length(y),all(y %in% 0:1))
  o<-order(score);w<-weights[o,,drop=FALSE];ys<-y[o]
  pos<-w*ys;neg<-w*(1-ys)
  if(anyDuplicated(score)) {
    groups<-match(score[o],unique(score[o]))
    pos<-rowsum(pos,groups,reorder=FALSE);neg<-rowsum(neg,groups,reorder=FALSE)
  }
  before<-matrixStats::colCumsums(neg)-neg/2
  den<-colSums(pos)*colSums(neg)
  value<-colSums(pos*before)/den;value[den==0]<-NA_real_;value
}
paired_bootstrap <- function(y,score,B=399L) {
  n<-length(y);w<-rmultinom(B,n,rep(1/n,n))
  a<-weighted_auc(y,score[,1],w);b<-weighted_auc(y,score[,2],w)
  samples<-cbind(AUC_A=a,AUC_B=b,delta=b-a)
  point<-c(auc_rank(y,score[,1]),auc_rank(y,score[,2]));point<-c(point,diff(point))
  ans<-cbind(estimate=point,lower=NA_real_,upper=NA_real_)
  rownames(ans)<-colnames(samples)
  for(j in 1:3) if(sum(is.finite(samples[,j]))>=.8*B)
    ans[j,2:3]<-quantile(samples[,j],c(.025,.975),na.rm=TRUE,names=FALSE)
  ans
}
simulation_summary <- function(a,truth) {
  # a: attempted replicates x (estimate, lower, upper); failures stay in denominator.
  R<-nrow(a);good<-is.finite(a[,1]);e<-a[good,1]-truth;n<-length(e)
  ci<-good&is.finite(a[,2])&is.finite(a[,3]);nc<-sum(ci)
  coverage<-if(nc)mean(a[ci,2]<=truth&a[ci,3]>=truth)else NA_real_
  length_ci<-a[ci,3]-a[ci,2]
  k<-min(20L,floor(n/25));batches<-split(e,rep(seq_len(k),length.out=n))
  rmse<-sqrt(mean(e^2));ps<-function(p,m) if(m>0)sqrt(p*(1-p)/m)else NA_real_
  data.table::data.table(replicates_attempted=R,estimates_valid=n,intervals_valid=nc,
    truth=truth,mean_estimate=mean(a[good,1]),bias=mean(e),bias_mcse=sd(e)/sqrt(n),
    empirical_sd=sd(e),sd_mcse=sd(vapply(batches,sd,numeric(1)))/sqrt(k),
    rmse=rmse,rmse_mcse=if(rmse>0)sqrt(var(e^2)/n)/(2*rmse)else 0,
    coverage=coverage,coverage_mcse=ps(coverage,nc),mean_interval_width=mean(length_ci),
    width_mcse=sd(length_ci)/sqrt(nc),failure_rate=1-n/R,failure_mcse=ps(1-n/R,R),
    interval_failure_rate=1-nc/R,interval_failure_mcse=ps(1-nc/R,R))
}
