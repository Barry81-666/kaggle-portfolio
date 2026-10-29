# Post-hoc figures: aggregate similarity and synthetic interval sensitivity.
library(data.table);library(ggplot2)
source("R/common.R");source("R/20_labels.R")
out<-"../../results/rsna-knee-public";fig<-"../../figures/rsna-knee-public"
theme_set(theme_minimal(base_size=11)+theme(panel.grid.minor=element_blank(),plot.title.position="plot"))
k<-fread(file.path(out,"T5_clusters.csv"))[variant=="mean_paired"]
m<-matrix(1,5,5,dimnames=list(source_names,source_names))
for(j in seq_len(nrow(k)))m[k$source_a[j],k$source_b[j]]<-m[k$source_b[j],k$source_a[j]]<-k$mean_or_median_kappa[j]
hc<-hclust(as.dist(1-m),method="average")
leafpos<-match(seq_len(5),hc$order);xx<-yy<-numeric(4);segments<-list()
for(i in 1:4) {
  children<-hc$merge[i,];x<-vapply(children,function(c)if(c<0)leafpos[-c]else xx[c],numeric(1));y<-vapply(children,function(c)if(c<0)0 else yy[c],numeric(1))
  xx[i]<-mean(x);yy[i]<-hc$height[i]
  segments[[i]]<-data.table(x=c(x,x[1]),xend=c(x,x[2]),y=c(y,yy[i]),yend=rep(yy[i],3))
}
seg<-rbindlist(segments)
p<-ggplot(seg)+geom_segment(aes(x=x,xend=xend,y=y,yend=yend),linewidth=.8,color="#285f6b")+
 scale_x_continuous(breaks=1:5,labels=hc$labels[hc$order])+expand_limits(y=0)+
 labs(title="Five label sources form two stable similarity groups",subtitle="Post-hoc average-linkage clustering: 1 - mean Cohen kappa across 12 equally weighted findings",
 x=NULL,y="Merge dissimilarity",caption="The k=2 partition is unchanged across 1,000 joint study bootstraps, median kappa and complete-case analysis.\nTwo clusters do not mean two statistically independent sources; k=2 was chosen after viewing the agreement heatmap.")+
 theme(panel.grid.major.x=element_blank(),plot.caption=element_text(hjust=0,size=9))
f<-fread(file.path(out,"T5_focus.csv"));f<-rbind(f[,.(finding,source_a,source_b,kappa)],f[,.(finding,source_a=source_b,source_b=source_a,kappa)],
 CJ(finding=c("Effusion","Synovitis"),source_a=source_names)[,.(finding,source_a,source_b=source_a,kappa=1)])
levels<-hc$labels[hc$order];f[,source_a:=factor(source_a,levels=levels)];f[,source_b:=factor(source_b,levels=rev(levels))]
q<-ggplot(f,aes(source_a,source_b,fill=kappa))+geom_tile(color="white")+geom_text(aes(label=sprintf("%.2f",kappa)),size=3.4)+
 scale_fill_gradient(low="#faf6dc",high="#278a8a",limits=c(0,1),name="Cohen kappa")+facet_wrap(~finding)+
 labs(title="Effusion separates the groups most clearly",x=NULL,y=NULL,
 caption="Primary paired-known labels; denominators and 95% intervals are in the accompanying table. Synovitis Steven/Pilkwang: 605 paired studies.\nThese marginal agreements do not establish copying, conditional dependence or imaging accuracy.")+
 theme(panel.grid=element_blank(),plot.caption=element_text(hjust=0,size=9))
png(file.path(fig,"F5c_source_clusters.png"),width=2100,height=1700,res=180,bg="white")
grid::grid.newpage();grid::pushViewport(grid::viewport(layout=grid::grid.layout(2,1,heights=c(.48,.52))))
print(p,vp=grid::viewport(layout.pos.row=1));print(q,vp=grid::viewport(layout.pos.row=2));dev.off()
a<-fread(file.path(out,"T8_interval_sensitivity.csv"))
names<-c(bootstrap_399="Percentile bootstrap\n399 resamples",bootstrap_1999="Percentile bootstrap\n1,999 resamples",delong_normal="DeLong normal",delong_logit="DeLong + logit")
a[,method:=factor(method,levels=names(names),labels=names)]
b<-rbind(a[,.(method,type="Coverage among valid intervals",value=coverage,se=coverage_mcse)],
 a[,.(method,type="Successful coverage / all attempts",value=successful_coverage,se=successful_coverage_mcse)])
p<-ggplot(b,aes(method,value,color=type))+geom_hline(yintercept=.95,linetype=2,color="grey35")+
 geom_point(position=position_dodge(width=.35),size=2.6)+geom_errorbar(aes(ymin=value-1.96*se,ymax=value+1.96*se),width=.15,position=position_dodge(width=.35))+
 scale_color_manual(values=c("#247c85","#b35038"),name=NULL)+scale_y_continuous(labels=function(x)paste0(round(x*100),"%"),limits=c(.80,.97))+
 labs(title="More bootstrap draws barely help; the interval method matters",subtitle="Post-hoc: 4,000 synthetic expert samples, n = 58, prevalence = 15%, true AUC = 0.90",
 x=NULL,y="Nominal 95% interval coverage",caption="Bars: +/-1.96 Monte Carlo SE. Bootstrap draws are nested; all methods use the same samples.\nLogit intervals fail in 0.625% of attempts, versus 0.100% for other methods. No continuity correction; no real Gold58 data.")+
 theme(legend.position="bottom",plot.caption=element_text(hjust=0,size=9))
ggsave(file.path(fig,"F8_interval_sensitivity.png"),p,width=11.5,height=6,dpi=180,bg="white")
