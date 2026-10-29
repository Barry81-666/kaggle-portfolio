source("core.R")
library(ggplot2)
ctx<-guard()
figdir<-"../../figures/v1.4";dir.create(figdir,recursive=TRUE,showWarnings=FALSE)
theme_set(theme_minimal(base_size=12)+theme(panel.grid.minor=element_blank(),plot.title=element_text(face="bold"),
  legend.position="bottom",plot.caption=element_text(hjust=0,size=10)))
alignment<-fread(file.path(out_dir,"alignment-paired-changes.csv"))[metric=="agreement"]
alignment[,finding:=factor(finding,levels=rev(findings))]
a<-ggplot(alignment,aes(y=finding))+geom_segment(aes(x=100*before,xend=100*after,yend=finding),linewidth=1,color="#b8c4ca")+
  geom_point(aes(x=100*before,color="Original operational coding"),size=3)+
  geom_point(aes(x=100*after,color="Documented any-affirmed coding"),size=3)+
  scale_color_manual(NULL,values=c("Original operational coding"="#c05d43","Documented any-affirmed coding"="#087e8b"))+
  scale_x_continuous(limits=c(55,101),breaks=seq(60,100,10))+labs(x="Paired agreement (%)",y=NULL,
  title="Aligning report definitions changes apparent disagreement",
  subtitle="Pilkwang and Yunus; the same before/after-known studies for each finding",
  caption="Any-affirmed includes mild/trace. Pair n ranges from 599 to 3,990.\nAgreement is not diagnostic accuracy. Only two sources qualify; no new latent-class fit.")
ggsave(file.path(figdir,"definition-alignment.png"),a,width=10,height=6.8,dpi=180,bg="white")
s<-fread(file.path(out_dir,"simulation-summary.csv"))
e<-s[scenario=="equal_true_auc"]
e[,finding:=factor(finding,levels=rev(findings))]
e[,method_label:=factor(method,levels=c("full_direct","retained_both_agree"),labels=c("Direct majority: full sample","Both groups agree: retained sample"))]
p<-ggplot(e,aes(x=100*p_select_A_estimate,y=finding,color=method_label,shape=method_label))+
  geom_vline(xintercept=50,linetype=2,color="grey55")+
  geom_errorbar(aes(xmin=100*pmax(0,p_select_A_estimate-1.96*p_select_A_mcse),xmax=100*pmin(1,p_select_A_estimate+1.96*p_select_A_mcse)),orientation="y",width=.13,position=position_dodge(width=.35))+
  geom_point(size=2.7,position=position_dodge(width=.35))+
  scale_color_manual(NULL,values=c("#c05d43","#087e8b"))+scale_shape_manual(NULL,values=c(16,17))+
  scale_x_continuous(limits=c(0,100),breaks=seq(0,100,25))+labs(x="Probability of selecting model A (%)",y=NULL,
  title="Equal true AUC does not imply equal selection probability",
  subtitle="A inherits G1 style; B inherits G2 style; both full-population true AUCs = 0.85",
  caption="2,000 replicates/finding; bars are +/-1.96 Monte Carlo SE. Hypothetical truth/error assumptions.\nFiltering changes the evaluated population. On common retained cases, both references are identical.")
ggsave(file.path(figdir,"equal-auc-selection.png"),p,width=10,height=7,dpi=180,bg="white")
bias<-rbindlist(lapply(c("A","B"),function(m) e[,.(finding,method_label,model=m,
   estimate=get(paste0("label_bias_",m,"_estimate")),mcse=get(paste0("label_bias_",m,"_mcse")))]))
b<-ggplot(bias,aes(x=estimate,y=finding,color=method_label,shape=method_label))+
  geom_vline(xintercept=0,color="grey55",linetype=2)+
  geom_point(size=2.4,position=position_dodge(width=.35))+facet_wrap(~model,ncol=2,labeller=label_both)+
  scale_color_manual(NULL,values=c("#c05d43","#087e8b"))+scale_shape_manual(NULL,values=c(16,17))+
  labs(x="Consensus AUC minus synthetic-truth AUC on the same cases",y=NULL,
  title="Group filtering does not remove label-reference bias",
  subtitle="Primary equal-true-AUC scenario; separate from effects of selecting easier cases",
  caption="Synthetic truth is assumed, not observed disease status. Error bars omitted at this scale; MCSEs are in the tables.")
ggsave(file.path(figdir,"auc-label-bias.png"),b,width=12,height=7,dpi=180,bg="white")
u<-s[scenario %in% c("A_better","B_better")]
u[,finding:=factor(finding,levels=rev(findings))]
u[,method_label:=factor(method,levels=c("full_direct","retained_both_agree"),labels=c("Direct majority: full sample","Both groups agree: retained sample"))]
u[,scenario_label:=factor(scenario,levels=c("A_better","B_better"),labels=c("A better: 0.86 vs 0.85","B better: 0.85 vs 0.86"))]
q<-ggplot(u,aes(x=100*misselection_global_estimate,y=finding,color=method_label,shape=method_label))+
  geom_point(size=2.5,position=position_dodge(width=.35))+facet_wrap(~scenario_label,ncol=2)+
  scale_color_manual(NULL,values=c("#c05d43","#087e8b"))+scale_shape_manual(NULL,values=c(16,17))+
  scale_x_continuous(limits=c(0,100),breaks=c(0,25,50,75,100))+labs(x="Probability of choosing the lower full-population true-AUC model (%)",y=NULL,
  title="Filtering helps some comparisons and harms others",
  caption="2,000 replicates/finding/scenario. The retained population can have a different true ordering.\nPaired method contrasts and within-sample oracle disagreement are reported separately.")
ggsave(file.path(figdir,"unequal-auc-misselection.png"),q,width=12,height=7,dpi=180,bg="white")
message("Four review figures written.")
