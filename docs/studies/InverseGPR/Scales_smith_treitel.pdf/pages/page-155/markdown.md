140

Bayesian versus Frequentist Methods of Inference

Let $f$ denote the joint distribution of models and data. The distribution (marginal) of the data is obtained by integrating $f$ over the models

$$h(\mathbf{d}) = \int_{\mathcal{M}} f(\mathbf{m}, \mathbf{d}) d\mathbf{m},$$

where $\mathcal{M}$ is the space of models. From Bayes' theorem, the conditional distribution of $\mathbf{m}$ given $\mathbf{d}$ is

$$p(\mathbf{m}|\mathbf{d}) = \frac{f(\mathbf{d}|\mathbf{m})\rho(\mathbf{m})}{h(\mathbf{d})},$$

where $\rho(\mathbf{m})$, the prior distribution, is the marginal of $f$ with respect to $\mathbf{m}$. The conditional distribution, $p(\mathbf{m}|\mathbf{d})$, is the so-called Bayesian posterior distribution, which updates the prior information in view of the data.

One can define a number of reasonable estimators of $\mathbf{m}$ based on $p(\mathbf{m}|\mathbf{d})$. For example, the $\hat{\mathbf{m}}$ that maximizes $p(\mathbf{m}|\mathbf{d})$ (or that is close, in probability, to $\mathbf{m}$.) Or one could compute the estimator that gives the smallest Bayes risk for a given prior and loss function. It can be shown [Lehmann [Leh83], p.239] that, for square error loss function, the Bayes estimator is the posterior mean.

Here is a simple example of using a normal prior to estimate a normal mean. Assume that there are $n$ observations, $(d_1, d_2, ..., d_n) = \mathbf{d}$, which are $iid$ $N(\eta, \sigma^2)$ and that we want to estimate the mean, $\eta$, given that the prior, $\rho$, is $N(\mu, \beta^2)$. Up to a constant factor, the joint distribution of $\eta$ and $\mathbf{d}$ is [Lehmann [Leh83], p.243]

$$f(\mathbf{d}, \eta) = \exp \left[ -\frac{1}{2\sigma} \sum_{i=1}^n (d_i - \eta)^2 \right] \exp \left[ -\frac{1}{2\beta} (\eta - \mu)^2 \right],$$

The posterior mean is

$$\hat{\eta} = \mathrm{E}(\eta|\mathbf{d}) = \frac{n\hat{\mathbf{d}}/\sigma^2 + \mu/\beta^2}{n/\sigma^2 + 1/\beta^2},$$

where $\hat{\mathbf{d}}$ is the arithmetic mean of the data. The posterior variance is

$$\mathrm{Var}(\eta|\mathbf{d}) = \frac{1}{n/\sigma^2 + 1/\beta^2}.$$

Notice that the posterior variance is always reduced by the presence of a nonzero $\beta$. The posterior mean, which is the Bayes estimator for square error loss, can be written as

$$\hat{\eta}(\mathbf{d}) = \left[ \frac{n/\sigma^2}{n/\sigma^2 + 1/\beta^2} \right] \hat{\mathbf{d}} + \left[ \frac{1/\beta^2}{n/\sigma^2 + 1/\beta^2} \right] \mu.$$

We see that the Bayes estimator is a weighted average of the mean of the data and the mean of the Bayesian prior distribution; the latter is the Bayes estimator before any data have been observed. The Bayes risk is the integral, over the data, of the posterior variance of $\eta$. Since the posterior variance does not depend of $\mathbf{d}$, the Bayes risk is just the posterior variance. Note also that as $\beta \to 0$, increasingly strong prior information, the estimate converges to the prior mean. As $\beta \to \infty$, increasingly weak prior information, the Bayes estimate converges to the mean of the data. Also note that as $\beta \to \infty$ the prior becomes improper (not normalizable).

1