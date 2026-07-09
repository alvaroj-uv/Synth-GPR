11.3 Practical Implementation

173

problem has no nontrivial null space. Recall that for jumping, the linearized problem, with solution $\mathbf{x}^j$, is

$$A\mathbf{x}^j = A\mathbf{x}_0 + \mathbf{y} - \mathbf{y}_0 \tag{11.72}$$

whereas for creeping

$$A(\mathbf{x}^c - \mathbf{x}_0) = \mathbf{y} - \mathbf{y}_0. \tag{11.73}$$

The addition of regularization produces the augmented systems

$$\tilde{A}\mathbf{x}^j = \begin{pmatrix} \mathbf{y} - \mathbf{y}_0 + A\mathbf{x}_0 \\ 0 \end{pmatrix} \tag{11.74}$$

and

$$\tilde{A}(\mathbf{x}^c - \mathbf{x}_0) = \begin{pmatrix} \mathbf{y} - \mathbf{y}_0 \\ 0 \end{pmatrix}. \tag{11.75}$$

Inverting, one has

$$\mathbf{x}^j = \tilde{A}^\dagger \begin{pmatrix} \mathbf{y} - \mathbf{y}_0 + A\mathbf{x}_0 \\ 0 \end{pmatrix} = \tilde{A}^\dagger \begin{pmatrix} \mathbf{y} - \mathbf{y}_0 \\ 0 \end{pmatrix} + \tilde{A}^\dagger \begin{pmatrix} A\mathbf{x}_0 \\ 0 \end{pmatrix}. \tag{11.76}$$

and

$$\mathbf{x}^c - \mathbf{x}_0 = \tilde{A}^\dagger \begin{pmatrix} \mathbf{y} - \mathbf{y}_0 \\ 0 \end{pmatrix}. \tag{11.77}$$

Thus

$$\mathbf{x}^j - \mathbf{x}^c = \tilde{A}^\dagger \begin{pmatrix} A\mathbf{x}_0 \\ 0 \end{pmatrix} - \mathbf{x}_0. \tag{11.78}$$

For $\lambda > 0$ the augmented matrix is nonsingular, therefore one can write

$$\mathbf{x}_0 = \tilde{A}^\dagger \tilde{A}\mathbf{x}_0.$$

Using the definition of $\tilde{A}$

$$\mathbf{x}_0 = \tilde{A}^\dagger \begin{pmatrix} A \\ \sqrt{\lambda}R \end{pmatrix} \mathbf{x}_0 = \tilde{A}^\dagger \begin{pmatrix} A\mathbf{x}_0 \\ 0 \end{pmatrix} + \tilde{A}^\dagger \begin{pmatrix} 0 \\ \sqrt{\lambda}R\mathbf{x}_0 \end{pmatrix}. \tag{11.79}$$

Finally from (11.78) and (11.79) one obtains

$$\mathbf{x}^j - \mathbf{x}^c = -\tilde{A}^\dagger \begin{pmatrix} 0 \\ \sqrt{\lambda}R\mathbf{x}_0 \end{pmatrix}. \tag{11.80}$$

As in (11.71), the difference between the two solutions depends on the initial model. But when smoothing is applied, the creeping solution possesses components related to the slope of $\mathbf{x}_0$ (first difference smoothing) or to the roughness of $\mathbf{x}_0$ (second difference smoothing) which are not present in the jumping solution. An important corollary of this result is that for smooth initial models, jumping and creeping will give the same results when roughness penalties are employed to regularize the calculation. Examples illustrating the comparative advantages of jumping and creeping are contained in [SDG90].

If the columns of the regularization operator are linearly independent, then the columns of the augmented matrix are too.

1