## 7.4 The Steepest Descent Method

Consider that we have a probability distribution defined over an $n$-dimensional space $\mathcal{X}$. Having chosen the coordinates $\mathbf{x} \equiv \{x^1, x^2, \ldots, x^n\}$ over the space, the probability distribution is represented by the probability density $f(\mathbf{x})$ whose homogeneous limit (in the sense developed in section 2.2) is $\mu(\mathbf{x})$. We wish to calculate the coordinates $\mathbf{x}_{\mathrm{ML}}$ of the maximum likelihood point. By definition (equation 89),

$$\mathbf{x} = \mathbf{x}_{\mathrm{ML}} \quad \Longleftrightarrow \quad \frac{f(\mathbf{x})}{\mu(\mathbf{x})} \quad \text{maximum} \quad , \tag{102}$$

i.e.,

$$\mathbf{x} = \mathbf{x}_{\mathrm{ML}} \quad \Longleftrightarrow \quad S(\mathbf{x}) \quad \text{minimum} \quad , \tag{103}$$

where $S(\mathbf{x})$ is the misfit (equation 90)

$$S(\mathbf{x}) = -k \log \frac{f(\mathbf{x})}{\mu(\mathbf{x})} \quad . \tag{104}$$

Let us denote by $\widehat{\gamma}(\mathbf{x}_k)$ the gradient of $S(\mathbf{x})$ at point $\mathbf{x}_k$, i.e. (equation 99),

$$(\widehat{\gamma}_0)_p = \frac{\partial S}{\partial x^p}(\mathbf{x}_0) \quad . \tag{105}$$

We have seen above that $\widehat{\gamma}(\mathbf{x})$ should not be interpreted as a direction in the space $\mathcal{X}$ but as a direction in the dual space. The gradient can be converted into a direction using a metric $\mathbf{g}(\mathbf{x})$ over $\mathcal{X}$. In simple situations the metric $\mathbf{g}$ will be the one used to define the volume element of the space, i.e., we will have $\mu(\mathbf{x}) = k v(\mathbf{x}) = k \sqrt{\det \mathbf{g}(\mathbf{x})}$, but this is not a necessity, and iterative algorithms may be accelerated by astute introduction of ad-hoc metrics.

Given, then, the gradient $\widehat{\gamma}(\mathbf{x}_k)$ (at some particular point $\mathbf{x}_k$) to any possible choice of metric $\mathbf{g}(\mathbf{x})$ we can define the direction of steepest ascent associated to the metric $\mathbf{g}$, by (equation 101)

$$\gamma(\mathbf{x}_k) = \mathbf{g}^{-1}(\mathbf{x}_k) \widehat{\gamma}(\mathbf{x}_k) \quad . \tag{106}$$

The algorithm of steepest descent is an iterative algorithm passing from point $\mathbf{x}_k$ to point $\mathbf{x}_{k+1}$ by making a 'small jump' along the local direction of steepest descent,

$$\mathbf{x}_{k+1} = \mathbf{x}_k - \varepsilon_k \mathbf{g}_k^{-1} \widehat{\gamma}_k \quad , \tag{107}$$

where $\varepsilon_k$ is an ad-hoc (real, positive) value adjusted to force the algorithm to converge rapidly (if $\varepsilon_k$ is chosen too small the convergence may be too slow; it is it chosen too large, the algorithm may even diverge).

Many elementary presentations of the steepest descent algorithm just forget to include the metric $\mathbf{g}_k$ in expression 107. These algorithms are not consistent. Even the physical dimensionality of the equation is not assured. 'Numerical' problems in computer implementations of steepest descent algorithms can often be traced to the fact that the metric has been neglected.

**Example 22** *In the context of example 20, where the misfit function $S(\mathbf{m})$ is given by*

$$2 S(\mathbf{m}) = (\mathbf{f}(\mathbf{m}) - \mathbf{d}_{\mathrm{obs}})^t \mathbf{C}_D^{-1} (\mathbf{f}(\mathbf{m}) - \mathbf{d}_{\mathrm{obs}}) + (\mathbf{m} - \mathbf{m}_{\mathrm{prior}})^t \mathbf{C}_M^{-1} (\mathbf{m} - \mathbf{m}_{\mathrm{prior}}) \quad , \tag{108}$$

*the gradient $\widehat{\gamma}$, whose components are $\widehat{\gamma}_\alpha = \partial S / \partial m^\alpha$, is given by the expression*

$$\widehat{\gamma}(\mathbf{m}) = \mathbf{F}^t(\mathbf{m}) \mathbf{C}_D^{-1} (\mathbf{f}(\mathbf{m}) - \mathbf{d}_{\mathrm{obs}}) + \mathbf{C}_M^{-1} (\mathbf{m} - \mathbf{m}_{\mathrm{prior}}) \quad , \tag{109}$$

*where $\mathbf{F}$ is the matrix of partial derivatives*

$$F^{i\alpha} = \frac{\partial f^i}{\partial m^\alpha} \quad . \tag{110}$$

*An example of computation of partial derivatives is given in appendix K. [END OF EXAMPLE.]*

31