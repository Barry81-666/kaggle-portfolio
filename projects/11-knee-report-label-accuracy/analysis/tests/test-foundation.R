# Run from projects/11-knee-report-label-accuracy/analysis. All observations below are synthetic.
source("R/common.R")
source("R/20_labels.R")
source("R/30_simulation.R")
set.seed(20261028)

stopifnot(binary_agreement(c(0,0,1,1),c(0,0,1,1))["kappa"]==1,
          binary_agreement(c(0,0,1,1),c(1,1,0,0))["kappa"]== -1,
          is.na(binary_agreement(rep(1,5),rep(1,5))["kappa"]),
          binary_agreement(c(0,1,NA),c(0,NA,1))["n"]==1)
z <- majority_disagreements(rbind(c(0,0,1),c(1,1,1)))
stopifnot(is.na(z[1,1]),is.na(z[1,2]),z[1,3]==1,all(z[2,]==0))
stopifnot(auc_rank(c(0,1),c(1,1))==.5,is.na(auc_rank(c(1,1),c(0,1))),
          correct_auc(.9,.2)>1,is.na(correct_auc(.9,.01)))
if (requireNamespace("pROC",quietly=TRUE)) {
  y<-rep(0:1,each=50); score<-round(rnorm(100)+y,1)
  expected<-as.numeric(pROC::auc(pROC::roc(y,score,levels=c(0,1),direction="<",quiet=TRUE)))
  stopifnot(abs(auc_rank(y,score)-expected)<1e-12)
} else stop("Install the locked pROC dependency for the independent AUC comparison.")

# Compare Monte Carlo mean with the analytically known mixture identity.
factor <- mixture_factor(.15,.85,.85)
expected <- .5+factor*(.9-.5)
naive <- replicate(100,{
  x<-simulate_labels(n=10000,rho=0)
  auc_rank(x$label,x$score)
})
mcse<-sd(naive)/sqrt(length(naive))
stopifnot(abs(mean(naive)-expected)<max(.005,4*mcse))
dependent<-simulate_labels(n=200000,rho=.4)
stopifnot(abs(auc_rank(dependent$label,dependent$score)-expected)>.01)
cat("PASS: agreement degeneracy, missingness, leave-one-out ties, AUC/pROC parity, unbounded correction, and rho=0 identity.\n")
cat(sprintf("Synthetic identity error %.6f; Monte Carlo SE %.6f (100 replicates).\n",mean(naive)-expected,mcse))

bad <- data.frame(StudyInstanceUID="synthetic",Report="excluded")
stopifnot(inherits(try(check_label_schema(bad),silent=TRUE),"try-error"))
for (f in list.files("R",pattern="[.]R$",full.names=TRUE)) parse(f)
cat("PASS: forbidden schema rejection and all R files parse. No empirical analysis run.\n")
