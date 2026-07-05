164

Iterative Linear Solvers

- The inner product of two vectors.
- The sum of a vector and a scalar times a vector.

Since most of the calculation in $CG$ will be taken up by the matrix-vector products, it is ideally suited for use on sparse matrices. Whereas a dense matrix-vector inner product takes $O(n^2)$ floating point operations, if the matrix is sparse, this can be reduced to $O(nzero)$, where $nzero$ is the number of nonzero matrix elements.

To close this section a number of related details for the $CD$ and $CG$ algorithms will be shown.

# Lemma 4

$$(\mathbf{r}_i, \mathbf{p}_j) = 0 \quad \text{for } 0 \le j < i \le n \tag{11.44}$$

$$(\mathbf{r}_i, \mathbf{p}_i) = (\mathbf{r}_i, \mathbf{r}_i) \quad \text{for } i \le n \tag{11.45}$$

$$(\mathbf{r}_i, \mathbf{r}_j) = 0 \quad \text{for } 0 \le i < j \le n \tag{11.46}$$

$$-\frac{(\mathbf{r}_{k+1}, A\mathbf{p}_k)}{(\mathbf{p}_k, A\mathbf{p}_k)} = \frac{(\mathbf{r}_{k+1}, \mathbf{r}_{k+1})}{(\mathbf{r}_k, \mathbf{r}_k)} \tag{11.47}$$

$$\frac{(\mathbf{p}_k, \mathbf{r}_k)}{(\mathbf{p}_k, A\mathbf{p}_k)} = \frac{(\mathbf{r}_k, \mathbf{r}_k)}{(\mathbf{p}_k, A\mathbf{p}_k)} \tag{11.48}$$

Proof. (11.44), (11.45), and (11.46) are by induction on $n$. (11.47) and (11.48) then follow immediately from this. Details are left as an exercise. Equation (11.45) arises interestingly if we ask under what circumstances the conjugate gradient residual is exactly zero. It can be shown that $\mathbf{r}_{i+1} = 0$ if and only if $(\mathbf{r}_i, \mathbf{p}_i) = (\mathbf{r}_i, \mathbf{r}_i)$.

As a final consideration, notice that although the gradient algorithms guarantee that the error $\| \mathbf{z} - \mathbf{x}_k \|$ is reduced at each iteration, it is not the case that the residual $\| \mathbf{h} - A\mathbf{x}_k \|$ is also reduced. Of course, the overall trend is for the residual to be reduced, but from step to step, relatively large fluctuations may be observed. There are several generalizations of the basic Hestenes-Stiefel $CG$ algorithm, known as residual reducing methods, which are guaranteed to reduce the residual at each step. For more details see Paige and Saunders [PS82] and Chandra [Cha78].

### 11.2.7 Finite Precision Arithmetic

The exact convergence implied by the Conjugate Direction Theorem is never achieved in practice with $CG$ since the search vectors are computed recursively and tend to loose their A-orthogonality with time. $CD$ methods were originally conceived as being "direct" in the sense of yielding the "exact" solution after a finite sequence of steps,

1