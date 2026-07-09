2

Balgaisha Mukanova, Vladimir G. Romanov

and ill-conditionedness of the ISP for wave equation with variable speed function and final measured data has been studied in [12]. Uniqueness results for multidimensional parabolic and hyperbolic ISPs have been established in [13]. Stability estimate and a reconstruction formula for $f(x)$ in the hyperbolic equation $u_{tt} = \Delta u + \sigma(t)f(x)$, $x \in \Omega \subset \mathbb{R}^r$, $t > 0$, from the Neumann type additional data $\partial u(x, t; f)/\partial n$ have been obtained in [14]. Regarding the numerical approaches to hyperbolic coefficient inverse problems, we refer to monographs [6], [7].

Most of numerical approaches to ISP for parabolic and hyperbolic equations deal with source term in separable form $F(x)H(t)$ (see, for instance, [2], [14], [15], [16] and references therein). In this paper the function $H(x, t)$ has the form $H(t - x/c)$, since, as it is shown below, the linearized GPR data interpretation problem takes the form (1)-(2); therefore the proposed method is applicable in radar techniques. In practice inverse problems arising in GPR techniques are solved via different approximate ways, most relevant of them are described in [17] and in the review [18].

In this paper, we develop new non-iterative algorithm for identifying the spacewise dependent source $F(x)$ in (1)-(2). This algorithm is based on integral formula for the solution of wave equation (1) and use of the $N$th partial sum of the Fourier expansion for the term $F(x)$. Substituting then this formula in the regularized cost functional

$$J_\alpha(F) := \frac{1}{2}\|u(0, \cdot; F) - g(\cdot)\|_{L^2(0,T)}^2 + \frac{\alpha}{2}\|F\|_{L^2(0,l)}^2, \quad \alpha > 0, \tag{3}$$

where $l = l(T)$, we obtain a system of algebraic equations which unique solution gives an approximate regularized solution of the considered inverse problem. The algorithm is simple, effective and does not require any iterative procedures. Our numerical results demonstrate that the accuracy of all reconstructions are sufficient for high noise levels of measured data. The similar approach for an inverse source problem related to the advection–diffusion equation has been proposed in [15], [16].

The paper is organized as follows. In Section 2 we reduce the GPR data interpretation problem to the ISP (1)-(2). Numerical algorithm for identification of a spacewise dependent source from Dirichlet type measured output data is described in Section 3. Results of computational experiments are given in Section 4. Some concluding remarks are made in Section 5.

## 2 Linearized mathematical model of GPR method

Let us formulate the 1D inverse problem for the model of GPR technique. As it is common in geophysics, assume that the medium fills the half-space $z > 0$ and the half-space $z < 0$ corresponds to the air. Let the electrical permittivity $\varepsilon$ of the medium depend on the coordinate $z$ only, magnetic permittivity $\mu = \mu_0 = \text{const} > 0$ in the whole space and the conductivity is negligible. Let the current source with intensity

$$j^{\varepsilon x}(t) = \Phi(t)\delta(z), \ \Phi(t) = 0 \text{ if } t \le 0, \ \Phi(t) \in C^2[0, \infty), \ \Phi''(+0) \ne 0,$$

be placed at the boundary $z = 0$ and directed along the axis $y$. Then it follows from Maxwell's equations that the electromagnetic field depends on $(z, t)$ only. The field has