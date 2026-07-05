10.3 Priors in High Dimensional Spaces: The Curse of Dimensionality

147

which is finite.

We will adopt Equation (10.4) as the definition of relative entropy in the discrete case, and, as commonly done, the last expression of Equation (10.6) as the definition of relative entropy in the continuous case. $q(x)$, or $q_i$, represents a state of information against which we make comparisons. Finally it is worth mentioning that the negative of the quantity $H[p(x); q(x)]$, known as cross-entropy, was first defined by Kullback [Kul59] as the *directed divergence*. This quantity defines the amount of *information* of the probability density $p(x)$ with respect to $q(x)$. See also [SJ81].

Convinced that entropy is a suitable measure for the uncertainty of a probability distribution, Jaynes [Jay57] showed that a useful tool for conservatively assigning probabilities was to maximize the entropy of the unknown distribution subject to constraints on its moments.

Mathematically this variational problem can be expressed by maximizing Equation (10.4) subjected to the normalization of the distribution

$$\sum_{i=1}^{N} p(x_i) = 1, \tag{10.6}$$

and to other constraints given in the form of expectations

$$\langle w_k(x) \rangle = \sum_{i=1}^{N} w_k(x_i) p(x_i), \quad k = 1, ..., K. \tag{10.7}$$

This is equivalent to the unconstrained problem, given by

$$\begin{aligned} S(p; \lambda, q) &= - \sum_{i=1}^{N} p(x_i) \ln \frac{p(x_i)}{q(x_i)} \\ &\quad - (\lambda_0 - 1) \left[ \sum_{i=1}^{N} p(x_i) - 1 \right] \\ &\quad - \sum_{k=1}^{K} \lambda_k \left[ \sum_{i=1}^{N} w_k(x_i) p(x_i) - \mu_k \right], \tag{10.8} \end{aligned}$$

where $\mu_k$ are sample estimates of $\langle w_k(x) \rangle$ and the $\lambda_k$ are the Lagrange multipliers associated with the constraints. Note that the term $(\lambda_0 - 1)$ is just a redefinition of the zero-order Lagrange multiplier introduced for convenience. If we take the first variation of the functional $S(p; \lambda, q)$ with respect to the probabilities, we get that $\delta S(p; \lambda, q)$ equals

$$\sum_{i=1}^{N} \left[ \frac{\partial H}{\partial p(x_i)} - (\lambda_0 - 1) - \sum_{k=1}^{K} \lambda_k w_k(x_i) \right] \delta p(x_i), \tag{10.9}$$

with

$$\frac{\partial H}{\partial p(x_i)} = - \left[ \ln \frac{p(x_i)}{q(x_i)} + 1 \right]. \tag{10.10}$$

1