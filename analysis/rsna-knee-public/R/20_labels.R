# Agreement primitives only. Latent-class fitting is a later, approved phase.
binary_agreement <- function(a,b) {
  if (length(a)!=length(b)) stop("Unpaired labels.")
  use <- !is.na(a)&!is.na(b); a<-a[use]; b<-b[use]
  if (!length(a)) return(c(n=0,agreement=NA,kappa=NA,pabak=NA))
  if (any(!a %in% c(0,1)) || any(!b %in% c(0,1))) stop("Labels must be binary or missing.")
  po <- mean(a==b); pe <- mean(a)*mean(b)+(1-mean(a))*(1-mean(b))
  c(n=length(a),agreement=po,kappa=if(pe==1) NA_real_ else (po-pe)/(1-pe),pabak=2*po-1)
}

majority_disagreements <- function(labels) {
  labels <- as.matrix(labels)
  if (ncol(labels)<3 || any(!is.na(labels)&!labels %in% c(0,1))) stop("Need at least three binary sources.")
  out <- matrix(NA_real_,nrow(labels),ncol(labels),dimnames=dimnames(labels))
  for (j in seq_len(ncol(labels))) {
    rest <- labels[,-j,drop=FALSE]
    n <- rowSums(!is.na(rest)); positives <- rowSums(rest,na.rm=TRUE)
    majority <- ifelse(n==0 | positives*2==n,NA_real_,as.numeric(positives*2>n))
    out[,j] <- as.numeric(labels[,j]!=majority)
  }
  out
}
