56

A Little Linear Algebra

That will do. But so will

$$\frac{1}{\sqrt{2}} \left[ \begin{array}{cc} -1 & 1 \\ 1 & 1 \end{array} \right]. \tag{4.94}$$

So, as you can see, repeated eigenvalues give us choice. And for symmetric matrices we nearly always choose to diagonalize with orthogonal matrices.

### Exercises

1. Give specific (nonzero) examples of 2 by 2 matrices satisfying the following properties:

$$A^2 = 0, A^2 = -I_2, \text{ and } AB = -BA \tag{4.95}$$

2. Let $A$ be an upper triangular matrix. Suppose that all the diagonal elements are nonzero. Show that the columns must be linearly independent and that the null-space contains only the zero vector.

3. Figure out the column space and null space of the following two matrices:

$$\left[ \begin{array}{cc} 1 & -1 \\ 0 & 0 \end{array} \right] \text{ and } \left[ \begin{array}{ccc} 0 & 0 & 0 \\ 0 & 0 & 0 \end{array} \right] \tag{4.96}$$

4. Which of the following two are subspaces of $\mathbf{R}^n$: the plane of all vectors whose first component is zero; the plane of all vectors whose first component is 1.

5. Let

$$\mathbf{x} = \left[ \begin{array}{c} 9 \\ -12 \end{array} \right]. \tag{4.97}$$

Compute $\|x\|_1$, $\|x\|_2$, and $\|x\|_\infty$.

6. Define the unit $\ell_p$-ball in the plane $\mathbf{R}^2$ as the set of points satisfying

$$\|x\|_{\ell_p} \le 1. \tag{4.98}$$

Draw a picture of this ball for $p = 1, 2, 3$ and $\infty$.

7. Show that $B = (A^T A)^{-1} A^T$ is a left inverse and $C = A^T (AA^T)^{-1}$ is a right inverse of a matrix $A$, provided that $AA^T$ and $A^T A$ are invertible. It turns out that $A^T A$ is invertible if the rank of $A$ is equal to $n$, the number of columns; and $AA^T$ is invertible if the rank is equal to $m$, the number of rows.

8. Consider the matrix

$$\left[ \begin{array}{cc} a & b \\ c & d \end{array} \right] \tag{4.99}$$

The trace of this matrix is $a + d$ and the determinant is $ad - cb$. Show by direct calculation that the product of the eigenvalues is equal to the determinant and the sum of the eigenvalues is equal to the trace.

0