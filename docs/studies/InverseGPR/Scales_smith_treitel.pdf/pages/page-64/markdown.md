4.7 Eigenvalues and Eigenvectors

49

$A\mathbf{x} = \mathbf{y}$ it follows that $\mathbf{x} = C\mathbf{y}$. But $C$ is not necessarily unique. On the other hand, if there exists a left inverse $BA = I$, then $BA\mathbf{x} = B\mathbf{y}$, which implies that $\mathbf{x} = B\mathbf{y}$.

Some examples. Consider first the case of more equations than unknowns $n > m$. Let

$$A = \begin{bmatrix} -1 & 0 \\ 0 & 3 \\ 0 & 0 \end{bmatrix} \quad (4.62)$$

Since the columns are linearly independent and there are more rows than columns, there can be at most one solution. You can readily verify that any matrix of the form

$$\begin{bmatrix} -1 & 0 & \gamma \\ 0 & 1/3 & \iota \end{bmatrix} \quad (4.63)$$

is a left inverse. The particular left inverse given by the formula $(A^T A)^{-1} A^T$ (cf. the exercise at the end of this chapter) is the one for which $\gamma$ and $\iota$ are zero. But there are infinitely many other left inverses. As for solutions of $A\mathbf{x} = \mathbf{y}$, if we take the inner product of $A$ with the vector $(x_1, x_2)^T$ we get

$$\begin{bmatrix} -x_1 \\ 3x_2 \\ 0 \end{bmatrix} = \begin{bmatrix} y_1 \\ y_2 \\ y_3 \end{bmatrix} \quad (4.64)$$

So, clearly, we must have $x_1 = -y_1$ and $x_2 = 1/3y_2$. But, there will not be any solution unless $y_3 = 0$.

Next, let's consider the case of more columns (unknowns) than rows (equations) $n < m$. Let

$$A = \begin{bmatrix} -1 & 0 & 0 \\ 0 & 3 & 0 \end{bmatrix} \quad (4.65)$$

Here you can readily verify that any matrix of the form

$$\begin{bmatrix} -1 & 0 \\ 0 & 1/3 \\ \gamma & \iota \end{bmatrix} \quad (4.66)$$

is a right inverse. The particular right inverse (shown in the exercise at the end of this chapter) $A^T (AA^T)^{-1}$ corresponds to $\gamma = \iota = 0$.

Now if we look at solutions of the linear system $A\mathbf{x} = \mathbf{y}$ with $\mathbf{x} \in \mathbf{R}^3$ and $\mathbf{y} \in \mathbf{R}^2$ we find that $x_1 = -y_1$, $x_2 = 1/3y_2$, and that $x_3$ is completely undetermined. So there is an infinite set of solutions corresponding to the different values of $x_3$.

## 4.7 Eigenvalues and Eigenvectors

Usually when a matrix operates on a vector, it changes the direction of the vector. But for a special class of vectors, *eigenvectors*, the action of the matrix is to simply scale

0