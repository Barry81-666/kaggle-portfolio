# DeLong placements for one empirical AUC; no smoothing or continuity correction.
delong_single <- function(y,score) {
  positive<-score[y==1];negative<-score[y==0]
  if(length(positive)<2||length(negative)<2)return(c(auc=NA_real_,variance=NA_real_))
  h<-outer(positive,negative,function(x,z)(x>z)+.5*(x==z))
  c(auc=mean(h),variance=var(rowMeans(h))/length(positive)+var(colMeans(h))/length(negative))
}
delong_intervals <- function(y,score) {
  d<-delong_single(y,score);a<-unname(d[1]);v<-unname(d[2])
  out<-matrix(NA_real_,2,2,dimnames=list(c("delong_normal","delong_logit"),c("lower","upper")))
  if(!all(is.finite(d)))return(out)
  out[1,]<-pmin(1,pmax(0,a+c(-1,1)*qnorm(.975)*sqrt(v)))
  if(a>0&&a<1&&v>0)out[2,]<-plogis(qlogis(a)+c(-1,1)*qnorm(.975)*sqrt(v)/(a*(1-a)))
  out
}
