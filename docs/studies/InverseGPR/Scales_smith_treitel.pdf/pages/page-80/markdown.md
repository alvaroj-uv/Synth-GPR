65

Now $A$ applied to the least squares solution is the approximation to the data from within the column space. So $A\mathbf{m}_{\mathrm{ls}}$ is precisely the projection of the data $\mathbf{d}$ onto the column space:

$$A\mathbf{m}_{\mathrm{ls}} = A(A^T A)^{-1} A^T \mathbf{d}.$$

Before when we did orthogonal projections, the projecting vectors/matrices were orthogonal, so the $A^T A$ term would have been the identity, but the outer product structure in $A\mathbf{m}_{\mathrm{ls}}$ is evident.

The generalized inverse projects the data onto the column space of $A$.

A few observations:

- When $A$ is invertible (square, full rank) $A(A^T A)^{-1} A^T = AA^{-1}(A^T)^{-1} A^T = I$, so every vector projects onto itself.
- $A^T A$ has the same null space as $A$. Proof: clearly if $A\mathbf{m} = 0$, then $A^T A\mathbf{m} = 0$. Going the other way, suppose $A^T A\mathbf{m} = 0$. Then $\mathbf{m}^T A^T A\mathbf{m} = 0$. But this can also be written as $(A\mathbf{m}, A\mathbf{m}) = \|A\mathbf{m}\|^2 = 0$. By the properties of the norm, $\|A\mathbf{m}\|^2 = 0 \Rightarrow A\mathbf{m} = 0$.
- As a corollary of this, if $A$ has linearly independent columns (i.e., the rank $r = m$) then $A^T A$ is invertible.

### A Model Null Space

Now let us consider the existence of a model null space $V_0$ (but no data null space $U_0$), so $m > n \ge r$. Once again, using the SVD, we can show that (since $\mathbf{m}^\dagger = A^\dagger \mathbf{d}$)

$$A\mathbf{m}^\dagger = A A^\dagger \mathbf{d} = U_r \Lambda_r V_r^T \quad V_r \Lambda_r^{-1} U_r^T \quad \mathbf{d} = \mathbf{d}$$

since $V_r^T V_r = I_r$ and $U_r U_r^T = I_r = I_n$. But since $\mathbf{m}^\dagger$ is expressible in terms of the $V_r$ vectors (and not the $V_0$ vectors), it is clear that the generalized inverse solution is a model that satisfies $A\mathbf{m}^\dagger = \mathbf{d}$ but is entirely confined to $V_r$.

A consequence of this is that an arbitrary least squares solution (i.e., any solution of the normal equations) can be represented as the sum of the generalized solution with some component in the model null space:

$$\mathbf{m}_{\mathrm{ls}} = \mathbf{m}^\dagger + \sum_{i=r+1}^{M} \alpha_i \mathbf{v}_i \tag{5.3}$$

1