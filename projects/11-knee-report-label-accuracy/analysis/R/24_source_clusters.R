# Post-hoc descriptive similarity analysis; see DECISIONS v1.3.
library(data.table)
source("R/common.R")
source("R/20_labels.R")
started <- proc.time()[3]
raw <- external_data_dir(); approval <- require_sap_approval(raw)
a <- readRDS(file.path(raw,"aligned-primary-labels.rds"))$labels
stopifnot(identical(dim(a),c(4349L,5L,12L)))
out <- "../results"

pair_kappas <- function(y,w=rep(1,nrow(y))) {
  vapply(seq_len(ncol(pairs)),function(k) {
    i<-pairs[1,k];j<-pairs[2,k];use<-!is.na(y[,i])&!is.na(y[,j]);ww<-w[use]
    n<-sum(ww);p<-sum(ww*y[use,i])/n;q<-sum(ww*y[use,j])/n
    po<-sum(ww*(y[use,i]==y[use,j]))/n;pe<-p*q+(1-p)*(1-q)
    if(is.finite(pe)&&pe<1)(po-pe)/(1-pe)else NA_real_
  },numeric(1))
}
cluster_kappa <- function(kappa) {
  m<-matrix(1,5,5,dimnames=list(source_names,source_names))
  for(k in seq_len(ncol(pairs))) m[pairs[1,k],pairs[2,k]]<-m[pairs[2,k],pairs[1,k]]<-kappa[k]
  stopifnot(all(is.finite(m)))
  hclust(as.dist(1-m),method="average")
}
pat<-lapply(1:12,function(j)pattern_table(a[,,j]))
kap<-vapply(1:12,function(j)pair_kappas(pat[[j]]$y,pat[[j]]$count),numeric(10))
cckap<-vapply(1:12,function(j)pair_kappas(a[complete.cases(a[,,j]),,j]),numeric(10))
ref<-fread(file.path(out,"T4_agreement.csv"))[metric=="kappa"]
for(j in 1:12)for(k in 1:10)stopifnot(abs(kap[k,j]-ref[finding==findings[j]&source_a==source_names[pairs[1,k]]&source_b==source_names[pairs[2,k]],estimate])<1e-12)
variants<-list(mean_paired=rowMeans(kap),median_paired=apply(kap,1,median),mean_complete=rowMeans(cckap))
trees<-lapply(variants,cluster_kappa)
set.seed(2026102901);B<-1000L;co<-matrix(0,5,5)
for(b in seq_len(B)) {
  ix<-sample.int(dim(a)[1],replace=TRUE)
  kb<-vapply(1:12,function(j)pair_kappas(pat[[j]]$y,tabulate(pat[[j]]$code[ix],nrow(pat[[j]]$y))),numeric(10))
  g<-cutree(cluster_kappa(rowMeans(kb)),k=2)
  co<-co+outer(g,g,"==")
}
res<-rbindlist(lapply(names(variants),function(v) {
  g<-cutree(trees[[v]],k=2)
  data.table(variant=v,source_a=source_names[pairs[1,]],source_b=source_names[pairs[2,]],
    mean_or_median_kappa=variants[[v]],same_cluster_k2=g[pairs[1,]]==g[pairs[2,]],
    bootstrap_same_cluster=if(v=="mean_paired")co[t(pairs)]/B else NA_real_,bootstrap_replicates=if(v=="mean_paired")B else 0L)
}))
fwrite(res,file.path(out,"T5_clusters.csv"))
mem<-rbindlist(lapply(names(trees),function(v)data.table(variant=v,source=source_names,cluster_k2=unname(cutree(trees[[v]],2)))))
fwrite(mem,file.path(out,"T5_membership.csv"))
focus<-ref[finding %in% c("Effusion","Synovitis")]
den<-fread(file.path(out,"T4_pair_denominators.csv"))
focus<-merge(focus,den[,.(finding,source_a,source_b,pair_known_n)],by=c("finding","source_a","source_b"))
fwrite(focus[,.(finding,source_a,source_b,kappa=estimate,lower,upper,pair_known_n)],file.path(out,"T5_focus.csv"))
saveRDS(list(trees=trees,co_membership=co/B,kappa=kap,complete_case_kappa=cckap),file.path(raw,"posthoc-clusters.rds"))
jsonlite::write_json(list(analysis="post-hoc v1.3",primary_sap_commit=approval$sap_commit,seed=2026102901,bootstrap_replicates=B,
  linkage="average",dissimilarity="1 - equal-finding mean Cohen kappa",cut_k=2,
  elapsed_minutes=unname((proc.time()[3]-started)/60),executed_on=as.character(Sys.Date())),file.path(out,"clusters-run.json"),auto_unbox=TRUE,pretty=TRUE)
print(mem);print(res[variant=="mean_paired"])
print(ref[source_a %in% c("Steven","Pilkwang")&source_b %in% c("Pilkwang","Lixin"),.(findings_ge_0.9=sum(estimate>=.9),min=min(estimate),max=max(estimate)),by=.(source_a,source_b)])
