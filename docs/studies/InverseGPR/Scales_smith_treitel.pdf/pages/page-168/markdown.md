11.1 Classical Iterative Methods

153

# Algorithm 1 Jacobi's Method

$$B = D, \qquad I - B^{-1}A = J \tag{11.9}$$

$$a_{j,j}x_{j(i+1)} + \sum_{k \neq j} a_{j,k}x_{k(i)} = h_j \quad j = 1, 2, \dots, n, \quad i = 0, 1, \dots \tag{11.10}$$

where the subscript in parentheses refers to the iteration number. Jacobi's method is also called the "total step method." To get the "single step" or Gauss-Seidel method choose $B$ to be the lower triangular part of $A$ including the diagonal:

# Algorithm 2 Gauss-Seidel Method

$$B = D - E, \qquad I - B^{-1}A = (I - L)^{-1}U = H \tag{11.11}$$

$$\sum_{k < j} a_{j,k}x_{k(i+1)} + a_{j,j}x_{j(i+1)} + \sum_{k > j} a_{j,k}x_{k(i)} = h_j \quad j = 1, 2, \dots, n, \quad i = 0, 1, \dots \tag{11.12}$$

More generally still, one may consider using a class of splitting matrices $B(\omega)$ depending on a parameter $\omega$, and choosing $\omega$ in such a way as to make the spectral radius of $I - B^{-1}(\omega)A$ as small as possible. The "relaxation" methods are based on the following choice for $B$:

# Algorithm 3 Relaxation Methods

$$B(\omega) = \frac{1}{\omega}D(I - \omega L) \tag{11.13}$$

$$B(\omega)\mathbf{x}_{i+1} = (B(\omega) - A)\mathbf{x}_i + \mathbf{h} \qquad i = 0, 1, \dots \tag{11.14}$$

For $\omega > 1$ this is called overrelaxation, while for $\omega < 1$ it is called underrelaxation. For $\omega = 1$ (11.14) reduces to Gauss-Seidel. The rate of convergence of this method is determined by the spectral radius of

$$I - B^{-1}(\omega)A = (I - \omega L)^{-1}[(1 - \omega)I + \omega U] \tag{11.15}$$

The books by Young [You71] and Stoer & Bulirsch [SB80] have many convergence results for relaxation methods. An important one, due to Ostrowski and Reich is:

Theorem 12 For positive definite matrices $A^b$

$$\rho(I - B^{-1}(\omega)A) < 1 \qquad \forall \ 0 < \omega < 2. \tag{11.16}$$

In particular, the Gauss-Seidel method ($\omega = 1$) converges for positive definite matrices.

For a proof of this result, see [SB80], pages 547-548. This result can be considerably sharpened for what Young calls type-A matrices or the "consistently ordered" matrices (see, for example, [You71], chapter 5).

$^b$A matrix $A$ is positive if $(x, Ax) \geq 0$ for all $x$. It is positive definite if the inequality is strict.

1