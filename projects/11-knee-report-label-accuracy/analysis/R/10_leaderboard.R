# Tested summary primitives; the empirical A pipeline follows SAP approval.
leaderboard_summary <- function(public, private) {
  keep <- is.finite(public) & is.finite(private)
  x <- public[keep]; y <- private[keep]
  if (length(x) < 3L || any(x < 0 | x > 1 | y < 0 | y > 1)) stop("Invalid paired scores.")
  d <- y-x
  data.frame(n=length(x), spearman=cor(x,y,method="spearman"),
             kendall_tau_b=cor(x,y,method="kendall"), bias=mean(d), sd_difference=sd(d),
             loa_lower=mean(d)-1.96*sd(d), loa_upper=mean(d)+1.96*sd(d),
             difference_q025=unname(quantile(d,.025)), difference_q975=unname(quantile(d,.975)))
}

top_with_ties <- function(scores, n) {
  if (n < 1 || any(!is.finite(scores))) stop("Invalid rank inputs.")
  scores >= sort(scores,decreasing=TRUE)[min(n,length(scores))]
}

deming_fit <- function(public, private, lambda) {
  if (length(public)!=length(private) || length(public)<3L || lambda<=0 || !is.finite(lambda)) stop("Invalid Deming inputs.")
  if (any(!is.finite(c(public,private)))) stop("Missing Deming inputs.")
  xx <- var(public); yy <- var(private); xy <- cov(public,private)
  if (abs(xy)<1e-14) return(c(intercept=NA_real_,slope=NA_real_,lambda=lambda))
  slope <- (yy-lambda*xx + sqrt((yy-lambda*xx)^2+4*lambda*xy^2))/(2*xy)
  c(intercept=mean(private)-slope*mean(public),slope=slope,lambda=lambda)
}
