110

Linear Inverse Problems With Uncertain Data

So the model vector $\mathbf{m}$ is $(z, c)$ since $c$ and $z$ are both unknown, and the data vector $\mathbf{d}$ is simply $t$. The forward problem is $g(\mathbf{m}) = z/c$. Notice that $g$ is linear in depth, but nonlinear in sound speed $c$. We can linearize the forward problem by doing a Taylor series expansion about some model $(z_0, c_0)$ and retaining only the first order term:

$$t = t_0 + \frac{z_0}{c_0} \left[ \frac{1}{z_0}, -\frac{1}{c_0} \right] \left[ \begin{array}{c} \delta z \\ \delta c \end{array} \right] \tag{7.10}$$

where $t_0 = z_0/c_0$. Pulling the $t_0$ over to the left side and diving by $t_0$ we have

$$\frac{\delta t}{t_0} = [1, -1] \left[ \begin{array}{c} \frac{\delta z}{z_0} \\ \frac{\delta c}{c_0} \end{array} \right] \tag{7.11}$$

In this particular case the linearization is independent of the starting model $(z_0, c_0)$ since by computing the total derivative of of $t$ we get

$$\frac{\delta t}{t} = \frac{\delta z}{z} - \frac{\delta c}{c}. \tag{7.12}$$

In other words, by defining new parameters to be the logarithms of the old parameters, or the dimensionless perturbations, (but keeping the same symbols for convenience) we have

$$t = z - c. \tag{7.13}$$

In any case, the linear(-ized) forward operator is the $1 \times 2$ matrix $A = (1, -1)$ and

$$A^T A = \left[ \begin{array}{cc} 1 & -1 \\ -1 & 1 \end{array} \right]. \tag{7.14}$$

Let's work out the SVD of $A$ by hand. First, let us make the convention that model vectors and data vectors are column vectors. We could make them row vectors too, but we must keep to some convention in order to avoid getting confused. So

The forward operator matrix $A$ must be a 1 by 2 matrix

$$A = [1 \quad -1]$$

since $\mathbf{d} \in \mathbf{R}^1$ and $\mathbf{m} \in \mathbf{R}^2$. Therefore

$$A^T A = \left[ \begin{array}{c} 1 \\ -1 \end{array} \right] [1 \quad -1] = \left[ \begin{array}{cc} 1 & -1 \\ -1 & 1 \end{array} \right]$$

and

$$AA^T = [1 \quad -1] \left[ \begin{array}{c} 1 \\ -1 \end{array} \right] = 2.$$

So the eigenvalue of a $1 \times 1$ matrix (a scalar) is just this number. The eigenvalues of $AA^T$ are the squares of the singular values, so the one and only non-zero singular value is $\sqrt{2}$.

1