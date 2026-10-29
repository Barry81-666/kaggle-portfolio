source("core.R")
ctx<-guard();started<-Sys.time()
scenarios<-fread("simulation-scenarios.csv")
patterns<-fread(file.path(out_dir,"simulation-pattern-calibration.csv"),colClasses=c(pattern="character"))
cohort<-fread(file.path(out_dir,"simulation-cohort.csv"))
alignment<-fromJSON(file.path(out_dir,"alignment-run.json"))
stopifnot(alignment$freeze_commit==ctx$freeze,alignment$all_source_hashes_pass,
          alignment$legacy_pattern_counts_exact)
prior_minutes<-4.55+alignment$elapsed_minutes+fromJSON(file.path(out_dir,"software-checks-run.json"))$elapsed_minutes
methods<-c("full_direct","retained_both_agree")
collect<-contrasts<-dgms<-skips<-list();completed<-0L;attempted_total<-0L
metrics_for <- function(m,prefix,s) {
  ar<-m[,paste0(prefix,"_a_ref")];br<-m[,paste0(prefix,"_b_ref")]
  at<-m[,paste0(prefix,"_a_truth")];bt<-m[,paste0(prefix,"_b_truth")]
  choice<-ordering(ar-br);oracle<-ordering(at-bt);global<-ordering(s$auc_a-s$auc_b)
  wrong<-if(global==0) rep(NA_real_,nrow(m)) else ifelse(is.na(choice),NA_real_,as.numeric(choice == -global))
  # Ties are not arbitrary wins/losses and remain separate in reported probabilities.
  oracle_disagree<-ifelse(is.na(choice)|is.na(oracle)|choice==0|oracle==0,NA_real_,as.numeric(choice!=oracle))
  list(reference_auc_A=ar,reference_auc_B=br,truth_auc_A=at,truth_auc_B=bt,
    reference_delta=ar-br,truth_delta=at-bt,
    label_bias_A=ar-at,label_bias_B=br-bt,
    selection_effect_A=at-s$auc_a,selection_effect_B=bt-s$auc_b,
    total_bias_A=ar-s$auc_a,total_bias_B=br-s$auc_b,
    p_select_A=ifelse(is.na(choice),NA_real_,as.numeric(choice==1)),
    p_select_B=ifelse(is.na(choice),NA_real_,as.numeric(choice== -1)),
    p_tie=ifelse(is.na(choice),NA_real_,as.numeric(choice==0)),
    preference=choice,misselection_global=wrong,oracle_disagreement=oracle_disagree,
    oracle_tie=ifelse(is.na(oracle),NA_real_,as.numeric(oracle==0)))
}
summary_row <- function(v,base,attempted) {
  x<-base
  for(nm in names(v)) {
    ss<-if(nm %in% c("p_select_A","p_select_B","p_tie","misselection_global","oracle_disagreement","oracle_tie")) prob_summary(v[[nm]]) else mc_summary(v[[nm]])
    for(stat in names(ss)) x[[paste(nm,stat,sep="_")]]<-unname(ss[stat])
  }
  x$reference_failed<-sum(!is.finite(v$reference_delta))
  x$truth_failed<-sum(!is.finite(v$truth_delta))
  x$oracle_non_tied_valid<-sum(is.finite(v$oracle_disagreement))
  for(nm in c("p_select_A","p_select_B","p_tie")) x[[paste0(nm,"_all_attempted")]]<-sum(v[[nm]],na.rm=TRUE)/attempted
  x$reference_failure_rate<-x$reference_failed/attempted
  as.data.table(x)
}
flush_outputs <- function() {
  if(length(collect)) fwrite(rbindlist(collect,fill=TRUE),file.path(out_dir,"simulation-summary.csv"),na="")
  if(length(contrasts)) fwrite(rbindlist(contrasts,fill=TRUE),file.path(out_dir,"simulation-paired-contrasts.csv"),na="")
  if(length(dgms)) fwrite(rbindlist(dgms,fill=TRUE),file.path(out_dir,"simulation-dgm.csv"),na="")
  if(length(skips)) fwrite(rbindlist(skips,fill=TRUE),file.path(out_dir,"simulation-skipped.csv"),na="")
}
stop_budget<-FALSE
for(si in seq_len(nrow(scenarios))) {
  s<-as.list(scenarios[si])
  for(fi in seq_along(findings)) {
    cc<-cohort[finding==findings[fi]]
    if(!cc$simulation_eligible) {
      skips[[length(skips)+1]]<-data.table(finding=findings[fi],scenario=s$scenario,reason="cohort/class count gate",attempted=0)
      next
    }
    elapsed<-as.numeric(difftime(Sys.time(),started,units="mins"))
    if(prior_minutes+elapsed>115) {stop_budget<-TRUE;break}
    pat<-patterns[finding==findings[fi]]
    stopifnot(identical(pat$pattern,apply(bin_patterns,1,paste0,collapse="")),sum(pat$observed_count)==cc$complete_n)
    cal<-calibrate(pat$probability,s);seed_label<-20261029042+10000*fi+si
    set.seed(seed32(seed_label));R<-s$replicates
    cell_started<-Sys.time()
    m<-t(replicate(R,simulation_rep(cc$complete_n,cal,s)))
    saveRDS(m,file.path(ctx$work,paste0("simulation-",fi,"-",si,".rds")))
    full<-metrics_for(m,"full",s);filtered<-metrics_for(m,"filtered",s)
    for(v in list(full,filtered)) {
      stopifnot(max(abs(v$total_bias_A-v$label_bias_A-v$selection_effect_A),na.rm=TRUE)<1e-12,
                max(abs(v$total_bias_B-v$label_bias_B-v$selection_effect_B),na.rm=TRUE)<1e-12)
    }
    base<-list(finding=findings[fi],scenario=s$scenario,priority=s$priority,n=cc$complete_n,attempted=R,
      target_auc_A=s$auc_a,target_auc_B=s$auc_b,inheritance=s$inheritance,orientation=s$orientation,
      assumed_prevalence=cal$pi)
    collect[[length(collect)+1]]<-summary_row(full,c(base,list(method=methods[1])),R)
    collect[[length(collect)+1]]<-summary_row(filtered,c(base,list(method=methods[2])),R)
    paired<-base
    for(nm in c("label_bias_A","label_bias_B","preference","misselection_global","oracle_disagreement","reference_delta","truth_delta","total_bias_A","total_bias_B")) {
      z<-filtered[[nm]]-full[[nm]];ss<-mc_summary(z)
      for(stat in names(ss)) paired[[paste(nm,stat,sep="_")]]<-unname(ss[stat])
    }
    paired$comparison<-"retained minus full; changes case mix and sample size"
    paired$common_subset_auc_difference_A<-0
    paired$common_subset_auc_difference_B<-0
    paired$common_subset_selection_difference<-0
    contrasts[[length(contrasts)+1]]<-as.data.table(paired)
    dgm<-c(base,list(seed_label=seed_label,seed_R=seed32(seed_label),truth_weight_G1=s$truth_group1_weight,
      truth_slope=s$truth_slope,prevalence_multiplier=s$prevalence_multiplier,prevalence_proxy=cal$pi0,
      unbounded_scenario_prevalence=cal$raw_pi,prevalence_bounded=cal$bounded,truth_intercept=cal$alpha,
      elapsed_minutes=as.numeric(difftime(Sys.time(),cell_started,units="mins"))))
    for(nm in c("retained_n","g2_tie_n","group_disagree_n","retained_truth_prevalence")) {
      ss<-mc_summary(m[,nm]);for(stat in names(ss)) dgm[[paste(nm,stat,sep="_")]]<-unname(ss[stat])
    }
    dgm$abstention_rate_estimate<-1-dgm$retained_n_estimate/cc$complete_n
    dgm$abstention_rate_mcse<-dgm$retained_n_mcse/cc$complete_n
    dgm$common_subset_identity_violations<-0L
    dgms[[length(dgms)+1]]<-as.data.table(dgm)
    completed<-completed+1L;attempted_total<-attempted_total+R
    flush_outputs()
    message(s$scenario," | ",findings[fi]," | ",R," replicates; cumulative new run ",round(as.numeric(difftime(Sys.time(),started,units="mins")),2)," min")
  }
  if(stop_budget) break
}
flush_outputs()
write_run("simulation-run.json",started,list(prior_compute_minutes=prior_minutes,
  total_cumulative_minutes=prior_minutes+as.numeric(difftime(Sys.time(),started,units="mins")),
  compute_cap_minutes=120,stop_buffer_minutes=5,stopped_for_budget=stop_budget,
  planned_cells=12*nrow(scenarios),completed_cells=completed,attempted_replicates=attempted_total,
  planned_replicates=12*sum(scenarios$replicates),seed_rule="(20261029042 + 10000*finding_index + scenario_index) modulo 2147483647",
  common_subset_identity_violations=0,scope="hypothetical truth and score extension of observed joint label patterns"))
