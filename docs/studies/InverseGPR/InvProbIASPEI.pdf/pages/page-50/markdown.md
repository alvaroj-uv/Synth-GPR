update the prior probability $P(\cdot)$, replacing it by the conditional probability $P(\cdot|\mathcal{B}) = P(\cdot \cap \mathcal{B})/P(\mathcal{B})$. It equals $P(\cdot)$ inside $\mathcal{B}$ and is zero outside (center of the figure). If instead of the hard constraint $x \in \mathcal{B}$ we have a soft information about the location of $x$, represented by the probability distribution $Q(\cdot)$ (right of the figure), the intersection of the two states of information $P$ and $Q$ gives a new state of information (here, $\mu(x)$ is the probability density representing the state of null information, and, to simplify the figure, has been assumed to be constant). The comparison of the right with the center of the figure shows that the AND operation generalizes the notion of conditional probability. In the special case where the probability density representing the second state of information, $Q(\cdot)$, equals the null information probability density inside the domain $\mathcal{B}$ and is zero outside, then, the notion of intersection of states of information exactly reduces to the notion of conditional probability.

Now the interpretation of the neutral element for the AND operation can be made clear. We postulated that the neutral probability distribution $M$ is such that for any probability distribution $P$, $P \wedge M = P$. This means that if a point is realized according to a probability distribution $P$, and if a (finite accuracy) measure of the coordinates of the point produces the information represented by $M$, the posterior probability distribution, $P \wedge M$ is still $P$: the probability distribution $M$ is not carrying any information at all. Accordingly, we call $M$ the null information probability distribution. Sometimes, the probability density representing this state of null information is constant over all the space; sometimes, it is not, as explained in section 2.2. It is worth mentioning that this particular state of information enters in the Shannon's definition of Information Content (Shannon, 1948).

It is unfortunate that, when dealing with probability distributions over continuous spaces, conditional probabilities are often misused. Section P describes the so-called Borel-Kolmogorov paradox: using conditional probability densities in a space with coordinates $(x, y)$ will give results that will not be consistent with those obtained by the use of conditional probability densities on the same space but where other coordinates $(u, v)$ are used (if the change of coordinates is nonlinear). Jaynes (1995) gives an excellent, explicit, account of the paradox. But his choice for resolving the paradox is different from our's: while Jaynes just insists on the technical details of how some limits have to be taken in order to ensure consistency, we radically decide to abandon the notion of conditional probability, and replace it by the intersection of states of information (the AND operation) which is naturally consistent under a change of variables.

## H Homogeneous Probability for Elastic Parameters

In this appendix, we start from the assumption that the uncompressibility modulus and the shear modulus are Jeffreys parameters (they are the eigenvalues of the stiffness tensor $c_{ijk\ell}$), and find the expression of the homogeneous probability density for other sets of elastic parameters, like the set { Young's modulus - Poisson ratio } or the set { Longitudinal wave velocity - Tranverse wave velocity }.

### H.1 Uncompressibility Modulus and Shear Modulus

The 'Cartesian parameters' of elastic theory are the logarithm of the uncompressibility modulus and the logarithm of the shear modulus

$$\kappa^* = \log \frac{\kappa}{\kappa_0} \quad ; \quad \mu^* = \log \frac{\mu}{\mu_0} \quad , \tag{189}$$

where $\kappa_0$ and $\mu_0$ are two arbitrary constants. The homogeneous probability density is just constant for these parameters (a constant that we set arbitrarily to one)

$$f_{\kappa^*\mu^*}(\kappa^*, \mu^*) = 1 \quad . \tag{190}$$

As is often the case for homogeneous 'probability' densities, $f_{\kappa^*\mu^*}(\kappa^*, \mu^*)$ is not normalizable. Using the jacobian rule, it is easy to transform this probability density into the equivalent one for the positive parameters themselves

$$f_{\kappa\mu}(\kappa, \mu) = \frac{1}{\kappa\mu} \quad . \tag{191}$$

This $1/x$ form of the probability density remains invariant if we take any power of $\kappa$ and of $\mu$. In particular, if instead of using the uncompressibility $\kappa$ we use the compressibility $\gamma = 1/\kappa$, the Jacobian rule simply gives $f_{\gamma\mu}(\gamma, \mu) = 1/(\gamma\mu)$.

Associated to the probability density 190 there is the Euclidean definition of distance

$$ds^2 = (d\kappa^*)^2 + (d\mu^*)^2 \quad , \tag{192}$$

50