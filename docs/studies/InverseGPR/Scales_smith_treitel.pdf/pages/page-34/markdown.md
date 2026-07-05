2.3 What is an Answer?

19

### Suppose $\rho_T$ is Known

Suppose that we know that the density of kryptonite is exactly

$$\rho_T = 1.7\pi$$

In that case, we **must** have

$$P_{T|O}(\rho_T, \rho_O) = \delta(\rho_T - 1.7\pi)$$

(where $\delta(x)$ is the Dirac delta-function) *no matter what the observed value $\rho_O$ is.*

We are not asserting that the *observed* densities are all equal to $1.7\pi$: the observations are still subject to measurement noise. We do claim that the observations must always be consistent with the required value of $\rho_T$ (or that some element of this theory is wrong). This shows clearly that $P_{T|O} \neq P_{O|T}$ since one is a delta function, while the other must show the effects of experimental errors.

### Suppose $\rho_T$ is Constrained

Suppose that we don't know the true density of $K$ exactly, but we're sure it lies within some range of values:

$$P(\rho_T) = \begin{cases} C_K & \text{if } 5.6 > \rho_T > 5.1 \\ 0 & \text{otherwise} \end{cases}$$

where $C_K$ is a constant and $P$ refers to the probability distribution of possible values of the density. In that case, we'd expect $P_{T|O}$ must be zero for impossible values of $\rho_T$ but should have the same shape everywhere else since the density distribution of chunks taken from the pool is flat for those values. (The distribution does have to be renormalized, so that the probability of getting *some* value is one, but we can ignore this for now.) So we'd expect something like Figure 2.7.

### What Are We Supposed to Learn from All This?

We hope it's clear from these examples that the final value of $P_{T|O}$ depends upon both the errors in the measurement process and the distribution of *possible* true values determined by the source from which we acquired our sample(s). This is clearly the case for the second type of experiment (in which we draw multiple samples from a pool), but we have just shown above that it is also true when we have but a single sample and a single measurement. One of the reasons we afford so much attention to the simple one-sample experiment is that in geophysics we typically have only one sample, namely Earth.

What we're supposed to learn from all this, then, is

1