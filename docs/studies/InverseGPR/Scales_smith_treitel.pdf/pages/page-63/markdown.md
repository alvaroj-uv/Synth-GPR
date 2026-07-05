48

A Little Linear Algebra

## 4.6 Matrix Inverses

A *left inverse* of a matrix $A \in \mathbf{R}^{n \times m}$ is defined to be a matrix $B$ such that

$$BA = I. \tag{4.59}$$

A *right inverse* $C$ therefore must satisfy

$$AC = I. \tag{4.60}$$

If there exists a left and a right inverse of $A$ then they must be equal since matrix multiplication is associative:

$$AC = I \Rightarrow B(AC) = B \Rightarrow (BA)C = B \Rightarrow C = B. \tag{4.61}$$

Now if we have more equations than unknowns then the columns cannot possibly span all of $\mathbf{R}^n$. Certainly the rank $r$ must be less than or equal to $n$, but it can only equal $n$ if we have at least as many unknowns as equations. The basic existence result is then [Str88]:

$$\begin{bmatrix} & & \\ & \mathbf{R}^{n \times m} & \mathbf{R}^m & \mathbf{R}^n \end{bmatrix} = \begin{bmatrix} & & \\ & \mathbf{R}^n & \mathbf{R}^n \end{bmatrix}$$

**Theorem 2 Existence of solutions to $A\mathbf{x} = \mathbf{y}$** *The system $A\mathbf{x} = \mathbf{y}$ has at least one solution $\mathbf{x}$ for every $\mathbf{y}$ (there might be infinitely many solutions) if and only if the columns span $\mathbf{R}^n$ ($r = n$), in which case there exists an $m \times n$ right inverse $C$ such that $AC = I_n$. This is only possible if $n \leq m$.*

Don't be mislead by the picture above into neglecting the important special case when $m = n$. The point is that the basic issues of existence and, next, uniqueness, depend on whether there are more or fewer rows than equations. The statement of uniqueness is [Str88]:

$$\begin{bmatrix} & & \\ & \mathbf{R}^{n \times m} & \mathbf{R}^m & \mathbf{R}^n \end{bmatrix} = \begin{bmatrix} & & \\ & \mathbf{R}^n & \mathbf{R}^n \end{bmatrix}$$

**Theorem 3 Uniqueness of solutions to $A\mathbf{x} = \mathbf{y}$** *There is at most one solution to $A\mathbf{x} = \mathbf{y}$ (there might be none) if and only if the columns of $A$ are linearly independent ($r = m$), in which case there exists an $m \times n$ left inverse $B$ such that $BA = I_m$. This is only possible if $n \geq m$.*

Clearly then, in order to have both existence and uniqueness, we must have that $r = m = n$. This precludes having existence and uniqueness for rectangular matrices. For square matrices $m = n$, so **existence implies uniqueness and uniqueness implies existence**.

Using the left and right inverses we can find solutions to $A\mathbf{x} = \mathbf{y}$: if they exist. For example, given a right inverse $A$, then since $AC = I$, we have $AC\mathbf{y} = \mathbf{y}$. But since

0