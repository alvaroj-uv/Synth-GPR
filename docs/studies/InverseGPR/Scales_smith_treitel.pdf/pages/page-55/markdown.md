40

A Little Linear Algebra

For $p = 2$ this is just the ordinary euclidean norm: $\|\mathbf{x}\|_2 = \sqrt{\mathbf{x}^T\mathbf{x}}$. A finite limit of the $\ell_p$ norm exists as $p \to \infty$ called the $\ell_\infty$ norm:

$$\|x\|_{\ell_\infty} = \max_{1 \le i \le n} |x_i| \tag{4.39}$$

Any norm on vectors in $\mathbf{R}^n$ induces a norm on matrices via

$$\|A\| = \max_{\mathbf{x} \neq 0} \frac{\|A\mathbf{x}\|}{\|\mathbf{x}\|}. \tag{4.40}$$

A matrix norm that is not induced by any vector norm is the Frobenius norm defined for all $A \in \mathbf{R}^{n \times m}$ as

$$\|A\|_F = \left( \sum_{i=1}^m \sum_{j=1}^n A_{ij}^2 \right)^{1/2}. \tag{4.41}$$

Some examples (see [GvL83]): $\|A\|_1 = \max_j \|\mathbf{a}_j\|_1$ where $\mathbf{a}_j$ is the j-th column of $A$. Similarly $\|A\|_\infty$ is the maximum 1-norm of the rows of $A$. For the euclidean norm we have $(\|A\|_2)^2 =$ maximum eigenvalue of $A^T A$. The first two of these examples are reasonably obvious. The third is far from so, but is the reason the $\ell_2$ norm of a matrix is called the *spectral* norm. We will prove this latter result shortly after we've reviewed the properties of eigenvalues and eigenvectors.

### Minor digression: breakdown of the $\ell_p$ norm

Since we have alluded in the previous footnote to some difficulty with the $\ell_p$ norm for $p < 1$ it might be worth a brief digression on this point in order to emphasize that this difficulty is not merely of academic interest. Rather, it has important consequences for the algorithms that we will develop in the chapter on "robust estimation" methods. For the rectangular (and invariably singular) linear systems we will need to solve in inverse calculations, it is useful to pose the problem as one of optimization; to wit,

$$\min_x \|Ax - y\|. \tag{4.42}$$

It can be shown that for the $\ell_p$ family of norms, if this optimization problem has a solution, then it is unique: provided the matrix has full column rank and $p > 1$. (By full column rank we mean that all the columns are linearly independent.) For $p = 1$ the norm loses, in the technical jargon, strict convexity. A proof of this result can be found in [SG88]. It is easy to illustrate. Suppose we consider the one parameter linear system:

$$\begin{bmatrix} 1 \\ \lambda \end{bmatrix} x = \begin{bmatrix} 1 \\ 0 \end{bmatrix}. \tag{4.43}$$

0