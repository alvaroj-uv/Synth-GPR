180

BIBLIOGRAPHY

one has

$$\left[ \frac{\mathbf{p}_0 \mathbf{p}_0}{(\mathbf{q}_0, \mathbf{q}_0)} + \frac{\mathbf{p}_1 \mathbf{p}_1}{(\mathbf{q}_1, \mathbf{q}_1)} \right] = \left[ \begin{array}{ll} 0.12627 & 0.05080 \\ 0.05080 & 0.03193 \end{array} \right].$$

But this is nothing more than $\left[ A^T A \right]^{-1}$ which was previously calculated:

$$\left[ A^T A \right]^{-1} = \frac{1}{689} \left[ \begin{array}{ll} 22 & 35 \\ 35 & 87 \end{array} \right] = \left[ \begin{array}{ll} 0.12627 & 0.05080 \\ 0.05080 & 0.03193 \end{array} \right].$$

In this particular case $A^\dagger A = I$ so the parameters are perfectly well resolved in the absence of noise.

# Exercises

1. Prove Equation (11.22).

2. Show that

$$f(\mathbf{z}) - f(\mathbf{x}_k) = -\frac{1}{2}(\mathbf{x}_k - \mathbf{z}, A(\mathbf{x}_k - \mathbf{z}))$$

where $\mathbf{z}$ is a solution to $A\mathbf{x} = \mathbf{h}$ and $A$ is a symmetric, positive definite matrix.

3. Prove Lemma 4.

4. With steepest descent, we saw that in order for the residual vector to be exactly zero, it was necessary for the initial approximation to the solution to lie on one of the principle axes of the quadratic form. Show that with CG, in order for the residual vector to be exactly zero we require that

$$(\mathbf{r}_i, \mathbf{p}_i) = (\mathbf{r}_i, \mathbf{r}_i)$$

which is always true by virtue of Lemma 3.

## Bibliography

[Björ75] A. Björk. Methods for sparse linear least-squares problems. In J. Bunch and D. Rose, editors, *Sparse Matrix Computations*. Academic, New York, 1975.

[Cha78] R. Chandra. *Conjugate gradient methods for partial differential equations*. PhD thesis, Yale University, New Haven, CT, 1978.

[CM79] S. Campbell and C. Meyer. *Generalized inverses of linear transformations*. Pitman, London, 1979.

[CW80] J. Cullum and R. Willoughby. The Lanczos phenomenon—an interpretation based upon conjugate gradient optimization. *Linear Algebra and Applications*, 29:63–90, 1980.

1