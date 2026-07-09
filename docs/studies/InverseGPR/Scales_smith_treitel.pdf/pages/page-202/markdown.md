BIBLIOGRAPHY

187

It follows that the variance of the $j$-th component of $\hat{\mathbf{m}}^p$ is monotonically nondecreasing with $p$. So, while we can formally decrease the variance by using fewer eigenvectors, we end up with a less resolution because we won't have enough structure in the remaining eigenvectors to characterize the model.

In general we cannot compute the bias for an estimate of the true model without taking into account the discretization, but let's neglect this for the moment and assume that $A$ represents the exact forward problem and that the true model lies within $R^m$. The bias of $\hat{\mathbf{m}}^r$ is the component of the true model in the row space of $A$, assuming zero-mean errors.$^c$ So, apart from the component of the true model in the row space of $A$, the bias of $\hat{\mathbf{m}}^p$ is

$$\text{bias}(\hat{\mathbf{m}}^p) = E[\hat{\mathbf{m}}^p - \hat{\mathbf{m}}^r] = \sum_{i=p+1}^r \mathbf{v}_i \frac{\mathbf{u}_i^T \mathbf{d}}{\lambda^i}.$$

## Bibliography

[BG67] G. Backus and F. Gilbert. Numerical applications of a formalism for geophysical inverse problems. *Geophysical Journal of the Royal Astronomical Society*, 13:247–276, 1967.

[Nol85] G. Nolet. *Journal of Computational Physics*, 1985.

$^c E[\hat{\mathbf{m}} - \mathbf{m}] = E[A^\dagger A\mathbf{m} + A^\dagger \mathbf{d} - \mathbf{m}] = (A^\dagger A - I)\mathbf{m}$. Now $A^\dagger A$ projects onto the null space of $A$, so $A^\dagger A - I$ projects onto the orthogonal complement of this, which is the row space.

1