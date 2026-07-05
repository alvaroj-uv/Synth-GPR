2.4 What does it mean to condition on the truth?

21

Let us consider the simplest possible case, one observation, one parameter connected by the forward problem:

$$d = m + \epsilon.$$

Assume that the prior distribution for $m$ is $N(0, \beta^2)$ (the normal or Gaussian probability with 0 mean and variance $\beta^2$). Assume that the experimental error $\epsilon$ is $N(0, \sigma^2)$. If we make repeated measurement of $d$ on the same physical system (fixed $m$), then the measurements will be centered about $m$ (assuming no systematic errors) with variance just due to the experimental errors, $\sigma^2$. So we conclude that the probability (which we will call $f$) of $d$ given $m$ is

$$f(d|m) = N(m, \sigma^2). \tag{2.3}$$

The definition of conditional probability is that

$$f(d, m) = f(d|m)f(m) \tag{2.4}$$

where $f(d, m)$ is the joint probability for model and data and $f(m)$ is the probability on models independent of data; that's our prior probability. So in this case the joint distribution $f(m, d)$ is

$$f(d, m) = N(m, \sigma^2) \times N(0, \beta^2) \propto \exp \left[ -\frac{1}{2\sigma^2}(d - m)^2 \right] \times \exp \left[ -\frac{1}{2\beta^2}m^2 \right]. \tag{2.5}$$

So, if measuring the density repeatedly maps out $f(d|m)$, then what is $f(d)$? We can get $f(d)$ formally by just integrating $f(d, m)$ over all $m$:

$$f(d) \equiv \int f(d, m)dm = \int_{-\infty}^{\infty} \exp \left[ -\frac{1}{2\sigma^2}(d - m)^2 \right] \times \exp \left[ -\frac{1}{2\beta^2}m^2 \right] dm.$$

This is the definition of a marginal probability. But now you can see that the variations in $f(d)$ depend on the a priori variations in $m$—we're integrating over the universe of possible $m$ values. This is definitely not what we do when we make a measurement.

### 2.4.1 Another example

Here is a more complicated example of the same idea, which we extend to the solution of a toy "inverse" problem. It involves using $n$ measurements and a normal prior to estimate a normal mean.

Assume that there are $n$ observations $\mathbf{d} = (d_1, d_2, ...d_n)$ which are $iid^d$ $N(a, \sigma^2)$ and that we want to estimate the mean $a$ given that the prior on $a$ $f(a)$ is $N(\mu, \beta^2)$. Up to a constant factor, the joint distribution for $a$ and $\mathbf{d}$ is:

$^d$The term $iid$ is used to denote independent, identically distributed random variables. This means that the random variables are statistically independent of one another and they all have the same probability law.

1