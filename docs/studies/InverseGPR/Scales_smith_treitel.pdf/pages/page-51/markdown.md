36

A Little Linear Algebra

A matrix which equals its transpose ($A^T = A$) is said to be symmetric. If $A^T = -A$ the matrix is said to be skew-symmetric. We can split any square matrix $A$ into a sum of a symmetric and a skew-symmetric part via

$$ A = \frac{1}{2}(A + A^T) + \frac{1}{2}(A - A^T). \tag{4.10} $$

The Hermitian transpose of a matrix is the complex conjugate of its transpose. Thus if

$$ A = \left[ \begin{array}{ccc} 4 - i & 8 & 12 + i \\ -12 & -8 & -4 - i \end{array} \right] \tag{4.11} $$

then

$$ \bar{A}^T \equiv A^H = \left[ \begin{array}{cc} 4 + i & -12 \\ 8 & -8 \\ 12 - i & -4 + i \end{array} \right]. \tag{4.12} $$

Sometimes it is useful to have a special notation for the columns of a matrix. So if

$$ A = \left[ \begin{array}{cc} 2 & 5 \\ 3 & 8 \\ 1 & 0 \end{array} \right] \tag{4.13} $$

then we write

$$ A = \left[ \begin{array}{cc} \mathbf{a}_1 & \mathbf{a}_2 \end{array} \right] \tag{4.14} $$

where

$$ \mathbf{a}_1 = \left[ \begin{array}{c} 2 \\ 3 \\ 1 \end{array} \right]. \tag{4.15} $$

Addition of two matrices $A$ and $B$ only makes sense if they have the same number of rows and columns, in which case we can add them component-wise

$$ (A + B)_{ij} = [A_{ij} + B_{ij}]. \tag{4.16} $$

For example if

$$ A = \left[ \begin{array}{ccc} 1 & 2 & 3 \\ -3 & -2 & -1 \end{array} \right] \tag{4.17} $$

and

$$ B = \left[ \begin{array}{ccc} 0 & 6 & 2 \\ 1 & 1 & 1 \end{array} \right] \tag{4.18} $$

Then

$$ A + B = \left[ \begin{array}{ccc} 1 & 8 & 5 \\ -2 & -1 & 0 \end{array} \right]. \tag{4.19} $$

Scalar multiplication, once again, is done component-wise. If

$$ A = \left[ \begin{array}{ccc} 1 & 2 & 3 \\ -3 & -2 & -1 \end{array} \right] \tag{4.20} $$

0