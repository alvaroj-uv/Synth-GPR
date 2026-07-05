11.4 Sparse SVD

175

on the superdiagonal ($\beta_i$ are the $CG$ scale factors). Finally, let $\Delta_k$ be the matrix $diag(\rho_0, \ldots, \rho_{k-1})$, where $\rho_i \equiv \| \mathbf{r}_i \|$.

Using the recursion

$$\mathbf{p}_{i+1} = \mathbf{r}_i + \beta_{i+1} \mathbf{p}_i \qquad i = 2, \ldots, k$$

and the fact that $\mathbf{p}_1 = \mathbf{r}_0$, it follows by direct matrix multiplication that

$$R_k = P_k B_k.$$

Therefore

$$R_k^T A R_k = B_k^T P_k^T A P_k B_k.$$

The reason for looking at $R_k^T A R_k$ is that since $R_k$ is orthogonal (cf. Lemma 4), the matrix $R_k^T A R_k$ must have the same eigenvalues as $A$ itself.

But since the $\mathbf{p}$ vectors are A-orthogonal, it follows that

$$P_k^T A P_k = diag[(\mathbf{p}_1, A \mathbf{p}_1), \ldots, (\mathbf{p}_k, A \mathbf{p}_k)].$$

Using this and normalizing the $R$ matrix with $\Delta$ gives the following tridiagonalization of $A$

$$T_k = \Delta_k^{-1} B_k^T diag[(\mathbf{p}_1, A \mathbf{p}_1), \ldots, (\mathbf{p}_k, A \mathbf{p}_k)] B_k \Delta_k^{-1}. \tag{11.82}$$

Carrying through the matrix multiplications gives the elements of $T_k$

$$\begin{array}{rcl} (T_k)_{i,i} & = & \left[ \frac{1}{\alpha_i} + \frac{\beta_i}{\alpha_{i-1}} \qquad i = 1, \ldots, k \right] \\ (T_k)_{i,i+1} & = & \left[ -\frac{\sqrt{\beta_{i+1}}}{\alpha_i} \qquad i = 1, \ldots, k-1 \right] \end{array} \tag{11.83} \tag{11.84}$$

In other words, just by doing $CG$ one gets a symmetric tridiagonalization of the matrix for free. Needless to say, computing the eigenvalues of a symmetric tridiagonal matrix is vastly simpler and less costly than extracting them from the original matrix. For rectangular matrices, simply apply the least squares form of $CG$ and use the $\alpha$ and $\beta$ scale factors in (11.83) and (11.84), to get a symmetric tridiagonalization of the normal equations. Then, just take their positive square roots to get the singular values. The calculation of the eigenvalues of symmetric tridiagonal matrices is the subject of a rather large literature. See [Sca89] for details.

The following example illustrates the idea of iterative eigenvalue computation. We will consider the Hilbert matrix, whose $i - j$ element is $\frac{1}{i+j+1}$. This matrix arises in the theory of approximation and is known to be highly ill-conditioned.$^h$

The matrix in question is an eighth-order Hilbert matrix:

$^h$A simple explanation for this was contributed to the Usenet news group sci.math by Zdislav V. Kovarik. The idea is you can interpret the $i - j$ element as the inner product of $x^i$ and $x^j$ on the interval $[0, 1]$. Now, the cosine of the angle between $x^k$ and $x^-(k+1)$ is just $\frac{1}{2+k+2}$. So you can see that as $k$ increases, this matrix, which consists of the scalar products of these almost linearly dependent vectors, is bound to be nearly singular.

1