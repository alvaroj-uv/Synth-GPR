6.6 Expectations and Variances

89

is often rather poorly realized, if it is realized at all.”

And perhaps the best summary of all, Gabriel Lippmann speaking to Henri Poincaré: “Everybody believes the [normal law] of errors: the experimenters because they believe that it can be proved by mathematics, and the mathematicians because they believe it has been established by observation.”

## 6.6 Expectations and Variances

Notation: we use $E[x]$ to denote the expectation of a random variable with respect to its probability law $f(x)$. Sometimes it is useful to write this as $E_f[x]$ if we are dealing with several probability laws at the same time.

If the probability is discrete then

$$E[x] = \sum_i x_i f(x_i).$$

If the probability is continuous then

$$E[x] = \int_{-\infty}^{\infty} x f(x) \, dx.$$

Mixed probabilities (partly discrete, partly continuous) can be handled in a similar way using Stieltjes integrals [Bar76].

We can also compute the expectation of functions of random variables:

$$E[\phi(x)] = \int_{-\infty}^{\infty} \phi(x) f(x) \, dx.$$

It will be left as an exercise to show that the expectation of a constant $a$ is $a$ ($E[a] = a$) and the expectation of a constant $a$ times a random variable $x$ is $a$ times the expectation of $x$ ($E[ax] = aE[x]$).

Recall that the variance of $x$ is defined to be

$$V(x) = E[(x - E(x))^2] = E[(x - \mu)^2]$$

where $\mu = E[x]$.

Here is an important result for expectations: $E[(x - \mu)^2] = E[x^2] - \mu^2$. The proof is easy.

$$\begin{array}{rcl} E[(x - \mu)^2] & = & E[x^2 - 2x\mu + \mu^2] & (6.49) \\ & = & E[x^2] - 2\mu E[x] + \mu^2 & (6.50) \\ & = & E[x^2] - 2\mu^2 + \mu^2 & (6.51) \\ & = & E[x^2] - \mu^2 & (6.52) \end{array}$$

0