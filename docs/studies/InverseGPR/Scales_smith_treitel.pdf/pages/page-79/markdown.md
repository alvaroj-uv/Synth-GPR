64

SVD and Resolution in Least Squares

is a $V_0$ space, or $U_r$ if there is a $U_0$ space. All we can be certain of is that $V_r^T V_r$ and $U_r^T U_r$ will be $r$-dimensional identity matrices, So we do know that

$$A^T A = V_r \Lambda_r^2 V_r^T.$$

$A^T A$ is certainly invertible (since in this case there is assumed to be no model null space) so the least squares solution is

$$\mathbf{m}_{\text{ls}} = (V_r \Lambda_r^2 V_r^T)^{-1} (U_r \Lambda_r V_r^T)^T \mathbf{d} = V_r \Lambda_r^{-1} U_r^T \mathbf{d}.$$

But this is precisely $A^\dagger \mathbf{d}$. Let us denote the generalized inverse solution by $\mathbf{m}^\dagger = A^\dagger \mathbf{d}$. In the special case that there is no model null space $V_0$, $\mathbf{m}_{\text{ls}} = \mathbf{m}^\dagger$.$^b$

Now we saw above that $A$ maps arbitrary model vectors $\mathbf{m}$ into vectors that have no component in $U_0$. On the other hand it is easy to show (using the SVD) that

$$U_r^T (\mathbf{d} - A \mathbf{m}^\dagger) = U_r^T \mathbf{d} - U_r^T U_r U_r^T \mathbf{d} = \mathbf{0}.$$

This means that $A \mathbf{m}^\dagger$ (since it lies in $U_r$) must be perpendicular to $\mathbf{d} - A \mathbf{m}^\dagger$ (since it lies in $U_0$).

### A Geometrical Interpretation of Least Squares [Str88]

If $\mathbf{d}$ were in the column space of $A$, then there would exist a vector $\mathbf{m}$ such that $A \mathbf{m} = \mathbf{d}$. On the other hand, if $\mathbf{d}$ is not in the column space of $A$ a reasonable strategy is to try to find an approximate solution from within the column space. In other words, find a linear combination of the columns of $A$ that is as close as possible in a least squares sense to the data. Let's call this approximate solution $\mathbf{m}_{\text{ls}}$. Since $A \mathbf{m}_{\text{ls}}$ is, by definition, confined to the column space of $A$ then $A \mathbf{m}_{\text{ls}} - \mathbf{d}$ (the error in fitting the data) must be in the orthogonal complement of the column space. (The orthogonal complement was defined on page 47.) The orthogonal complement of the column space is the left null space, so $A \mathbf{m}_{\text{ls}} - \mathbf{d}$ must get mapped into zero by $A^T$:

$$A^T (A \mathbf{m}_{\text{ls}} - \mathbf{d}) = 0$$

or

$$A^T A \mathbf{m}_{\text{ls}} = A^T \mathbf{d}$$

which is just the normal equation again. Now we saw in the last chapter that the outer product of a vector or matrix with itself defined a projection operator onto the subspace spanned by the vector (or columns of the matrix). If we look again at the normal equations and assume for the moment that the matrix $A^T A$ is invertible, then the least squares solution is:

$$\mathbf{m}_{\text{ls}} = (A^T A)^{-1} A^T \mathbf{d}$$

$^b$ $\mathbf{m}^\dagger$ is the generalized inverse solution, $A^\dagger \mathbf{d}$. It turns out this is unique, as we will prove shortly. $\mathbf{m}_{\text{ls}}$ is any solution of the normal equations. The complete connection between these two concepts will be made shortly when we treat the case of a model null space.

1