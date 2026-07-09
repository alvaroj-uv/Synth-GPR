84

A Summary of Probability and Statistics

The covariance and the correlation measure how similar the two random variables are. This similarity is distilled into a dimensionless number called the correlation coefficient:

$$r = \frac{C_{XY}}{\sigma_X \sigma_Y} \tag{6.39}$$

where $\sigma_X$ is the variance of $X$ and $\sigma_Y$ is the variance of $Y$.

Using Schwarz's inequality, namely that

$$\left| \int \int f(x, y) g(x, y) dx dy \right|^2 \leq \int \int |f(x, y)|^2 dx dy \int \int |g(x, y)|^2 dx dy \tag{6.40}$$

and taking

$$f = (x - E(x)) \sqrt{(\rho(x, y))}$$

and

$$g = (y - E(x)) \sqrt{(\rho(x, y))}$$

it follows that

$$|C_{XY}| \leq \sigma_x \sigma_y. \tag{6.41}$$

This proves that $0 \leq r \leq 1$. A correlation coefficient of 1 means that the fluctuations in $X$ and $Y$ are essentially identical. This is perfect correlation. A correlation coefficient of -1 means that the fluctuations in $X$ and $Y$ are essentially identical but with the opposite sign. This is perfect anticorrelation. A correlation coefficient of 0 means $X$ and $Y$ are uncorrelated.

Two independent random variables are always uncorrelated. But dependent random variables can be uncorrelated too.

Here is an example from [Goo00]. Let $\Theta$ be uniformly distributed on $[-\pi/2, \pi/2]$. Let $X = \cos \Theta$ and $Y = \sin \Theta$. Since knowledge of $Y$ completely determines $X$, these two random variables are clearly dependent. But

$$C_{XY} = \frac{1}{\pi} \int_{-\pi/2}^{\pi/2} \cos \theta \sin \theta d\theta = 0$$

### marginal probabilities

From an $n$-dimensional joint distribution, we often wish to know the probability that some subset of the variables take on certain values. These are called *marginal* probabilities. For example, from $\rho(x, y)$, we might wish to know the probability $P(x \in I_1)$. To find this all we have to do is integrate out the contribution from $y$. In other words

$$P(x \in I_1) = \frac{1}{\pi} \int_{I_1} \int_{-\infty}^{\infty} e^{-(x^2 + y^2)} dx dy. \tag{6.42}$$

0