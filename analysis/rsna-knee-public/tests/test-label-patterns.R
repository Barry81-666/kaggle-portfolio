source("R/20_labels.R")
set.seed(2026102808)
y<-matrix(sample(c(0,1,NA_real_),500,replace=TRUE,prob=c(.5,.3,.2)),100,5)
for(repeat_sample in 1:30) {
  idx<-sample.int(100,100,replace=TRUE);p<-pattern_table(y)
  w<-tabulate(p$code[idx],length(p$count));s<-weighted_stats(p$y,w);expanded<-y[idx,]
  for(k in seq_len(ncol(pairs))) {
    i<-pairs[1,k];j<-pairs[2,k];d<-binary_agreement(expanded[,i],expanded[,j])
    for(stat in c("agreement","kappa","pabak"))
      stopifnot(abs(s[paste(stat,source_names[i],source_names[j],sep="|")]-d[stat])<1e-12)
  }
  cc<-expanded[complete.cases(expanded),,drop=FALSE];np<-rowSums(cc);prev<-mean(cc)
  po<-mean((np*(np-1)+(5-np)*(4-np))/20);pe<-prev^2+(1-prev)^2
  stopifnot(abs(s["fleiss|all"]-(po-pe)/(1-pe))<1e-12)
}
cat("Compressed joint-bootstrap statistics equal directly expanded paired and Fleiss estimates.\n")
