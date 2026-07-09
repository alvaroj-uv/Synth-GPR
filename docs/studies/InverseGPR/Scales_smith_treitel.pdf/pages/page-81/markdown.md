66

SVD and Resolution in Least Squares

where by $\mathbf{m}_{\mathrm{ls}}$ we mean *any* solution of the normal equations. An immediate consequence of this is that the length of $\mathbf{m}_{\mathrm{ls}}$ must be at least as great as the length of $\mathbf{m}^{\dagger}$ since

$$\|\mathbf{m}_{\mathrm{ls}}\|^2 = \|\mathbf{m}^{\dagger}\|^2 + \sum_{i=r+1}^{M} \alpha_i^2. \tag{5.4}$$

To prove this just remember that $\|\mathbf{m}_{\mathrm{ls}}\|^2$ is the dot product of $\mathbf{m}_{\mathrm{ls}}$ with itself. Take the dot product of the right-hand-side of Equation 5.3 with itself. Not only are the vectors $\mathbf{v}_i$ mutually orthonormal, but they are orthogonal to $\mathbf{m}^{\dagger}$ since $\mathbf{m}^{\dagger}$ lives in $V_r$ and $V_r$ is orthogonal to $V_0$.

This is referred to the minimum norm property of the generalized inverse. Of all the infinity of solutions of the normal equations (assuming there is a model null space), the generalized inverse solution is the one of smallest length.

### Both a Model and a Data Null Space

In the case of a data null space, we saw that the generalized inverse solution minimized the least squares mis-fit of data and model response. While in the case of a model null space, the generalized inverse solution minimized the length of the solution itself. If there are both model and data null spaces, then the generalized inverse simultaneously optimizes these goals. As an exercise, set the derivative of

$$\|A\mathbf{m} - \mathbf{d}\|^2 + \|\mathbf{m}\|^2$$

with respect to $\mathbf{m}$ equal to zero. The calculation is sketched on page 63. You should get the following generalization of the normal equations:

$$\left(A^T A + I\right)\mathbf{m} = A^T \mathbf{d}.$$

You can show that the matrix $A^T A + I$ is invertible for any $A$. How?

### 5.0.3 Examples

Consider the linear system

$$\left[ \begin{array}{ccc} 1 & 1 & 0 \\ 0 & 0 & 1 \end{array} \right] \left( \begin{array}{c} m_1 \\ m_2 \\ m_3 \end{array} \right) = \left( \begin{array}{c} 1 \\ 1 \end{array} \right).$$

From the SVD we have

$$A^{\dagger} = \left[ \begin{array}{cc} \frac{1}{2} & 0 \\ \frac{1}{2} & 0 \\ 0 & 1 \end{array} \right].$$

1