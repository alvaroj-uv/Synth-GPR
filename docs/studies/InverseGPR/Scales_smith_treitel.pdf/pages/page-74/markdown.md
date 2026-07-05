# Chapter 5

## SVD and Resolution in Least Squares

In section 4.8 we introduced the singular value decomposition (SVD). The SVD is a natural generalization of the eigenvector decomposition to arbitrary (even rectangular) matrices. It plays a fundamental role in linear inverse problems.

### 5.0.1 A Worked Example

Let's begin by doing a worked example. Suppose that

$$A = \begin{bmatrix} 1 & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

and hence that

$$A^T = \begin{bmatrix} 1 & 0 \\ 1 & 0 \\ 0 & 1 \end{bmatrix}, \quad A^T A = \begin{bmatrix} 1 & 1 & 0 \\ 1 & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix}, \quad AA^T = \begin{bmatrix} 2 & 0 \\ 0 & 1 \end{bmatrix}$$

The eigenvalue problem for $AA^T$ is easy; since it is diagonal, its diagonal entries are the eigenvalues. To find the eigenvalues of $A^T A$ we need to find the roots of the characteristic polynomial

$$\text{Det} \begin{vmatrix} 1-\lambda & 1 & 0 \\ 1 & 1-\lambda & 0 \\ 0 & 0 & 1-\lambda \end{vmatrix} = (1-\lambda) \left[ (1-\lambda)^2 - 1 \right] = 0$$

which are 2, 1 and 0.

Now we can compute the data eigenvectors $\mathbf{u_i}$ by solving the eigenvalue problem

1