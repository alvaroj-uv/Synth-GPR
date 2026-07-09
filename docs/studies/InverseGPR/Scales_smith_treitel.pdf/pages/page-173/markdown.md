158

Iterative Linear Solvers

Symmetric, positive definite matrices can be diagonalized by orthogonal matrices: $A = RDR^T$, $A^{-1} = RD^{-1}R^T$, where $D$ is the diagonal matrix of the eigenvalues of $A$, and $R$ is orthogonal. Using the diagonalization of $A$,

$$\frac{1}{2}(\mathbf{p}, A\mathbf{p}) = \frac{1}{2}(D^{-1}\mathbf{y}, \mathbf{y})$$

where $\mathbf{y} \equiv R^T\mathbf{r}$. This last inner product can be written explicitly as

$$\frac{1}{2}(D^{-1}\mathbf{y}, \mathbf{y}) = \frac{1}{2}\sum_{i=1}^{n}\lambda_i^{-1}y_i^2$$

where $\lambda_i$ is the i-th eigenvalue of $A$. Next, we have the bounds

$$\frac{1}{2\lambda_{max}}\sum_{i=1}^{n}y_i^2 \le \frac{1}{2}\sum_{i=1}^{n}\lambda_i^{-1}y_i^2 \le \frac{1}{2\lambda_{min}}\sum_{i=1}^{n}y_i^2.$$

Since the vector $\mathbf{y}$ is related to the residual $r$ by rotation, they must have the same length ($\|\mathbf{y}\|^2 = \|R\mathbf{r}\|^2 = (R\mathbf{r}, R\mathbf{r}) = (\mathbf{r}, R^T R\mathbf{r}) = (\mathbf{r}, \mathbf{r}) = \|\mathbf{r}\|^2$.) Recalling that

$$f(\mathbf{x}) - f(\mathbf{z}) = \frac{1}{2}(\mathbf{p}, A\mathbf{p}) = \frac{1}{2}(D^{-1}\mathbf{y}, \mathbf{y})$$

one has

$$\frac{1}{2\lambda_{max}}\|\mathbf{r}\|^2 \le f(\mathbf{x}) - f(\mathbf{z}) \le \frac{1}{2\lambda_{min}}\|\mathbf{r}\|^2$$

which completes the proof.

We can get a complete picture of what's really happening in this method by considering a simple example. Suppose we wish to solve

$$A\mathbf{x} = \mathbf{h} \tag{11.31}$$

where $A = \text{diag}(10, 1)$ and $\mathbf{h} = (1, -1)$. If we start the steepest descent iterations with $\mathbf{x}_0 = (0, 0)$ then the first few residuals vectors are: $(1, -1)$, $(-9/11, -9/11)$, $(81/121, 81/121)$ and so on. In general the even residuals are proportional to $(1, -1)$ and the odd ones are proportional to $(-1, -1)$. The coefficients are $(9/11)^n$, so the norm of the residual vector at the $i$-th step is $\mathbf{r}_i = \sqrt{2}(9/11)^i$. If the matrix were $A = \text{diag}(100, 1)$ instead, the norm of the $i$-th residual would be $\mathbf{r}_i = \sqrt{2}(99/101)^i$: steepest descent would be very slow to converge.

This can be seen graphically from a plot of the solution vector as a function of iteration superposed onto a contour plot of the quadratic form associated with the matrix $A$, shown in Figure (11.1).

It is not a coincidence that the residuals at each step of steepest descent are orthogonal to the residuals before and after. We can prove this generally:

$$\mathbf{r}_k = \mathbf{h} - A\mathbf{x}_k \tag{11.32}$$

$$= \mathbf{h} - A(\mathbf{x}_{k-1} + \alpha_k\mathbf{r}_{k-1}) \tag{11.33}$$

$$= \mathbf{r}_{k-1} - \alpha_k A\mathbf{r}_{k-1}. \tag{11.34}$$

1