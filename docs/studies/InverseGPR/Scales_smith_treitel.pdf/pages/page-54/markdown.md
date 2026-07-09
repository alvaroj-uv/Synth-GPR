4.2 Matrix and Vector Norms

39

Now convince yourself that $Q^T Q = I_n$ implies that $QQ^T = I_n$ as well. In this case the rows of $Q$ must be orthonormal vectors too.

Another interpretation of the matrix-vector inner product is as a mapping from one vector space to another. Suppose $A \in \mathbf{R}^{n \times m}$, then $A$ maps vectors in $\mathbf{R}^m$ into vectors in $\mathbf{R}^n$. An orthogonal matrix has an especially nice geometrical interpretation. To see this first notice that for any matrix $A$, the inner product $(A \cdot \mathbf{x}) \cdot \mathbf{y}$, which we write as $(A\mathbf{x}, \mathbf{y})$, is equal to $(\mathbf{x}, A^T\mathbf{y})$, as you will verify in one of the exercises at the end of the chapter. Similarly

$$(A^T\mathbf{x}, \mathbf{y}) = (\mathbf{x}, A\mathbf{y}). \tag{4.36}$$

As a result, for an orthogonal matrix $Q$

$$(Q\mathbf{x}, Q\mathbf{x}) = (Q^T Q \mathbf{x}, \mathbf{x}) = (\mathbf{x}, \mathbf{x}). \tag{4.37}$$

Now, as you already know, and we will discuss shortly, the inner product of a vector with itself is related to the length, or norm, of that vector. Therefore an orthogonal matrix maps a vector into another vector of the same norm. In other words it does a rotation.

## 4.2 Matrix and Vector Norms

We need some way of comparing the relative “size” of vectors and matrices. For scalars, the obvious answer is the absolute value. The absolute value of a scalar has the property that it is never negative and it is zero if and only if the scalar itself is zero. For vectors and matrices both we can define a generalization of this concept of length called a norm. A norm is a function from the space of vectors onto the scalars, denoted by $\|\cdot\|$ satisfying the following properties for any two vectors $v$ and $u$ and any scalar $\alpha$:

# Definition 3 Norms

N1: $\|v\| > 0$ for any $v \neq 0$ and $\|v\| = 0 \Leftrightarrow v = 0$

N2: $\|\alpha v\| = |\alpha|\|v\|$

N3: $\|v + u\| \leq \|v\| + \|u\|$

Here we use the symbol $\Leftrightarrow$ to mean if and only if. Property N3 is called the triangle inequality.

The most useful class of norms for vectors in $\mathbf{R}^n$ is the $\ell_p$ norm defined for $p \geq 1$ by

$$\|\mathbf{x}\|_{\ell_p} = \left( \sum_{i=1}^n |x_i|^p \right)^{1/p}. \tag{4.38}$$

0