source("R/33_interval_methods.R")
# Independent library comparison, including ties and a boundary case.
for(s in list(c(.2,.4,.4,.8,.6,.4,.9,.8),c(.1,.2,.3,.4,.7,.8,.9,1))) {
  y<-rep(0:1,each=4);roc<-pROC::roc(y,s,levels=c(0,1),direction="<",quiet=TRUE)
  d<-delong_single(y,s);ci<-delong_intervals(y,s)
  stopifnot(abs(d[1]-as.numeric(pROC::auc(roc)))<1e-12,
    abs(d[2]-as.numeric(pROC::var(roc,method="delong")))<1e-12,
    max(abs(ci[1,]-as.numeric(suppressWarnings(pROC::ci.auc(roc,method="delong")))[c(1,3)]))<1e-12)
}
stopifnot(all(ci[1,]==1),all(is.na(ci[2,])),all(is.na(delong_intervals(c(0,0,1),c(.2,.3,.4)))))
cat("DeLong library parity and boundary-policy tests passed.\n")
