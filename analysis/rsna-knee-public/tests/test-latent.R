source("R/22_latent_model.R")
library(data.table)
# Prior predictive checks precede real-data fitting. The orientation is global,
# so a source may individually have negative Youden index.
set.seed(2026102804)
pat<-binary_patterns(5)
for(pr in list(c(2,2),c(1,1),c(4,2))) {
  for(i in 1:1000) {
    repeat {a<-rbeta(10,pr[1],pr[2]);if(sum(a)>5)break}
    p<-pattern_probabilities(pat,rbeta(1,1,1),a[1:5],a[6:10])
    stopifnot(all(p>=0),abs(sum(p)-1)<1e-12)
  }
}
# Recovery under the exact generative model, with known nonidentical accuracies.
truth<-c(.27,.81,.86,.89,.91,.93,.90,.88,.94,.95,.92)
p<-pattern_probabilities(pat,truth[1],truth[2:6],truth[7:11])
counts<-as.numeric(rmultinom(1,20000,p))
d<-fit_latent(counts,pat,iterations=4000,warmup=1000,seed=2026102805)
s<-latent_summary(d)
stopifnot(all(abs(s$median-truth)<.025),all(s$rhat<1.01),all(s$ess_bulk>400),
 all(apply(d,c(1,2),function(z)sum(z[-1]))>5))
# A likelihood check: enumerated probabilities match direct
# individual Bernoulli mixture probabilities for a hand-written pattern.
z<-c(1,0,1,0,1)
manual<-truth[1]*prod(ifelse(z==1,truth[2:6],1-truth[2:6]))+
 (1-truth[1])*prod(ifelse(z==1,1-truth[7:11],truth[7:11]))
stopifnot(abs(manual-p[1+sum(z*2^(0:4))])<1e-12)
cat("Prior predictive normalization and independent-model recovery passed. Max recovery error:",max(abs(s$median-truth)),"\n")
