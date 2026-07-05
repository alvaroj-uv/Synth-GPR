160

Iterative Linear Solvers

Symbolic arithmetic packages, including Mathematica, can solve the problem in exact arithmetic. This is very useful for analysis of the effects of rounding errors.

Figure out geometrically what steepest descent is doing. Does SD ever converge in finitely many steeps on this problem in exact arithmetic? In this case you should be able to derive an analytic expression for the residual vector. Make plots showing the level curves of the quadratic form associated with $A$. Then plot the solution vector as a function of iteration. The changes should always be normal to the contours. Under what circumstances can the residual vector be exactly zero? What is the geometrical interpretation of this?

Do your conclusions generalize to symmetric non-diagonal matrices?

What happens if you change the matrix from $\mathrm{diag}(10,1)$ to $\mathrm{diag}(100,1)$?

## 11.2.5 The Method of Conjugate Directions

The problem with steepest descent (SD) is that for ill-conditioned matrices the residual vector doesn't change much from iteration to iteration. A simple scheme for improving its performance goes back to Fox, Husky, and Wilkinson [FHW49] and is called the conjugate direction ($CD$) method. Instead of minimizing along the residual vector, as in SD, minimize along 'search vectors' $\mathbf{p}_k$ which are assumed (for now) to be orthogonal with respect to the underlying matrix. This orthogonality will guarantee convergence to the solution in at most $n$ steps, where $n$ is the order of the matrix.

So replace the step

$$
\mathbf{x}_k = \mathbf{x}_{k-1} + \alpha_k \mathbf{r}_{k-1}
$$

with

$$
\mathbf{x}_k = \mathbf{x}_{k-1} + \alpha_k \mathbf{p}_{k-1}
$$

where $\mathbf{p}$ is to be defined. As in SD the idea is to minimize $f$ along these lines. The scale factors $\alpha$, as in SD, are determined by the minimization. Using the proof of Lemma 2,

$$
\begin{array}{rcl}
f(\mathbf{x}_k + \alpha \mathbf{p}_k) & = & f(\mathbf{x}_k) + \frac{1}{2}(\alpha \mathbf{p}_k, A \alpha \mathbf{p}_k) - (\alpha \mathbf{p}_k, \mathbf{r}_k) \\
& = & f(\mathbf{x}_k) + \frac{1}{2}\alpha^2(\mathbf{p}_k, A \mathbf{p}_k) - \alpha(\mathbf{p}_k, \mathbf{r}_k)
\end{array}
\tag{11.37}
$$

Setting $\frac{\partial f(\mathbf{x}_k + \alpha \mathbf{p}_k)}{\partial \alpha} = 0$ gives

$$
\alpha \equiv \alpha_{k+1} = \frac{(\mathbf{p}_k, \mathbf{r}_k)}{(\mathbf{p}_k, A \mathbf{p}_k)} = \frac{(\mathbf{r}_k, \mathbf{r}_k)}{(\mathbf{p}_k, A \mathbf{p}_k)}.
$$

The last expression for $\alpha$ is part of Lemma 4

1