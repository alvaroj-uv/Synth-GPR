BIBLIOGRAPHY

133

Here $\mathbf{m}_{\text{map}}$ is the maximum of the posterior distribution, which for a Gaussian is also the mean. So to find our estimator we need to optimize Equation 9.3. But that is equivalent to minimizing the exponent:

$$\min_{\mathbf{m}} \left[ (G\mathbf{m} - \mathbf{d}_{obs})^T C_D^{-1} (G\mathbf{m} - \mathbf{d}_{obs}) + (\mathbf{m} - \mathbf{m}_{\text{prior}})^T C_M^{-1} (\mathbf{m} - \mathbf{m}_{\text{prior}}) \right]. \quad (9.6)$$

But this is nothing but a weighted least squares problem. This is even easier to see if we introduce the square roots of the covariance matrices. Then the first term above is

$$\left( (C_D^{-1/2})^T (G\mathbf{m} - \mathbf{d}_{obs}), C_D^{-1/2} (G\mathbf{m} - \mathbf{d}_{obs}) \right) = \| C_D^{-1/2} (G\mathbf{m} - \mathbf{d}_{obs}) \|^2$$

while the second term is

$$\| C_M^{-1/2} (\mathbf{m} - \mathbf{m}_{\text{prior}}) \|^2.$$

Here we have used two important facts. This first is that the inverse of a symmetric matrix is symmetric. The second is that every symmetric matrix has a square root. To see this consider the diagonalization of such a matrix via an orthogonal transformation:

$$A = Q \Lambda Q^T.$$

So it is not too hard to see that

$$A = \left( Q \Lambda^{1/2} Q^T \right) \left( Q \Lambda^{1/2} Q^T \right) = Q \Lambda^{1/2} \Lambda^{1/2} Q^T = Q \Lambda Q^T$$

where the meaning of $\Lambda^{1/2}$ is clear since it is diagonal with real elements. So $Q \Lambda^{1/2} Q^T$ is the square root of $A$.

## Bibliography

[Tar87] A. Tarantola. *Inverse Problem Theory*. Elsevier, New York, 1987.

1