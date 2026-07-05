172

Iterative Linear Solvers

This point merits a brief digression since the effects of damping or smoothing will be different according as one is doing jumping or creeping. Suppose the nonlinear inverse problem is: given $\mathbf{y}$, find $\mathbf{x}$ such that $\mathbf{y} - F(\mathbf{x})$ is minimized in some sense. Expanding the forward problem $F$ to first order in a Taylor series about some model $\mathbf{x}_0$ gives

$$\mathbf{y} = \mathbf{y}_0 + F'(\mathbf{x}_0)(\mathbf{x} - \mathbf{x}_0) \quad (11.64)$$

where $\mathbf{y}_0 \equiv F(\mathbf{x}_0)$. Denoting the Jacobian $F'$ by $A$, there are two alternative least squares solutions of the linearized equations

$$\text{Jumping } \mathbf{x}^j = A^\dagger(A\mathbf{x}_0 + \mathbf{y} - \mathbf{y}_0) \quad (11.65)$$

$$\text{Creeping } \mathbf{x}^c = \mathbf{x}_0 + A^\dagger(\mathbf{y} - \mathbf{y}_0) \quad (11.66)$$

differing only in how the pseudo-inverse is applied.

In creeping $\mathbf{x} - \mathbf{x}_0$ is a minimum norm least squares solution of the linearized forward equations, whereas in jumping the updated model $\mathbf{x}$ is itself a minimum norm least squares solution. The difference between the jumping and creeping (in the absence of regularization) is readily seen to be

$$\mathbf{x}^j - \mathbf{x}^c = (A^\dagger A - I)\mathbf{x}_0. \quad (11.67)$$

Expressing the initial model in terms of its components in the row space and null space of $A$,

$$\mathbf{x}_0 = \mathbf{x}_0^{row} + \mathbf{x}_0^{null} \quad (11.68)$$

and noting that

$$\mathbf{x}_0^{row} = A^\dagger A \mathbf{x}_0 \quad (11.69)$$

then

$$\mathbf{x}^j = \mathbf{x}_0^{row} + A^\dagger(\mathbf{y} - \mathbf{y}_0) \quad (11.70)$$

and (11.67) becomes

$$\mathbf{x}^j - \mathbf{x}^c = -\mathbf{x}_0^{null}. \quad (11.71)$$

Thus, the creeping and jumping solutions differ by the component of the initial model that lies in the null space of $A$: some remnants of the initial model that appear in $\mathbf{x}^c$ are not present in $\mathbf{x}^j$. Only if $A$ is of full column rank (giving $A^\dagger A = I$) will the two solutions be the same for any initial guess. In the next sections it will be seen that this analysis must be modified when regularization is employed.

### 11.3.5 How Smoothing Affects Jumping and Creeping

In the absence of regularization, the jumping and creeping solutions differ only by the component of the initial model in the null space of the Jacobian matrix. Regularization changes things somewhat since the matrix associated with the regularized forward

1