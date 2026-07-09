10.2 Example: A Toy Inverse Problem

141

### 10.1.2 What is the Most Conservative Prior?

It often happens that there is not enough information to choose a prior density for the unknown parameters, or that the information available is not easily translated into a probabilistic statement; yet we need a prior to be able to apply Bayes' theorem. In this case we try to find a 'noninformative', or 'conservative', prior that will allow us to conduct the Bayesian inference while injecting a minimum of artificial information; that is, information which is not justified by the physical process.

We have defined the Bayes risk, $r_\rho$, and the Bayes estimator for a given prior density. It stands to reason that the more informative the prior the smaller its associated risk; we therefore say that a prior, $\rho$, is *least favorable* if $r_\rho \geq r_{\rho'}$ for any other prior, $\rho'$. A least favorable prior is associated with the greatest unavoidable loss.

In the frequentist approach the greatest unavoidable loss is associated with the maximum of the risk (10.1) over all the possible models. An estimator that minimizes this maximum risk is called a *minimax* estimator. Under certain conditions the Bayes estimator corresponding to a least favorable prior actually minimizes the maximum risk [see Lehmann [Leh83]]. This is true, for example, when the Bayes estimator has a constant risk. In this sense we can think of a least favorable prior as being a route to the most conservative Bayesian estimator.

How does one find a conservative (noninformative) prior? There is no easy answer, even the terms 'conservative' and 'noninformative' are not well defined. One possibility is to define a measure of information (e.g., entropy) and determine a prior which minimizes/maximizes this measure (e.g., maximum entropy). We could also look for priors which are invariant under some family of transformations.

## 10.2 Example: A Toy Inverse Problem

We consider a simple example of estimating the mean, $\eta$, of a unit variance normal distribution, $N(\eta, 1)$, with an observation, $d$, from $N(\eta, 1)$ given that $|\eta|$ is known to be bounded by $\beta$. Following Stark [Sta97], we will use this as a model of an inverse problem with a prior constraint. Without the prior bound, $d$ is an estimator of $\eta$ but we hope to do better (obtain a smaller risk) by including the bound information. How can we include this information in the estimation procedure? One possibility is to use a Bayesian approach and assign a prior distribution to $\eta$ which is uniform on $[-\beta, \beta]$. We will show that this distribution injects stronger information than might be evident.

1