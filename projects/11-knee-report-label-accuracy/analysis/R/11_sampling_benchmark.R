# Approved SAP v1.1, A3.2: synthetic sampling benchmark, no real predictions.
source("R/common.R")
source("R/30_simulation.R")
library(data.table)
library(jsonlite)
dest<-external_data_dir()
approval<-require_sap_approval(dest)
if(approval$sap_commit!="074d903aebfcef77bb7418e270380a9b693cc70d") stop("Expected the v1.1 freeze.")
started<-Sys.time()
set.seed(2026102901)
outdir<-"../results"
figdir<-"../figures"
dir.create(outdir,showWarnings=FALSE,recursive=TRUE)
dir.create(figdir,showWarnings=FALSE,recursive=TRUE)

macro_sample<-function(n,prevalence,auc,latent_rho) {
  zy<-sqrt(latent_rho)*rnorm(n)+sqrt(1-latent_rho)*matrix(rnorm(n*12),n,12)
  y<-1L*(zy>qnorm(1-prevalence))
  eps<-sqrt(latent_rho)*rnorm(n)+sqrt(1-latent_rho)*matrix(rnorm(n*12),n,12)
  score<-sqrt(2)*qnorm(auc)*y+eps
  a<-vapply(seq_len(12),function(j) auc_rank(y[,j],score[,j]),numeric(1))
  macro<-if(all(is.finite(a))) mean(a) else NA_real_
  # Realized across-finding binary correlation is not the latent Gaussian rho.
  realized<-suppressWarnings(cor(y))
  list(auc=macro,label_correlation=mean(realized[upper.tri(realized)],na.rm=TRUE))
}
base<-data.table(scenario="baseline",prevalence=.15,auc=.95,latent_rho=.3,public_multiplier=1,private_multiplier=1)
grid<-copy(base)
for (v in c(.05,.30,.50)) grid<-rbind(grid,copy(base)[,`:=`(scenario=paste0("prevalence_",v),prevalence=v)])
for (v in c(.94,.96)) grid<-rbind(grid,copy(base)[,`:=`(scenario=paste0("auc_",v),auc=v)])
for (v in c(0,.6)) grid<-rbind(grid,copy(base)[,`:=`(scenario=paste0("dependence_",v),latent_rho=v)])
for (p in c(.8,1,1.2)) for (q in c(.8,1,1.2)) if(p!=1 || q!=1) {
  grid<-rbind(grid,copy(base)[,`:=`(scenario=paste0("size_",p,"_",q),public_multiplier=p,private_multiplier=q)])
}
grid[,`:=`(n_public=round(390*public_multiplier),n_private=round(910*private_multiplier))]
R<-2000L
summaries<-list(); baseline_draws<-NULL
for(i in seq_len(nrow(grid))) {
  if(as.numeric(difftime(Sys.time(),started,units="mins"))>38) break
  g<-grid[i]
  z<-matrix(NA_real_,R,4)
  done<-0L
  for(b in seq_len(R)) {
    a<-macro_sample(g$n_public,g$prevalence,g$auc,g$latent_rho)
    d<-macro_sample(g$n_private,g$prevalence,g$auc,g$latent_rho)
    z[b,]<-c(a$auc,d$auc,a$label_correlation,d$label_correlation); done<-b
    if(b%%100==0 && as.numeric(difftime(Sys.time(),started,units="mins"))>39) break
  }
  z<-z[seq_len(done),,drop=FALSE]
  valid<-is.finite(z[,1])&is.finite(z[,2]); zz<-z[valid,,drop=FALSE]
  if(nrow(zz)<100) next
  difference<-zz[,2]-zz[,1]
  weighted<-(g$n_public*zz[,1]+g$n_private*zz[,2])/(g$n_public+g$n_private)
  # Independent batches give Monte Carlo SE for variance and SD without Gaussian assumptions.
  k<-min(20L,floor(nrow(zz)/50))
  batches<-split(seq_len(nrow(zz)),rep(seq_len(k),length.out=nrow(zz)))
  batch_var<-vapply(batches,function(j)var(difference[j]),numeric(1))
  batch_sd<-vapply(batches,function(j)sd(difference[j]),numeric(1))
  v<-var(difference); vmc<-sd(batch_var)/sqrt(k)
  s<-sd(difference); smc<-sd(batch_sd)/sqrt(k)
  summaries[[i]]<-cbind(g,data.table(replicates_attempted=done,replicates_valid=nrow(zz),undefined_macro=done-nrow(zz),
    mean_public=mean(zz[,1]),mean_private=mean(zz[,2]),mean_difference=mean(difference),
    mean_difference_mcse=s/sqrt(nrow(zz)),sd_public=sd(zz[,1]),sd_private=sd(zz[,2]),
    sd_difference=s,sd_difference_mcse=smc,variance_difference=v,variance_mcse=vmc,
    variance_mc_lower=max(0,v-1.96*vmc),variance_mc_upper=v+1.96*vmc,
    realized_label_correlation=mean(zz[,3:4]),cor_weighted_mean_difference=cor(weighted,difference),
    difference_q025=unname(quantile(difference,.025)),difference_q975=unname(quantile(difference,.975)),
    evidence_type="synthetic_sampling_benchmark",observed_variance=NA_real_,excess_variance_ratio=NA_real_))
  if(g$scenario=="baseline") baseline_draws<-difference
  message("Completed synthetic scenario ",i,"/",nrow(grid)," (",done," replicates)")
}
if(!length(summaries)) stop("No completed scenario; no results emitted.")
result<-rbindlist(summaries)
fwrite(result,file.path(outdir,"T3_sampling_benchmark.csv"),na="")
saveRDS(list(grid=grid,baseline_draws=baseline_draws),file.path(dest,"sampling-benchmark-draws.rds"))
# F2's observed overlay is deliberately not drawn until paired leaderboard data exist.
png(file.path(figdir,"F2_sampling_reference_only.png"),width=1500,height=1050,res=170)
par(mar=c(5,5,5,2))
hist(baseline_draws,breaks=40,probability=TRUE,col="#a8c6dd",border="white",
     xlab="Simulated private - public macro AUC",main="Sampling reference: no leaderboard data overlay")
abline(v=0,lty=2,col="#444444")
lines(density(baseline_draws),col="#1f5a85",lwd=2)
mtext("Synthetic only | 12 findings | n=390/910 | AUC=0.95 | prevalence=0.15 | latent rho=0.3",side=3,line=.3,cex=.65)
dev.off()
write_json(list(sap_commit=approval$sap_commit,seed=2026102901,R=R,
  scenarios_completed=nrow(result),scenarios_planned=nrow(grid),
  started_utc=format(started,tz="UTC",usetz=TRUE),finished_utc=format(Sys.time(),tz="UTC",usetz=TRUE),
  elapsed_minutes=as.numeric(difftime(Sys.time(),started,units="mins")),
  status="synthetic_reference_only_no_observed_variance_ratio",R_version=as.character(getRversion())),
  file.path(outdir,"sampling-run.json"),pretty=TRUE,auto_unbox=TRUE)
