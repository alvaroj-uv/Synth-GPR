112

Linear Inverse Problems With Uncertain Data

The important thing to notice here is that this says the velocity and depth are completely correlated (off diagonal entries magnitude equal to 1), and that the correlation is negative. This means that increasing one is the same as decreasing the other. The covariance matrix itself has the following eigenvalue/eigenvector decomposition.

$$\operatorname{Cov}(\mathbf{m}) = \left(\frac{\sigma}{2}\right)^2 \left[ \begin{array}{cc} 1 & 1 \\ -1 & 1 \end{array} \right] \left[ \begin{array}{cc} 1 & 0 \\ 0 & 0 \end{array} \right] \left[ \begin{array}{cc} 1 & -1 \\ 1 & 1 \end{array} \right]. \tag{7.18}$$

These orthogonal matrices correspond to rotations of the velocity/depth axes. These axes are associated with the line $z/c = t$. So for a given travel time $t$, we can be anywhere on the line $z = tc$: there is complete uncertainty in model space along this line and this uncertainty is reflected in the zero eigenvalue of the covariance matrix.

For a two-dimensional problem such as this the correlation coefficient measures the similarity in the fluctuations in the two random variables. Here the two random variables are our estimates of $z$ and $c$. Formally the correlation coefficient is defined to be:

$$r = \frac{C_{zc}}{\sigma_z \sigma_c}.$$

Since the covariance matrix is symmetric $C_{zc} = C_{cz}$. $\sigma_z$ and $\sigma_c$ are just the standard deviations of the corresponding parameter estimates: $\sigma_z = \sqrt{C_z z}$ and $\sigma_c = \sqrt{C_c c}$. So

$$r = \frac{-1}{1}.$$

It is not hard to show that for a two-dimensional Gaussian probability density, the level surfaces (contours of constant probability) are ellipses (circles and lines being special cases of ellipses). If the two random variables are zero-mean and have the same variances, then the level surfaces fall into one of three classes depending on the size of the correlation coefficient. First note that the correlation coefficient is always less than or equal to one in absolute value. If $r = 0$ then the level surfaces are circles. If $0 < |r| < 1$, then the level surfaces are true ellipses. Finally, if $|r| = 1$ the level surfaces are lines, as in the example above.

### 7.1.1 The Damped Least Squares Problem

The generalized inverse solution of the two-parameter problem is

$$m^{\dagger} = A^{\dagger} t = \frac{t}{2} \left[ \begin{array}{c} 1 \\ -1 \end{array} \right]. \tag{7.19}$$

As we have seen before, least squares tends to want to average over ignorance. Since we cannot determine velocity and depth individually, but only their ratio, least squares puts half the data into each. Damping does not change this, it is still least squares, but it does change the magnitude of the computed solution. Since damping penalizes the

1