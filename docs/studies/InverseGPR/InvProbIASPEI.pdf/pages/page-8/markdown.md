**Rule 3** *If the expression of the probability density representing the homogeneous probability distribution is known in one system of coordinates, then it is known in any other system of coordinates, through the Jacobian rule.*

Indeed, in the expression above, $g(r, \theta, \varphi) = k r^2 \sin \theta$, we recognize the Jacobian between the geographical and the Cartesian coordinates (where the probability density is constant).

For short, when we say *the homogeneous probability density* we mean *the probability density representing the homogeneous probability distribution*. **One should remember that, in general, the homogeneous probability density is not constant.**

Let us now examine 'positive parameters', like a temperature, a period, or a seismic wave propagation velocity. One of the properties of the parameters we have in mind is that they occur in pairs of mutually reciprocal parameters:

|  Period | $T = 1/\nu$ | ; | Frequency | $\nu = 1/T$  |
| --- | --- | --- | --- | --- |
|  Resistivity | $\rho = 1/\sigma$ | ; | Conductivity | $\sigma = 1/\rho$  |
|  Temperature | $T = 1/(k\beta)$ | ; | Thermodynamic parameter | $\beta = 1/(kT)$  |
|  Mass density | $\rho = 1/\ell$ | ; | Lightness | $\ell = 1/\rho$  |
|  Compressibility | $\gamma = 1/\kappa$ | ; | Bulk modulus (uncompressibility) | $\kappa = 1/\gamma$  |
|  Wave velocity | $c = 1/n$ | ; | Wave slowness | $n = 1/c$ .  |

When working with physical theories, one may freely choose one of these parameters or its reciprocal.

Sometimes these pairs of equivalent parameters come from a definition, like when we define frequency $\nu$ as a function of the period $T$, by $\nu = 1/T$. Sometimes these parameters arise when analyzing an idealized physical system. For instance, Hooke's law, relating stress $\sigma_{ij}$ to strain $\varepsilon_{ij}$ can be expressed as $\sigma_{ij} = c_{ij}^{k\ell} \varepsilon_{k\ell}$, thus introducing the stiffness tensor $c_{ijk\ell}$, or as $\varepsilon_{ij} = d_{ij}^{k\ell} \sigma_{k\ell}$, thus introducing the compliance tensor $d_{ijk\ell}$, the inverse of the stiffness tensor. Then the respective eigenvalues of these two tensors belong to the class of scalars analyzed here.

Let us take, as an example, the pair conductivity-resistivity (this may be thermal, electric, etc.). Assume we have two samples in the laboratory $S_1$ and $S_2$ whose resistivities are respectively $\rho_1$ and $\rho_2$. Correspondingly, their conductivities are $\sigma_1 = 1/\rho_1$ and $\sigma_2 = 1/\rho_2$. How should we define the 'distance' between the 'electrical properties' of the two samples? As we have $|\rho_2 - \rho_1| \neq |\sigma_2 - \sigma_1|$, choosing one of the two expressions as the 'distance' would be arbitrary. Consider the following definition of 'distance' between the two samples

$$D(S_1, S_2) = \left| \log \frac{\rho_2}{\rho_1} \right| = \left| \log \frac{\sigma_2}{\sigma_1} \right| \quad . \tag{7}$$

This definition (i) treats symmetrically the two equivalent parameters $\rho$ and $\sigma$ and, more importantly, (ii) has an *invariance of scale* (what matters is how many 'octaves' we have between the two values, not the plain difference between the values). In fact, it is the only definition of distance between the two samples $S_1$ and $S_2$ that has an invariance of scale and is additive (i.e., $D(S_1, S_2) + D(S_2, S_3) = D(S_1, S_3)$).

Associated to the distance $D(x_1, x_2) = |\log (x_2/x_1)|$ is the distance element (differential form of the distance)

$$dL(x) = \frac{dx}{x} \quad . \tag{8}$$

This being a 'one-dimensional volume' we can apply now the rule 1 above to get the expression of the homogeneous probability density for such a positive parameter:

$$f(x) = \frac{k}{x} \quad . \tag{9}$$

Defining the reciprocal parameter $y = 1/x$ and using the Jacobian rule we arrive at the homogeneous probability density for $y$:

$$g(y) = \frac{k}{y} \quad . \tag{10}$$

These two probability densities have the same form: the two reciprocal parameters are treated symmetrically. Introducing the logarithmic parameters

$$x^* = \log \frac{x}{x_0} \quad ; \quad y^* = \log \frac{y}{y_0} \quad , \tag{11}$$

8