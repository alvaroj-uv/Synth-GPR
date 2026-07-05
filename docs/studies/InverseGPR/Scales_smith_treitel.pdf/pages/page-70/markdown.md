4.10 A few examples

55

On the other hand, if we only include the terms in the sum associated with the $r$ nonzero singular values, then we get a projection operator onto the non-null space (which is the row space). So

$$\sum_{i=1}^{r} \mathbf{v}_{i} \mathbf{v}_{i}^{T} = V_{r} V_{r}^{T}$$

is a projection operator onto the row space. By the same reasoning

$$\sum_{i=r+1}^{m} \mathbf{v}_{i} \mathbf{v}_{i}^{T} = V_{0} V_{0}^{T}$$

is a projection operator onto the null space. Putting this all together we can say that

$$V_{r} V_{r}^{T} + V_{0} V_{0}^{T} = I.$$

This says that any vector in $\mathbf{R}^{m}$ can be written in terms of its component in the null space and its component in the row space of $A$. Let $\mathbf{x} \in \mathbf{R}^{m}$, then

$$\mathbf{x} = I \mathbf{x} = \left( V_{r} V_{r}^{T} + V_{0} V_{0}^{T} \right) \mathbf{x} = (\mathbf{x})_{\text{row}} + (\mathbf{x})_{\text{null}}. \tag{4.90}$$

## 4.10 A few examples

This example shows that often matrices with repeated eigenvalues cannot be diagonalized. But symmetric matrices can **always** be diagonalized.

$$A = \left[ \begin{array}{cc} 3 & 1 \\ 0 & 3 \end{array} \right] \tag{4.91}$$

The eigenvalues of this matrix are obviously 3 and 3. This matrix has a one-dimensional family of eigenvectors; any vector of the form $(x, 0)^{T}$ will do. So it cannot be diagonalized, it doesn't have enough eigenvectors.

Now consider

$$A = \left[ \begin{array}{cc} 3 & 0 \\ 0 & 3 \end{array} \right] \tag{4.92}$$

The eigenvalues of this matrix are still 3 and 3. But it will be diagonalized **by any invertible matrix**! So, of course, to make our lives simple we will choose an orthogonal matrix. How about

$$\left[ \begin{array}{cc} 0 & 1 \\ 1 & 0 \end{array} \right]? \tag{4.93}$$

0