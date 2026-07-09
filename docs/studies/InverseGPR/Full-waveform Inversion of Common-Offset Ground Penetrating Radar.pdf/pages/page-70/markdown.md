This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

JAZAYERI et al.: SBD OF GPR DATA

5

Equations (28) and (29) have closed-form solutions

$$\mathbf{r}^{k+1} = \mathbf{P}^{-1} \left( \alpha \mathbf{H}^T \mathbf{t}_1^k - \mathbf{g}_1^k + \mathbf{y} + \beta \mathbf{t}_2^k - \mathbf{g}_2^k \right) \tag{31}$$

and

$$\mathbf{t}_1^{k+1} = \frac{\mathbf{H} \mathbf{r}^{k+1} - \mathbf{y} + \mathbf{g}_1^k}{1 + \frac{\alpha}{\alpha}} \tag{32}$$

where $\mathbf{P} = \alpha \mathbf{H}^T \mathbf{H} + \beta \mathbf{I}$ and $\mathbf{I}$ is the identity matrix. Finally, in the case of (30), Goldstein and Osher argue that a single-iteration update is enough to approximate the solution. Accordingly, the single-iteration solution of (30) is defined as

$$\mathbf{t}_2^{k+1} = \text{prox}_{\frac{\alpha}{\alpha}} (\mathbf{r}^{k+1} + \mathbf{g}_2^k) \tag{33}$$

where prox is a proximity operator and is defined as $\text{prox}_r(\mathbf{a}) = \text{sign}(\mathbf{a}) \odot \max(|\mathbf{a}| - r, 0)$ and $\odot$ is the Hadamard product. At this point by using (31)–(33) along with (26) and (27), we finalize the alternating split Bregman algorithm (Algorithm 1).

Algorithm 1 Alternating Split Bregman Algorithm as a Minimizer of 24 in the Time Domain

Require: d, H, $\lambda_r$, $\alpha$, $\beta$
Initialize: $k = 0, \mathbf{t}_1^0 = \mathbf{t}_2^0 = \mathbf{g}_1^0 = \mathbf{g}_1^0 = \mathbf{0}$
while $\|\mathbf{r}^k - \mathbf{r}^{k-1}\|_2^2 > tol$ do
$\mathbf{r}^{k+1} = \mathbf{P}^{-1} (\alpha \mathbf{H}^T [\mathbf{t}_1^k - \mathbf{g}_1^k + \mathbf{y}] + \beta [\mathbf{t}_2^k - \mathbf{g}_2^k])$
$\mathbf{t}_1^{k+1} = \frac{\mathbf{H} \mathbf{r}^{k+1} - \mathbf{y} + \mathbf{g}_1^k}{1 + \frac{\alpha}{\alpha}}$
$\mathbf{t}_2^{k+1} = \text{prox}_{\frac{\alpha}{\alpha}} (\mathbf{r}^{k+1} + \mathbf{g}_2^k)$
$\mathbf{g}_1^{k+1} = \mathbf{g}_1^k - [\mathbf{t}_1^{k+1} - (\mathbf{H} \mathbf{r}^{k+1} - \mathbf{y})]$
$\mathbf{g}_2^{k+1} = \mathbf{g}_2^k - [\mathbf{t}_2^{k+1} - \mathbf{r}^{k+1}]$
$k \leftarrow k + 1$
end while
return $\mathbf{r} = \mathbf{r}^k$

Algorithm 1 can efficiently solve (24). However, close inspection of the algorithm shows the matrix $\mathbf{P}$ has a block diagonal structure with each block being a Toeplitz matrix that can be diagonalized in the frequency domain. Accordingly, the update of $\mathbf{r}^{k+1}$ step can be formulated as a Wiener deconvolution in the frequency domain without any direct inversion of the $\mathbf{P}$ matrix. Hence, we formulate the alternating split Bregman algorithm in the frequency domain to decrease the computational cost of the algorithm. To do so, the Fourier equivalent of variables is defined as $\hat{\mathbf{w}} = \mathcal{F}\mathbf{w}$, $\hat{\mathbf{r}} = \mathcal{F}\mathbf{r}$, where $\mathcal{F}$ is a Fourier transform operator with $\mathcal{F}_{m,n} = \exp(-i2\pi mn/N)$, $i = -1, m, n = 0, 1, 2, \dots, N-1$, and the inverse Fourier transform is $\mathcal{F}^{-1} = (1/N)\mathcal{F}$, where indicates the complex conjugate. Using these Fourier pairs, we can write $\mathbf{H} = \mathcal{F}^{-1}\mathbf{H}_f\mathcal{F}$ where $\mathbf{H}_f$ is a diagonal matrix with $J$ matrices built from $\text{diag}(\hat{\mathbf{w}})$ where $\text{diag}(\cdot)$ reshapes the vector to a diagonal matrix. Now, we have all the ingredients to formulate the alternating split Bregman algorithm in the frequency domain (Algorithm 2).

2) Updating the Wavelet: To update the wavelet, we need to solve (18), which has the closed-form solution shown in (19). Equation (19) can also be solved in the frequency domain since

Algorithm 2 Alternating Split Bregman Algorithm as a Minimizer of 24 in the Frequency Domain

Require: d, $\mathbf{H}_f$, $\hat{\mathbf{w}}$, $\lambda_r$, $\alpha$, $\beta$
Define: $\mathbf{D} = \text{diag}(\frac{1}{\alpha(\|\mathbf{H}_f\|^2 + \beta)})$
Initialize: $k = 0, \mathbf{t}_1^0 = \mathbf{t}_2^0 = \mathbf{g}_1^0 = \mathbf{g}_1^0 = \mathbf{0}$
while $\|\hat{\mathbf{r}}^k - \hat{\mathbf{r}}^{k-1}\|_2^2 > tol$ do
$\hat{\mathbf{r}}^{k+1} = \mathbf{D} (\alpha \mathbf{H}_f \mathcal{F} [\mathbf{t}_1^k - \mathbf{g}_1^k + \mathbf{y}] + \beta \mathcal{F} [\mathbf{t}_2^k - \mathbf{g}_2^k])$
$\mathbf{t}_1^{k+1} = \frac{\mathcal{F}^{-1} \mathbf{H}_f \hat{\mathbf{r}}^{k+1} - \mathbf{y} + \mathbf{g}_1^k}{1 + \frac{\alpha}{\alpha}}$
$\mathbf{t}_2^{k+1} = \text{prox}_{\frac{\alpha}{\alpha}} (\mathcal{F}^{-1} \hat{\mathbf{r}}^{k+1} + \mathbf{g}_2^k)$
$\mathbf{g}_1^{k+1} = \mathbf{g}_1^k - [\mathbf{t}_1^{k+1} - (\mathcal{F}^{-1} \mathbf{H}_f \hat{\mathbf{r}}^{k+1} - \mathbf{y})]$
$\mathbf{g}_2^{k+1} = \mathbf{g}_2^k - [\mathbf{t}_2^{k+1} - \mathcal{F}^{-1} \hat{\mathbf{r}}^{k+1}]$
$k \leftarrow k + 1$
end while
return $\mathbf{r} = \mathbf{t}_2^k$

the matrix $\mathbf{R}$ has a Toeplitz structure and can be diagonalized in the frequency domain

$$\mathbf{w} = \mathcal{F}^{-1} \left[ \frac{J_{j-1}}{J_{j-1}} \hat{\mathbf{r}}_j \odot \hat{\mathbf{d}}_j \right] \tag{34}$$

where $\hat{\mathbf{r}} = J_{j-1} \hat{\mathbf{r}}_j \odot \hat{\mathbf{r}}_j$, $\odot$ is the Hadamard product, and $\hat{\mathbf{r}}_j$ and $\hat{\mathbf{d}}_j$ are the Fourier pairs of reflectivity and data in trace $j$, respectively.

### C. SBD Algorithm

After defining the initialization step and the main optimization workflow for updating the reflectivity series and the wavelet, we can finalize the SBD algorithm. We use the more efficient frequency domain methods. Algorithm 3 shows the steps.

Algorithm 3 SBD Algorithm

Require: d, L, $\lambda_r$, $\lambda_w$, $\alpha$, $\beta$
Define initial wavelet [using Algorithm initialization]: $\mathbf{w}^0$
k=0
while $\|\mathbf{H}\mathbf{r} - \mathbf{d}\|_2^2 > tol$ do
Update $\mathbf{H}^k$ using $\mathbf{w}^k$
Update reflectivity [using Algorithm 2]
$\mathbf{r}^{k+1} = \text{argmin} \|\mathbf{H}^k \mathbf{r} - \mathbf{d}\|_2^2 + \lambda_r \|\mathbf{r}\|_1$
Update $\mathbf{R}^{k+1}$ using $\mathbf{r}^{k+1}$
Update wavelet [using (34)]
$\mathbf{w}^{k+1} = \text{argmin} \|\mathbf{R}^{k+1} \mathbf{w} - \mathbf{d}\|_2^2 + \lambda_w \|\mathbf{w}\|_2^2$
$k \leftarrow k + 1$
end while
return $\mathbf{r} \leftarrow \mathbf{r}^k, \mathbf{w} \leftarrow \mathbf{w}^k$

### III. PARAMETER SELECTION

In this section, we describe our parameter selection strategies. The main parameters are length of wavelet $L$, regularization parameter for reflectivity update $\lambda_r$, and regularization

60