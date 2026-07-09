where

$$\psi(\mathbf{x}, t) = \sum_{i} \int_{t_2}^{t_1} dt' \, G(\mathbf{x}_i, t'; \mathbf{x}, t) \, \delta\widehat{p}(\mathbf{x}_i, t') \, , \tag{347}$$

or, using the kernel of the tranposed Green's operator,

$$\psi(\mathbf{x}, t) = \sum_{i} \int_{t_2}^{t_1} dt' \, G^T(\mathbf{x}, t; \mathbf{x}_i, t') \, \delta\widehat{p}(\mathbf{x}_i, t') \, . \tag{348}$$

The field $\psi(\mathbf{x}, t)$ can be interpreted as the solution of the transposed wave equation, with a point source at each point $\mathbf{x}_i$ where we have a receiver, radiating the value $\delta\widehat{p}(\mathbf{x}_i, t')$. As we have the transposed of the Green's operator, the field $\psi(\mathbf{x}, t)$ must satisfy dual boundary conditions, i.e., in our case, final conditions of rest.

### M.11 The Continuous Inverse Problem

Let be $\mathbf{p} = \mathbf{f}(\boldsymbol{\kappa}^*)$ the function calculating the theoretical data associated to the model $\boldsymbol{\kappa}$ (resolution of the forward problem). We seek the model minimizing the sum

$$S(\boldsymbol{\kappa}^*) = \frac{1}{2} \left( \parallel \mathbf{f}(\boldsymbol{\kappa}^*) - \mathbf{p}_{\text{obs}} \parallel^2 + \parallel \boldsymbol{\kappa}^* - \boldsymbol{\kappa}_{\text{prior}}^* \parallel^2 \right) \tag{349}$$

$$= \frac{1}{2} \left( \langle \mathbf{C}_p^{-1}(\mathbf{f}(\boldsymbol{\kappa}^*) - \mathbf{p}_{\text{obs}}) \, , \, \mathbf{f}(\boldsymbol{\kappa}^*) - \mathbf{p}_{\text{obs}} \rangle + \langle \mathbf{C}_{\kappa^*}^{-1}(\boldsymbol{\kappa}^* - \boldsymbol{\kappa}_{\text{prior}}^*) \, , \, \boldsymbol{\kappa}^* - \boldsymbol{\kappa}_{\text{prior}}^* \rangle \right) \, .$$

Using, in this functional context, the steepest descent algorithm proposed in section 7.4, we arrive at

$$\kappa_{n+1}^* = \kappa_n^* - \epsilon \left( \mathbf{C}_{\kappa^*} \mathbf{F}_n^T \mathbf{C}_p^{-1} \left( \mathbf{p}_n - \mathbf{p}_{\text{obs}} \right) + \left( \boldsymbol{\kappa}_n^* - \boldsymbol{\kappa}_{\text{prior}}^* \right) \right) \, , \tag{350}$$

where $\mathbf{p}_n = \mathbf{f}(\boldsymbol{\kappa}_n^*)$ and where $\mathbf{F}_n^T$ is the transposed operatoir defined above, at point $\boldsymbol{\kappa}_n^*$.

Covariances aside, we see that the fundamental object appearing in this inversion algorithm is the transposed operator $\mathbf{F}^T$. As it has been interpreted above, we have all the elements to understand how this sort of inverse problems are solved. For more details, see Tarantola (1984, 1986, 1987).

## N Random Walk Design

The design of a random walk that equilibrates at a desired distribution $p(\mathbf{x})$ can be formulated as the design of an equilibrium flow having a throughput of $p(\mathbf{x}_i)\mathbf{d}\mathbf{x}_i$ particles in the neighborhood of point $\mathbf{x}_i$. The simplest equilibrium flows are symmetric, that is, they satisfy

$$F(\mathbf{x}_i, \mathbf{x}_j) = F(\mathbf{x}_j, \mathbf{x}_i) \tag{351}$$

That is, the transition $\mathbf{x}_i \leftarrow \mathbf{x}_j$ is as likely as the transition $\mathbf{x}_i \rightarrow \mathbf{x}_j$. It is easy to define a symmetric flow, but it will in general not have the required throughput of $p(\mathbf{x}_j)\mathbf{d}\mathbf{x}_j$ particles in the neighborhood of point $\mathbf{x}_j$. This requirement can be satisfied if the following adjustment of the flow density is made: first multiply $F(\mathbf{x}_i, \mathbf{x}_j)$ with a positive constant $c$. This constant must be small enough to assure that the throughput of the resulting flow density $cF(\mathbf{x}_i, \mathbf{x}_j)$ at every point $\mathbf{x}_j$ is smaller than the desired probability $p(\mathbf{x}_j)\mathbf{d}\mathbf{x}_j$ of its neighborhood. Finally, at every point $\mathbf{x}_j$, add a flow density $F(\mathbf{x}_j, \mathbf{x}_j)$, going from the point to itself, such that the throughput at $\mathbf{x}_j$ gets the right size $p(\mathbf{x}_j)\mathbf{d}\mathbf{x}_j$. Neither the flow scaling nor the addition of $F(\mathbf{x}_j, \mathbf{x}_j)$ will destroy the equilibrium property of the flow. In practice, it is unnecessary to add a flow density $F(\mathbf{x}_j, \mathbf{x}_j)$ explicitly, since it is implicit in our algorithms that if no move away from the current point takes place, the move goes from the current point to itself. This rule automatically adjusts the throughput at $\mathbf{x}_j$ to the right size $p(\mathbf{x}_j)\mathbf{d}\mathbf{x}_j$

## O The Metropolis Algorithm

Characteristic of a random walk is that the probability of going to a point $\mathbf{x}_i$ in the space $\mathcal{X}$ in a given step (iteration) depends only on the point $\mathbf{x}_j$ it came from. We will define the conditional probability density $P(\mathbf{x}_i \mid \mathbf{x}_j)$ of the location of the next destination $\mathbf{x}_i$ of the random walker, given that it currently is at neighbouring point $\mathbf{x}_j$.

77