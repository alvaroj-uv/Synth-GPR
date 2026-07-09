10.3 Priors in High Dimensional Spaces: The Curse of Dimensionality 145

But even this objection can be overcome with a different choice of probability distribution to soften the constraint. For example, choose $m$ to be uniformly distributed on $[0, 1]$ and choose the $n - 1$ spherical polar angles uniformly on their respective domains. This probability is uniform on $\|\mathbf{m}\|$, but non-uniform on the ball. However it is consistent with the constraint and has the property that the mean and variance of $m^2$ is independent of the dimension of the space.

So, as Backus has said, we must be very careful in replacing a hard constraint with a probability distribution, especially in a high-dimensional model space. Apparently innocent choices may lead to unexpected behavior.

## Appendix: Entropy

This appendix is a brief introduction to entropy as it relates to inversion. For more details see [GMS01]. In Bayesian inversion we use probabilities to represent states of information. But just how does one quantify such a state? Is it possible to say that one probability has more information than another?

Consider an experiment with $N$ possible outcomes each occurring with a probability $p_i$. In analogy with the statistical mechanical definition of entropy, [Sha48] introduced the following definition of the entropy for such discrete probabilities:

$$H(p) = - \sum_i p_i \log p_i. \tag{10.3}$$

Following Shannon, three postulates should be satisfied by $H(p)$ or any other measure of information. Those are:

2. Monotonicity, and

These postulates are discussed in detail in [GMS01], here a qualitative understanding is sufficient. The first postulate requires that we should not gain or loose a large amount of information by making a small change to the probabilities. The second postulate, monotonicity, refers to the information associated with a collection of independent, equally likely events. It is clear that in such a case the uncertainty must increase monotonically with the number of possible outcomes. The third postulate requires that it should not matter how one regroups the events of a given set. The entropy of the set should stay the same.

To see the meaning of Equation 10.3, consider an experiment whose outcome is known with absolute certainty. Then, the corresponding probability density is a Kronecker

1