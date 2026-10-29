source("core.R")
ctx<-guard();started<-Sys.time();dat<-read_inputs(ctx)
old<-dat$old;new<-old;moderate<-matrix(NA_real_,4349,12)
known<-codes<-list()
mapping<-fread("definition-map.csv")
gate<-mapping[,.(alignable_sources=sum(status=="documented_alignment")),by=.(target,finding)]
gate[,lcm_permitted:=lcm_allowed(alignable_sources)]
stopifnot(!any(gate$lcm_permitted))
fwrite(gate,file.path(out_dir,"alignment-eligibility.csv"))
for(f in 1:12) {
  yp<-yunus_map(dat$tables[[4]][[findings[f]]]);ym<-yunus_map(dat$tables[[4]][[findings[f]]],TRUE)
  new[,4,f]<-yp$y;moderate[,f]<-ym$y
  x<-dat$tables[[4]][[findings[f]]]
  codes[[f]]<-data.table(finding=findings[f],value=ifelse(is.na(x),"NA",sprintf("%.12g",x)),
      status=ifelse(yp$undocumented,"undocumented",ifelse(yp$unknown,"unknown","documented_known")))[,.N,by=.(finding,value,status)]
  for(j in c(3,4)) known[[length(known)+1]]<-data.table(finding=findings[f],source=source_names[j],target="any_affirmed",cohort_n=4349,
    old_known_n=sum(!is.na(old[,j,f])),new_known_n=sum(!is.na(new[,j,f])),
    old_positive_n=sum(old[,j,f]==1,na.rm=TRUE),new_positive_n=sum(new[,j,f]==1,na.rm=TRUE),
    common_known_n=sum(!is.na(old[,j,f])&!is.na(new[,j,f])))
  known[[length(known)+1]]<-data.table(finding=findings[f],source="Yunus",target="moderate_or_greater",cohort_n=4349,
    old_known_n=sum(!is.na(old[,4,f])),new_known_n=sum(!is.na(moderate[,f])),
    old_positive_n=sum(old[,4,f]==1,na.rm=TRUE),new_positive_n=sum(moderate[,f]==1,na.rm=TRUE),
    common_known_n=sum(!is.na(old[,4,f])&!is.na(moderate[,f])))
}
fwrite(rbindlist(known),file.path(out_dir,"alignment-denominators.csv"))
fwrite(rbindlist(codes),file.path(out_dir,"yunus-code-counts.csv"))
# Reconstruct all legacy aggregate point estimates and complete pattern counts.
legacy<-fread("../../results/T4_agreement.csv")
legacy_patterns<-fread("../../results/T6_pattern_checks.csv",colClasses=c(pattern="character"))
max_error<-0;calibration<-patterns<-list()
for(f in 1:12) {
  pt<-pattern_table(old[,,f]);v<-weighted_stats(pt$y,pt$count)
  want<-legacy[finding==findings[f]]
  key<-paste(want$metric,want$source_a,sep="|")
  ix<-nzchar(want$source_b);key[ix]<-paste(key[ix],want$source_b[ix],sep="|")
  stopifnot(all(key %in% names(v)),identical(is.na(unname(v[key])),is.na(want$estimate)))
  err<-max(abs(v[key]-want$estimate),na.rm=TRUE);max_error<-max(max_error,err);stopifnot(err<1e-10)
  complete<-complete.cases(old[,,f]);counts<-pattern_counts(old[complete,,f]);p<-counts/sum(counts)
  namesp<-apply(bin_patterns,1,paste0,collapse="")
  lp<-legacy_patterns[finding==findings[f]]
  stopifnot(all(counts[match(lp$pattern,namesp)]==lp$observed_count))
  patterns[[f]]<-data.table(finding=findings[f],pattern=namesp,observed_count=counts,probability=p,
     majority=pattern_votes$major,retained=pattern_votes$keep,g2_tie=pattern_votes$g2_tie,group_disagree=pattern_votes$group_disagree)
  n<-sum(counts);nplus<-sum(counts*pattern_votes$major)
  calibration[[f]]<-data.table(finding=findings[f],cohort_n=4349,complete_n=n,excluded_n=4349-n,reference_positive_n=nplus,
    reference_positive_fraction=nplus/n,observed_retained_n=sum(counts*pattern_votes$keep),
    retained_fraction=sum(p*pattern_votes$keep),g2_tie_fraction=sum(p*pattern_votes$g2_tie),
    between_group_disagreement_fraction=sum(p*pattern_votes$group_disagree),
    scenario_prevalence_proxy=sum(p*(pattern_votes$g1+pattern_votes$g2)/2),
    simulation_eligible=n>=100 & min(nplus,n-nplus)>=5)
}
fwrite(rbindlist(patterns),file.path(out_dir,"simulation-pattern-calibration.csv"))
fwrite(rbindlist(calibration),file.path(out_dir,"simulation-cohort.csv"))
# Fixed samples for before/after comparisons; one joint cohort resample per draw.
fixed<-lapply(1:12,function(f) complete.cases(cbind(old[,c(3,4),f],new[,c(3,4),f])))
fixed_mod<-lapply(1:12,function(f) !is.na(old[,4,f])&!is.na(moderate[,f]))
points<-lapply(1:12,function(f) {
  use<-fixed[[f]]
  a<-pair_stats(old[use,3,f],old[use,4,f]);b<-pair_stats(new[use,3,f],new[use,4,f])
  list(before=a,after=b,change=b-a)
})
B<-2000L;set.seed(seed32(20261029041))
boot<-array(NA_real_,c(B,5,12));boot_mod<-matrix(NA_real_,B,12)
for(b in seq_len(B)) {
  ix<-sample.int(4349,4349,replace=TRUE)
  for(f in 1:12) {
    k<-ix[fixed[[f]][ix]]
    boot[b,,f]<-pair_stats(new[k,3,f],new[k,4,f])-pair_stats(old[k,3,f],old[k,4,f])
    m<-ix[fixed_mod[[f]][ix]];boot_mod[b,f]<-mean(moderate[m,f]-old[m,4,f])
  }
}
align<-rbindlist(lapply(1:12,function(f) rbindlist(lapply(1:5,function(k) {
  z<-boot[,k,f];nv<-sum(is.finite(z));ci<-if(nv>=.8*B) quantile(z,c(.025,.975),na.rm=TRUE,names=FALSE) else c(NA,NA)
  data.table(finding=findings[f],target="any_affirmed",source_a="Pilkwang",source_b="Yunus",common_n=sum(fixed[[f]]),
    metric=names(points[[f]]$before)[k],before=points[[f]]$before[k],after=points[[f]]$after[k],change=points[[f]]$change[k],
    change_lower=ci[1],change_upper=ci[2],bootstrap_valid=nv,bootstrap_attempted=B)
}))))
fwrite(align,file.path(out_dir,"alignment-paired-changes.csv"),na="")
mod<-rbindlist(lapply(1:12,function(f) {
  k<-fixed_mod[[f]];z<-boot_mod[,f];nv<-sum(is.finite(z));ci<-if(nv>=.8*B) quantile(z,c(.025,.975),na.rm=TRUE) else c(NA,NA)
  data.table(finding=findings[f],target="moderate_or_greater",source="Yunus",common_n=sum(k),
    before=mean(old[k,4,f]),after=mean(moderate[k,f]),change=mean(moderate[k,f]-old[k,4,f]),
    change_lower=ci[1],change_upper=ci[2],bootstrap_valid=nv,bootstrap_attempted=B)
}))
fwrite(mod,file.path(out_dir,"alignment-moderate-single-source.csv"),na="")
# All-five context remains explicitly non-harmonized; comparisons have fixed pair samples.
context<-rbindlist(lapply(1:12,function(f) rbindlist(lapply(1:ncol(pairs),function(k) {
  js<-pairs[,k];use<-complete.cases(cbind(old[,js,f],new[,js,f]))
  a<-binary_agreement(old[use,js[1],f],old[use,js[2],f]);b<-binary_agreement(new[use,js[1],f],new[use,js[2],f])
  data.table(finding=findings[f],source_a=source_names[js[1]],source_b=source_names[js[2]],common_n=sum(use),
    before_agreement=a["agreement"],after_agreement=b["agreement"],change_agreement=b["agreement"]-a["agreement"],
    before_kappa=a["kappa"],after_kappa=b["kappa"],change_kappa=b["kappa"]-a["kappa"],
    interpretation="non-harmonized sensitivity; other three sources retain operational codes")
}))))
fwrite(context,file.path(out_dir,"nonharmonized-five-source-context.csv"),na="")
saveRDS(list(boot=boot,boot_moderate=boot_mod),file.path(ctx$work,"alignment-bootstrap.rds"))
write_run("alignment-run.json",started,list(seed_label=20261029041,seed_R=seed32(20261029041),bootstrap_replicates=B,
  cohort_n=4349,all_frozen_hashes_pass=TRUE,all_source_hashes_pass=TRUE,legacy_max_point_error=max_error,
  legacy_pattern_counts_exact=TRUE,new_lcm_fits=0))
message("Alignment completed; all legacy points/patterns reconstructed; no LCM fitted.")
