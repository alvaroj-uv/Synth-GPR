156

Iterative Linear Solvers

**Lemma 3** *For some choice of a constant $\alpha$*

$$f(\mathbf{x}) = f(\mathbf{x} + 2\alpha\mathbf{r}) \tag{11.25}$$

$$f(\mathbf{x} + \alpha\mathbf{r}) - f(\mathbf{x}) \leq 0 \tag{11.26}$$

*where $\mathbf{r}$ is the residual vector and $\mathbf{x}$ is arbitrary.*

In other words, there exists a constant $\alpha$ such that by moving by an amount $2\alpha$ along the residual, one ends up on the other side of the ellipsoid $f(\mathbf{x}) = constant$. And further, if one moves to the midpoint of this line, one is assured of being closer to (or at the very least, not farther away from) the global minimum. The proof of this assertion is by construction. From the definition of $f$ one has for arbitrary $\mathbf{x}, \alpha$

$$\begin{aligned} f(\mathbf{x} + 2\alpha\mathbf{r}) &= \frac{1}{2}((\mathbf{x} + 2\alpha\mathbf{r}), A(\mathbf{x} + 2\alpha\mathbf{r})) - (h, (\mathbf{x} + 2\alpha\mathbf{r})) + c \\ &= f(\mathbf{x}) + \frac{1}{2}\{(2\alpha\mathbf{r}, A\mathbf{x}) + (2\alpha\mathbf{r}, A2\alpha\mathbf{r}) + (\mathbf{x}, A2\alpha\mathbf{r})\} - (\mathbf{h}, 2\alpha\mathbf{r}) \\ &= f(\mathbf{x}) + 2\alpha(\mathbf{r}, A\mathbf{x}) + 2\alpha^2(\mathbf{r}, A\mathbf{r}) - 2\alpha(\mathbf{h}, \mathbf{r}) \\ &= f(\mathbf{x}) - 2\alpha(\mathbf{r}, \mathbf{r}) + 2\alpha^2(\mathbf{r}, A\mathbf{r}) \end{aligned}$$

using $A\mathbf{x} = \mathbf{h} - \mathbf{r}$.

Therefore, choosing $\alpha$ to be $(\mathbf{r}, \mathbf{r})/(\mathbf{r}, A\mathbf{r})$ implies that $f(\mathbf{x} + 2\alpha\mathbf{r}) = f(\mathbf{x})$. Repeating the argument for $f(\mathbf{x} + \alpha\mathbf{r})$ with the same choice of $\alpha$, one sees immediately that

$$f(\mathbf{x} + \alpha\mathbf{r}) = f(\mathbf{x}) - \frac{1}{2}\frac{(\mathbf{r}, \mathbf{r})^2}{(\mathbf{r}, A\mathbf{r})} \leq f(\mathbf{x})$$

which completes the proof for $A$ symmetric and positive definite.

This lemma provides all that is necessary to construct a globally convergent gradient algorithm for finding the solutions of symmetric, positive definite linear systems, or equivalently, finding the minima of positive definite quadratic forms. By globally convergent we mean that it converges for any starting value.

**Algorithm 4 Method of Steepest Descent** *Choose $\mathbf{x}_0$. This gives $\mathbf{r}_0 = \mathbf{h} - A\mathbf{x}_0$. Then for $k = 1, 2, 3, \dots*

$$\begin{aligned} \alpha_k &= (\mathbf{r}_{k-1}, \mathbf{r}_{k-1})/(\mathbf{r}_{k-1}, A\mathbf{r}_{k-1}), \\ \mathbf{x}_k &= \mathbf{x}_{k-1} + \alpha_k \mathbf{r}_{k-1} \\ \mathbf{r}_k &= \mathbf{h} - A\mathbf{x}_k \end{aligned} \tag{11.27}$$

Since it has already been shown that $f(\mathbf{x} + \alpha\mathbf{r}) \leq f(\mathbf{x})$ for any $\mathbf{x}$, it follows that

$$f(\mathbf{x}_0) \geq f(\mathbf{x}_1) \geq \dots \geq f(\mathbf{x}_k) \dots \tag{11.28}$$

1