61

This means that $v_{13} + v_{23} = 0$ and $v_{33} = 0$, so the normalized model null space singular vector is

$$V_0 = \begin{pmatrix} -\frac{1}{\sqrt{2}} \\ \frac{1}{\sqrt{2}} \\ 0 \end{pmatrix}.$$

We can verify the SVD directly

$$\begin{aligned} A &= U_r \Lambda_r V_r^T \\ &= \begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix} \begin{bmatrix} \sqrt{2} & 0 \\ 0 & 1 \end{bmatrix} \begin{bmatrix} \frac{1}{\sqrt{2}} & 0 \\ \frac{1}{\sqrt{2}} & 0 \\ 0 & 1 \end{bmatrix}^T = \begin{bmatrix} 1 & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix} \end{aligned}$$

Remember, the only way that there can be no null space at all (no $U_0$ or $V_0$) is if $n = m = r$.

## 5.0.2 The Generalized Inverse

Recall the SVD of $A$ is $A = U \Lambda V^T$. $U$ is $n \times n$, $V$ is $m \times m$ and $\Lambda$ is $n \times m$. If there are no zero singular values the following matrix provides a one-sided inverse of $A$:

$$A^\dagger = V \Lambda^{-1} U^T$$

where $\Lambda^{-1}$ refers to the $m \times n$ matrix with $1/\lambda_i$ on its main diagonal. The matrix $A^\dagger$ is called the generalized inverse of $A$, or the pseudo-inverse. Be careful to keep the dimensions straight; in the SVD

$$A = U \Lambda V^T$$

we know that $V$ must be $m \times m$ (its columns span model space) and $U$ must be $n \times n$ (its columns span data space). Therefore $\Lambda$ must be $n \times m$. Similarly if we write

$$V \Lambda^{-1} U^T$$

it is clear that $\Lambda^{-1}$ must refer to an $m \times n$ matrix. $^a$

Whether $A^\dagger$ will be a left inverse or a right inverse depends on whether there are more equations than unknowns ($n \geq m$) or fewer ($m \geq n$). There is a two-sided (ordinary) inverse if and only if $m = n = r$, where $r$ is the rank. To see how this goes consider a concrete case, $m = 3$ and $n = r = 2$ So

$$\Lambda = \begin{bmatrix} \lambda_1 & 0 & 0 \\ 0 & \lambda_2 & 0 \end{bmatrix} \quad n \times m$$

$^a$For this reason perhaps it is an abuse of notation to write $\Lambda^{-1}$. Perhaps we should write $\Lambda^\dagger$ instead. The main danger of the current notation is that one is tempted to assume that $\Lambda^{-1} \Lambda = \Lambda \Lambda^{-1} = I$, which, as we have seen is not true in general.

1