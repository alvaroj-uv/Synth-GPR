166

Iterative Linear Solvers

Cholesky decomposition of the matrix and simply throwing away any nonzero elements which appear where the original matrix had a zero. In other words, one could enforce the sparsity pattern of $A$ on its approximate factorization. For details on these “incomplete factorization” methods see [Man80], [Ker78], and [GvL83], for example.

### 11.2.8 *CG* Methods for Least-Squares

Conjugate gradient can be extended to the least squares solution of arbitrary linear systems. Solutions of the normal equations

$$A^T A \mathbf{x} = A^T \mathbf{h} \tag{11.52}$$

are critical points of the function

$$\| A \mathbf{x} - \mathbf{h} \|^2 \equiv ((A \mathbf{x} - \mathbf{h}), (A \mathbf{x} - \mathbf{h})). \tag{11.53}$$

Note that $A^T A$ is always symmetric and nonnegative. The basic facts for least-squares solutions are these: if the system $A \mathbf{x} = \mathbf{h}$ is overdetermined, i.e., if there are more rows than columns, and if the columns are linearly independent, then there is a unique least-squares solution. On the other hand, if the system is underdetermined or if some of the columns are linearly dependent then the least-squares solutions are not unique. (For a complete discussion see the book by Campbell and Meyer [CM79].) In the latter case, the solution to which $CG$ converges will depend on the initial approximation. Hestenes [Hes75] shows that if $\mathbf{x}_0 = 0$, the usual case, then $CG$ converges to the least-squares solution of smallest Euclidean norm.

In applying $CG$ to the normal equations avoid explicitly forming the products $A^T A$. This is because the matrix $A^T A$ is usually dense even when $A$ is sparse. But $CG$ does not actually require the matrix, only the action of the matrix on arbitrary vectors. So one could imagine doing the matrix-vector vector multiplies $A^T A \mathbf{x}$ by first doing $A \mathbf{x}$ and then dotting $A^T$ into the resulting vector. Unfortunately, since the condition number of $A^T A$ is the square of the condition number of $A$, this results in slowly convergent iteration if $\kappa(A)$ is reasonably large. The solution to this problem is contained, once again, in Hestenes' and Stiefel's original paper [HS52]. The idea is to apply $CG$ to the normal equations, but to factor terms of the form $A^T \mathbf{h} - A^T A \mathbf{x}$ into $A^T (\mathbf{h} - A \mathbf{x})$, doing the subtraction before the final matrix multiplication. The result is

**Algorithm 7 Conjugate Gradient Least Squares (*CGLS*)** *Choose* $\mathbf{x}_0$. *Put* $\mathbf{s}_0 =$

1