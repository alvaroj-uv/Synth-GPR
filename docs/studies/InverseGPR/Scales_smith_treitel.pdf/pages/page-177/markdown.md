162

Iterative Linear Solvers

It was shown above that $(\mathbf{p}_k, A(\mathbf{x}_k - \mathbf{x}_0)) = 0$. Therefore one can subtract

$$(\mathbf{p}_k, A(\mathbf{x}_k - \mathbf{x}_0)) / (\mathbf{p}_k, A\mathbf{p}_k)$$

from the expression for $\xi_k$ without changing it. Thus,

$$\begin{array}{rl} \xi_k & = \frac{(\mathbf{p}_k, A(\mathbf{z} - \mathbf{x}_0))}{(\mathbf{p}_k, A\mathbf{p}_k)} - \frac{(\mathbf{p}_k, A(\mathbf{x}_k - \mathbf{x}_0))}{(\mathbf{p}_k, A\mathbf{p}_k)} \\ & = \frac{(\mathbf{p}_k, A(\mathbf{z} - \mathbf{x}_k))}{(\mathbf{p}_k, A\mathbf{p}_k)} \\ & = \frac{(\mathbf{p}_k, \mathbf{r}_k)}{(\mathbf{p}_k, A\mathbf{p}_k)}. \end{array}$$

This is precisely the scale factor $\alpha_k$ used in the $CD$ iterations, which completes the proof. Thus we have

**Algorithm 5 Method of Conjugate Directions** *Choose $\mathbf{x}_0$. This gives $\mathbf{r}_0 = \mathbf{h} - A\mathbf{x}_0$. Let $\{\mathbf{p}_i\}_{i=1}^N$ be a set of $A$-orthogonal vectors. Then for $k = 1, 2, 3, \ldots$*

$$\alpha_k = (\mathbf{r}_{k-1}, \mathbf{r}_{k-1}) / (\mathbf{p}_{k-1}, A\mathbf{p}_{k-1}),$$

$$\mathbf{x}_k = \mathbf{x}_{k-1} + \alpha_k \mathbf{p}_{k-1} \tag{11.40}$$

$$\mathbf{r}_k = \mathbf{h} - A\mathbf{x}_k$$

The A-orthogonality can be seen to arise geometrically from the fact that the vector which points from the current location $\mathbf{x}$ to the global minimum of the quadratic form $\mathbf{z}$ must be A-orthogonal to the tangent plane of the quadratic form. To see this observe that since since the residual $\mathbf{r}$ must be normal to the surface, a tangent $\mathbf{t}$ must satisfy $(\mathbf{t}, \mathbf{r}) = 0$. Therefore $0 = (\mathbf{t}, A\mathbf{x} - \mathbf{h}) = (\mathbf{t}, A\mathbf{x} - A\mathbf{z}) = (\mathbf{t}, A\mathbf{p})$, where $\mathbf{p} = \mathbf{x} - \mathbf{z}$.

So far, all this shows is that if $n$ vectors, orthogonal with respect to the matrix $A$ can be found, then the conjugate direction algorithm will give solutions to the linear systems of the matrix. One can imagine applying a generalized form of Gram-Schmidt orthogonalization to an arbitrary set of linearly independent vectors. In fact Hestenes and Stiefel [HS52] show that A-orthogonalizing the $n$ unit vectors in $\mathbf{R}^n$ and using them in $CD$ leads essentially to Gaussian elimination. But this is no real solution since Gram-Schmidt requires $O(n^3)$ operations, and the search vectors, which will generally be dense even when the matrix is sparse, must be stored. The real advance to $CD$ was made by Hestenes and Stiefel, who showed that A-orthogonal search vectors could be computed on the fly. This is the conjugate gradient method.

### 11.2.6 The Method of Conjugate Gradients

Using the machinery that has been developed, it is a relatively easy task to describe the conjugate gradient ($CG$) algorithm as originally proposed by Hestenes and Stiefel

1