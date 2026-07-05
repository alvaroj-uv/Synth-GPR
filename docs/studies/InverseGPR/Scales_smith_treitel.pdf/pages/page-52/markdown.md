4.1 Linear Vector Spaces

37

and $\alpha = 4$ then

$$\alpha A = \left[ \begin{array}{rrr} 4 & 8 & 12 \\ -12 & -8 & -4 \end{array} \right]. \tag{4.21}$$

So both matrices and vectors can be thought of as vectors in the abstract sense. Matrices can also be thought of as operators acting on vectors in $\mathbf{R}^n$ via the matrix-vector inner (or "dot") product. If $A \in \mathbf{R}^{n \times m}$ and $\mathbf{x} \in \mathbf{R}^m$, then $A \cdot \mathbf{x} = \mathbf{y} \in \mathbf{R}^n$ is defined by

$$y_i = \sum_{j=1}^m A_{ij} x_j. \tag{4.22}$$

This is an algebraic definition of the inner product. We can also think of it geometrically. Namely, the inner product is a linear combination of the columns of the matrix. For example,

$$A \cdot \mathbf{x} = \left[ \begin{array}{ll} a_{11} & a_{12} \\ a_{21} & a_{22} \\ a_{31} & a_{32} \end{array} \right] \cdot \left[ \begin{array}{l} x_1 \\ x_2 \end{array} \right] = x_1 \left[ \begin{array}{l} a_{11} \\ a_{21} \\ a_{31} \end{array} \right] + x_2 \left[ \begin{array}{l} a_{12} \\ a_{22} \\ a_{32} \end{array} \right]. \tag{4.23}$$

A special case of this occurs when $A$ is just an ordinary vector. We can think of this as $A \in \mathbf{R}^{n \times m}$ with $n = 1$. Then $\mathbf{y} \in \mathbf{R}^1$ is just a scalar. A vector $\mathbf{z}$ in $\mathbf{R}^{1 \times m}$ looks like

$$(z_1, z_2, z_3, \cdots, z_m) \tag{4.24}$$

so the inner product of two vectors $\mathbf{z}$ and $\mathbf{x}$ is just

$$[z_1, z_2, z_3, \cdots, z_n] \cdot \left[ \begin{array}{c} x_1 \\ x_2 \\ x_3 \\ \vdots \\ x_n \end{array} \right] = [z_1 x_1 + z_2 x_2 + z_3 x_3 + \cdots + z_n x_n]. \tag{4.25}$$

By default, a vector $\mathbf{x}$ is regarded as a column vector. So this vector-vector inner product is also written as $\mathbf{z}^T \mathbf{x}$ or as $(\mathbf{z}, \mathbf{x})$. Similarly if $A \in \mathbf{R}^{n \times m}$ and $B \in \mathbf{R}^{m \times p}$, then the matrix-matrix $AB$ product is defined to be a matrix in $\mathbf{R}^{n \times p}$ with components

$$(AB)_{ij} = \sum_{k=1}^m a_{ik} b_{kj}. \tag{4.26}$$

For example,

$$AB = \left[ \begin{array}{ll} 1 & 2 \\ 3 & 4 \end{array} \right] \left[ \begin{array}{ll} 0 & 1 \\ 2 & 3 \end{array} \right] = \left[ \begin{array}{ll} 4 & 7 \\ 8 & 15 \end{array} \right]. \tag{4.27}$$

On the other hand, note well that

$$BA = \left[ \begin{array}{ll} 0 & 1 \\ 2 & 3 \end{array} \right] \left[ \begin{array}{ll} 1 & 2 \\ 3 & 4 \end{array} \right] = \left[ \begin{array}{ll} 3 & 4 \\ 11 & 16 \end{array} \right] \neq AB. \tag{4.28}$$

0