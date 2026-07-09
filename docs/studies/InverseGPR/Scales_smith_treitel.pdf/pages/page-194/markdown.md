11.4 Sparse SVD

179

### 11.4.3 Explicit Calculation of the Pseudo-Inverse

Finally, we point out a clever result of Hestenes which seems to have been largely ignored. In the paper [Hes75] he proves the following. Let $r$ be the rank of $A$ an arbitrary matrix, and let $\mathbf{p}$ and $\mathbf{q}$ be the CGLS search vectors, and let $\mathbf{x}_0 = 0$. Then

$$A^{\dagger} = \left[ \frac{\mathbf{p}_0 \mathbf{p}_0}{(\mathbf{q}_0, \mathbf{q}_0)} + \frac{\mathbf{p}_1 \mathbf{p}_1}{(\mathbf{q}_1, \mathbf{q}_1)} + \cdots \frac{\mathbf{p}_{r-1} \mathbf{p}_{r-1}}{(\mathbf{q}_{r-1}, \mathbf{q}_{r-1})} \right] A^T \tag{11.85}$$

is the generalized pseudo-inverse of $A$. A generalized pseudo-inverse satisfies only two of the four Penrose conditions, to wit:

$$A^{\dagger} A A^{\dagger} = A^{\dagger} \tag{11.86}$$

$$A A^{\dagger} A = A \tag{11.87}$$

To illustrate this result, consider the following least squares problem:

$$\left[ \begin{array}{cc} 1 & 2 \\ -4 & 5 \\ -1 & 3 \\ 2 & -7 \end{array} \right] \left[ \begin{array}{c} \mathbf{x} \\ y \end{array} \right] = \left[ \begin{array}{c} 5 \\ 6 \\ 5 \\ -12 \end{array} \right].$$

The column rank of the matrix is 2. It is straightforward to show that

$$\left[ A^T A \right]^{-1} = \frac{1}{689} \left[ \begin{array}{cc} 22 & 35 \\ 35 & 87 \end{array} \right].$$

Therefore the pseudo-inverse is

$$A^{\dagger} = \left[ A^T A \right]^{-1} A^T = \frac{1}{689} \left[ \begin{array}{cccc} 157 & -173 & 18 & -71 \\ 79 & -30 & 31 & -84 \end{array} \right].$$

Now apply the CGLS algorithm. The relevant calculations are

$$\mathbf{p}_0 = \left[ \begin{array}{c} -48 \\ 139 \end{array} \right], \quad \mathbf{q}_0 = \left[ \begin{array}{c} 230 \\ 887 \\ 465 \\ -1069 \end{array} \right].$$

$$\mathbf{p}_1 = \left[ \begin{array}{c} 9.97601 \\ 4.28871 \end{array} \right], \quad \mathbf{q}_1 = \left[ \begin{array}{c} 18.55343 \\ -18.46049 \\ 2.89012 \\ -10.06985 \end{array} \right], \quad \mathbf{x}_2 = \left[ \begin{array}{c} 1.00000 \\ 2.00000 \end{array} \right],$$

which is the solution. Recalling (11.85)

$$A^{\dagger} = \left[ \frac{\mathbf{p}_0 \mathbf{p}_0}{(\mathbf{q}_0, \mathbf{q}_0)} + \frac{\mathbf{p}_1 \mathbf{p}_1}{(\mathbf{q}_1, \mathbf{q}_1)} + \cdots \frac{\mathbf{p}_{r-1} \mathbf{p}_{r-1}}{(\mathbf{q}_{r-1}, \mathbf{q}_{r-1})} \right] A^T \tag{11.88}$$

1