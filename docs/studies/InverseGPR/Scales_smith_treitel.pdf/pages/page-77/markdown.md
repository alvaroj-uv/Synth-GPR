62

SVD and Resolution in Least Squares

and hence

$$\Lambda^{-1} = \left[ \begin{array}{cc} 1/\lambda_1 & 0 \\ 0 & 1/\lambda_2 \\ 0 & 0 \end{array} \right] \cdot m \times n$$

Since $A^\dagger$ is $V\Lambda^{-1}U^T$ then

$$A^\dagger A = V\Lambda^{-1}U^T U \Lambda V^T = V\Lambda^{-1}\Lambda V^T.$$

Unfortunately we cannot simply replace $\Lambda^{-1}\Lambda$ by the identity:

$$\left[ \begin{array}{cc} 1/\lambda_1 & 0 \\ 0 & 1/\lambda_2 \\ 0 & 0 \end{array} \right] \left[ \begin{array}{ccc} \lambda_1 & 0 & 0 \\ 0 & \lambda_2 & 0 \end{array} \right] = \left[ \begin{array}{ccc} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 0 \end{array} \right].$$

Therefore

$$V\Lambda^{-1}\Lambda V^T \neq I.$$

On the other hand if we multiply $A$ on the right by $A^\dagger$ we get

$$AA^\dagger = U\Lambda\Lambda^{-1}U^T.$$

And

$$\Lambda\Lambda^{-1} = \left[ \begin{array}{ccc} \lambda_1 & 0 & 0 \\ 0 & \lambda_2 & 0 \end{array} \right] \left[ \begin{array}{cc} 1/\lambda_1 & 0 \\ 0 & 1/\lambda_2 \\ 0 & 0 \end{array} \right] = \left[ \begin{array}{cc} 1 & 0 \\ 0 & 1 \end{array} \right].$$

So in this case we can see that $A^\dagger$ is a right inverse but not a left inverse. You can verify for yourself that if there were more unknowns than data ($n \geq m$), $A^\dagger$ would be a left inverse of $A$.

If there are zero singular values, then the only thing different we must do is project out those components. The SVD then becomes:

$$A = U_r \Lambda_r V_r^T.$$

The generalized inverse is then defined to be

$$A^\dagger \equiv V_r \Lambda_r^{-1} U_r^T.$$

Note that in this case $\Lambda_r$ is an $r \times r$ matrix so

$$A^\dagger A = V_r V_r^T$$

and

$$AA^\dagger = U_r U_r^T.$$

The first of these is an identity matrix only if $r = m$ and the second only if $r = n$. You will show in an exercise however that in any case

$$A^\dagger AA^\dagger = A^\dagger$$

$$AA^\dagger A = A$$

Let us explore the significance of the generalized inverse bit by bit. This discussion is patterned on that in Chapter 12 of [AR80].

1