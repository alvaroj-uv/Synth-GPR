7.1 The World's Second Smallest Inverse Problem

111

Now since the data space is one-dimensional, the data-space eigenvector is just a normalized vector in $\mathbf{R}^1$-which is just 1. So $U_r = 1$. To get $V_r$ we don't even need $A^T A$ since we know that

$$A^T U_r = V_r \Lambda_r.$$

So

$$\left[ \begin{array}{c} 1 \\ -1 \end{array} \right] \cdot 1 = \sqrt{2} V_r \Rightarrow V_r = \frac{1}{\sqrt{2}} \left[ \begin{array}{c} 1 \\ -1 \end{array} \right].$$

The complete SVD then is

$$A = 1 \cdot \sqrt{2} \cdot \frac{1}{\sqrt{2}} \left[ \begin{array}{c} 1 \\ -1 \end{array} \right]^T = 1 \cdot \sqrt{2} \cdot \frac{1}{\sqrt{2}} \left[ \begin{array}{cc} 1 & -1 \end{array} \right].$$

where $U_r = 1$, $\Lambda_r = \sqrt{2}$, and $V_r = 1/\sqrt{2} \left[ \begin{array}{cc} 1 & -1 \end{array} \right]^T$.

So, the eigenvalues of $A^T A$ are 2 and 0. 2 is the eigenvalue of the (unnormalized) eigenvector $(1, -1)^T$, while 0 is the eigenvalue of $(1, 1)^T$. The latter follows from the fact that $A V_0 = 0$ so

$$\left[ \begin{array}{cc} 1 & -1 \end{array} \right] \left[ \begin{array}{c} v_0 \\ v_1 \end{array} \right] = 0 \Rightarrow V_0 = \left[ \begin{array}{c} 1 \\ 1 \end{array} \right]$$

This has a simple physical interpretation. An out-of-phase perturbation of velocity and depth (increase one and decrease the other) changes the travel time, while an in phase perturbation (increase both) does not. Since an in phase perturbation must be proportional to $(1, 1)^T$, it stands to reason that this vector would be in the null space of $A$. But notice that we have made this physical argument without reference to the linearized (log parameter) problem. However, since we spoke in terms of perturbations to the model, the assumption of a linear problem was implicit. In other words, by thinking of the physics of the problem we were able to guess the singular vectors of the linearized problem without even considering the linearization explicitly.

In the notation we developed for the SVD, we can say that $V_r$, the matrix of non-null-space model singular vectors is $(1, -1)^T$, while $V_0$, the matrix of null-space singular vectors is $(1, 1)^T$. And hence, using the normalized singular vectors, the resolution operator is

$$V_r V_r^T = \frac{1}{\sqrt{2}} \left[ \begin{array}{cc} 1 & -1 \\ -1 & 1 \end{array} \right]. \tag{7.15}$$

The covariance matrix of the depth/velocity model is

$$A^\dagger \text{Cov}(\mathbf{d}) A^{\dagger T} = \sigma^2 A^\dagger A^{\dagger T} \tag{7.16}$$

assuming the single travel time datum has normally distributed error. Hence the covariance matrix is

$$\text{Cov}(\mathbf{m}) = \left( \frac{\sigma}{2} \right)^2 \left[ \begin{array}{cc} 1 & -1 \\ -1 & 1 \end{array} \right]. \tag{7.17}$$

1