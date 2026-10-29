# Presentation only: run from the project directory; uses unchanged aggregate results.
library(data.table)
library(ggplot2)
x <- fread("results/v1.4/simulation-summary.csv")
scenarios <- c("no_inheritance", "equal_true_auc", "swap_training_groups")
x <- x[method == "full_direct" & scenario %in% scenarios]
stopifnot(nrow(x) == 36L, all(x$target_auc_A == .85), all(x$target_auc_B == .85))
finding_order <- unique(x$finding[x$scenario == "equal_true_auc"])
x[, scenario_index := match(scenario, scenarios)]
# Deterministic horizontal spacing makes all 12 finding-level points visible.
x[, point_x := scenario_index + (match(finding, finding_order) - 6.5) * .028]
x[, finding_group := fifelse(finding == "Medial Meniscus", "Medial meniscus",
                      fifelse(finding == "Lateral Meniscus", "Lateral meniscus", "Other findings"))]
x[, finding_group := factor(finding_group, levels=c("Other findings", "Medial meniscus", "Lateral meniscus"))]
p <- ggplot(x, aes(x=point_x, y=100*p_select_A_estimate, color=finding_group, shape=finding_group)) +
  geom_hline(yintercept=50, linetype=2, color="grey60", linewidth=.5) +
  geom_point(size=3.3, alpha=.9) +
  scale_color_manual(NULL, values=c("#087e8b", "#c05d43", "#7855a2")) +
  scale_shape_manual(NULL, values=c(16,17,15)) +
  scale_x_continuous(breaks=1:3, limits=c(.65,3.35), labels=c(
    "No inherited style\nInheritance variance = 0",
    "A inherits G1; B inherits G2\nInheritance variance = 0.5",
    "A inherits G2; B inherits G1\nInheritance variance = 0.5")) +
  scale_y_continuous(breaks=seq(0,100,25), limits=c(-3,103)) +
  labs(x=NULL, y="Probability of selecting model A (%)",
    title="Majority-reference selection follows inherited label style",
    subtitle="Equal full-population true AUCs (0.85); direct five-source majority reference",
    caption=paste(
      "Each point is one finding. G1: Steven/Pilkwang/Lixin; G2: Dread/Yunus.",
      "1,000 control replicates and 2,000 primary replicates per finding. Both meniscus exceptions are retained.",
      "Mechanism illustration under assumed truth and score errors; magnitudes do not estimate actual competition bias.", sep="\n")) +
  theme_minimal(base_size=12) +
  theme(panel.grid.minor=element_blank(), panel.grid.major.x=element_blank(),
    plot.title=element_text(face="bold"), axis.text.x=element_text(size=10),
    legend.position="bottom", plot.caption=element_text(hjust=0,size=9.5))
ggsave("figures/v1.4/majority-style-controls.png",p,width=11,height=6.5,dpi=180,bg="white")
