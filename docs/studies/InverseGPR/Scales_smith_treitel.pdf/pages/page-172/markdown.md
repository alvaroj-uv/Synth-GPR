11.2 Conjugate Gradient

157

is a monotone sequence which is bounded below by the unique minimum $f(\mathbf{z})$. That such a sequence must converge is intuitively clear and indeed follows from the Monotone Convergence Theorem. The proof of this theorem relies on a surprisingly deep property of real numbers: any nonempty set of real numbers which has a lower bound, has a greatest lower bound (called the infimum). Having thus established the convergence of $f(\mathbf{x}_k)$ to $f(\mathbf{z})$, the convergence of $\mathbf{x}_k$ to $\mathbf{z}$ follows from Lemma 2 and the properties of inner products:

$$f(\mathbf{z}) - f(\mathbf{x}_k) = -\frac{1}{2}(\mathbf{x}_k - \mathbf{z}, A(\mathbf{x}_k - \mathbf{z})) \to 0 \Rightarrow \mathbf{x}_k - \mathbf{z} \to 0 \tag{11.29}$$

since $A$ is positive definite.

There is a drawback to steepest descent, which occurs when the ratio of the largest to the smallest eigenvalue (the condition number $\kappa$) is very large; the following result quantifies ill-conditioning for quadratic minimization problems.

**Theorem 13** *Let $\lambda_{max}$ and $\lambda_{min}$ be the largest and smallest eigenvalues of the symmetric positive definite matrix $A$. Let $\mathbf{z}$ be the minimum of $f(\mathbf{x})$ and $\mathbf{r}$ the residual associated with an arbitrary $\mathbf{x}$. Then*

$$\frac{\|\mathbf{r}\|}{2\lambda_{max}} \le f(\mathbf{x}) - f(\mathbf{z}) \le \frac{\|\mathbf{r}\|}{2\lambda_{min}} \tag{11.30}$$

*where $\|\mathbf{x}\|^2 \equiv (\mathbf{x}, \mathbf{x})$ is the Euclidean norm.*

If all the eigenvalues of $A$ were the same, then the level surfaces of $f$ would be spheres, and the steepest descent direction would point towards the center of the sphere for any initial vector $\mathbf{x}$. Similarly, if there are clusters of nearly equal eigenvalues, then steepest descent will project out the spherical portion of the level surfaces associated with those eigenvalues nearly simultaneously. But if there are eigenvalues of very different magnitude then the portions of the level surfaces associated with them will be long thin ellipsoids. As a result, the steepest descent direction will not point towards the quadratic minimum. Depending upon the distribution of eigenvalues, steepest descent has a tendency to wander back and forth across the valleys, with the residual changing very little from iteration to iteration.

The proof of this result is as follows. Let $\mathbf{x} = \mathbf{z} + \mathbf{p}$ where $\mathbf{x}$ is arbitrary. From Lemma 2,

$$f(\mathbf{x}) - f(\mathbf{z}) = \frac{1}{2}(\mathbf{p}, A\mathbf{p})$$

Now, $\mathbf{p} = -A^{-1}\mathbf{r}$, so that

$$\frac{1}{2}(A^{-1}\mathbf{r}, \mathbf{r}) = \frac{1}{2}(\mathbf{p}, A\mathbf{p})$$

1