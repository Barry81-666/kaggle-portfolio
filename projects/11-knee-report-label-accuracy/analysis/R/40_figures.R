library(data.table)
library(ggplot2)
source("R/common.R")
out<-"../results";fig<-"../figures"
dir.create(fig,recursive=TRUE,showWarnings=FALSE)
theme_set(theme_minimal(base_size=11)+theme(panel.grid.minor=element_blank(),plot.title.position="plot"))
a<-fread(file.path(out,"T4_agreement.csv"))[metric=="kappa"]
a[,pair:=paste(source_a,source_b,sep=" / ")];a[,finding:=factor(finding,rev(findings))]
p<-ggplot(a,aes(pair,finding,fill=estimate))+geom_tile(color="white")+
 geom_text(aes(label=sprintf("%.2f",estimate)),size=3)+
 scale_fill_gradient(low="#faf6dc",high="#278a8a",limits=c(0,1),name="Cohen kappa")+
 labs(title="Agreement varies by finding and source pair",subtitle="Five report-label sources; pairwise-known studies within the 4,349-study intersection",
 x=NULL,y=NULL,caption="Agreement is not accuracy. Unknowns follow source-specific conventions; paired denominators vary.")+
 theme(axis.text.x=element_text(angle=45,hjust=1),panel.grid=element_blank())
ggsave(file.path(fig,"F5_label_agreement.png"),p,width=11,height=6.6,dpi=180,bg="white")
a<-fread(file.path(out,"T4_denominators.csv"));a[,unknown:=1-known_n/cohort_n];a[,finding:=factor(finding,rev(findings))]
p<-ggplot(a,aes(source,finding,fill=unknown))+geom_tile(color="white")+
 geom_text(aes(label=sprintf("%.1f%%",100*unknown)),size=3.2)+
 scale_fill_gradient(low="#f5f3ec",high="#cf8660",limits=c(0,1),name="Unknown fraction")+
 labs(title="Unmentioned findings sharply reduce complete-case samples",subtitle="Unknown includes source-documented abstentions; no undocumented code is invented",
 x=NULL,y=NULL,caption="Dread and Lixin have no documented unknown code. A full score table does not establish complete reporting.")+
 theme(panel.grid=element_blank())
ggsave(file.path(fig,"F5b_unknown_labels.png"),p,width=9,height=6.6,dpi=180,bg="white")
a<-fread(file.path(out,"T6_predictive_checks.csv"))[grepl("Pearson",discrepancy)&finding!="Synovitis"]
a[,finding:=factor(finding,rev(findings))]
b<-melt(a,id.vars="finding",measure.vars=c("observed_discrepancy_median","replicated_discrepancy_median"),variable.name="series")
b[,series:=ifelse(series=="observed_discrepancy_median","Observed data","Replicated under model")]
p<-ggplot(b,aes(value,finding,color=series))+geom_point(size=2.6)+scale_x_log10()+
 scale_color_manual(values=c("Observed data"="#a43b2b","Replicated under model"="#247c85"),name=NULL)+
 labs(title="Convergence does not rescue a poorly fitting independence model",
 subtitle="Median response-pattern discrepancy across 2,000 posterior predictive draws; 11 converged primary fits",
 x="Pearson discrepancy, expected-count denominator + 0.5 (log scale)",y=NULL,
 caption="Synovitis is excluded from this inference: its primary chains did not converge. Larger observed values indicate misfit.")+
 theme(legend.position="bottom")
ggsave(file.path(fig,"F6_model_misfit.png"),p,width=10,height=6.4,dpi=180,bg="white")
method_names<-c(naive="Naive imperfect labels",oracle_correction="Known-parameter correction",independent_expert_n58="Independent expert sample (n=58)")
a<-fread(file.path(out,"T7_simulation.csv"))[estimand=="AUC_A"]
a[,method:=factor(method,levels=names(method_names),labels=method_names)];a[,size:=paste0("Imperfect-label sample n = ",n)]
a[,dependence:=ifelse(rho==0,"Conditionally independent errors (rho = 0)","Score-dependent errors (rho = 0.2)")]
p<-ggplot(a,aes(method,bias,color=method))+geom_hline(yintercept=0,color="grey50",linetype=2)+
 geom_errorbar(aes(ymin=bias-1.96*bias_mcse,ymax=bias+1.96*bias_mcse),width=.15)+geom_point(size=2.5)+
 facet_grid(dependence~size)+scale_color_manual(values=c("#617f9c","#b35038","#28786c"),guide="none")+
 labs(title="More observations reduce noise, but cannot repair a false correction assumption",
 subtitle="Synthetic true AUC = 0.90; prevalence = 0.15; Se = Sp = 0.85; 2,000 replicates per cell",
 x=NULL,y="Mean estimated AUC minus true AUC",
 caption="Error bars are +/-1.96 Monte Carlo SE of bias, not study confidence intervals. Correction uses known parameters and is not clipped.")+
 theme(axis.text.x=element_text(angle=22,hjust=1,size=8),strip.text.y=element_text(size=9))
ggsave(file.path(fig,"F7_auc_bias.png"),p,width=12,height=7.5,dpi=180,bg="white")
a<-fread(file.path(out,"T7_ordering.csv"))[method!="oracle_correction"]
a[,method:=factor(method,levels=names(method_names),labels=method_names)];a[,dependence:=paste0("Error dependence rho = ",rho)]
p<-ggplot(a,aes(factor(n),correct_order,color=method,group=method))+geom_hline(yintercept=.5,linetype=2,color="grey50")+
 geom_line()+geom_point(size=2.5)+geom_errorbar(aes(ymin=correct_order-1.96*correct_order_mcse,ymax=correct_order+1.96*correct_order_mcse),width=.08)+
 facet_wrap(~dependence)+scale_color_manual(values=c("#617f9c","#28786c"),name=NULL)+
 coord_cartesian(ylim=c(.45,.72))+labs(title="A small true AUC difference remains difficult to order",
 subtitle="Synthetic AUCs 0.90 vs 0.91; paired-score residual correlation 0.8; 2,000 replicates per cell",
 x="Imperfect-label sample size (the independent expert comparator stays at n = 58)",y="Probability of strictly correct model order",
 caption="Bars: +/-1.96 Monte Carlo SE. Ties count as not strictly correct. Common positive correction leaves the order unchanged.")+
 theme(legend.position="bottom")
ggsave(file.path(fig,"F7b_model_ordering.png"),p,width=11,height=5.8,dpi=180,bg="white")
