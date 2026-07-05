174

Iterative Linear Solvers

## 11.4 Sparse Singular Value Calculations$^{8}$

The singular value decomposition is one of the most useful items in the inverter's toolkit. With the *SVD* one can compute the pseudo-inverse solution of rectangular linear systems, analyze resolution (within the linear and Gaussian assumptions), study the approximate null space of the forward problem, and more. The now classical Golub-Reinsch approach to *SVD* [GR70] begins by reducing the matrix to block bidiagonal form via a sequence of transformations known as Householder transformations. The Householder transformations annihilate matrix elements below the diagonal, one column at a time. Unfortunately, after each transformation has been applied, the sparsity pattern in the remaining lower triangular part of the matrix is the union of the sparsity pattern of the annihilated column and the rest of the matrix. After a very few steps, one is working with nearly full intermediate matrices. This makes conventional *SVD* unsuitable for large, sparse calculations. On the other hand, for some problems, such as studying the approximate null space of the forward problem, one doesn't really need the entire *SVD*; it suffices to compute the singular vectors associated with the small singular values ('small' here is defined relative the level of noise in the data). Or perhaps from experience one knows that one must iterate until all those eigenvectors down to a certain eigenvalue level have been included in the solution. Conventional *SVD* gives no choice in this matter, it's all or nothing. In this section we shall consider the use of iterative methods such as conjugate gradient for computing some or all singular value/singular vector pairs.

### 11.4.1 The Symmetric Eigenvalue Problem

For convenience (actually, to be consistent with the notation in [Sca89]) here is an equivalent form of the *CG* algorithm for symmetric, positive-definite systems $A\mathbf{x} = \mathbf{y}$.

**Algorithm 8 Method of Conjugate Gradients** Let $\mathbf{x}_0 = 0, \mathbf{r}_0 = \mathbf{p}_1 = \mathbf{y}$ and $\beta_1 = 0$. Then for $i = 1, 2, \dots$

$$
\begin{aligned}
\beta_i &= \frac{(\mathbf{r}_{i-1}, \mathbf{r}_{i-1})}{(\mathbf{r}_{i-2}, \mathbf{r}_{i-2})} \\
\mathbf{p}_i &= \mathbf{r}_{i-1} + \beta_i \mathbf{p}_{i-1} \\
\alpha_i &= \frac{(\mathbf{r}_{i-1}, \mathbf{r}_{i-1})}{(\mathbf{p}_i, A\mathbf{p}_i)} \\
\mathbf{x}_i &= \mathbf{x}_{i-1} + \alpha_i \mathbf{p}_i \\
\mathbf{r}_i &= \mathbf{r}_{i-1} - \alpha_i A\mathbf{p}_i
\end{aligned}
\tag{11.81}
$$

Now define two matrices $R_k$ and $P_k$ whose columns are, respectively, the residual and search vectors at the $k-th$ step of *CG*; $R_k = (\mathbf{r}_0, \dots, \mathbf{r}_{k-1})$ and $P_k = (\mathbf{p}_1, \dots, \mathbf{p}_k)$. Let $B_k$ be the bidiagonal matrix with ones on the main diagonal and $(-\beta_i, i = 2, \dots, k)$

$^{8}$This section is based upon [Sca89]

1