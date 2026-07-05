132

From Bayes to Weighted Least Squares

ance matrix and $g(\mathbf{m})$ is the forward operator; and

$$\sqrt{\frac{(2\pi)^{-m}}{\det C_M}} \exp \left[ -\frac{1}{2}(\mathbf{m} - \mathbf{m}_{\text{prior}})^T C_M^{-1} (\mathbf{m} - \mathbf{m}_{\text{prior}}) \right], \tag{9.2}$$

where $m$ is the number of model parameters and $C_M$ is the covariance matrix describing the distribution of models about the prior model $\mathbf{m}_{\text{prior}}$. If the forward operator is linear, then the posterior distribution is itself a Gaussian. If the forward operator is nonlinear, then the posterior is non-Gaussian.

The physical interpretation of Equation 9.1 is that it represents the probability that a given model predicts the data. Remember that

$$\mathbf{d} = g(\mathbf{m}_{\text{true}}) + \mathbf{e}$$

where $\mathbf{e}$ is the noise. If we take expectations of both sides then

$$E[\mathbf{d}] = g(\mathbf{m}_{\text{true}}) + E[\mathbf{e}].$$

So if the errors are zero mean then the true model predicts the mean of the data. Of course, we don't know the true model, but if we have an estimate of it, say $\mathbf{m}$ then $g(\mathbf{m})$ is an estimate of the mean of the data and $\mathbf{d} - g(\mathbf{m})$ is an estimate of $\mathbf{e}$.

If we want to estimate the true model we still have the problem of defining what sort of estimator we want to use. Maybe this is not what we want. It may suffice to find regions in model space which have a high probability, as measured by the posterior. But for now let's consider the problem of estimating the true model. A reasonable choice turns out to be: look for the mean of the posterior.$^a$ If the forward operator is linear (so that $g(\mathbf{m}) = G\mathbf{m}$ for some matrix $G$), then Tarantola [Tar87] shows that the normalized product

$$\sigma(\mathbf{m}) \propto \exp -\frac{1}{2} \left[ (G\mathbf{m} - \mathbf{d}_{obs})^T C_D^{-1} (G\mathbf{m} - \mathbf{d}_{obs}) + (\mathbf{m} - \mathbf{m}_{\text{prior}})^T C_M^{-1} (\mathbf{m} - \mathbf{m}_{\text{prior}}) \right]. \tag{9.3}$$

can be written as

$$\sigma(\mathbf{m}) \propto \exp \left[ (\mathbf{m} - \mathbf{m}_{\text{map}})^T C_{M'}^{-1} (\mathbf{m} - \mathbf{m}_{\text{map}}) \right], \tag{9.4}$$

where

$$C_{M'} = \left[ G^T C_D^{-1} G + C_M^{-1} \right]^{-1}, \tag{9.5}$$

is the covariance matrix of the posterior probability. This is approximately true even when $g$ is nonlinear, provided it's not too nonlinear.

$^a$We will take up the reasonableness of this choice later.

1