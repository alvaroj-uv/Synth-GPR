6.4 Probability Functions and Densities

85

# covariances

The multidimensional generalization of the variance is the covariance. Let $\rho(\mathbf{x}) = \rho(x_1, x_2, ... x_n)$ be a joint probability density. The the $i - j$ components of the covariance matrix are defined to be:

$$C_{ij}(\mathbf{m}) = \int (x_i - m_i)(x_j - m_j)\rho(\mathbf{x}) \ d\mathbf{x} \tag{6.43}$$

where $\mathbf{m}$ is the mean of the distribution

$$\mathbf{m} = \int \mathbf{x}\rho(\mathbf{x}) \ d\mathbf{x}. \tag{6.44}$$

Equivalently we could say that

$$C = E[(\mathbf{x} - \mathbf{m})(\mathbf{x} - \mathbf{m})^T]. \tag{6.45}$$

From this definition it is obvious that $C$ is a symmetric matrix. The diagonal elements of the covariance matrix are just the ordinary variances (squares of the standard deviations) of the components:

$$C_{ii}(\mathbf{m}) = (\sigma_i)^2. \tag{6.46}$$

The off-diagonal elements describe the dependence of pairs of components.

As a concrete example, the $n$-dimensional normalized gaussian distribution with mean $\mathbf{m}$ and covariance $C$ is given by

$$\rho(\mathbf{x}) = \frac{1}{(2\pi \det C)^{N/2}} \exp \left[ -\frac{1}{2}(\mathbf{x} - \mathbf{m})^T C^{-1} (\mathbf{x} - \mathbf{m}) \right]. \tag{6.47}$$

This result and many other analytic calculations involving multi-dimensional Gaussian distributions can be found in [MGB74] and [Goo00].

# An aside, diagonalizing the covariance

Since the covariance matrix is symmetric, we can always diagonalize it with an orthogonal transformation involving real eigenvalues. It we transform to principal coordinates (i.e., rotate the coordinates using the diagonalizing orthogonal transformation) then the covariance matrix becomes diagonal. So in these coordinates correlations vanish since they are governed by the off-diagonal elements of the covariance matrix. But suppose one or more of the eigenvalues is zero. This means that the standard deviation of that parameter is zero; i.e., our knowledge of this parameter is certain. Another way to say this is that one or more of the parameters is deterministically related to the others. This is not a problem since we can always eliminate such parameters from the probabilistic description of the problems. Finally, after diagonalizing $C$ we can scale the parameters by their respective standard deviations. In this new rotated, scaled coordinate system the covariance matrix is just the identity. In this sense, we can assume in a theoretical analysis that the covariance is the identity since in

0