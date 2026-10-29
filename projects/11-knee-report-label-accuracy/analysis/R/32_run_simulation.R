source("R/common.R")
source("R/31_paired_simulation.R")
library(data.table)
library(jsonlite)
dest<-external_data_dir();approval<-require_sap_approval(dest)
stopifnot(approval$sap_commit=="968c2a9cdb3be5978bbeed5128bad8ba843985f9")
started<-Sys.time();out<-"../results"
grid<-CJ(n=c(58L,977L),rho=c(0,.2));results<-ordering<-dgm<-list()
methods<-c("naive","oracle_correction","independent_expert_n58")
estimands<-c("AUC_A","AUC_B","delta");truth<-c(.90,.91,.01)
factor<-mixture_factor(.15,.85,.85)
for(g in seq_len(nrow(grid))) {
  set.seed(2026102807+g)
  z<-array(NA_real_,c(20000,3,3,3),dimnames=list(NULL,methods,estimands,c("estimate","lower","upper")))
  total<-c(N=0,positive=0,tp=0,tn=0,negative=0);done<-0L;target<-2000L
  repeat {
    for(b in (done+1L):target) {
      x<-simulate_pair(grid$n[g],rho=grid$rho[g]);v<-paired_bootstrap(x$label,x$score)
      z[b,1,,]<-v;z[b,2,1:2,]<-.5+(v[1:2,]-.5)/factor;z[b,2,3,]<-v[3,]/factor
      expert<-simulate_pair(58,rho=grid$rho[g]);z[b,3,,]<-paired_bootstrap(expert$y,expert$score)
      total<-total+c(grid$n[g],sum(x$y),sum(x$y==1 & x$label==1),sum(x$y==0 & x$label==0),sum(x$y==0))
      done<-b
      if(b%%250==0) {
        message("C n=",grid$n[g]," rho=",grid$rho[g],": ",b," replicates")
        if(as.numeric(difftime(Sys.time(),started,units="mins"))>38) break
      }
    }
    mc<-vapply(1:3,function(m)max(vapply(1:3,function(e) sd(z[seq_len(done),m,e,1],na.rm=TRUE)/sqrt(sum(is.finite(z[seq_len(done),m,e,1]))),numeric(1))),numeric(1))
    if(all(mc<.005)||done>=20000||as.numeric(difftime(Sys.time(),started,units="mins"))>38) break
    target<-min(done+2000L,20000L)
  }
  z<-z[seq_len(done),,,,drop=FALSE]
  # Positive common scaling cannot alter ordering. Verify numerically every run.
  stopifnot(identical(z[,1,3,1]>0,z[,2,3,1]>0))
  saveRDS(z,file.path(dest,paste0("C-replicates-",g,".rds")))
  for(m in 1:3) for(e in 1:3) {
    s<-simulation_summary(z[,m,e,],truth[e]);good<-is.finite(z[,m,e,1]);n<-sum(good)
    outside<-if(e<=2)mean(z[good,m,e,1]<0|z[good,m,e,1]>1) else mean(abs(z[good,m,e,1])>1)
    results[[length(results)+1L]]<-cbind(grid[g],data.table(method=methods[m],estimand=estimands[e]),s,
      data.table(out_of_range=outside,out_of_range_mcse=sqrt(outside*(1-outside)/n)))
  }
  for(m in 1:3) {
    delta<-z[,m,3,1];ok<-is.finite(delta);ci<-is.finite(z[,m,3,2]);p<-mean(delta[ok]>0)
    ties<-mean(delta[ok]==0);reverse<-mean(delta[ok]<0);superior<-mean(z[ci,m,3,2]>0)
    ordering[[length(ordering)+1L]]<-cbind(grid[g],data.table(method=methods[m],attempted=done,valid=sum(ok),
      correct_order=p,correct_order_mcse=sqrt(p*(1-p)/sum(ok)),tie_rate=ties,
      reversed_order=reverse,superiority_rate=superior,intervals_valid=sum(ci),
      tie_mcse=sqrt(ties*(1-ties)/sum(ok)),reversal_mcse=sqrt(reverse*(1-reverse)/sum(ok)),
      superiority_mcse=sqrt(superior*(1-superior)/sum(ci))))
  }
  dgm[[g]]<-cbind(grid[g],data.table(replicates=done,realized_prevalence=total["positive"]/total["N"],
    realized_sensitivity=total["tp"]/total["positive"],realized_specificity=total["tn"]/total["negative"],
    correction_factor=factor,max_bias_mcse=max(mc),target_mcse_met=all(mc<.005)))
  fwrite(rbindlist(results),file.path(out,"T7_simulation.csv"),na="")
  fwrite(rbindlist(ordering),file.path(out,"T7_ordering.csv"),na="")
  fwrite(rbindlist(dgm),file.path(out,"T7_dgm.csv"),na="")
  if(as.numeric(difftime(Sys.time(),started,units="mins"))>38) break
}
write_json(list(sap_commit=approval$sap_commit,seed_base=2026102807,bootstrap_replicates=399,
 prevalence=.15,sensitivity=.85,specificity=.85,auc_a=.90,auc_b=.91,score_residual_correlation=.8,
 scenarios_completed=length(dgm),scenarios_planned=4,elapsed_minutes=as.numeric(difftime(Sys.time(),started,units="mins")),
 completed_utc=format(Sys.time(),tz="UTC",usetz=TRUE),evidence="synthetic only; oracle parameters known; no Gold58 observations"),
 file.path(out,"simulation-run.json"),auto_unbox=TRUE,pretty=TRUE)
