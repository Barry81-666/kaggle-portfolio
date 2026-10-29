source("R/31_paired_simulation.R")
set.seed(2026102806)
# Explicit resampling with ties verifies the weighted U-statistic independently.
y<-c(0,1,0,1,1,0);s<-c(.1,.5,.5,.8,.8,.3)
w<-rmultinom(100,length(y),rep(1/length(y),length(y)))
direct<-apply(w,2,function(v){idx<-rep(seq_along(y),v);auc_rank(y[idx],s[idx])})
stopifnot(isTRUE(all.equal(weighted_auc(y,s,w),direct)))
# Known-answer DGM: prevalence, Se/Sp, paired correlation, independent noise identity.
x<-simulate_pair(300000,rho=0)
factor<-mixture_factor(.15,.85,.85)
obs<-auc_rank(x$label,x$score[,1]); expected<-.5+factor*(.90-.5)
stopifnot(abs(mean(x$y)-.15)<.004,abs(mean(x$label[x$y==1])-.85)<.008,
 abs(mean(x$label[x$y==0]==0)-.85)<.005,abs(obs-expected)<.005)
b<-paired_bootstrap(x$y[1:58],x$score[1:58,],99)
stopifnot(all(dim(b)==c(3,3)),b[3,1]==b[2,1]-b[1,1])
cat("Weighted tied-score bootstrap and paired DGM known-answer checks passed. Identity error:",obs-expected,"\n")
