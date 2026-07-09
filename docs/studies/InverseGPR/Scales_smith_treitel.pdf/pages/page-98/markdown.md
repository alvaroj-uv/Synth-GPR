6.4 Probability Functions and Densities

83

### 6.4.2 Multi-variate probabilities

We can readily generalize a one-dimensional distribution such

$$P(x \in I_1) = \frac{1}{\sqrt{\pi}} \int_{I_1} e^{-x^2} \, dx, \tag{6.33}$$

where $I_1$ is a subset of $R^1$, the real line, to two dimensions:

$$P((x, y) \in I_2) = \frac{1}{\pi} \int \int_{I_2} e^{-(x^2 + y^2)} \, dx \, dy \tag{6.34}$$

where $I_2$ is a subset of the real plane $R^2$. So $\rho(x, y) = \frac{1}{\pi} e^{-(x^2 + y^2)}$ is an example of a joint probability density on two variables. We can extend this definition to any number of variables. In general, we denote by $\rho(x_1, x_2, \ldots x_N)$ a joint density for the $N$-dimensional random variable. Sometimes we will write this as $\rho(\mathbf{x})$. By definition, the probability that the $N$-vector $\mathbf{x}$ lies in some subset $A$ of $\mathbf{R}^N$ is given by:

$$P[\mathbf{x} \in A] = \int_A \rho(\mathbf{x}) \, d\mathbf{x} \tag{6.35}$$

where $d\mathbf{x}$ refers to some $N$-dimensional volume element.

### independence

We saw above that conditional probabilities were related to joint probabilities by

$$P(AB) = P(B|A)P(A) = P(A|B)P(B)$$

from which result Bayes theorem follows. The same result holds for random variables. If a random variable $X$ is *independent* of event $Y$, the probability of $Y$ does not depend on the probability of $X$. That is, $P(x|y) = P(x)$ and $P(y|x) = P(y)$. Hence for independent events, $P(x, y) = P(x)Py$.

Once we have two random variables $X$ and $Y$, with a joint probability $P(x, y)$, we can think of their moments. The joint $n - m$ moment of $X$ and $Y$ about 0 is just

$$E[x^n y^m] = \int \int x^n y^m \rho(x, y) dx dy. \tag{6.36}$$

The 1-1 moment about zero is called the *correlation* of the two random variables:

$$\Gamma_{XY} = E[xy] = \int \int xy \rho(x, y) dx dy. \tag{6.37}$$

On the other hand, the 1-1 moment about the means is called the *covariance*:

$$C_{XY} = E[(x - E(x))(y - E(y))] = \Gamma_{XY} - E[x]E[y]. \tag{6.38}$$

0