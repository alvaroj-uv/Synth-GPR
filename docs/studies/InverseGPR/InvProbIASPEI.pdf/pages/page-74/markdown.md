are associated to the dual boundary conditions 315 (the hats here mean that the transpose operator operator operates in the dual spaces (see section M.3). This being understood, we can write $\mathbf{L}^T = \mathbf{L}$ and $\mathbf{G}^T = \mathbf{G}$, and rewrite equations 316 as

$$\mathbf{L} \widehat{\mathbf{p}} = \widehat{\mathbf{S}} \quad ; \quad \widehat{\mathbf{p}} = \mathbf{G} \widehat{\mathbf{S}} \quad . \tag{317}$$

The hats have to be maintained, to remember that the fields with a hat must satisfy boundary conditions dual to those satisfied by the fields without a hat.

Using the transposed of the Green operator, we can write

$$\widehat{p}(\mathbf{x}, t) = \int dV(\mathbf{x}') \int_{t_2}^{t_1} dt' \, G^T(\mathbf{x}, t; \mathbf{x}', t') \, \widehat{S}(\mathbf{x}', t') \, , \tag{318}$$

equation identical to

$$\widehat{p}(\mathbf{x}, t) = \int dV(\mathbf{x}') \int_{t_1}^{t_2} dt' \, G(\mathbf{x}', t'; \mathbf{x}, t) \, \widehat{S}(\mathbf{x}', t') \, . \tag{319}$$

### M.8 Born Approximation for the Acoustic Wave Equation

Let us start from equation 309, using the same notations:

$$\frac{1}{\kappa} \frac{\partial^2 p}{\partial t^2} - \operatorname{div} \left( \frac{1}{\rho} \mathbf{grad} \, p \right) = S \, . \tag{320}$$

I shall denote $\mathbf{p}$ the function $\{p(\mathbf{x}, t)\}$ as a whole, and not its value at a given point of space and time. Similarly, $\boldsymbol{\kappa}$ and $\boldsymbol{\rho}$ will denote the functions $\{\kappa(\mathbf{x})\}$ and $\{\rho(\mathbf{x})\}$.

Given appropriate boundary and initial conditions, and given a source function, the acoustic wave equation defines an application $\{\boldsymbol{\kappa}, \boldsymbol{\rho}\} \to \mathbf{p} = \psi(\boldsymbol{\kappa}, \boldsymbol{\rho})$, i.e., an application that associates to each medium $\{\boldsymbol{\kappa}, \boldsymbol{\rho}\}$ the (unique) pressure field $\mathbf{p}$ that satisfies the wave equation (with given boundary and initial conditions).

Let $\mathbf{p}_0$ be the pressure field propagating in the medium defined by $\boldsymbol{\kappa}_0$ and $\boldsymbol{\rho}_0$, i.e., $\mathbf{p}_0 = \psi(\boldsymbol{\kappa}_0, \boldsymbol{\rho}_0)$, and let $\mathbf{p}$ be the pressure field propagating in the medium defined by $\boldsymbol{\kappa}$ and $\boldsymbol{\rho}$, i.e., $\mathbf{p} = \psi(\boldsymbol{\kappa}, \boldsymbol{\rho})$. Clearly, if $\boldsymbol{\kappa}$ and $\boldsymbol{\rho}$ are close (in a sense to be defined) to $\boldsymbol{\kappa}_0$ and $\boldsymbol{\rho}_0$, then, the wavefield $\mathbf{p}$ will be close to $\mathbf{p}_0$.

Let us obtain an explicit expression for the first order approximation to $\mathbf{p}$. This is known as the (first) Born approximation of the wavefield. Both $\kappa$ and $\rho$ could be perturbed, but I simplify the discussion here by considering only perturbations in the uncompressibility $\kappa$. The reader may easily obtain the general case.

The pressure $P$ is, in thermodynamics, a positive quantity. When considering small variations around some 'ambient pressure' $P_0$, we can define

$$p = P_0 \log \frac{P}{P_0} \, . \tag{321}$$

For small pressure perturbations, we have

$$p = P_0 \log \left( 1 + \frac{(P - P_0)}{P_0} \right) \approx P - P_0 \, . \tag{322}$$

So defined, the pressure perturbation $p$ may take positive or negative values, corresponding to an elastic medium that is compressed or stretched. In the terminology of section 2, this is a Cartesian quantity.

The uncompressibility and the volumetric mass are positive, Jeffreys quantities.

In most texts, the difference $\mathbf{p} - \mathbf{p}_0$ is calculated as a function of the difference $\boldsymbol{\kappa} - \boldsymbol{\kappa}_0$, but we have seen that this is not the right way, as the resulting approximation will depend on the fact that we are using uncompressibility $\kappa(\mathbf{x})$ instead of compressibility $\gamma(\mathbf{x}) = 1/\kappa(\mathbf{x})$.

At this point we may introduce the logarithmic parameters, and proceed trivially. The logarithmic uncompressibilities for the reference medium and for the perturbed medium are

$$\kappa_0^* = \log \frac{\kappa_0}{K} \quad ; \quad \kappa^* = \log \frac{\kappa}{K} \quad , \tag{323}$$

where $K$ and $R$ are arbitrary constants (having the right physical dimension). Reciprocally,

$$\kappa_0 = K \exp \kappa_0^* \quad ; \quad \kappa = K \exp \kappa^* \quad . \tag{324}$$

74