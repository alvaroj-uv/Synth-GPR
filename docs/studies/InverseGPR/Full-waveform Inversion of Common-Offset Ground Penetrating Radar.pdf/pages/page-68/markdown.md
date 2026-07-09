This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

JAZAYERI et al.: SBD OF GPR DATA

3

2) Deconvolution to Estimate the Wavelet: In a process analogous to Section I-B.1, deterministic deconvolution can be used to remove the effect of the reflectivity series from the data, if the reflectivity series is known. This can be done at well locations, where well logs are used to generate the reflectivity series [30], [31]. The generated reflectivity series are then used to estimate the waveform. The result can serve as a global waveform for further types of modeling or as an input to an FWI workflow. In GPR, a well-known approach is to estimate the subsurface reflectivity series by performing ray-based inversion. The estimated reflectivity equivalent structure (which is used in the same manner as well data for seismic) is then deconvolved from the collected data to estimate the wavelet [14]–[16]. In this case, deconvolution simply is done by finding a filter $\mathbf{f}_r$ such that when applied to the data, the output would represent the wavelet

$$\mathbf{w} = \mathbf{F}_r \mathbf{d} \tag{9}$$

where $\mathbf{F}_r$ is the convolution matrix built from $\mathbf{f}_r$ and $\mathbf{w}$ is the estimated wavelet. Ideally, $\mathbf{F}_r$ should be the inverse of $\mathbf{R}$ where $\mathbf{R}$ is a matrix with entries

$$\mathbf{R} = \begin{pmatrix} \mathbf{R}_1 \\ \mathbf{R}_2 \\ \mathbf{R}_3 \\ \vdots \\ \mathbf{R}_{J-1} \\ \mathbf{R}_J \end{pmatrix}. \tag{10}$$

The $\mathbf{R}$ matrix is not invertible, so the simplest solution for inverting the matrix is the Wiener deconvolution method, which is the solution to

$$\mathbf{w} = \underset{\mathbf{w}}{\operatorname{argmin}} \|\mathbf{R}\mathbf{w} - \mathbf{d}\|_2^2. \tag{11}$$

Equation (11) is a convex optimization problem and has a closed-form solution

$$\mathbf{w} = (\mathbf{R}^T \mathbf{R})^{-1} \mathbf{R}^T \mathbf{d}. \tag{12}$$

Comparing (9) and (12) implies that $\mathbf{F}_r = (\mathbf{R}^T \mathbf{R})^{-1} \mathbf{R}^T$. To estimate a physically plausible wavelet, we also incorporate more information about the wavelet into (11)

$$\mathbf{w} = \underset{\mathbf{w}}{\operatorname{argmin}} \|\mathbf{R}\mathbf{w} - \mathbf{d}\|_2^2 + \lambda_w \mathcal{R}(\mathbf{w}) \tag{13}$$

where $\mathcal{R}(\mathbf{w})$ is a regularization term which enhances some desired features in the estimated wavelet and $\lambda_w$ is a regularization parameter that balances the importance of data fidelity and the knowledge of the wavelet.

3) Blind Deconvolution: If neither the signature of the wavelet nor the subsurface reflectivity structure is known, the problem is a so-called blind deconvolution problem [23], [24], [32]. This is, of course, a common real-world scenario, and thus, there are many reasons that blind deconvolution solutions are desirable. Even when borehole data are used to build reflectivity series, large data gaps remain between boreholes, and the larger reflectivity structure is incompletely known. Ray-based inversion to obtain geometry of subsurface reflectors can be inaccurate since it uses only the first arrival times of the diffracted pulses, a very small portion of the total

recorded signal. The ray-based inversion process itself can be time-consuming. Finally, errors in the ray-based results (or any reflectivity structure) will harm estimates of the wavelet. In the real world, the signature of a GPR wavelet is generally unknown and affected not only by the instrument but also by coupling between antenna and soil, and soil electrical characteristics that are, in turn, influenced by soil moisture content. For FWI, which better uses the total recorded signal, knowledge of the wavelet becomes extremely important. Any error in the phase or the amplitude of the wavelet propagates into the FWI subsurface characterization. To address this common scenario, namely, lack of a priori knowledge about both the wavelet and subsurface reflectivity structure, blind deconvolution formulates the problem in such a way that it simultaneously solves for the wavelet and the reflectivity series.

The general cost function in our blind deconvolution problem is defined as

$$\{\mathbf{w}, \mathbf{r}\} = \underset{\mathbf{w}, \mathbf{r}}{\operatorname{argmin}} \|\mathbf{H}\mathbf{r} - \mathbf{d}\|_p^p + \lambda_r \mathcal{R}(\mathbf{r}) + \lambda_w \mathcal{R}(\mathbf{w}) \tag{14}$$

where $p > 0$, $\lambda_w, \lambda_r > 0$, $\|\mathbf{a}\|_p^p = \sum_{i=1}^N |a_i|^p$ with $\mathbf{a} = [a_1, a_2, \dots, a_{N-1}, a_N]^T$, and $\|\mathbf{H}\mathbf{r} - \mathbf{d}\|_p^p$ is a closed convex function.

# C. Problem Statement and the Proposed Approach

In this writeup, we assume that an added noise term in the data has a Gaussian distribution and the subsurface reflectivity series can be cast as a sparse series (i.e., few reflectors that in the GPR case could represent any anomaly that reflects energy). The sparse reflectivity assumption is valid for layered media and shows promising performance in the context of the deconvolution problem [2], [20], [23], [24], [33]. We also assume that the wavelet is a smooth function. After incorporating these assumptions into (14), we have

$$\{\mathbf{w}, \mathbf{r}\} = \underset{\mathbf{w}, \mathbf{r}}{\operatorname{argmin}} \|\mathbf{H}\mathbf{r} - \mathbf{d}\|_2^2 + \lambda_r \|\mathbf{r}\|_1 + \lambda_w \|\mathbf{w}\|_2^2 \tag{15}$$

and we remind the reader that (15) is equal to

$$\{\mathbf{w}, \mathbf{r}\} = \underset{\mathbf{w}, \mathbf{r}}{\operatorname{argmin}} \|\mathbf{R}\mathbf{w} - \mathbf{d}\|_2^2 + \lambda_r \|\mathbf{r}\|_1 + \lambda_w \|\mathbf{w}\|_2^2. \tag{16}$$

Equation (15) is solved with an alternating minimization technique. First, we solve for reflectivity series by fixing the wavelet, simplifying (15) to

$$\mathbf{r} = \underset{\mathbf{r}}{\operatorname{argmin}} \|\mathbf{H}\mathbf{r} - \mathbf{d}\|_2^2 + \lambda_r \|\mathbf{r}\|_1 \tag{17}$$

which is an $\ell_2 - \ell_1$ problem and can be solved with any $\ell_2 - \ell_1$ solvers, such as unconstrained basis pursuit denoising (UBPDN) via alternating split Bregman algorithms [2], [34], [35], Euclid in a Taxicab $\ell_1/\ell_2$ regularization [36], majorization-minimization optimization [37], alternating minimization [1], and gradient projection [38]. In this paper, we use the UBPDN solved with the alternating split Bregman algorithm to estimate the sparse reflectivity structure.

The next step is to estimate the wavelet by fixing the reflectivity series. In this case, (15) or equivalently (16)

58