# Agreement and aggregate-pattern summaries for SAP v1.2.
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

source_names <- c("Dread", "Steven", "Pilkwang", "Yunus", "Lixin")
# All statistics are functions of weighted response patterns. Missing=2.
pattern_table <- function(y) {
  code <- rowSums(ifelse(is.na(y),2,y) * rep(3^(0:4),each=nrow(y)))+1L
  present <- sort(unique(code))
  patterns <- t(vapply(present-1L, function(z) (z %/% 3^(0:4)) %% 3, numeric(5)))
  patterns[patterns==2] <- NA_real_
  list(y=patterns, code=match(code,present), count=tabulate(match(code,present),length(present)))
}
pairs <- combn(5,2)
weighted_stats <- function(y,w) {
  N <- sum(w); known <- !is.na(y); yy <- y; yy[!known] <- 0
  denom <- colSums(w*known); pos <- colSums(w*yy)
  value <- c(pos/denom, 1-denom/N)
  names(value) <- c(paste0("positive|",source_names),paste0("missing|",source_names))
  for(k in seq_len(ncol(pairs))) {
    i<-pairs[1,k]; j<-pairs[2,k]; use<-known[,i]&known[,j]; n<-sum(w[use])
    p1<-sum(w[use]*yy[use,i])/n; p2<-sum(w[use]*yy[use,j])/n
    po<-sum(w[use]*(yy[use,i]==yy[use,j]))/n; pe<-p1*p2+(1-p1)*(1-p2)
    v<-c(agreement=po,kappa=if(is.finite(pe)&&pe<1) (po-pe)/(1-pe) else NA_real_,pabak=2*po-1)
    names(v)<-paste(names(v),source_names[i],source_names[j],sep="|"); value<-c(value,v)
  }
  cc<-rowSums(known)==5; nc<-sum(w[cc]); np<-rowSums(yy[cc,,drop=FALSE]); pc<-sum(w[cc]*np)/(5*nc)
  pbar<-sum(w[cc]*(np*(np-1)+(5-np)*(4-np))/20)/nc; pe<-pc^2+(1-pc)^2
  value<-c(value,"fleiss|all"=if(is.finite(pe)&&pe<1) (pbar-pe)/(1-pe) else NA_real_)
  d<-majority_disagreements(y)
  for(k in seq_len(ncol(pairs))) {
    i<-pairs[1,k];j<-pairs[2,k];use<-!is.na(d[,i])&!is.na(d[,j]);ww<-w[use]; n<-sum(ww)
    p1<-sum(ww*d[use,i])/n;p2<-sum(ww*d[use,j])/n; joint<-sum(ww*d[use,i]*d[use,j])/n
    v<-c(joint_disagreement=joint,disagreement_phi=(joint-p1*p2)/sqrt(p1*(1-p1)*p2*(1-p2)))
    names(v)<-paste(names(v),source_names[i],source_names[j],sep="|");value<-c(value,v)
  }
  value[!is.finite(value)]<-NA_real_;value
}
