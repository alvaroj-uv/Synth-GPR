**Example 20** *In the context of Gaussian distributions we have found the probability density (see example 12)*

$$\sigma_m(\mathbf{m}) = \tag{95}$$

$$= k \exp \left( -\frac{1}{2} \left( (\mathbf{m} - \mathbf{m}_{\text{prior}})^t \mathbf{C}_M^{-1} (\mathbf{m} - \mathbf{m}_{\text{prior}}) + (\mathbf{f}(\mathbf{m}) - \mathbf{d}_{\text{obs}})^t \mathbf{C}_D^{-1} (\mathbf{f}(\mathbf{m}) - \mathbf{d}_{\text{obs}}) \right) \right) .$$

*The limit of this distribution for infinite variances is a constant, so in this case $\mu_m(\mathbf{m}) = k$. The misfit function $S(\mathbf{m}) = -\log(\sigma_m(\mathbf{m})/\mu_m(\mathbf{m}))$ is then given by*

$$2 S(\mathbf{m}) = (\mathbf{m} - \mathbf{m}_{\text{prior}})^t \mathbf{C}_M^{-1} (\mathbf{m} - \mathbf{m}_{\text{prior}}) + (\mathbf{f}(\mathbf{m}) - \mathbf{d}_{\text{obs}})^t \mathbf{C}_D^{-1} (\mathbf{f}(\mathbf{m}) - \mathbf{d}_{\text{obs}}) . \tag{96}$$

*The reader should remember that this misfit function is valid only for weakly nonlinear problems (see examples 10 and 12). The maximum likelihood model here is the one that minimizes the sum of squares 96. This corresponds to the least squares criterion. [END OF EXAMPLE.]*

### 7.3 Gradient and Direction of Steepest Ascent

One must not consider as synonymous the notions of 'gradient' and 'direction of steepest ascent'. Consider, for instance, an *adimensional* misfit function$^{21}$ $S(P,T)$ over a pressure $P$ and a temperature $T$. Any sensible definition of the gradient of $S$ will lead to an expression like

$$\text{grad } S = \begin{pmatrix} \frac{\partial S}{\partial P} \\ \frac{\partial S}{\partial T} \end{pmatrix} \tag{97}$$

and this by no means can be regarded as a 'direction' in the $(P,T)$ space (for instance, the components of this 'vector' does not have the dimensions of pressure and temperature, but of inverse pressure and inverse temperature).

Mathematically speaking, *the gradient of a function $S(\mathbf{x})$ at a point $\mathbf{x}_0$ is the linear function that is tangent to $S(\mathbf{x})$ at $\mathbf{x}_0$.* This definition of gradient is consistent with the more elementary one, based on the use of the first order expansion

$$S(\mathbf{x}_0 + \delta\mathbf{x}) = S(\mathbf{x}_0) + \widehat{\gamma}_0^T \delta\mathbf{x} + \dots \tag{98}$$

Here $\widehat{\gamma}_0$ is called the gradient of $S(\mathbf{x})$ at point $\mathbf{x}_0$. It is clear that $S(\mathbf{x}_0) + \widehat{\gamma}_0^T \delta\mathbf{x}$ is a linear function, and that it is tangent to $S(\mathbf{x})$ at $\mathbf{x}_0$, so the two definitions are in fact equivalent. Explicitly, the components of the gradient at point $\mathbf{x}_0$ are

$$(\widehat{\gamma}_0)_p = \frac{\partial S}{\partial x^p}(\mathbf{x}_0) . \tag{99}$$

Everybody is well trained at computing the gradient of a function (event if the interpretation of the result as a direction in the original space is wrong). How can we pass from the gradient to the direction of steepest ascent (a bona fide direction in the original space)? In fact, the gradient (at a given point) of a function defined over a given space $\mathcal{E}$ is an element of the dual of the space. To obtain a direction in $\mathcal{E}$ we must pass from the dual to the primal space. As usual, it is the metric of the space that maps the dual of the space into the space itself. So if $\mathbf{g}$ is the metric of the space where $S(\mathbf{x})$ is defined, and if $\widehat{\gamma}$ is the gradient of $S$ at a given point, the *direction of steepest ascent* is

$$\gamma = \mathbf{g}^{-1} \widehat{\gamma} . \tag{100}$$

The direction of steepest ascent must be interpreted as follows: if we are at a point $\mathbf{x}$ of the space, we can consider a very small hypersphere around $\mathbf{x}_0$. The direction of steepest ascent points towards the point of the sphere at which $S(\mathbf{x})$ attains its maximum value.

**Example 21** *In the context of least squares, we consider a misfit function $S(\mathbf{m})$ and a covariance matrix $\mathbf{C}_M$. If $\widehat{\gamma}_0$ is the gradient of $S$, at a point $\mathbf{x}_0$, and if we use $\mathbf{C}_M$ to define distances in the space, the direction of steepest ascent is*

$$\gamma_0 = \mathbf{C}_M \widehat{\gamma}_0 . \tag{101}$$

[END OF EXAMPLE.]

$^{21}$We take this example because typical misfit functions are adimensional (have no physical dimensions) but the argument has general validity.

30