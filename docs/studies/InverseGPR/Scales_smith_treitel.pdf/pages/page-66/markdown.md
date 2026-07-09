4.7 Eigenvalues and Eigenvectors

51

**Theorem 4 Matrix diagonalization** *Let $A$ be an $n \times n$ matrix with $n$ linearly independent eigenvectors. Let $S$ be a matrix whose columns are these eigenvectors. Then $S^{-1}AS$ is a diagonal matrix $\Lambda$ whose elements are the eigenvalues of $A$.*

The proof is easy. The elements in the first column of the product matrix $AS$ are precisely the elements of the vector which is the inner product of $A$ with the first column of $S$. The first column of $S$, say $\mathbf{s}_1$, is, by definition, an eigenvector of $A$. Therefore the first column of $AS$ is $\lambda_1\mathbf{s}_1$. Since this is true for all the columns, it follows that $AS$ is a matrix whose columns are $\lambda_i\mathbf{s}_i$. But now we're in business since

$$[\lambda_1\mathbf{s}_1\ \lambda_2\mathbf{s}_2\ \cdots\ \lambda_n\mathbf{s}_n] = [\mathbf{s}_1\ \mathbf{s}_2\ \cdots\ \mathbf{s}_n]\operatorname{diag}(\lambda_1, \lambda_2, \cdots, \lambda_n) \equiv S\Lambda. \quad (4.75)$$

Therefore $AS = S\Lambda$ which means that $S^{-1}AS = \Lambda$. $S$ must be invertible since we've assumed that all it's columns are linearly independent.

Some points to keep in mind:

- Any matrix in $\mathbf{R}^{n \times n}$ with $n$ distinct eigenvalues can be diagonalized.
- Because the eigenvectors themselves are not unique, the diagonalizing matrix $S$ is not unique.
- Not all square matrices possess $n$ linearly independent eigenvectors.
- A matrix can be invertible without being diagonalizable.

We can summarize these ideas with a theorem whose proof can be found in linear algebra books.

**Theorem 5 Linear independence of eigenvectors** *If $n$ eigenvectors of an $n \times n$ matrix correspond to $n$ different eigenvalues, then the eigenvectors are linearly independent.*

An important class of matrices for inverse theory are the real symmetric matrices. The reason is that since we have to deal with rectangular matrices, we often end up treating the matrices $A^T A$ and $AA^T$ instead. And these two matrices are manifestly symmetric. In the case of real symmetric matrices, the eigenvector/eigenvalue decomposition is especially nice, since in this case the diagonalizing matrix $S$ can be chosen to be an orthogonal matrix $Q$.

**Theorem 6 Orthogonal decomposition of a real symmetric matrix** *A real symmetric matrix $A$ can be factored into*

$$A = Q\Lambda Q^T \quad (4.76)$$

*with orthonormal eigenvectors in $Q$ and real eigenvalues in $\Lambda$.*

0