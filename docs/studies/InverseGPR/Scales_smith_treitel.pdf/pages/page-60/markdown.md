4.4 Linear Dependence and Independence

45

## 4.4 Linear Dependence and Independence

Suppose we have $n$ vectors

$$\{\mathbf{x}_1, \mathbf{x}_2, \cdots, \mathbf{x}_n\} \tag{4.52}$$

of the same dimension. The question is, under what circumstances can the linear combination of these vectors be zero:

$$\alpha_1\mathbf{x}_1 + \alpha_2\mathbf{x}_2 + \cdots \alpha_n\mathbf{x}_n = 0. \tag{4.53}$$

If this is true with at least one of the coefficients $\alpha_i$ nonzero, then we could isolate a particular vector on the right hand side, expressing it as a linear combination of the other vectors. In this case the original set of $n$ vectors are said to be *linearly dependent*. On the other hand, if the only way for this sum of vectors to be zero is for all the coefficients themselves to be zero, then we say that the vectors are *linearly independent*.

Now, this linear combination of vectors can also be written as a matrix-vector inner product. With $\mathbf{a} = (\alpha_1, \alpha_2, \cdots, \alpha_n)$, and $X = (\mathbf{x}_1, \mathbf{x}_2, \cdots, \mathbf{x}_n)$ we have the condition for linear dependence being

$$X\mathbf{a} = 0 \tag{4.54}$$

for some nonzero vector $\mathbf{a}$, and the condition for linear independence being

$$X\mathbf{a} = 0 \Rightarrow \mathbf{a} = 0. \tag{4.55}$$

As a result, if we are faced with a linear system of equations to solve

$$A\mathbf{x} = \mathbf{b} \tag{4.56}$$

we can think in two different ways. On the one hand, we can investigate the equation in terms of the *existence* of a vector $\mathbf{x}$ satisfying the equation. On the other hand, we can think in terms of the *compatibility* of the right hand side with the columns of the matrix.

Linear independence is also central to the notion of how big a vector space is—its *dimension*. It's intuitively clear that no two linearly independent vectors are adequate to represent an arbitrary vector in $\mathbf{R}^3$. For example, $(1, 0, 0)$ and $(0, 1, 0)$ are linearly independent, but there are no scalar coefficients that will let us write $(1, 1, 1)$ as a linear combination of the first two. Conversely, since any vector in $\mathbf{R}^3$ can be written as a combination of the three vectors $(1, 0, 0)$, $(0, 1, 0)$, and $(0, 0, 1)$, it is impossible to have more than three linearly independent vectors in $\mathbf{R}^3$.

The dimension of a space is the number of linearly independent vectors required to represent an arbitrary element.

0