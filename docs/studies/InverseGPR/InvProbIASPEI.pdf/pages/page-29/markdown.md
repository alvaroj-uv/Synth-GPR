## 7.1 Maximum Likelihood Point

Let us consider a space $\mathcal{X}$, with a volume element $dV$ defined. If the coordinates $\mathbf{x} \equiv \{x^1, x^2, \ldots, x^n\}$ are chosen over the space, the volume element has an expression $dV(\mathbf{x}) = v(\mathbf{x}) d\mathbf{x}$, and each probability distribution over $\mathcal{X}$ can be represented by a probability density $f(\mathbf{x})$. For any fixed small volume $\Delta V$ we can search for the point $\mathbf{x}_{\mathrm{ML}}$ such that the probability $dP$ of the small volume, when centered around $\mathbf{x}_{\mathrm{ML}}$, attains a maximum. In the limit $\Delta V \to 0$ this defines the *maximum likelihood point*. The maximum likelihood point may be unique (if the probability distribution is unimodal), may be degenerated (if the probability distribution is 'chevron-shaped') or may be multiple (as when we have the sum of a few bell-shaped functions).

The maximum likelihood point is **not** the point at which the probability density is maximum. Our definition implies that a maximum must be attained by the ratio between the probability density and the function $v(\mathbf{x})$ defining the volume element $^{20}$:

$$\mathbf{x} = \mathbf{x}_{\mathrm{ML}} \quad \Longleftrightarrow \quad F(\mathbf{x}) = \frac{f(\mathbf{x})}{v(\mathbf{x})} \quad \text{maximum} \quad . \tag{88}$$

As the homogeneous probability density is $\mu(\mathbf{x}) = k v(\mathbf{x})$ (see rule 2), we can equivalently define the maximum likelihood point by the condition

$$\mathbf{x} = \mathbf{x}_{\mathrm{ML}} \quad \Longleftrightarrow \quad \frac{f(\mathbf{x})}{\mu(\mathbf{x})} \quad \text{maximum} \quad . \tag{89}$$

The point at which a probability density has its maximum is, in general, not $\mathbf{x}_{\mathrm{ML}}$. In fact, the maximum of a probability density does not correspond to an intrinsic definition of a point: a change of coordinates $\mathbf{x} \mapsto \mathbf{y} = \boldsymbol{\psi}(\mathbf{x})$ would change the probability density $f(\mathbf{x})$ into the probability density $g(\mathbf{y})$ (obtained using the Jacobian rule), but the point of the space at which $f(\mathbf{x})$ is maximum is not the same as the point of the space where $g(\mathbf{y})$ is maximum (unless the change of variables is linear). This contrasts with the maximum likelihood point, as defined by equation 89, that is an intrinsically defined point: no matter which coordinates we use in the computation we always obtain the same point of the space.

## 7.2 Misfit

One of the goals here is to develop gradient-based methods for obtaining the maximum of $F(\mathbf{x}) = f(\mathbf{x})/\mu(\mathbf{x})$. As a quite general rule, gradient-based methods perform quite poorly for (bell-shaped) probability distributions, as when one is far from the maximum the probability densities tend to be quite flat, and it is difficult to get, reliably, the direction of steepest ascent. Taking a logarithm transforms a bell-shaped distribution into a paraboloid-shaped distribution on which gradient methods work well.

The logarithmic volumetric probability, or *misfit*, is defined as $S(\mathbf{x}) = -\log(F(\mathbf{x})/F_0)$, where $p'$ and $F_0$ are two constants, and is given by

$$S(\mathbf{x}) = -\log \frac{f(\mathbf{x})}{\mu(\mathbf{x})} \quad . \tag{90}$$

The problem of maximization of the (typically) bell-shaped function $f(\mathbf{x})/\mu(\mathbf{x})$ has been transformed into the problem of minimization of the (typically) paraboloid-shaped function $S(\mathbf{x})$:

$$\mathbf{x} = \mathbf{x}_{\mathrm{ML}} \quad \Longleftrightarrow \quad S(\mathbf{x}) \quad \text{minimum} \quad . \tag{91}$$

**Example 19** *The conjunction $\sigma(\mathbf{x})$ of two probability densities $\rho(\mathbf{x})$ and $\vartheta(\mathbf{x})$ was defined (equation 13) as*

$$\sigma(\mathbf{x}) = p \frac{\rho(\mathbf{x}) \vartheta(\mathbf{x})}{\mu(\mathbf{x})} \quad . \tag{92}$$

*Then,*

$$S(\mathbf{x}) = S_{\rho}(\mathbf{x}) + S_{\vartheta}(\mathbf{x}) \quad , \tag{93}$$

*where*

$$S_{\rho}(\mathbf{x}) = -\log \frac{\rho(\mathbf{x})}{\mu(\mathbf{x})} \quad ; \quad S_{\vartheta}(\mathbf{x}) = -\log \frac{\vartheta(\mathbf{x})}{\mu(\mathbf{x})} \quad . \tag{94}$$

[END OF EXAMPLE.]

$^{20}$The ratio $F(\mathbf{x}) = f(\mathbf{x})/v(\mathbf{x})$ is what we refer to as *the volumetric probability* associated to the probability density $f(\mathbf{x})$. See appendix A.

29