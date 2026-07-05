This implies that $\sigma_m(\mathbf{m})$ is a Gaussian probability density. The values $\widetilde{\mathbf{m}}$ and $\widetilde{\mathbf{C}}_M$ of the center and covariance matrix, respectively, of the Gaussian representing the posterior information in the model space, can be computed using certain matrix identities (see, for instance, Tarantola, 1987, problem 1.19). This gives

$$\widetilde{\mathbf{m}} = \left(\mathbf{F}^T \mathbf{C}_D^{-1} \mathbf{F} + \mathbf{C}_M^{-1}\right)^{-1} \left(\mathbf{F}^T \mathbf{C}_D^{-1} \mathbf{d}_{\text{obs}} + \mathbf{C}_M^{-1} \mathbf{m}_{\text{prior}}\right) \tag{175}$$

$$= \mathbf{m}_{\text{prior}} + \left(\mathbf{F}^T \mathbf{C}_D^{-1} \mathbf{F} + \mathbf{C}_M^{-1}\right)^{-1} \mathbf{F}^T \mathbf{C}_D^{-1} \left(\mathbf{d}_{\text{obs}} - \mathbf{F} \mathbf{m}_{\text{prior}}\right) \tag{176}$$

$$= \mathbf{m}_{\text{prior}} + \mathbf{C}_M \mathbf{F}^T \left(\mathbf{F} \mathbf{C}_M \mathbf{F}^T + \mathbf{C}_D\right)^{-1} \left(\mathbf{d}_{\text{obs}} - \mathbf{F} \mathbf{m}_{\text{prior}}\right) \tag{177}$$

and

$$\widetilde{\mathbf{C}}_M = \left(\mathbf{F}^T \mathbf{C}_D^{-1} \mathbf{F} + \mathbf{C}_M^{-1}\right)^{-1} \tag{178}$$

$$= \mathbf{C}_M - \mathbf{C}_M \mathbf{F}^T \left(\mathbf{F} \mathbf{C}_M \mathbf{F}^T + \mathbf{C}_D\right)^{-1} \mathbf{F} \mathbf{C}_M \quad . \tag{179}$$

If we do not have any prior information on the model parameters, then $\mathbf{C}_M \to \infty \mathbf{I}$, i.e.,

$$\mathbf{C}_M^{-1} \to 0 \, . \tag{180}$$

Formulas 175 and 178 then become

$$\widetilde{\mathbf{m}} = \left(\mathbf{F}^T \mathbf{C}_D^{-1} \mathbf{F}\right)^{-1} \left(\mathbf{F}^T \mathbf{C}_D^{-1} \mathbf{d}_{\text{obs}}\right) \tag{181}$$

and

$$\widetilde{\mathbf{C}}_M = \left(\mathbf{F}^T \mathbf{C}_D^{-1} \mathbf{F}\right)^{-1} \quad . \tag{182}$$

In the very special circumstance where we have the same number of 'data parameters' and 'model parameters', i.e., the case where the matrix $\mathbf{F}$ is a square matrix. Assume that the matrix is regular so its inverse exists. It is easy to see that equation 181 then becomes

$$\widetilde{\mathbf{m}} = \mathbf{F}^{-1} \mathbf{d}_{\text{obs}} \quad . \tag{183}$$

We see that in this special case $\widetilde{\mathbf{m}}$ is just the Cramer solution of the linear equation $\mathbf{d}_{\text{obs}} = \mathbf{F} \widetilde{\mathbf{m}}$.

## G The Structure of an Inference Space

Note: This appendix is a reproduction of a section of the e-paper arXiv:math-ph/0009029 that can be found at http://arXiv.org/abs/math-ph/0009029.

Before Kolmogorov, probability calculus was made using the intuitive notions of "chance" or "hazard". Kolmogorov's axioms clarified the underlying mathematical structure and brought probability calculus inside well defined mathematics. In this section we will recall these axioms. Our opinion is that the use in physical theories (where we have invariance requirements) of probability distributions, through the notions of conditional probability or the so-called Bayesian paradigm suffers today from the same defects as probability calculus suffered from before Kolmogorov. To remedy this, we introduce in this section, in the space of all probability distributions, two logical operations (OR and AND) that give the necessary mathematical structure to the space.

### G.1 Kolmogorov's Concept of Probability

A point $\mathbf{x}$, that can materialize itself anywhere inside a domain $\mathcal{D}$, may be realized, for instance, inside $\mathcal{A}$, a subdomain of $\mathcal{D}$. The probability of realization of the point is completely described if we have introduced a probability distribution (in Kolmogorov's sense) on $\mathcal{D}$, i.e., if to every subdomain $\mathcal{A}$ of $\mathcal{D}$ we are able to associate a real number $P(\mathcal{A})$, called the probability of $\mathcal{A}$, having the three properties:

- For any subdomain $\mathcal{A}$ of $\mathcal{D}$, $P(\mathcal{A}) \ge 0$.
- If $\mathcal{A}_i$ and $\mathcal{A}_j$ are two disjoint subsets of $\mathcal{D}$, then, $P(\mathcal{A}_i \cup \mathcal{A}_j) = P(\mathcal{A}_i) + P(\mathcal{A}_j)$.
- For a sequence of events $\mathcal{A}_1 \supseteq \mathcal{A}_2 \supseteq \cdots$ tending to the empty set, we have $P(\mathcal{A}_i) \to 0$.

We will not necessarily assume that a probability distribution is normed to unity ($P(\mathcal{D}) = 1$). Although one refers to this as a measure, instead of a probability, we will not use this distinction. Sometimes, our probability

47