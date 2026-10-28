# Synthetic DGM and known-answer checks; no real labels or predictions required.
auc_rank <- function(y, score) {
  if (length(y)!=length(score)) stop("Unpaired AUC inputs.")
  use <- !is.na(y)&is.finite(score); y<-y[use]; score<-score[use]
  if(any(!y %in% c(0,1))) stop("Outcome must be binary.")
  n1<-as.double(sum(y==1)); n0<-as.double(sum(y==0))
  if (!n1 || !n0) return(NA_real_)
  (sum(rank(score,ties.method="average")[y==1])-n1*(n1+1)/2)/(n1*n0)
}

mixture_factor <- function(prevalence, sensitivity, specificity) {
  if(any(!is.finite(c(prevalence,sensitivity,specificity))) ||
     any(c(prevalence,sensitivity,specificity)<=0 | c(prevalence,sensitivity,specificity)>=1)) stop("Use probabilities strictly inside (0,1).")
  ppv<-sensitivity*prevalence/(sensitivity*prevalence+(1-specificity)*(1-prevalence))
  npv<-specificity*(1-prevalence)/(specificity*(1-prevalence)+(1-sensitivity)*prevalence)
  ppv+npv-1
}

correct_auc <- function(naive, factor) {
  if (!is.finite(factor) || abs(factor)<.1) return(NA_real_)
  .5+(naive-.5)/factor # Deliberately not clipped to [0,1].
}

simulate_labels <- function(n=10000, prevalence=.15, auc=.9, sensitivity=.85,
                            specificity=.85, rho=0) {
  if (n<2 || rho<0 || rho>=1 || auc<=0 || auc>=1) stop("Invalid simulation settings.")
  mixture_factor(prevalence,sensitivity,specificity)
  y<-rbinom(n,1,prevalence); z<-rnorm(n)
  score<-sqrt(2)*qnorm(auc)*y+z
  # High scores increase positive report labels within either true class.
  u<-rho*z+sqrt(1-rho^2)*rnorm(n)
  positive_probability<-ifelse(y==1,sensitivity,1-specificity)
  label<-as.integer(u>qnorm(1-positive_probability))
  data.frame(y=y,score=score,label=label)
}
