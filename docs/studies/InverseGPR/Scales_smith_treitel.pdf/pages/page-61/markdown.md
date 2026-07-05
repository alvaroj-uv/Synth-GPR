46

A Little Linear Algebra

## 4.5 The Four Fundamental Spaces

Suppose you have an $n$-dimensional space and $n$ linearly independent vectors in that space. These vectors are said to be *basis vectors* since any element of the space can be written as a linear combination of the basis vectors. For instance, two basis vectors for $\mathbf{R}^2$ are $(1, 0)$ and $(0, 1)$. Any element of $\mathbf{R}^2$ can be written as some constant times $(1, 0)$ plus another constant times $(0, 1)$. Any other pair of linearly independent vectors would also work, such as $(2, 0)$ and $(1, 15)$.

OK, so take two basis vectors for $\mathbf{R}^2$ and consider all possible linear combinations of them. This the set of *all* vectors

$$\alpha(1, 0) + \beta(0, 1),$$

where $\alpha$ and $\beta$ are arbitrary scalars. This is called the *span* of the two vectors and in this case it obviously consists of all of $\mathbf{R}^2$. The span of $(1, 0)$ is just the x-axis in $\mathbf{R}^2$.

On the other hand, if we consider these two vectors as being in $\mathbf{R}^3$, so that we write them as $(1, 0, 0)$ and $(0, 1, 0)$, then their span clearly doesn't fill up all of $\mathbf{R}^3$. It does, however, fill up a subspace of $\mathbf{R}^3$, the $x-y$ plane. The technical definition of a subspace is that it is a subset *closed* under addition and scalar multiplication:

**Definition 4** *Subspaces: A subspace of a vector space is a nonempty subset $S$ that satisfies*

*S1: The sum of any two elements from $S$ is in $S$, and*

*S2: The scalar multiple of any element from $S$ is in $S$.*

If we take a general matrix $A \in \mathbf{R}^{n \times m}$, then the span of the columns must be a subspace of $\mathbf{R}^n$. Whether this subspace amounts to the whole of $\mathbf{R}^n$ obviously depends on whether the columns are linearly independent or not. This subspace is called the *column space* of the matrix and is usually denoted by $R(A)$, for 'range'. The dimension of the column space is called the *rank* of the matrix.

Another fundamental subspace associated with any matrix $A$ is associated with the solutions of the homogeneous equation $A\mathbf{x} = 0$. Why is this a subspace? Take any two such solutions, say $\mathbf{x}$ and $\mathbf{y}$ and we have

$$A(\mathbf{x} + \mathbf{y}) = A\mathbf{x} + A\mathbf{y} = 0. \tag{4.57}$$

Hence Similarly,

$$A(\alpha\mathbf{x}) = \alpha A\mathbf{x}. \tag{4.58}$$

This subspace is called the *nullspace* or *kernel* and is extremely important from the point of view of inverse theory. As we shall see, in an inverse calculation the right

0