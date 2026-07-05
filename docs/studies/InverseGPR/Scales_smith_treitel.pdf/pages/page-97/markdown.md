82

A Summary of Probability and Statistics

This integral is done on page 104. Let $\Omega$ be the real line $-\infty \leq x \leq \infty$. Then $\rho(x) = \frac{1}{\sqrt{\pi}} e^{-x^2}$ is a probability density on $\Omega$. The probability of the event $x \geq 0$, is then

$$P(x \geq 0) = \frac{1}{\sqrt{\pi}} \int_0^\infty e^{-x^2} \, dx = \frac{1}{2}. \tag{6.27}$$

The probability of an arbitrary interval $I'$ is

$$P(x \in I') = \frac{1}{\sqrt{\pi}} \int_{I'} e^{-x^2} \, dx \tag{6.28}$$

Clearly, this probability is positive; it is normalized to one

$$P(-\infty \leq x \leq \infty) = \frac{1}{\sqrt{\pi}} \int_{-\infty}^\infty e^{-x^2} \, dx = 1; \tag{6.29}$$

the probability of an empty interval is zero.

### 6.4.1 Expectation of a Function With Respect to a Probability Law

Henceforth, we shall be interested primarily in numerical valued random phenomena; phenomena whose outcomes are real numbers. A probability law for such a phenomena $P$, can be thought of as determining a (in general non-uniform) distribution of a unit mass along the real line. This extends immediately to vector fields of numerical valued random phenomena, or even functions. Let $\rho(x)$ be the probability density associated with $P$, then we define the *expectation* of a function $f(x)$ with respect to $P$ as

$$E[f(x)] = \int_{-\infty}^\infty f(x) \rho(x) \, dx. \tag{6.30}$$

Obviously this expectation exists if and only if the improper integral converges. The *mean* of the probability $P$ is the expectation of $x$

$$E[x] = \int_{-\infty}^\infty x \rho(x) \, dx. \tag{6.31}$$

For any real number $\xi$, we define the n-th moment of $P$ about $\xi$ as $E[(x - \xi)^n]$. The most common moments are the *central moments*, which correspond to $E[(x - \bar{x})^n]$. The second central moment is called the *variance* of the probability law.

Keep in mind the connection between the ordinary variable $x$ and the random variable itself; let us call the latter $X$. Then the probability law $P$ and the probability density $p$ are related by

$$P(X < x) = \int_{-\infty}^x \rho(x') \, dx'. \tag{6.32}$$

We will summarize the basic results on expectations and variances later in this chapter.

0