BIBLIOGRAPHY

57

9. As we have seen, an orthogonal matrix corresponds to a rotation. Consider the eigenvalue problem for a simple orthogonal matrix such as

$$Q = \left[ \begin{array}{cc} 0 & -1 \\ 1 & 0 \end{array} \right] \tag{4.100}$$

How can a rotation map a vector into a multiple of itself?

10. Show that the eigenvalues of $A^j$ are the j-th powers of the eigenvalues of $A$.
11. Using the SVD show that

$$AA^T = U\Lambda\Lambda^T U \tag{4.101}$$

and

$$A^T A = V\Lambda^T \Lambda V. \tag{4.102}$$

The diagonal matrices $\Lambda\Lambda^T \in \mathbf{R}^{m \times m}$ and $\Lambda^T \Lambda \in \mathbf{R}^{n \times n}$ have different dimensions, but they have the same $r$ nonzero elements: $\sigma_1, \sigma_2, \cdots, \sigma_r$.

12. Compute the SVD of the matrix

$$A = \left[ \begin{array}{ccc} 1 & 1 & 0 \\ 0 & 0 & 1 \\ 0 & 0 & -1 \end{array} \right] \tag{4.103}$$

directly by computing the eigenvectors of $A^T A$ and $AA^T$. Show that the pseudoinverse solution to the linear system $Ax = y$ where $y = (1, 2, 1)^T$ is given by averaging the equations.

13. Prove that $(A\mathbf{x}, \mathbf{y}) = (\mathbf{x}, A^T\mathbf{y})$.
14. Prove that if $Q$ is an orthogonal matrix, that $Q\mathbf{x}$ is a rotation of $\mathbf{x}$.
15. What happens to the $\ell_p$ norm if $p < 1$? For example, is

$$\left( \sum_{i=1}^n |x_i|^{1/2} \right)^2 \tag{4.104}$$

a norm?

## Bibliography

[GvL83] G. Golub and C. van Loan. *Matrix Computations*. Johns Hopkins, Baltimore, 1983.

[Lan61] C. Lanczos. *Linear Differential Operators*. D. van Nostrand, 1961.

[MF53] P.M. Morse and H. Feshbach. *Methods of Theoretical Physics*. McGraw Hill, 1953.

0