68

SVD and Resolution in Least Squares

to the identity matrix, we would have perfect resolution. Using the SVD we have

$$\mathbf{m}^{\dagger} = V_{r}\Lambda_{r}^{-1}U_{r}^{T}U_{r}\Lambda_{r}V_{r}^{T}\mathbf{m} = V_{r}V_{r}^{T}\mathbf{m}.$$

We can use $U_{r}^{T}U_{r} = I$ whether there is a data null space or not. So in any case the matrix $V_{r}V_{r}^{T}$ is the "filter" relating the computed Earth parameters to the true ones. In the example above, with

$$A = \left[ \begin{array}{ccc} 1 & 1 & 0 \\ 0 & 0 & 1 \end{array} \right]$$

the resolution matrix $V_{r}V_{r}^{T}$ is equal to

$$\left[ \begin{array}{ccc} \frac{1}{\sqrt{2}} & \frac{1}{\sqrt{2}} & 0 \\ \frac{1}{\sqrt{2}} & \frac{1}{\sqrt{2}} & 0 \\ 0 & 0 & 1 \end{array} \right].$$

This says that the model parameter $m_{3}$ is perfectly well resolved, but that we can only resolve the average of the first two parameters $m_{1}$ and $m_{2}$. The more nonzero terms that appear in the rows of the resolution matrix, the more broadly averaged our inferences of the model parameters.

Data resolution is connected to the fact that the observed data may be different than the data predicted by the generalized inverse. The latter is just $A\mathbf{m}^{\dagger}$. But this is $AA^{\dagger}\mathbf{d}$. So if we call this $\mathbf{d}^{\dagger}$, then we have a relation very similar to that given by the resolution matrix:

$$\mathbf{d}^{\dagger} = AA^{\dagger}\mathbf{d} = U_{r}\Lambda_{r}V_{r}^{T}V_{r}\Lambda_{r}^{-1}U_{r}^{T}\mathbf{d} = U_{r}U_{r}^{T}\mathbf{d}$$

so we can think of the matrix $U_{r}U_{r}^{T}$ as telling us about how well the data are predicted by the computed model. In our example above, there is no data null space, so the data are predicted perfectly. But if there is a data null space then the row vectors of $U_{r}U_{r}^{T}$ will represent averages of the data.

# Exercises

1. Verify the following two "Penrose conditions":

$$A^{\dagger}AA^{\dagger} = A^{\dagger}$$

$$AA^{\dagger}A = A$$

2. Show that minimizing

$$\|A\mathbf{m} - \mathbf{d}\|^{2} + \lambda\|\mathbf{m}\|^{2}$$

with respect to $\mathbf{m}$ leads to the following generalized "normal equations"

$$\left(A^{T}A + \lambda I\right)\mathbf{m} = A^{T}\mathbf{d}.$$

3. Show that $A^{T}A + \lambda I$ is always an invertible matrix.

1