# Chapter 7

## Linear Inverse Problems With Uncertain Data

In Chapter 5 we showed that the SVD could be used to solve a linear inverse problem in which the only uncertainties were associated with the data. The canonical formulation of such a problem is

$$\mathbf{d} = A\mathbf{m} + \epsilon \tag{7.1}$$

where it is assumed that the forward operator $A$ is linear and exactly known and that the uncertainties arise from additive noise in the data. In most geophysical inverse problems, the vector $\mathbf{m}$ is properly defined in an infinite dimensional space of functions; for example, the elastic tensor as a function of space. As a practical matter the model space is usually discretized so that the problem is numerically finite dimensional. This is a potential source of error (bias, discretization error), but for now we will ignore this and assume that the discretization is very fine, but nevertheless finite. This is equivalent to assuming *a priori* that the true Earth model is confined to a finite dimensional subspace of the model space.

If there are no discretization errors, and if the forward model is linear and known, then the observations $\mathbf{d}$ are the response of the *true* model $\mathbf{m}_{\mathrm{T}}$ under the action of $A$, provided there are no measurement or other systematic errors.

As defined in Section 6.5 $\mathbf{m}^{\dagger}$ is a pseudo-inverse estimator of the true model: the generalized solution of Equation 7.1 is given by $\mathbf{m}^{\dagger} = A^{\dagger}\mathbf{d}$. Since $\mathbf{d}$ is the response of the true model, $\mathbf{m}_{\mathrm{true}}$, it follows that

$$\mathbf{m}^{\dagger} \equiv A^{\dagger}\mathbf{d} = A^{\dagger}(A\mathbf{m}_{\mathrm{true}} + \epsilon) = A^{\dagger}A\mathbf{m}_{\mathrm{true}} + A^{\dagger}\epsilon.$$

In terms of the SVD, the resolution matrix $A^{\dagger}A$ can be written $V_{r}V_{r}^{T}$ and so represents a projection operator onto the non-null space of the forward problem (i.e., the row space). Since none of the columns of $V_{r}$ lie in the null space of $A$, the net result of this

1