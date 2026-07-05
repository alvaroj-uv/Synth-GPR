90

A Summary of Probability and Statistics

An important result that we need is the variance of a sample mean. For this we use the following lemma, the proof of which will be left as an exercise:

**Lemma 1** If $a$ is a real number and $x$ a random variable, then $V(ax) = a^2 V(x)$.

From this it follows immediately that

$$V(\bar{x}) = \frac{1}{n^2} \sum_{i=1}^{n} V(x_i).$$

In particular, if the random variables are identically distributed, with mean $\mu$ then $V(\bar{x}) = \sigma^2/n$.

## 6.7 Bias

In statistics, the *bias* of an estimator of some parameter is defined to be the expectation of the difference between the parameter and the estimator:

$$B[\hat{\theta}] \equiv E[\hat{\theta} - \theta] \tag{6.53}$$

where $\hat{\theta}$ is the estimator of $\theta$. In a sense, we want the bias to be small so that we have a faithful estimate of the quantity of interest.

An estimator $\hat{\theta}$ of $\theta$ is unbiased if $E[\hat{\theta}] = \theta$

For instance, it follows from the law of large numbers that the sample mean is an unbiased estimator of the population mean. In symbols,

$$E[\bar{x}] = \mu. \tag{6.54}$$

However, the sample variance

$$s^2 \equiv \frac{1}{N} \sum_{i=1}^{N} (x_i - \bar{x})^2 \tag{6.55}$$

turns out not to be unbiased (except asymptotically) since $E[s^2] = \frac{n-1}{n}\sigma^2$. To get an unbiased estimator of the variance we use $E[\frac{n}{n-1}s^2]$. To see this note that

$$s^2 = \frac{1}{N} \sum_{i=1}^{n} (x_i - \bar{x})^2 = \frac{1}{N} \sum_{i=1}^{n} x_i^2 - 2x_i\bar{x} + \bar{x}^2 = \left( \frac{1}{N} \sum_{i=1}^{n} x_i^2 \right) - \bar{x}^2.$$

Hence the expected value of $s^2$ is

$$E[s^2] = \frac{1}{N} \sum_{i=1}^{n} E[x_i^2] - E[\bar{x}^2].$$

0