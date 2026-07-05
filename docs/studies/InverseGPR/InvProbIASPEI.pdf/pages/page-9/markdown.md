where $x_0$ and $y_0$ are arbitrary positive constants, and using the Jacobian rule, we arrive at the homogeneous probability densities

$$f'(x^*) = k \quad ; \quad g'(y^*) = k \quad . \tag{12}$$

This shows that the logarithm of a positive parameter (of the type considered above) is a 'Cartesian' parameter. In fact, it is the consideration of equations 12, together with the Jacobian rule, that allows full understanding of the (homogeneous) probability densities 9–10.

The association of the probability density $f(u) = k/u$ to positive parameters was first made by Jeffreys (1939). To honor him, we propose to use the term *Jeffreys parameters* for all the parameters of the type considered above. The $1/u$ probability density was advocated by Jaynes (1968), and a nontrivial use of it was made by Rietsch (1977) in the context of inverse problems.

**Rule 4** *The homogeneous probability density for a Jeffreys quantity $u$ is $f(u) = k/u$.*

**Rule 5** *The homogeneous probability density for a 'Cartesian parameter' $u$ (like the logarithm of a Jeffreys parameter, an actual Cartesian coordinate in an Euclidean space, or the Newtonian time coordinate) is $f(u) = k$. The homogeneous probability density for an angle describing the position of a point in a circle is also constant.*

If a parameter $u$ is a Jeffreys parameter with the homogeneous probability density $f(u) = k/u$, then its inverse, its square, and, in general, any power of the parameter is also a Jeffreys parameter, as it can easily be seen using the Jacobian rule.

**Rule 6** *Any power of a Jeffreys quantity (including its inverse) is a Jeffreys quantity.*

It is important to recognize when we do **not** face a Jeffreys parameter. Among the many parameters used in the literature to describe an isotropic linear elastic medium we find parameters like the Lamé's coefficients $\lambda$ and $\mu$, the bulk modulus $\kappa$, the Poisson ratio $\sigma$, etc. A simple inspection of the theoretical range of variation of these parameters shows that the first Lamé parameter $\lambda$ and the Poisson ratio $\sigma$ may take negative values, so they are certainly not Jeffreys parameters. In contrast, Hooke's law $\sigma_{ij} = c_{ijk\ell}\varepsilon^{k\ell}$, defining a linearity between stress $\sigma_{ij}$ and strain $\varepsilon_{ij}$, defines the positive definite stiffness tensor $c_{ijk\ell}$ or, if we write $\varepsilon_{ij} = d_{ijk\ell}\sigma^{k\ell}$, defines its inverse, the compliance tensor $d_{ijk\ell}$. The two reciprocal tensors $c_{ijk\ell}$ and $d_{ijk\ell}$ are 'Jeffreys tensors'. This is a notion whose development is beyond the scope of this paper, but we can give the following rule:

**Rule 7** *The eigenvalues of a Jeffreys tensor are Jeffreys quantities$^{6}$.*

As the two (different) eigenvalues of the stiffness tensor $c_{ijk\ell}$ are $\lambda_\kappa = 3\kappa$ (with multiplicity 1) and $\lambda_\mu = 2\mu$ (with multiplicity 5), we see that the incompressibility modulus $\kappa$ and the shear modulus $\mu$ are Jeffreys parameters$^{7}$ (as are any parameter proportional to them, or any power of them, including the inverses). If for some reason, instead of working with $\kappa$ and $\mu$, we wish to work with other elastic parameters, like for instance the Young modulus $Y$ and the Poisson ratio $\sigma$, or the two elastic wave velocities, then the homogeneous probability distribution must be found using the Jacobian of the transformation (see appendix H).

Some probability densities have conspicuous 'dispersion parameters', like the $\sigma$'s in the normal probability density $f(x) = k \exp\left(-\frac{(x-x_0)^2}{2\sigma^2}\right)$, in the lognormal probability $g(X) = \frac{k}{X} \exp\left(-\frac{(\log X/X_0)^2}{2\sigma^2}\right)$ or in the Fisher probability density (Fischer, 1953) $h(\vartheta, \varphi) = k \sin\theta \exp\left(\cos\theta / \sigma^2\right)$. A consistent probability model requires that when the dispersion parameter $\sigma$ tends to infinity, the probability density tends to the homogeneous probability distribution. For instance, in the three examples just given, $f(x) \rightarrow k$, $g(X) \rightarrow k/X$ and $h(\vartheta, \varphi) \rightarrow k \sin\theta$, which are the respective homogeneous probability densities for a Cartesian quantity, a Jeffreys quantity and the geographical coordinates on the surface of the sphere. We can state the

**Rule 8** *If a probability density has some 'dispersion parameters', then, in the limit where the dispersion parameters tend to infinity, the probability density must tend to the homogeneous one.*

$^{6}$This solves the complete problem for isotropic tensors only. It is beyond the scope of this text to propose rules valid for general anisotropic tensors: the necessary mathematics have not yet been developed.

$^{7}$The definition of the elastic constants was made before the tensorial structure of the theory was understood. Seismologists today should not use, at a theoretical level, parameters like the first Lamé coefficient $\lambda$ or the Poisson ratio. Instead they should use $\kappa$ and $\mu$ (and their inverses). In fact, our suggestion in this IASPEI volume is to use the true eigenvalues of the stiffness tensor, $\lambda_\kappa = 3\kappa$, and $\lambda_\mu = 2\mu$, which we propose to call the *eigen-bulk-modulus* and the *eigen-shear-modulus*, respectively.

9