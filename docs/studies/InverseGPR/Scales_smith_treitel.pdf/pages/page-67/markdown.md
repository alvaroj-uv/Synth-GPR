52

A Little Linear Algebra

## 4.8 Orthogonal decomposition of rectangular matrices

For dimensional reasons there is clearly no hope of the kind of eigenvector decomposition discussed above being applied to rectangular matrices. However, there is an amazingly useful generalization that pertains if we allow a different orthogonal matrix on each side of $A$. It is called the *Singular Value Decomposition* (SVD) and **works for any matrix whatsoever**. Essentially the singular value decomposition generates orthogonal bases of $\mathbf{R}^m$ and $\mathbf{R}^n$ simultaneously.

**Theorem 7 Singular value decomposition** *Any matrix $A \in \mathbf{R}^{n \times m}$ can be factored as*

$$A = U \Lambda V^T \tag{4.77}$$

*where the columns of $U \in \mathbf{R}^{n \times n}$ are eigenvectors of $AA^T$ and the columns of $V \in \mathbf{R}^{m \times m}$ are the eigenvectors of $A^T A$. $\Lambda \in \mathbf{R}^{n \times m}$ is a rectangular matrix with the singular values on its main diagonal and zero elsewhere. The singular values are the square roots of the eigenvalues of $A^T A$, which are the same as the nonzero eigenvalues of $AA^T$. Further, there are exactly $r$ nonzero singular values, where $r$ is the rank of $A$.*

The columns of $U$ and $V$ span the four fundamental subspaces. The column space of $A$ is spanned by the first $r$ columns of $U$. The row space is spanned by the first $r$ columns of $V$. The left nullspace of $A$ is spanned by the last $n - r$ columns of $U$. And the nullspace of $A$ is spanned by the last $m - r$ columns of $V$.

A direct approach to the SVD, due to the physicist Lanczos[Lan61], is to make a symmetric matrix out of the rectangular matrix $A$ as follows: Let

$$S = \left[ \begin{array}{cc} 0 & A \\ A^T & 0 \end{array} \right]. \tag{4.78}$$

Since $A$ is in $\mathbf{R}^{n \times m}$, $S$ must be in $\mathbf{R}^{(n+m) \times (n+m)}$.

$m$ by $n$ or $n$ by $m$? For the rest of this book we will interpret the matrix $A$ as mapping from the space of model parameters into the space of data—the forward problem. So there are $m$ parameters and $n$ data. But, obviously this is unnecessary for the interpretation of the results. Model space is simply $\mathbf{R}^m$ and data space is $\mathbf{R}^n$.

And since $S$ is symmetric it has orthogonal eigenvectors $\mathbf{w}_i$ with real eigenvalues $\lambda_i$

$$S \mathbf{w}_i = \lambda_i \mathbf{w}_i. \tag{4.79}$$

If we split up the eigenvector $\mathbf{w}_i$, which is in $\mathbf{R}^{n+m}$, into an $n$-dimensional data part and an $m$-dimensional model part

$$\mathbf{w}_i = \left[ \begin{array}{c} \mathbf{u}_i \\ \mathbf{v}_i \end{array} \right] \tag{4.80}$$

0