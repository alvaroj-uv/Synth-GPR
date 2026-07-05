10.1 What Difference Does the Prior Make?

139

## 10.1 What Difference Does the Prior Make?

In a Bayesian calculation, whatever estimator we use depends on the prior and conditional distributions given the data. There is no clear established procedure to check how much information a prior injects into the posterior estimates. [This is one of the open problems mentioned in Kass and Wasserman [KW96].] In this example we will compare the *risks* of the estimators.

To measure the performance of an estimator, $\hat{\mathbf{m}}$, of $\mathbf{m}$ we define the loss function, $L(\mathbf{m}, \hat{\mathbf{m}})$; $L$ is a non-negative function which is zero for the true model. That is, for any other model $\mathbf{m}_1$, $L(\mathbf{m}, \mathbf{m}_1) \geq 0$ and $L(\mathbf{m}, \mathbf{m}) \equiv 0$. The loss is a measure of the cost of estimating the true model with $\hat{\mathbf{m}}$ when it is actually $\mathbf{m}$. For example, a common loss function is the square error: $L(\mathbf{m}, \hat{\mathbf{m}}) = (\mathbf{m} - \hat{\mathbf{m}})^2$. But there are other choices like $\ell_p$-norm error: $L(\mathbf{m}, \hat{\mathbf{m}}) = \|\mathbf{m} - \hat{\mathbf{m}}\|^p$.

The loss, $L(\mathbf{m}, \hat{\mathbf{m}})$, is a random variable since $\hat{\mathbf{m}}$ depends on the data. We average over the data to obtain an average loss. This is called the *risk* of $\hat{\mathbf{m}}$ given the model $\mathbf{m}$

$$R(\mathbf{m}, \hat{\mathbf{m}}) = \mathrm{E}_P L(\mathbf{m}, \hat{\mathbf{m}}), \tag{10.1}$$

where $P$ is the error probability distribution and $\mathrm{E}_P$ the expectation with respect to this distribution. For square error loss the risk is the usual mean square error.

### 10.1.1 Bayes Risk

The expected loss depends on the chosen model. Some estimators may have small risks for some models but not for others. To compare estimators we need a global measure that takes all plausible models into account. A natural choice is to take the expected value of the loss with respect to the posterior distribution, $p(\mathbf{m}|\mathbf{d})$, of the model given the data. This is called the *posterior risk*

$$r_{\mathbf{m}|\mathbf{d}} = \mathrm{E}_{\mathbf{m}|\mathbf{d}} L[\mathbf{m}, \hat{\mathbf{m}}(\mathbf{d})].$$

Alternatively we can take a weighted average of the risk (10.1) using the prior model distribution as weight function. This is the *Bayes risk*

$$r_\rho = \mathrm{E}_\rho R(\mathbf{m}, \hat{\mathbf{m}}),$$

where $\rho$ is the prior model distribution. An estimator with the smallest Bayes risk is called a *Bayes estimator*. Note that we have used a frequentist approach to define the Bayes risk, since we have not conditioned on the observed data. It does make sense, however, to expect good frequentist behavior if the Bayesian approach is to be used repeatedly with different data sets. In addition, it can be shown that, under very general conditions, minimizing the Bayes risk is equivalent to minimizing the posterior risk [Ber85].

1