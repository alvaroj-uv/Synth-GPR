4.1 Linear Vector Spaces

35

In the case of $n = 1$ the vector space $V$ and the scalars $F$ are the same. So trivially, $F$ is a vector space over $F$.

A few observations: first, by adding $-x$ to both sides of $x + y = x$, you can show that $x + y = x$ if and only if $y = 0$. This implies the uniqueness of the zero element and also that $\alpha \cdot 0 = 0$ for all scalars $\alpha$.

Functions themselves can be vectors. Consider the space of functions mapping some nonempty set onto the scalars, with addition and multiplication defined by:

$$f + g = f(t) + g(t) \tag{4.5}$$

and

$$\alpha f = \alpha f(t). \tag{4.6}$$

We use the square brackets to separate the function from its arguments. In this case, the zero element is the function whose value is zero everywhere. And the minus element is inherited from the scalars: $-f = -f(t)$.

### 4.1.1 Matrices

The set of all $n \times m$ matrices with scalar entries is a linear vector space with addition and scalar multiplication defined component-wise. We denote this space by $\mathbf{R}^{n \times m}$. Two matrices have the same dimensions if they have the same number of rows and columns. We use upper case roman letters to denote matrices, lower case roman$^a$ to denote ordinary vectors and greek letters to denote scalars. For example, let

$$A = \left[ \begin{array}{cc} 2 & 5 \\ 3 & 8 \\ 1 & 0 \end{array} \right]. \tag{4.7}$$

Then the components of $A$ are denoted by $A_{ij}$. The *transpose* of a matrix, denoted by $A^T$, is achieved by exchanging the columns and rows. In this example

$$A^T = \left[ \begin{array}{ccc} 2 & 3 & 1 \\ 5 & 8 & 0 \end{array} \right]. \tag{4.8}$$

Thus $A_{21} = 3 = A_{12}^T$.

You can prove for yourself that

$$(AB)^T = B^T A^T. \tag{4.9}$$

$^a$For emphasis, and to avoid any possible confusion, we will henceforth also use bold type for ordinary vectors.

0