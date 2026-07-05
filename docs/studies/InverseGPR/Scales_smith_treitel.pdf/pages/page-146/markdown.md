# Chapter 9

## From Bayes to Weighted Least Squares

In the last chapters we have developed the theory of least squares estimators for linear inverse problems in which the only uncertainty was the random errors in the data. Now we return to our earlier discussion of Bayes theorem and show how within the Bayesian strategy we can incorporate prior information on model parameters and still get away with solving weighted least squares calculations.

Denote by $f(\mathbf{m}, \mathbf{d})$ the joint distribution on models and data. Recall that from Bayes' theorem, the conditional probability on $\mathbf{m}$ given $\mathbf{d}$ is

$$p(\mathbf{m}|\mathbf{d}) = \frac{f(\mathbf{d}|\mathbf{m})\rho(\mathbf{m})}{h(\mathbf{d})},$$

where $f(\mathbf{d}|\mathbf{m})$ measures how well a model fits the data, $\rho(\mathbf{m})$ is the prior model distribution, and $h(\mathbf{d})$ is the marginal density of $\mathbf{d}$. The conditional probability $p(\mathbf{m}|\mathbf{d})$ is the so-called Bayesian posterior probability, expressing the idea that $p(\mathbf{m}|\mathbf{d})$ assimilates the data and prior information.

For now we will assume that all uncertainties (model and data) can be described by Gaussian distributions. Since any Gaussian distribution can be characterized by its mean and covariance, this means that we must specify a mean and covariance for both the a priori distribution and the data uncertainties.

In this case the Bayesian posterior probability is the normalized product of the following two functions:

$$\sqrt{\frac{(2\pi)^{-n}}{\det C_D}} \exp \left[ -\frac{1}{2}(g(\mathbf{m}) - \mathbf{d}_{\text{obs}})^T C_D^{-1} (g(\mathbf{m}) - \mathbf{d}_{\text{obs}}) \right], \tag{9.1}$$

where $\mathbf{d}_{\text{obs}}$ is the vector of observed data which dimension is $n$, $C_D$ is the data covari-

1