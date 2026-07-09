situation.

Quasi-linear problems are illustrated at the bottom-left of figure 9. If the relationship linking the observable data d to the model parameters m,

$$\mathbf{d} = \mathbf{g}(\mathbf{m}), \tag{117}$$

is approximately linear inside the domain of significant prior probability (i.e., inside the gray oval of the figure), then the posterior distribution is just as simple as the prior distribution. For instance, if the prior is Gaussian the posterior is also Gaussian.

In this case also, the problem can be reduced to the computation of the mean and the covariance of the Gaussian. Typically, one begins at some “starting model” $\mathbf{m}_0$ (typically, one takes for $\mathbf{m}_0$ the “a priori model” $\mathbf{m}_{\text{prior}}$) 28, linearizing the function $\mathbf{d} = \mathbf{g}(\mathbf{m})$ around $\mathbf{m}_0$ and one looks for a model $\mathbf{m}_1$ “better than $\mathbf{m}_0$”.

Iterating such an algorithm, one tends to the model $\mathbf{m}_{\infty}$ at which the “quasi-Gaussian” $\sigma_m(\mathbf{m})$ is maximum. The linearizations made in order to arrive to $\mathbf{m}_{\infty}$ are so far not an approximation: the point $\mathbf{m}_{\infty}$ is perfectly defined, independently of any linearization and any method used to find it. But once the convergence to this point has been obtained, a linearization of the function $\mathbf{d} = \mathbf{g}(\mathbf{m})$ around this point,

$$\mathbf{d} - \mathbf{g}(\mathbf{m}_{\infty}) = \mathbf{G}_{\infty} (\mathbf{m} - \mathbf{m}_{\infty}), \tag{118}$$

allows to obtain a good approximation to the posterior uncertainties. For instance, if the prior distribution is Gaussian this will give the covariance of the “tangent Gaussian”.

Between linear and quasi-linear problems there are the “linearizable problems”. The scheme at the top-right of figure 9 shows the case where the linearization of the function $\mathbf{d} = \mathbf{g}(\mathbf{m})$ around the prior model,

$$\mathbf{d} - \mathbf{g}(\mathbf{m}_{\text{prior}}) = \mathbf{G}_{\text{prior}} (\mathbf{m} - \mathbf{m}_{\text{prior}}), \tag{119}$$

gives a function that, inside the domain of significant probability, is very similar to the true (nonlinear) function.

In this case, there is no practical difference between this problem and the strictly linear problem, and the iterative procedure necessary for quasi-linear problems is here superfluous.

It remains to analyze the true nonlinear problems that, using a pleonasm, are sometimes called strongly nonlinear problems. They are illustrated at the bottom-right of figure 9.

In this case, even if the prior distribution is simple, the posterior distribution can be quite complicated. For instance, it can be multimodal. These problems are in general quite complex to solve, and only a Monte Carlo analysis, as described in the previous chapter, is feasible.

If full Monte Carlo methods cannot be used, because they are too expensive, then one can mix a random part (for instance, to choose the starting point) and a deterministic part. The optimization methods applicable to quasi-linear problems can, for instance, allow us to go from the randomly chosen starting point to the “nearest” optimal point. Repeating these computations for different starting points one can arrive at a good idea of the posterior distribution in the model space.

### 7.6.2 The Maximum Likelihood Model

The most likely model is, by definition, that at which the volumetric probability (see appendix A) $\sigma_\beta(\mathbf{m})$ attains its maximum. As $\sigma_\beta(\mathbf{m})$ is maximum when $S(\mathbf{m})$ is minimum, we see that the most likely model is also the the ‘best model’ obtained when using a ‘least squares criterion’. Should we have used the double exponential model for all the uncertainties, then the most likely model would be defined by a ‘least absolute values’ criterion.

There are many circumstances where the most likely model is not an interesting model. One trivial example is when the volumetric probability has a ‘narrow maximum’, with small total probability (see figure 10). A much less trivial situation arises when the number of parameters is very large, as for instance when we deal with a random function (that, strictly speaking, corresponds to an infinite number of random variables). Figure 11 for instance, shows a few realizations of a Gaussian function with zero mean and an (approximately) exponential correlation. The most likely function is the center of the Gaussian, i.e., the null function shown at the left. But this is not a representative sample of the probability distribution, as any realization of the probability distribution will have, with a probability very close to one, the ‘oscillating’ characteristics of the three samples shown at the right.

28 The term “a priori model” is an abuse of language. The correct term is “mean a priori model”.

34