50

A Little Linear Algebra

the vector:

$$A\mathbf{x} = \lambda\mathbf{x}. \tag{4.67}$$

If this is true, then $\mathbf{x}$ is an eigenvector of the matrix $A$ associated with the eigenvalue $\lambda$. Now, $\lambda\mathbf{x}$ equals $\lambda I\mathbf{x}$ so we can rearrange this equation and write

$$(A - \lambda I)\mathbf{x} = 0. \tag{4.68}$$

Clearly in order that $\mathbf{x}$ be an eigenvector we must choose $\lambda$ so that $(A - \lambda I)$ has a nullspace and we must choose $\mathbf{x}$ so that it lies in that nullspace. That means we must choose $\lambda$ so that $\operatorname{Det}(A - \lambda I) = 0$. This determinant is a polynomial in $\lambda$, called the characteristic polynomial. For example if

$$A = \left[ \begin{array}{cc} 5 & 3 \\ 4 & 5 \end{array} \right] \tag{4.69}$$

then the characteristic polynomial is

$$\lambda^2 - 10\lambda + 13 \tag{4.70}$$

whose roots are

$$\lambda = 5 + 2\sqrt{3}, \text{ and } \lambda = 5 - 2\sqrt{3}. \tag{4.71}$$

Now all we have to do is solve the two homogeneous systems:

$$\left[ \begin{array}{cc} 2\sqrt{3} & 3 \\ 4 & 2\sqrt{3} \end{array} \right] \left[ \begin{array}{c} x_1 \\ x_2 \end{array} \right] = 0 \tag{4.72}$$

and

$$\left[ \begin{array}{cc} -2\sqrt{3} & 3 \\ 4 & -2\sqrt{3} \end{array} \right] \left[ \begin{array}{c} x_1 \\ x_2 \end{array} \right] = 0 \tag{4.73}$$

from which we arrive at the two eigenvectors

$$\left[ \begin{array}{c} \frac{\sqrt{3}}{2} \\ 1 \end{array} \right], \left[ \begin{array}{c} -\frac{\sqrt{3}}{2} \\ 1 \end{array} \right] \tag{4.74}$$

But note well, that these eigenvectors are not unique. Because they solve a homogeneous system, we can multiply them by any scalar we like and not change the fact that they are eigenvectors.

This exercise was straightforward. But imagine what would have happened if we had needed to compute the eigenvectors/eigenvalues of a $10 \times 10$ matrix. Can you imagine having to compute the roots of a 10-th order polynomial? In fact, once you get past order 4, there is no algebraic formula for the roots of a polynomial. The eigenvalue problem is much harder than solving $A\mathbf{x} = \mathbf{y}$.

The following theorem gives us the essential computational tool for using eigenvectors.

0