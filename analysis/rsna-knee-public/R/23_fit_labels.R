source("R/common.R")
source("R/22_latent_model.R")
library(data.table)
library(jsonlite)
stopifnot(requireNamespace("posterior",quietly=TRUE))
dest<-external_data_dir();approval<-require_sap_approval(dest)
stopifnot(approval$sap_commit=="968c2a9cdb3be5978bbeed5128bad8ba843985f9")
started<-Sys.time();out<-"../../results/rsna-knee-public"
x<-readRDS(file.path(dest,"aligned-primary-labels.rds"));patterns<-binary_patterns(5)
summaries<-eligibility<-ppc<-pattern_ppc<-list();counter<-0L
prior_settings<-list(primary_beta22=c(2,2),uniform_beta11=c(1,1),optimistic_beta42=c(4,2))
for(f in seq_along(findings)) {
  y<-x$labels[,,f];y<-y[complete.cases(y),,drop=FALSE];N<-nrow(y)
  eligible<-N>=100 && all(colSums(y)>=5 & colSums(1-y)>=5)
  eligibility[[f]]<-data.table(finding=findings[f],complete_case_n=N,eligible=eligible,
    reason=if(eligible)"eligible" else "fewer than 100 complete studies or a source has fewer than five labels in either class")
  if(!eligible) next
  counts<-tabulate(1L+rowSums(y*rep(2^(0:4),each=N)),32)
  for(pr in seq_along(prior_settings)) {
    # Each completed fit is checkpointed; never silently exceed the total cap.
    if(as.numeric(difftime(Sys.time(),started,units="mins"))>35) stop("Latent fit budget reached; retain completed checkpoints outside checkout.")
    d<-fit_latent(counts,patterns,accuracy_prior=prior_settings[[pr]],seed=2026102803+100*f+10*pr)
    s<-latent_summary(d);extended<-FALSE
    if(any(!is.finite(s$rhat)|s$rhat>=1.01|s$ess_bulk<400|s$ess_tail<400)) {
      d<-fit_latent(counts,patterns,accuracy_prior=prior_settings[[pr]],iterations=12000L,warmup=4000L,seed=2026102803+100*f+10*pr)
      s<-latent_summary(d);extended<-TRUE
    }
    counter<-counter+1L
    s[,`:=`(finding=findings[f],prior=names(prior_settings)[pr],complete_case_n=N,extended=extended)]
    s[,source:="all"]
    s[parameter!="prevalence",source:=x$source_names[as.integer(sub(".*_","",parameter))]]
    s[,diagnostics_pass:=all(is.finite(rhat)&rhat<1.01&ess_bulk>=400&ess_tail>=400)]
    summaries[[counter]]<-s
    saveRDS(d,file.path(dest,paste0("latent-",f,"-",pr,".rds")))
    if(pr==1L) {
      # Replicate full response counts, including zero-count patterns, at posterior draws.
      set.seed(2026102903+f)
      pooled<-matrix(d,ncol=11);take<-sample.int(nrow(pooled),2000)
      pp<-rp<-matrix(NA_real_,2000,32);stats<-matrix(NA_real_,2000,2)
      for(b in seq_along(take)) {
        z<-pooled[take[b],];p<-pattern_probabilities(patterns,z[1],z[2:6],z[7:11]);expected<-N*p
        repcount<-as.numeric(rmultinom(1,N,p));pp[b,]<-p;rp[b,]<-repcount/N
        stats[b,]<-c(sum((counts-expected)^2/(expected+.5)),sum((repcount-expected)^2/(expected+.5)))
      }
      ppc[[f]]<-data.table(finding=findings[f],complete_case_n=N,discrepancy="Pearson pattern counts, expected+0.5 denominator",
        posterior_predictive_p=mean(stats[,2]>=stats[,1]),draws=2000,
        observed_discrepancy_median=median(stats[,1]),replicated_discrepancy_median=median(stats[,2]))
      pattern_ppc[[f]]<-data.table(finding=findings[f],pattern=apply(patterns,1,paste0,collapse=""),observed_count=counts,
        expected_proportion=colMeans(pp),predictive_lower=apply(rp,2,quantile,.025),predictive_upper=apply(rp,2,quantile,.975))
      # Pairwise agreement checks use the same posterior predictive replicates.
      pair<-combn(5,2)
      for(k in seq_len(ncol(pair))) {
        same<-as.numeric(patterns[,pair[1,k]]==patterns[,pair[2,k]])
        q<-as.numeric(rp %*% same)
        ppc[[length(findings)+10*(f-1)+k]]<-data.table(finding=findings[f],complete_case_n=N,
          discrepancy=paste0("pair_agreement:",x$source_names[pair[1,k]],":",x$source_names[pair[2,k]]),
          posterior_predictive_p=mean(q>=sum(counts*same)/N),draws=2000,
          observed_discrepancy_median=sum(counts*same)/N,replicated_discrepancy_median=median(q))
      }
    }
    message("LCM ",findings[f]," ",names(prior_settings)[pr]," diagnostics=",s$diagnostics_pass[1])
  }
}
fwrite(rbindlist(summaries),file.path(out,"T6_latent_parameters.csv"),na="")
fwrite(rbindlist(eligibility),file.path(out,"T6_eligibility.csv"))
fwrite(rbindlist(ppc),file.path(out,"T6_predictive_checks.csv"),na="")
fwrite(rbindlist(pattern_ppc),file.path(out,"T6_pattern_checks.csv"),na="")
write_json(list(sap_commit=approval$sap_commit,seed=2026102803,chains=4,iterations=6000,warmup=2000,
 extension_iterations=12000,extension_warmup=4000,model="conditional independence; complete cases; positive average Youden orientation",
 fits_completed=counter,elapsed_minutes=as.numeric(difftime(Sys.time(),started,units="mins")),
 completed_utc=format(Sys.time(),tz="UTC",usetz=TRUE),posterior_version=as.character(packageVersion("posterior"))),
 file.path(out,"latent-run.json"),auto_unbox=TRUE,pretty=TRUE)
