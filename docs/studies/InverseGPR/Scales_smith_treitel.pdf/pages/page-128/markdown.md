7.1 The World's Second Smallest Inverse Problem

113

norm of the solution, we can take an educated guess that the damped solution should, for large values of the damping parameter $\lambda$, tend to

$$\frac{t}{\lambda} \left[ \begin{array}{c} 1 \\ -1 \end{array} \right]. \tag{7.20}$$

For small values of $\lambda$, the damped solution must tend to the already computed generalized inverse solution. It will be shown shortly that the damped generalized inverse solution is

$$m_{\lambda}^{\dagger} = \frac{t}{\lambda + 2} \left[ \begin{array}{c} 1 \\ -1 \end{array} \right]. \tag{7.21}$$

### Exact Solution

The damped least squares estimator satisfies

$$(A^T A + \lambda I) \mathbf{m}_{\lambda} = A^T \mathbf{d}.$$

Since the matrix on the left is by construction invertible, we have

$$\mathbf{m}_{\lambda}^{\dagger} = (A^T A + \lambda I)^{-1} A^T \mathbf{d}.$$

If

$$A^T A = \left[ \begin{array}{cc} 1 & -1 \\ -1 & 1 \end{array} \right]$$

then

$$(A^T A + \lambda I)^{-1} = \frac{1}{(2 + \lambda)\lambda} \left[ \begin{array}{cc} 1 + \lambda & 1 \\ 1 & 1 + \lambda \end{array} \right].$$

So the exact damped least squares solution is

$$\mathbf{m}_{\lambda}^{\dagger} = \frac{1}{(2 + \lambda)\lambda} \left[ \begin{array}{cc} 1 + \lambda & 1 \\ 1 & 1 + \lambda \end{array} \right] \left[ \begin{array}{c} 1 \\ -1 \end{array} \right] t = \frac{t}{\lambda + 2} \left[ \begin{array}{c} 1 \\ -1 \end{array} \right].$$

Damping changes the covariance structure of the problem too. We will not bother deriving a analytic expression for the damped covariance matrix, but a few cases will serve to illustrate the main idea. The damped problem $[A^T A + \lambda I]\mathbf{m} = A^T \mathbf{d}$, is equivalent to the ordinary normal equations for the augmented matrix

$$A_{\lambda} \equiv \left[ \begin{array}{c} A \\ \sqrt{\lambda} I \end{array} \right] \tag{7.22}$$

where $A$ is the original matrix and $I$ is an identity matrix of dimension equal to the number of columns of $A$. In our toy problem this is

$$A_{\lambda} \equiv \left[ \begin{array}{cc} 1 & -1 \\ \sqrt{\lambda} & 0 \\ 0 & \sqrt{\lambda} \end{array} \right]. \tag{7.23}$$

1