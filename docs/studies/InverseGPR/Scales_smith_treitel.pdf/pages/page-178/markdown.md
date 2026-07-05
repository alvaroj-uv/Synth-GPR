11.2 Conjugate Gradient

163

[HS52].$^{c}$ In going from steepest descent to conjugate directions, minimization along the residuals was replaced by minimization along the search vectors. So it makes sense to consider computing the search vectors iteratively from residuals. Suppose we make the *ansatz* $\mathbf{p}_0 = \mathbf{r}_0$ and

$$\mathbf{p}_{k+1} = \mathbf{r}_{k+1} + \beta_{k+1}\mathbf{p}_k. \tag{11.41}$$

Can the coefficients $\beta$ be chosen so as to guarantee the A-orthogonality of the $\mathbf{p}$ vectors? Using (11.41), one has

$$(\mathbf{p}_k, A\mathbf{p}_{k+1}) = (\mathbf{p}_k, A\mathbf{r}_{k+1}) + \beta_{k+1}(\mathbf{p}_k, A\mathbf{p}_k). \tag{11.42}$$

If one chooses

$$\beta_{k+1} = -\frac{(\mathbf{p}_k, A\mathbf{r}_{k+1})}{(\mathbf{p}_k, A\mathbf{p}_k)}$$

then the A-orthogonality is guaranteed. In Lemma 4 it will be shown that

$$\beta_{k+1} = -\frac{(\mathbf{r}_{k+1}, A\mathbf{p}_k)}{(\mathbf{p}_k, A\mathbf{p}_k)} = \frac{(\mathbf{r}_{k+1}, \mathbf{r}_{k+1})}{(\mathbf{r}_k, \mathbf{r}_k)}$$

As a final touch, notice that the residuals can be calculated recursively; by induction

$$\begin{aligned} \mathbf{r}_{k+1} &\equiv \mathbf{h} - A\mathbf{x}_{k+1} \\ &= \mathbf{h} - A(\mathbf{x}_k + \alpha_{k+1}\mathbf{p}_k) \\ &= (\mathbf{h} - A\mathbf{x}_k) - \alpha_{k+1}A\mathbf{p}_k \\ &= \mathbf{r}_k - \alpha_{k+1}A\mathbf{p}_k. \end{aligned}$$

The result of all this work is:

**Algorithm 6 Method of Conjugate Gradients** *Choose* $\mathbf{x}_0$. *Put* $\mathbf{p}_0 = \mathbf{r}_0 = \mathbf{h} - A\mathbf{x}_0$. *Then for* $k = 0, 1, 2, \dots$

$$\begin{aligned} \alpha_{k+1} &= \frac{(\mathbf{r}_k, \mathbf{r}_k)}{(\mathbf{p}_k, A\mathbf{p}_k)} \\ \mathbf{x}_{k+1} &= \mathbf{x}_k + \alpha_{k+1}\mathbf{p}_k \\ \mathbf{r}_{k+1} &= \mathbf{r}_k - \alpha_{k+1}A\mathbf{p}_k \\ \beta_{k+1} &= \frac{(\mathbf{r}_{k+1}, \mathbf{r}_{k+1})}{(\mathbf{r}_k, \mathbf{r}_k)} \\ \mathbf{p}_{k+1} &= \mathbf{r}_{k+1} + \beta_{k+1}\mathbf{p}_k \end{aligned} \tag{11.43}$$

The $\alpha$ coefficients are the same as in the *CD* algorithm, whereas the $\beta$ coefficients arise from the *CG ansatz*: $\mathbf{p}_0 = \mathbf{r}_0, \mathbf{p}_{k+1} = \mathbf{r}_{k+1} + \beta_{k+1}\mathbf{p}_k$. From a computational point of view, note the simplicity of the algorithm. It involves nothing more than:

- The inner product of a matrix and a vector; and only one per iteration since $A\mathbf{p}_k$ can be calculated once and stored.

$^{c}$The method was invented independently by M. Hestenes [Hes51] and E. Stiefel [Sti52], who later collaborated on the famous paper of 1952.

1