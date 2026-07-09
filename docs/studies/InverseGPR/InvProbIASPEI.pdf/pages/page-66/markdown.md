Let us see here the main mathematical points to be understood prior to any attempt of 'functional inversion'. There are not many good books on functional analysis, the best probably is the 'Introduction to Functional Analysis' by Taylor and Lay (1980).

## M.2 The Functional Spaces Under Investigation

A seismologist may consider a (three-component) seismogram

$$\mathbf{u} = \{ \quad u^i(t) \quad ; \quad i = 1, 2, 3 \quad ; \quad t_0 \le t \le t_1 \quad \} \quad , \tag{239}$$

representing the displacement of a given material point of an elastic body, as a function of time. She/he may wish to define the norm of the function (in fact of 'the set of three functions') $\mathbf{u}$, denoted $\| \mathbf{u} \|$, as

$$\| \mathbf{u} \|^2 = \int_{t_0}^{t_1} dt \, u_i(t) u^i(t) \, , \tag{240}$$

where, as usual, $u_i u^i$ stands for the Euclidean scalar product. The space of all the elements $\mathbf{u}$ where this norm $\| \mathbf{u} \|$ is finite, is, by definition, an $L_2$ space.

This plain example is here to warn against wrong definitions of norm. For instance, we may measure a resistivity-versus-depth profile

$$\boldsymbol{\rho} = \{ \quad \rho(z) \quad ; \quad z_0 \le z \le z_1 \quad \} \quad , \tag{241}$$

but it will generally not make sense to define

$$\| \boldsymbol{\rho} \|^2 = \int_{z_0}^{z_1} dz \, \rho(z)^2 \quad \text{(bad definition)} \quad . \tag{242}$$

For the resistivity-versus-depth profile is equivalent to the conductivity-versus-depth profile

$$\boldsymbol{\sigma} = \{ \quad \sigma(z) \quad ; \quad z_0 \le z \le z_1 \quad \} \quad , \tag{243}$$

where, for any $z$, $\rho(z)\sigma(z) = 1$, and the definition of the norm

$$\| \boldsymbol{\sigma} \|^2 = \int_{z_0}^{z_1} dz \, \sigma(z)^2 \quad \text{(bad definition)} \quad , \tag{244}$$

would not be consistent with that of the norm $\| \boldsymbol{\rho} \|$ (we do not have, in general, any reason to assume that $\sigma(z)$ could be 'more $L_2$' than $\rho(z)$, or vice-versa). This is a typical example where the logarithmic variables $r = \log \rho / \rho_0$ and $s = \log \sigma / \sigma_0$ (where $\rho_0$ and $\sigma_0$ are arbitrary constants) allow the only sensible definition of norm

$$\| \mathbf{r} \|^2 = \| \mathbf{s} \|^2 = \int_{z_0}^{z_1} dz \, r(z)^2 = \int_{z_0}^{z_1} dz \, s(z)^2 \quad \text{(good definition)} \quad , \tag{245}$$

or, in terms of $\rho$ and $\sigma$,

$$\| \boldsymbol{\rho} \|^2 = \| \boldsymbol{\sigma} \|^2 = \int_{z_0}^{z_1} dz \left( \log \frac{\rho(z)}{\rho_0} \right)^2 = \int_{z_0}^{z_1} dz \left( \log \frac{\sigma(z)}{\sigma_0} \right)^2 \quad \text{(good definition)} \quad , \tag{246}$$

We see that the right functional spaces for the resistivity $\rho(z)$ or the conductivity $\sigma(z)$ is not $L_2$, but, to speak grossly, the exponential of $L_2$.

Although these examples concern the $L_2$ norm, the same comments apply to any $L_p$ norm. We will see below an example with the $L_1$ norm.

## M.3 Duality Product

Every time we define a functional space, and we start developing mathematical properties (for instance, analyzing the existence and unicity of solutions to partial differential equations), we face another function space, with the same degrees of freedom.

For instance, in elastic theory we may define the strain field $\boldsymbol{\varepsilon} = \{ \varepsilon^{ij}(\mathbf{x}, t) \}$. It will automatically appear another field, with the same variables (degrees of freedom) that, in this case, is the stress $\boldsymbol{\sigma} = \{ \sigma_{ij}(\mathbf{x}, t) \}$. The

66