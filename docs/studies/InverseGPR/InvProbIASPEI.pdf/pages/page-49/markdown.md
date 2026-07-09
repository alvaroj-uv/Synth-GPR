While fuzzy set theory is an alternative to classical probability (and is aimed at the solution of a different class of problems), our aim here is only to complete the classical probability theory. As explained below the solution given by equations 184 correspond to the natural generalisation of two fundamental operations in classical probability theory: that of “making histograms” and that of taking “conditional probabilities”. To simplify our language, we will sometimes use this correspondence between our theory and the fuzzy set theory, and will say that the OR operation, when applied to two probability distributions, corresponds to the union of the two states of information, while the AND operation corresponds to their intersection.

It is easy to write some extra conditions that distinguish the two solutions given by equations 184 and 185. For instance, as probability densities are normed using a multiplicative constant (this is not the case with the grades of membership in fuzzy set theory), it makes sense to impose the simplest possible algebra for the multiplication of probability densities $p(\mathbf{x}), q(\mathbf{x}) \ldots$ by constants $\lambda, \mu \ldots$:

$$[(\lambda + \mu)p](\mathbf{x}) = (\lambda p \vee \mu p)(\mathbf{x}) \quad ; \quad [\lambda(p \wedge q)](\mathbf{x}) = (\lambda p \wedge q)(\mathbf{x}) = (p \wedge \lambda q)(\mathbf{x}) \ . \tag{186}$$

This is different from finding a (minimal) set of axioms characterizing (uniquely) the proposed solution, which is an open problem.

One important property of the two operations OR and AND just introduced is that of invariance with respect to a change of variables. As we consider probability distribution over a continuous space, and as our definitions are independent of any choice of coordinates over the space, it must happen that we obtain equivalent results in any coordinate system. Changing for instance from the coordinates $\mathbf{x}$ to some other coordinates $\mathbf{y}$, will change a probability density $p(\mathbf{x})$ to $\tilde{p}(\mathbf{y}) = p(\mathbf{x}) |\partial\mathbf{x}/\partial\mathbf{y}|$. It can easily be seen that performing the OR or the AND operation, then changing variables, gives the same result than first changing variables, then, performing the OR or the AND operation.

Let us mention that the equivalent of equations 184 for discrete probability distributions is:

$$(p \vee q)_i = p_i + q_i \quad ; \quad (p \wedge q)_i = \frac{p_i q_i}{\mu_i} \ . \tag{187}$$

Although the OR and AND notions just introduced are consistent with classical logic, they are here more general, as they can handle states of information that are more subtle than just the “possible” or “impossible” ones.

### G.3 The Interpretation of the OR and the AND Operation

If an experimenter faces realizations of a random process and wants to investigate the probability distribution governing the process, he may start making histograms of the realizations. For instance, for realizations of a probability distribution over a continuous space, he will obtain histograms that, in some sense, will approach the probability density corresponding to the probability distribution.

A histogram is typically made by dividing the working space into cells, and by counting how many realizations fall inside each cell. A more subtle approach is possible. First, we have to understand that, in the physical sciences, when we say “a random point has materialized in an abstract space”, we may mean something like “this object, one among many that may exist, vibrates with some fixed period; let us measure as accurately as possible its period of oscillation”. Any physical measure of a real quantity will have attached uncertainties. This means that when, mathematically speaking, we measure “the coordinates of a point in an abstract space” we will not obtain a point, but a state of information over the space, i.e., a probability distribution.

If we have measured the coordinates of many points, the results of each measurement will be described by a probability density $p_i(\mathbf{x})$. The union of all these, i.e., the probability density

$$(p_1 \vee p_2 \vee \ldots)(\mathbf{x}) = \sum_i p_i(\mathbf{x}) \tag{188}$$

is a finer estimation of the background probability density than an ordinary histogram, as actual measurement uncertainties are used, irrespective of any division of the space into cells. If it happens that the measurement uncertainties can be described using box-car functions at fixed positions, then, the approach we propose reduces to the conventional making of histograms.

Figure 1 explains that our definition of the AND operation is a generalization of the notion of conditional probability. A probability distribution $P(\cdot)$ is represented, in the figure, by its probability density. To any region $\mathcal{A}$ of the plane, it associates the probability $P(\mathcal{A})$. If a point has been realized following the probability distribution $P(\cdot)$ and we are given the information that, in fact, the point is “somewhere” inside the region $\mathcal{B}$, then we can

49