186

More on the Resolution-Variance Tradeoff

where $U$ is an orthogonal matrix of “data” eigenvectors (i.e., they span $R^n$) and $V$ is an orthogonal matrix of “model” eigenvectors (they span $R^m$). $\Lambda$ is the $n \times m$ diagonal matrix of singular values $\lambda_i$. The pseudo-inverse of $A$ is

$$A^\dagger = V \Lambda^{-1} U^T$$

where $\Lambda^{-1}$ where denotes the $m \times n$ diagonal matrix obtained by inverting the nonzero singular values. To keep things simple, let’s assume that the covariance of the data errors is just the identity matrix. This will let us look at the structure of the covariance of $\hat{\mathbf{m}}$ as a function of the forward operator alone. It is easy to see that in this case

$$\mathrm{Cov}(\hat{\mathbf{m}}) = E[\hat{\mathbf{m}}\hat{\mathbf{m}}^T] = A^\dagger \mathrm{Cov}(\mathbf{d}) A^\dagger^T = V \Lambda^{-2} V^T = \sum_{i=1}^m \lambda_i^{-2} \mathbf{v}_i \mathbf{v}_i^T.$$

The last term on the right is the sum of the outer products of the columns of $V$ (these are the model space eigenvectors). So the covariance can be seen as a weighted projection operator onto the row space of $A$, with weights given by the inverse-square of the singular values.

With this it is not difficult to see that the $j$-th diagonal element of $\mathrm{Cov}(\hat{\mathbf{m}})$, which is the variance of the $j$-th model parameter is

$$\mathrm{Var}(\hat{\mathbf{m}}_j) = \sum_{i=1}^m \lambda_i^{-2} (\mathbf{v}_i)_j^2$$

where $(\mathbf{v}_i)_j$ is the $j$-th component of the $i$-th eigenvector.

If the rank of $A$ is less than $m$, say $r$, then all of the sums involving the pseudo-inverse are really only over the $r$ eigenvectors/eigenvalues. In particular

$$\mathrm{Var}(\hat{\mathbf{m}}_j) = \sum_{i=1}^r \lambda_i^{-2} (\mathbf{v}_i)_j^2.$$

This is because $A = U \Lambda V^T = U_r \Lambda_r V_r^T$ where the subscript $r$ means that we have eliminated the terms associated with zero singular values.

Now suppose we decide not to use all the $r$ model eigenvectors spanning the row space of $A$? For example we might need only $p$ eigenvectors to actually fit the data. Let us denote by $\hat{\mathbf{m}}^p$ the resulting estimate of $\hat{\mathbf{m}}$ (which is obviously confined to the $p$-dimensional subspace of $R^m$ spanned by the first $p$ model singular vectors):

$$\hat{\mathbf{m}}^p \equiv \sum_{i=1}^p \mathbf{v}_i \frac{\mathbf{u}_i^T \mathbf{d}}{\lambda_i}$$

where $\mathbf{u}_i$ is the $i$-th column of $U$ (i.e., the $i$-th data eigenvector). Using the result above for the variance of the $j$-th component of $\hat{\mathbf{m}}$ we can see that

$$\mathrm{Var}(\hat{\mathbf{m}}_j^p) = \sum_{i=1}^p \lambda_i^{-2} (\mathbf{v}_i)_j^2.$$

Remember that if a vector is in the null space of a matrix, then it is orthogonal to all the rows of the matrix. Hence the row space and the null space are orthogonal complements of one another.

1