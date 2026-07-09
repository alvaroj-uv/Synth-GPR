12.2 Using the SVD

185

where $c_D$ is a scale factor chosen to make $W$ have as simple a form as possible. For example, Nolet chooses $c_3 = 56\pi/9$. Plugging the definition of the pixel functions and of the PSF into (12.6) it follows that

$$W \left( \mathbf{r}_0 \right) = \sum_{i,j,k} f_i A_{ji} A_{ki} b_j \left( \mathbf{r} \right) b_k \left( \mathbf{r}_0 \right) \tag{12.7}$$

where

$$f_i = c_D \int_{\Omega} \left| \mathbf{r} - \mathbf{r}_0 \right|^{D+1} h_i \left( \mathbf{r} \right)^2 d^D \mathbf{r} \approx c_D \left| \hat{r}_i - \mathbf{r}_0 \right|^{D+1}$$

and where $\hat{r}_i$ is the centroid of the $i$th cell. Equation (12.7) shows how the width of the PSF depends on the $\mathbf{b}$ coefficients. Now all one needs is a similar expression for the error of the average model value $\langle m \left( \mathbf{r}_0 \right) \rangle$

$$\sigma^2 = \text{Var} \langle m \left( \mathbf{r}_0 \right) \rangle = \sum_{i,j=1}^n b_i \left( \mathbf{r}_0 \right) b_j \left( \mathbf{r}_0 \right) \text{Cov}(d_i, d_j) = \mathbf{b} \left( \mathbf{r}_0 \right) \cdot \mathbf{b} \left( \mathbf{r}_0 \right).$$

The last equality follows since if one assumes that the data are uncorrelated, then weights can always be chosen such that $\text{Cov}(d_i, d_j) = \delta_{ij}$. Thus, it has been shown that both the width of the PSF and the variance of the solution depend on $\mathbf{b}$; Thus one cannot tighten up the PSF without affecting the variance. The solution, at least formally, is to introduce a tradeoff parameter, say $w$, and jointly minimize

$$J(w, \mathbf{r}_0) \equiv W(\mathbf{r}_0) + w^2 \sigma^2(\mathbf{r}_0).$$

This last problem is straightforwardly solved but note that to compute the coefficients $\mathbf{b}$ which jointly minimize the variance and the width of the PSF requires the solution of a (large) least squares problem at each point in the model where the resolving power is desired. For large, sparse operators $A$, a far more efficient approach would be using the conjugate gradient methods outlined in Chapter 11.

## 12.2 Using the SVD

Now let us look at this tradeoff for a finite-dimensional problem using the SVD. Let $A$ be the forward modeling operator, now assumed to map $R^m$ to $R^n$:

$$\mathbf{d} = A\mathbf{m} + \mathbf{e}$$

where $\mathbf{e}$ is an $n$-vector of random errors. The least squares estimated model $\hat{\mathbf{m}}$ is given by $A^\dagger\mathbf{d}$, where $A^\dagger$ is the pseudo-inverse of $A$.

The covariance of $\hat{\mathbf{m}}$ is $E[\hat{\mathbf{m}}\hat{\mathbf{m}}^T]$.$^a$ We can get a simple result for this matrix using the singular value decomposition. The singular value decomposition of $A$ is

$$A = U\Lambda V^T$$

$^a$Assuming that the errors are zero mean since then $E[\hat{\mathbf{m}}] = E[A^\dagger\mathbf{d}] = A^\dagger E[\mathbf{d}] = 0$.

1