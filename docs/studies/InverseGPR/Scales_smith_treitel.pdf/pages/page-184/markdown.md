11.3 Practical Implementation

169

full index scheme, algorithms for matrix vector inner products are very simple. First, $\mathbf{y} = A\mathbf{x}$:

$$\forall k \quad y(irow(k)) = y(irow(k)) + elem(k) * \mathbf{x}(icol(k)). \tag{11.56}$$

And for $\mathbf{y} = A^T\mathbf{x}$:

$$\forall k \quad y(icol(k)) = y(icol(k)) + elem(k) * \mathbf{x}(irow(k)). \tag{11.57}$$

It is left as an exercise to construct similar operation within the row-pointer scheme. The matrix-vector inner product in the row-pointer scheme amounts to taking the inner product of each sparse row of the matrix with the vector and adding them up. If the rows are long enough, this way of doing things amounts to a substantial savings on a vectorizing computer since each row-vector inner product vectorizes with gather-scatter operations. At the same time, the long vector length would imply a substantial memory economy in this scheme. On the other hand, if the calculation is done on a scalar computer, and if memory limitations are not an issue, the full-index scheme is very efficient in execution since partial sums of the individual row-vector inner products are accumulated simultaneously. For the same reason, a loop involving the result vector will be recursive and hence not easily vectorized.

### 11.3.2 Data and Parameter Weighting

For inverse problems one is usually interested in weighted calculations: weights on data both to penalize(reward) bad(good) data and to effect a dimensionless stopping criterion such as $\chi^2$, and weights on parameters to take into account prior information on model space. If the weights are diagonal, they can be incorporated into the matrix-vector multiply routines via:

$$\forall k \quad y(icol(k)) = y(icol(k)) + elem(k) * \mathbf{x}(irow(k)) * W1(irow(k)) \tag{11.58}$$

for row or data weighting and

$$\forall k \quad y(irow(k)) = y(irow(k)) + elem(k) * \mathbf{x}(icol(k)) * W2(icol(k)) \tag{11.59}$$

for column or parameter weighting. Here, $W1$ and $W2$ are assumed to contain the diagonal elements of the weighting matrices.

### 11.3.3 Regularization

Just as most real inverse calculations involve weights, most real inverse calculations must be regularized somehow. This is because in practice linear least squares calculations usually involve singular matrices or matrices that are numerically singular (have very small eigenvalues). Regularization is the process by which these singularities are

1