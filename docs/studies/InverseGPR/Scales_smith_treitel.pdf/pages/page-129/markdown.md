114

Linear Inverse Problems With Uncertain Data

The covariance matrix for the augmented system is

$$\operatorname{Cov}(\mathbf{m}) = A_{\lambda}^{\dagger} \operatorname{Cov}(\mathbf{d}) A_{\lambda}^{\dagger T}. \tag{7.24}$$

For example, with $\lambda = 1$ the velocity/depth covariance is

$$\operatorname{Cov}(z, c) = \frac{\sigma^2}{3} \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}. \tag{7.25}$$

Right away we can see that since the eigenvalues of this matrix are 1 and 3, instead of a degenerate ellipsoid (infinite aspect ratio), the error ellipsoid of the damped problem has an aspect ratio of 3. As the damping increases, the covariance matrix becomes increasingly diagonal, resulting in a circular error ellipsoid. You will calculate the analytic result as an exercise. Your result should become degenerate as $\lambda \to 0$.

### Exercises

- Extend the two-parameter travel time inversion problem to the case in which the ray reflects from the flat interface at an angle of $\theta$, measured relative to the vertical. I.e, $\theta = 0$ would correspond to a ray that goes straight up and down. Assume that the travel time can be measured with an uncertainty of $\sigma$ second.
- Compute the pseudoinverse and resolution matrix of

$$\begin{pmatrix} 1 & -1 & 2 & 0 \\ 4 & -4 & 0 & 0 \end{pmatrix}$$

Assuming the right hand side is $(0, 1)^T$, what is the least squares estimator of the 4-dimensional model vector.

- Compute the pseudoinverse and resolution matrix of

$$\begin{pmatrix} 1 & -1 \\ 4 & -4 \\ 0 & 1 \\ 0 & -1 \end{pmatrix}$$

Assuming the right hand side is $(0, 1, -1, 0)^T$, what is the least squares estimator of the 4-dimensional model vector.

- Assuming the data covariance matrix is

$$\begin{pmatrix} 1 & 0 & 0 & 0 \\ 0 & .5 & 0 & 0 \\ 0 & 0 & .1 & 0 \\ 0 & 0 & 0 & .0001 \end{pmatrix}$$

compute the covariance of matrix of the least squares estimator.

1