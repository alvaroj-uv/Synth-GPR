184

More on the Resolution-Variance Tradeoff

In practice this sum will usually be truncated at a finite number of terms. For infinite dimensional vectors it is more traditional to write the inner product as $(\mathbf{m}, \mathbf{h}(\mathbf{r}))$ but we will continue to use the dot notation.

A basic tool of BG theory is **the point spread function** $A$. The point spread function (PSF) is defined in a formal manner by noting that a local average of the model $m(\mathbf{r})$ can be obtained at any point $\mathbf{r}_0$ by integrating the model and a locally defined unimodular function

$$\langle m(\mathbf{r}_0) \rangle = \int_\Omega A(\mathbf{r}, \mathbf{r}_0) m(\mathbf{r}) d^D\mathbf{r}. \quad (12.3)$$

Unimodular means that the function integrates to 1.

$$\int_\Omega A(\mathbf{r}, \mathbf{r}_0) d^D\mathbf{r} = 1.$$

Also, it is assumed that $A(\mathbf{r}, \mathbf{r}_0) \in \mathcal{M}$ for each $\mathbf{r}_0 \in \Omega$ and that the support of $A$ is concentrated at the point $\mathbf{r}_0$. Naturally, the more accurately the model is determined at each point, the more closely the PSF resembles a delta function – at that point. So estimating the PSF is equivalent to estimating a local average of the model. The more delta function-like is the PSF, the more precise our estimate of the model.

Like any other function in $\mathcal{M}$, the PSF can be expanded in terms of $h_i$.

$$A(\mathbf{r}, \mathbf{r}_0) = \sum_{i=1}^\infty a_i(\mathbf{r}_0) h_i(\mathbf{r}) \equiv \mathbf{a}(\mathbf{r}_0) \cdot \mathbf{h}(\mathbf{r}).$$

Thus (12.2) and (12.3) imply that

$$\langle m(\mathbf{r}_0) \rangle = \sum_{i=1}^\infty a_i(\mathbf{r}_0) m_i = \mathbf{a}(\mathbf{r}_0) \cdot \mathbf{m}. \quad (12.4)$$

It is clear that one can construct a PSF which will yield a local average of the model – any approximation to a delta function will do. Unfortunately, there is a tradeoff between the sharpness of the PSF and the variance, or RMS error, of the solution. To show this, BG assume that the local average of the model is a linear function of the data

$$\langle m(\mathbf{r}_0) \rangle = \sum_{i=1}^n b_i(\mathbf{r}_0) d_i = \mathbf{b}(\mathbf{r}_0) \cdot \mathbf{d} = (\mathbf{b}(\mathbf{r}_0), A\mathbf{m} + \mathbf{e}) \quad (12.5)$$

where $\mathbf{b}$ is to be determined. For the moment let's neglect the noise–for zero mean noise we can just take expectations. Comparing (12.4) and (12.5) one sees that the expansion coefficients of the PSF are simply

$$\mathbf{a}(\mathbf{r}_0) = A^T \mathbf{b}(\mathbf{r}_0) \quad (12.6)$$

Now, how one measures the “width” of the PSF is largely a matter of taste. Nolet [Nol85] makes the following natural choice

$$W(\mathbf{r}_0) = c_D \int_\Omega A(\mathbf{r}, \mathbf{r}_0)^2 |\mathbf{r} - \mathbf{r}_0|^{D+1} d^D\mathbf{r}$$

1