11.3 Practical Implementation

171

which is square and nonsingular, or we might use

$$R = \left[ \begin{array}{c c c c} 1 & -1 & 0 & \cdots \\ 0 & 1 & -1 & \cdots \\ & & \vdots & \\ 0 & \cdots & 1 & -1 \end{array} \right]$$

which is singular but has the same null space as the continuous derivative operator; i.e., it maps constant vectors into 0.

We must also augment the right hand side, with a number of zeros equal to the number of rows in the regularization matrix. We write the augmented right hand side

$$\tilde{\mathbf{y}} \equiv \left( \begin{array}{c} \mathbf{y} \\ 0 \end{array} \right).$$

Since $\tilde{A}^T\tilde{\mathbf{y}} = A^T\mathbf{y}$ and $\tilde{A}^T\tilde{A} = A^T A + \lambda R^T R$, the least squares solutions of $\tilde{A}\mathbf{x} = \tilde{\mathbf{y}}$ satisfy

$$(A^T A + \lambda R^T R)\mathbf{x} = A^T \mathbf{h}.$$

So to incorporate any regularization of the form of (11.62) all one has to do is augment the sparse matrix. Most commonly this means either damping, in which case $R$ is diagonal, or second-difference smoothing, in which case $R$ is tridiagonal.

### 11.3.4 Jumping Versus Creeping$^\text{e}$

The pseudo-inverse $A^\dagger$ itself has something of a smoothness condition built in. If the matrix $A$ has full column rank and the number of rows is greater than or equal to the number of columns (in which case the system is said to be overdetermined) then the least squares solution is unique. But if the system is underdetermined, the least squares solution is not unique since $A$ has a nontrivial null space. All of the least squares solutions differ only by elements of the null space of $A$. Of all of these, the pseudo-inverse solution is the one of smallest norm. That is, $\| \mathbf{x}^\dagger \| \leq \| \mathbf{x} \|$ for every $\mathbf{x}$ such that $A^T A \mathbf{x} = A^T y$, as we saw in Chapter 5.

This means, for example, that in a nonlinear least squares problem, where we perturb about a reference model and compute this perturbation at each step by solving a linear least squares problem, then the size of the steps will be minimized if the pseudo-inverse is used. This has led to the term “creeping” being used for this sort of inversion. On the other hand, if at each nonlinear step we solve for the unknown model directly, then using the pseudo-inverse will smallest norm will enforce the smallest norm property on the model itself, not the perturbation of this model about the background. This is called “jumping” since the size of the change in the solution between nonlinear iterations is not constrained to be small. The terms creeping and jumping are due to Parker [Par94].

$^\text{e}$This section and the next are taken from [SDG90].

1