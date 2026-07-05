170

Iterative Linear Solvers

tamed. We saw two different examples of regularization in Chapter 5. The first was truncating the SVD. We can throw away zero or small singular values and that regularizes the problem. But we also found that in the presence of a model null space it was useful to be able to penalize the size of the solution as well as the data misfit.

In other words we replaced the minimization problem

$$\min \| A\mathbf{x} - \mathbf{h} \|^2 \quad (11.60)$$

with

$$\min \| A\mathbf{x} - \mathbf{h} \|^2 + \| \mathbf{x} \|^2. \quad (11.61)$$

The first term is the data misfit, and the second is the “regularization” term. As shown here, the two aspects of the minimization (make the data misfit small, make the model norm small) get equal weight.

Now let us go two steps beyond this. First, let us introduce a fudge factor $\lambda$ to control the tradeoff between the two terms. Next, let us consider the possibility of minimizing not the norm of the model itself, but the norm of some linear function of the model $R\mathbf{h}$.

$$\min \| A\mathbf{x} - \mathbf{h} \|^2 + \lambda \| R\mathbf{x} \|^2 \quad (11.62)$$

If $R = I$, then we’re back to our familiar regularization. But now suppose that $R \equiv \partial^n, n = 0, 1, 2, \dots$ and $\partial^n$ is an $n-th$ order discrete difference operator. In this case the term $\| R\mathbf{x} \|^2$ penalizes the slope, roughness, or higher order derivative of the model. Penalizing roughness would be useful if we want a smooth solution.

The “normal equations” associated with this generalized objective function, obtained by setting the derivative of (11.62) equal to zero, are

$$(A^T A + \lambda R^T R)\mathbf{x} = A^T \mathbf{h}. \quad (11.63)$$

This sort of regularization is straightforward to implement in a sparse matrix framework by augmenting the matrix with the regularization term:

$$\tilde{A} \equiv \begin{pmatrix} A \\ \sqrt{\lambda}R \end{pmatrix}.$$

From this you can tell right away that $R$ must have the same number of columns as $A$. But in principle it can have any number of rows. For example, we might use

$$R = \begin{bmatrix} 1 & -1 & 0 & \cdots \\ 0 & 1 & -1 & \cdots \\ & & \vdots & \\ 0 & \cdots & 1 & -1 \\ 0 & 0 & \cdots & 1 \end{bmatrix}$$

1