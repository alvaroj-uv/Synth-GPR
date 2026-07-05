38

A Little Linear Algebra

This definition of matrix-matrix product even extends to the case in which both matrices are vectors. If $\mathbf{x} \in \mathbf{R}^m$ and $\mathbf{y} \in \mathbf{R}^n$, then $\mathbf{xy}$ (called the “outer” product and usually written as $\mathbf{xy}^T$) is

$$(xy)_{ij} = x_i y_j. \tag{4.29}$$

So if

$$\mathbf{x} = \left[ \begin{array}{c} -1 \\ 1 \end{array} \right] \tag{4.30}$$

and

$$\mathbf{y} = \left[ \begin{array}{c} 1 \\ 3 \\ 0 \end{array} \right] \tag{4.31}$$

then

$$\mathbf{xy}^T = \left[ \begin{array}{ccc} -1 & -3 & 0 \\ 1 & 3 & 0 \end{array} \right]. \tag{4.32}$$

### 4.1.2 Matrices With Special Structure

The identity element in the space of square $n \times n$ matrices is a matrix with ones on the main diagonal and zeros everywhere else

$$I_n = \left[ \begin{array}{cccc} 1 & 0 & 0 & 0 & \dots \\ 0 & 1 & 0 & 0 & \dots \\ 0 & 0 & 1 & 0 & \dots \\ \vdots & & & \ddots \\ 0 & \dots & 0 & 0 & 1 \end{array} \right]. \tag{4.33}$$

Even if the matrix is not square, there is still a *main diagonal* of elements given by $A_{ii}$ where $i$ runs from 1 to the smaller of the number of rows and columns. We can take any vector in $\mathbf{R}^n$ and make a diagonal matrix out of it just by putting it on the main diagonal and filling in the rest of the elements of the matrix with zeros. There is a special notation for this:

$$\text{diag}(x_1, x_2, \dots, x_n) = \left[ \begin{array}{ccccc} x_1 & 0 & 0 & 0 & \dots \\ 0 & x_2 & 0 & 0 & \dots \\ 0 & 0 & x_3 & 0 & \dots \\ \vdots & & & \ddots \\ 0 & \dots & 0 & 0 & x_n \end{array} \right]. \tag{4.34}$$

A matrix $Q \in \mathbf{R}^{n \times n}$ is said to be orthogonal if $Q^T Q = I_n$. In this case, each column of $Q$ is an orthornormal vector: $\mathbf{q}_i \cdot \mathbf{q}_i = 1$. So why are these matrices called orthogonal? No good reason. As an example

$$Q = \frac{1}{\sqrt{2}} \left[ \begin{array}{cc} 1 & -1 \\ 1 & 1 \end{array} \right]. \tag{4.35}$$

0