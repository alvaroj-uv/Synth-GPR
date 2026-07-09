If the linear operator $\mathbf{D}^T$ has to be the transposed of $\mathbf{D}$, for any $\widehat{\mathbf{v}}$ and for any $\mathbf{x}$ we must have (equation 267)

$$\langle \widehat{\mathbf{v}}, \mathbf{D}\mathbf{x} \rangle_{\mathcal{V}} = \langle \mathbf{D}^T \widehat{\mathbf{v}}, \mathbf{x} \rangle_{\mathcal{X}}. \tag{278}$$

[END OF EXAMPLE.]

Let us demonstrate that the derivative operator is an antisymmetric operator i.e, that

$$\mathbf{D}^T = -\mathbf{D}. \tag{279}$$

To demonstrate this, we will need to make a restrictive condition, interesting to analyze.

Using 279, equation 278 writes

$$\int_{t_1}^{t_2} dt \, \widehat{v}(t) \, (\mathbf{D}\mathbf{x})(t) = -\int_{t_1}^{t_2} dt \, (\mathbf{D}\widehat{\mathbf{v}})(t) \, x(t) \tag{280}$$

i.e.,

$$\int_{t_1}^{t_2} dt \, \widehat{v}(t) \, \frac{dx}{dt}(t) + \int_{t_1}^{t_2} dt \, \frac{d\widehat{v}}{dt}(t) \, x(t) = 0. \tag{281}$$

We have to check if this equation holds for any $x(t)$ and any $v(t)$.

The condition is equivalent to

$$\int_{t_1}^{t_2} dt \left( \widehat{v}(t) \, \frac{dx}{dt}(t) + \frac{d\widehat{v}}{dt}(t) \, x(t) \right) = 0, \tag{282}$$

i.e., to

$$\int_{t_1}^{t_2} dt \, \frac{d}{dt} \left( \widehat{v}(t) \, x(t) \right) = 0, \tag{283}$$

or, using the elementary properties of the integral, to

$$\widehat{v}(t_2) \, x(t_2) + \widehat{v}(t_1) \, x(t_1) = 0. \tag{284}$$

In general, there is no reason for this being true. So, in general, we can not say that $\mathbf{D}^T = -\mathbf{D}$.

If the spaces of functions we work with (here, the space of functions $v(t)$ and the space of functions $x(t)$) satisfy the condition 284 it is said that the spaces satisfy dual boundary conditions. If the spaces satisfy dual boundary conditions, then it is true that $\mathbf{D}^T = -\mathbf{D}$, i.e., that the derivative operator is antisymmetric.

A typical example of dual boundary conditions being satisfied is in the case where all the functions $x(t)$ vanish at the initial time, and all the functions $\widehat{v}(t)$ vanish at the final time:

$$x(t_1) = 0 \quad ; \quad \widehat{v}(t_2) = 0 \quad . \tag{285}$$

The notation $\mathbf{D}^T = -\mathbf{D}$ is very suggestive. One has, nevertheless, to remember that (with the boundary conditions chose) while $\mathbf{D}$ acts on functions that vanish at the initial time, $\mathbf{D}^T$ acts on functions $\widehat{v}(t)$ that vanish at the final time.

Consider now the operator $\mathbf{D}^2$ (second derivative)

$$\gamma(t) = \frac{dx^2}{dt^2}(t). \tag{286}$$

Following the same lines of reasoning as above, the reader may easily demonstrate that the second derivative operator is symmetrical, i.e., $(\mathbf{D}^2)^T = \mathbf{D}^2$, provided that the functional spaces into consideration satisfy the dual boundary condition

$$\widehat{\gamma}(t_2) \, \frac{dx}{dt}(t_2) - \frac{d\widehat{\gamma}}{dt}(t_2) \, x(t_2) = \widehat{\gamma}(t_1) \, \frac{dx}{dt}(t_1) - \frac{d\widehat{\gamma}}{dt}(t_1) \, x(t_1). \tag{287}$$

A typical example where this condition is satisfied is when we have

$$x(t_1) = 0 \quad ; \quad \frac{dx}{dt}(t_1) = 0 \quad ; \quad \widehat{\gamma}(t_2) = 0 \quad ; \quad \frac{d\widehat{\gamma}}{dt}(t_2) = 0 \quad , \tag{288}$$

70