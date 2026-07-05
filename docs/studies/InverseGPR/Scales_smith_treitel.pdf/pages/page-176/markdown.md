11.2 Conjugate Gradient

161

So, provided the scale factors $\alpha_k$ satisfy the last equation, one is guaranteed to minimize the residual along the search vector $\mathbf{p}_k$. The conditions necessary for the search vectors are given by the following theorem.

**Theorem 14 Conjugate Direction Theorem** *Suppose that the search vectors are chosen such that $(\mathbf{p}_i, A\mathbf{p}_j) = 0$ if $i \neq j$ (A-orthogonality), then the CD method converges to the exact solution in at most $n$ steps.*

**Proof.** Using the $CD$ iteration

$$\mathbf{x}_k = \mathbf{x}_{k-1} + \alpha_k \mathbf{p}_{k-1}, \qquad k = 1, 2, \dots$$

one has by induction

$$\mathbf{x}_k - \mathbf{x}_0 = \alpha_1 \mathbf{p}_0 + \alpha_2 \mathbf{p}_1 + \dots + \alpha_k \mathbf{p}_{k-1}$$

for any $\mathbf{x}_0$ chosen. Since the $\mathbf{p}$ vectors are A-orthogonal, it follows that

$$(\mathbf{p}_k, A(\mathbf{x}_k - \mathbf{x}_0)) = 0.$$

The A-orthogonality also implies that the $\mathbf{p}$ vectors must be linearly independent. Thus any vector in $\mathbf{R}^n$ can be represented as an expansion in the $\{\mathbf{p}_k\}_{k=0}^{n-1}$. In particular, the unknown solution $\mathbf{z}$ of the linear system can be written

$$\mathbf{z} = \gamma_0 \mathbf{p}_0 + \dots + \gamma_{n-1} \mathbf{p}_{n-1}.$$

Taking the inner product of this equation with first $A$ and then $\mathbf{p}_i$, and using the A-orthogonality gives

$$(\mathbf{p}_i, A\mathbf{z}) = \gamma_i (\mathbf{p}_i, A\mathbf{p}_i) \Rightarrow \gamma_i = \frac{(\mathbf{p}_i, A\mathbf{z})}{(\mathbf{p}_i, A\mathbf{p}_i)}.$$

The idea of the proof is to show that these numbers, namely the $\gamma_i$, are precisely the coefficients of the $CD$ algorithm; that would automatically yield convergence since by proceeding with $CD$ we would construct this expansion of the solution. Just as an arbitrary vector $\mathbf{x}$ can be expanded in terms of the linearly independent search vectors, so can $\mathbf{z} - \mathbf{x}_0$ where $\mathbf{x}_0$ is still the initial approximation. Thus,

$$\mathbf{z} - \mathbf{x}_0 = \sum_{i=0}^{n-1} \frac{(\mathbf{p}_i, A(\mathbf{z} - \mathbf{x}_0))}{(\mathbf{p}_i, A\mathbf{p}_i)} \mathbf{p}_i \equiv \sum_{i=0}^{n-1} \xi_i \mathbf{p}_i \tag{11.38}$$

where

$$\xi_k = \frac{(\mathbf{p}_k, A(\mathbf{z} - \mathbf{x}_0))}{(\mathbf{p}_k, A\mathbf{p}_k)}. \tag{11.39}$$

1