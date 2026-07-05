86

A Summary of Probability and Statistics

## 6.5 Random Sequences

Often we are faced with a number of measurements $\{x_i\}$ that we want to use to estimate the quantity being measured $x$. A seismometer recording ambient noise, for example, is sampling the velocity or displacement as a function of time associated with some piece of the earth. We don't necessarily know the probability law associated with the underlying random process, we only know its sampled values. Fortunately, measures such as the mean and standard deviation computed from the sampled values converge to the true mean and standard deviation of the random process.

The *sample average* or *sample mean* is defined to be

$$\bar{x} \equiv \frac{1}{N} \sum_{i=1}^{N} x_i$$

**sample moments:** Let $x_1, x_2, \dots x_N$ be a random random sample from the probability density $\rho$. Then the $r$-th sample moment about 0, is given by

$$\frac{1}{N} \sum_{i=1}^{N} x_i^r.$$

If $r = 1$ this is the sample mean, $\bar{x}$. Further, the $r$-th sample moment about $\bar{x}$, is given by

$$M_r \equiv \frac{1}{N} \sum_{i=1}^{N} (x_i - \bar{x})^r.$$

How is the sample mean $\bar{x}$ related to the mean of the underlying random variable (what we will shortly call the expectation, $E[X]$)? This is the content of the *law of large numbers*; here is one form due to Khintchine (see [Bru65] or [Par60]):

**Theorem 9** *Khintchine's Theorem: If $\bar{x}$ is the sample mean of a random sample of size $n$ from the population induced by a random variable $x$ with mean $\mu$, and if $\epsilon > 0$ then:*

$$P[\|\bar{x} - \mu\| \geq \epsilon] \to 0 \text{ as } n \to \infty.$$

In the technical language of probability the sample mean $\bar{x}$ is said to *converge in probability* to the population mean $\mu$. The sample mean is said to be an "estimator" of true mean.

A related result is

**Theorem 10** *Chebyshev's inequality: If a random variable $X$ has finite mean $\bar{x}$ and*

0