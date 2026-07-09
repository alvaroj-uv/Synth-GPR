will also be symmetric, and hence an equilibrium flow density. A “modified” algorithm with flow density $\psi(\mathbf{x}_i, \mathbf{x}_j)$ and equilibrium probability density $r(\mathbf{x}_j)$ is obtained by dividing $\varphi(\mathbf{x}_i, \mathbf{x}_j)$ with the product probability density $r(\mathbf{x}_j) = p(\mathbf{x}_j)q(\mathbf{x}_j)$. This gives the transition probability density

$$\begin{array}{rcl} P(\mathbf{x}_i, \mathbf{x}_j)^{\text{modified}} & = & F(\mathbf{x}_i, \mathbf{x}_j) \frac{\psi(\mathbf{x}_i, \mathbf{x}_j)}{p(\mathbf{x}_j)q(\mathbf{x}_j)} \\ & = & P(\mathbf{x}_i \mid \mathbf{x}_j) \frac{\psi(\mathbf{x}_i, \mathbf{x}_j)}{q(\mathbf{x}_j)}, \end{array}$$

which is the product of the original transition probability density, and a new probability — the acceptance probability

$$P_{ij}^{\text{acc}} = \frac{\psi(\mathbf{x}_i, \mathbf{x}_j)}{q(\mathbf{x}_j)}. \tag{357}$$

If we choose to multiply $F(\mathbf{x}_i, \mathbf{x}_j)$ with the symmetric flow density

$$\psi_{ij} = \text{Min}(q(\mathbf{x}_i), q(\mathbf{x}_j)), \tag{358}$$

we obtain the Metropolis acceptance probability

$$P_{ij}^{\text{metrop}} = \text{Min}\left(1, \frac{q(\mathbf{x}_i)}{q(\mathbf{x}_j)}\right), \tag{359}$$

which is one for $q(\mathbf{x}_i) \ge q(\mathbf{x}_j)$, and equals $q(\mathbf{x}_i)/q(\mathbf{x}_j)$ when $q(\mathbf{x}_i) < q(\mathbf{x}_j)$.

The efficiency of an acceptance rule can be defined as the sum of acceptance probabilities for all possible transitions. The acceptance rule with maximum efficiency is obtained by simultaneously maximizing $\psi(\mathbf{x}_i, \mathbf{x}_j)$ for all pairs of points $\mathbf{x}_j$ and $\mathbf{x}_i$. Since the only constraint on $\psi(\mathbf{x}_i, \mathbf{x}_j)$ (except for positivity) is that $\psi(\mathbf{x}_i, \mathbf{x}_j)$ is symmetric and $\psi(\mathbf{x}_k, \mathbf{x}_l) \le q(\mathbf{x}_l)$, for all $k$ and $l$, we have $\psi(\mathbf{x}_i, \mathbf{x}_j) \le q(\mathbf{x}_j)$ and $\psi(\mathbf{x}_i, \mathbf{x}_j) \le q(\mathbf{x}_i)$. This means that the acceptance rule with maximum efficiency is the Metropolis rule, where

$$\psi_{ij} = \text{Min}(q(\mathbf{x}_i), q(\mathbf{x}_j)). \tag{360}$$

## P The Borel ‘Paradox’

A description of the paradox is given, for instance, by Kolmogorov (1933), in his Foundations of the Theory of Probability (see figure 31 here).

Figure 31: A reproduction of a section of Kolmogorov’s book Foundations of the theory of probability (1950, pp. 50–51). He describes the so-called “Borel paradox”. We do not agree with his conclusion as he ignores the fact that the surface of the sphere is a metric space, so it allows an intrinsic definition of conditional probability density (see main text).

### § 2. Explanation of a Borel Paradox

Let us choose for our basic set $E$ the set of all points on a spherical surface. Our $\mathcal{F}$ will be the aggregate of all Borel sets of the spherical surface. And finally, our $P(A)$ is to be proportional to the measure set of $A$. Let us now choose two diametrically opposite points for our poles, so that each meridian circle will be uniquely defined by the longitude $\psi, 0 \le \psi < \pi$. Since $\psi$ varies from 0 only to $\pi$, — in other words, we are considering complete meridian circles (and not merely semicircles) — the latitude $\theta$ must vary

79