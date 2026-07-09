6.7 Bias

91

Using a previous result, for each of the identically distributed $x_i$ we have

$$E[x_i^2] = V(x) + E[x]^2 = \sigma^2 + \mu^2.$$

And

$$E[\bar{x}^2] = V(\bar{x}) + E[\bar{x}]^2 = \frac{1}{n}\sigma^2 + \mu^2.$$

So

$$E[s^2] = \sigma^2 + \mu^2 - \frac{1}{n}\sigma^2 - \mu^2 = \frac{n-1}{n}\sigma^2.$$

Finally, there is the notion of the *consistency* of an estimator. An estimator $\hat{\theta}$ of $\theta$ is consistent if for every $\epsilon > 0$

$$P[|\hat{\theta} - \theta| < \epsilon] \to 1 \text{ as } n \to \infty.$$

Consistency just means that if the sample size is large enough, the estimator will be close to the thing being estimated.

Later on, when we talk about inverse problems we will see that bias represents a potentially significant component of the uncertainty in the results of the calculations. Since the bias depends on something we do not know, the true value of the unknown parameter, it will be necessary to use *a priori* information in order to estimate it.

### Mean-squared error, bias and variance

The mean-squared error (MSE) for an estimator $m$ of $m_T$ is defined to be

$$\text{MSE}(m) \equiv E[(m - m_T)^2] = E[m^2 - 2mm_T + m_T^2] = \bar{m}^2 - 2\bar{m}m_T + m_T^2. \tag{6.56}$$

By doing a similar analysis of the variance and bias we have:

$$\text{Bias}(m) \equiv E[m - m_T] = \bar{m} - m_T \tag{6.57}$$

and

$$\text{Var}(m) \equiv E[(m - \bar{m})^2] = E[m^2 - 2m\bar{m} + \bar{m}^2] = \bar{m}^2 - \bar{m}^2. \tag{6.58}$$

So you can see that we have: $\text{MSE} = \text{Var} + \text{Bias}^2$. As you can see, for a given mean-squared error, there is a trade-off between variance and bias. The following example illustrates this trade-off.

### Example: Estimating the derivative of a smooth function

We start with a simple example to illustrate the effects of noise and prior information in the performance of an estimator. Later we will introduce tools from statistical decision theory to study the performance of estimators given different types of prior information.

0