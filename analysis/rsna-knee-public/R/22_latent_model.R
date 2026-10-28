# Two-class conditional-independence model on binary response-pattern counts.
binary_patterns <- function(k) as.matrix(expand.grid(rep(list(0:1),k)))
pattern_probabilities <- function(patterns, prevalence, se, sp) {
  p1<-exp(patterns %*% log(se)+(1-patterns) %*% log1p(-se))
  p0<-exp(patterns %*% log1p(-sp)+(1-patterns) %*% log(sp))
  as.numeric(prevalence*p1+(1-prevalence)*p0)
}
truncated_beta <- function(a,b,lower) {
  lower<-max(0,lower)
  if(lower>=1) stop("Impossible orientation update.")
  survival<-pbeta(lower,a,b,lower.tail=FALSE)
  if(!is.finite(survival)||survival<=0) stop("Numerically unresolved truncated conditional.")
  min(1-1e-12,max(1e-12,qbeta(runif(1)*survival,a,b,lower.tail=FALSE)))
}
fit_latent <- function(counts,patterns,accuracy_prior=c(2,2),prevalence_prior=c(1,1),
                       iterations=6000L,warmup=2000L,chains=4L,seed=2026102803) {
  k<-ncol(patterns);N<-sum(counts)
  stopifnot(length(counts)==nrow(patterns),all(counts>=0),iterations>warmup)
  names<-c("prevalence",paste0("Se_",seq_len(k)),paste0("Sp_",seq_len(k)))
  ans<-array(NA_real_,c(iterations-warmup,chains,1+2*k),dimnames=list(NULL,NULL,names))
  for(ch in seq_len(chains)) {
    set.seed(seed+ch); prev<-runif(1,.08,.6);se<-runif(k,.65,.95);sp<-runif(k,.65,.95)
    for(it in seq_len(iterations)) {
      odds<-qlogis(prev)+as.numeric(patterns %*% log(se/(1-sp))+(1-patterns) %*% log((1-se)/sp))
      z<-rbinom(length(counts),counts,plogis(odds));n1<-sum(z);n0<-N-n1
      prev<-rbeta(1,prevalence_prior[1]+n1,prevalence_prior[2]+n0)
      prev<-min(1-1e-12,max(1e-12,prev))
      tp<-colSums(z*patterns);tn<-colSums((counts-z)*(1-patterns))
      for(j in seq_len(k)) se[j]<-truncated_beta(accuracy_prior[1]+tp[j],accuracy_prior[2]+n1-tp[j],k-sum(se[-j])-sum(sp))
      for(j in seq_len(k)) sp[j]<-truncated_beta(accuracy_prior[1]+tn[j],accuracy_prior[2]+n0-tn[j],k-sum(se)-sum(sp[-j]))
      if(it>warmup) ans[it-warmup,ch,]<-c(prev,se,sp)
    }
  }
  ans
}
latent_summary <- function(draws) {
  data.table::rbindlist(lapply(seq_len(dim(draws)[3]),function(j) {
    z<-draws[,,j];ci<-quantile(z,c(.025,.5,.975),names=FALSE)
    data.table::data.table(parameter=dimnames(draws)[[3]][j],median=ci[2],lower=ci[1],upper=ci[3],
      rhat=posterior::rhat(z),ess_bulk=posterior::ess_bulk(z),ess_tail=posterior::ess_tail(z),
      boundary_fraction=mean(z<.01|z>.99))
  }))
}
