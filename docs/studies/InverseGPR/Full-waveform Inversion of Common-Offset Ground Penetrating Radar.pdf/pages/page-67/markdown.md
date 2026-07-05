This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

2

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING

reflectivity series iteratively while removing any constraints on the phase of the wavelet. The optimization problem in this paper is nonlinear when we consider both reflectivity series and the wavelet as unknowns. However, if we fix the wavelet, the cost function will be linear with regards to the reflectivity series and vice versa. There are nonlinear algorithms that aim at finding the global solution of the original problem; however, nonlinear algorithms are computationally expensive. Instead, we solve the cost function in an alternating fashion, which allows us to use fast and efficient solvers. The drawback is that the algorithm is a local minimization technique and, therefore, requires a proper initial model. To remedy this shortcoming, we carefully capture an initial wavelet estimate from the data (this initial estimate is improved upon in the optimization process). The selection of parameters required for the inversion is automated. The blind recovery of the reflectivity series and wavelet is found to be stable on a range of synthetic and field data scenarios. The examples selected to show in this paper focus on distinct cylindrical sources, such as pipes and roots, in a soil background. In these scenarios, the proposed method provides a higher resolution reflectivity series than Wiener deconvolution and appears to be more stable in the presence of noise.

We begin this paper with the larger context for this paper, introducing convolution, deconvolution, and blind deconvolution models. Within this framework, our method is detailed and then tested on both synthetic and field data.

### A. Convolution Model

The impulse response of the earth can be modeled as a linear time-invariant system [28]. In geophysics, the impulse response is called the reflectivity series. Assuming a stationary blurring kernel, the recorded GPR data at the surface are defined as the convolution of the blurring kernel with the impulse response of the earth. The blurring kernel refers to an imperfection of the system (low-pass filter), which results in lowering the resolution of the recorded data. If we assume that the blurring kernel does not change through time, it is called a stationary blurring kernel. In different fields of study, this imperfection is defined as the blurring kernel, source signature, source wavelet, point spread function, wavelet, and so on. In the geophysics community, this low-pass filter comes from the source wavelet which is band-limited, and when it is convolved with the reflectivity series, it lowers the resolution of the data. In this paper, we will call this blurring kernel the source wavelet or wavelet for short. The input-output relationship for this system can be written as follows:

$$
d_j[n] = \sum_k w[n-k] r_j[k] + e_j[n], \quad j = 1, 2, \dots J \tag{1}
$$

where the GPR data in the trace $j$ are given by $\mathbf{d}_j = (d_j[0], d_j[1], \dots, d_j[N-1])^T$. Similarly, the impulse response for trace $j$ is given by $\mathbf{r}_j = (r_j[0], r_j[1], \dots, r_j[M-1])^T$, $\mathbf{e}_j = (e_j[0], e_j[1], \dots, e_j[N-1])^T$ is the additive noise term, and the stationary GPR wavelet is $\mathbf{w} = (w[0], w[1], \dots, w[L-1])^T$, and $T$ stands for transpose operator. We stress that $N = M + L - 1$. In matrix vector notation,

(1) can be cast as

$$
\mathbf{d}_j = \mathbf{W} \mathbf{r}_j + \mathbf{e}_j, \quad j = 1, 2, \dots J \tag{2}
$$

where $\mathbf{W}$ is the convolution matrix built from the wavelet. To be more specific, the matrix $\mathbf{W}$ has a Toeplitz structure with entries

$$
\mathbf{W} = \begin{pmatrix}
w(0) & & & & \\
w(1) & w(0) & & & \\
w(2) & w(1) & w(0) & & \\
& \vdots & & \ddots & \\
& & & w(L-1) & w(L-2) \\
& & & & w(L-1)
\end{pmatrix}. \tag{3}
$$

We would also like to remind the readers that using commutative property of convolution, (2) is equivalent to

$$
\mathbf{d}_j = \mathbf{R}_j \mathbf{w} + \mathbf{e}_j, \quad j = 1, 2, \dots J \tag{4}
$$

where $\mathbf{R}_j$ is the convolution matrix built from the reflectivity series of channel $j$ with proper dimensions.

### B. Deconvolution Model

1) *Deconvolution to Estimate the Reflectivities*: Deterministic deconvolution can be used to remove the effect of the wavelet from the data if the wavelet is known. In some rare cases, the signature of the source is known, as, for example, if the source is fully controlled. In other cases, the wavelet can be estimated from the data. This is done, for example, in marine seismic by averaging the signature of the ocean bottom reflector [29]. Assuming that the wavelet is known *a priori*, the idea is to design a filter $\mathbf{f}_w$ such that when applied to the data, the output would represent the reflectivity series

$$
\mathbf{r} = \mathbf{F}_w \mathbf{d} \tag{5}
$$

where $\mathbf{d} = [\mathbf{d}_1^T, \mathbf{d}_2^T, \dots, \mathbf{d}_N^T]^T$, $\mathbf{F}_w$ is the convolution matrix built from $\mathbf{f}_w$, and $\mathbf{r} = [\mathbf{r}_1^T, \mathbf{r}_2^T, \dots, \mathbf{r}_J^T]^T$ is the estimated reflectivity series. Ideally, $\mathbf{F}_w$ should be the inverse of $\mathbf{H}$ where $\mathbf{H}$ is a block diagonal matrix with $J$ blocks each block being equal to $\mathbf{W}$. Unfortunately, the $\mathbf{H}$ matrix is not invertible. The simplest solution for inverting the $\mathbf{H}$ matrix is the Wiener deconvolution method, which is the solution to

$$
\mathbf{r} = \underset{\mathbf{r}}{\operatorname{argmin}} \|\mathbf{H}\mathbf{r} - \mathbf{d}\|_2^2. \tag{6}
$$

Equation (6) is a convex optimization problem and has a closed-form solution

$$
\mathbf{r} = (\mathbf{H}^T \mathbf{H})^{-1} \mathbf{H}^T \mathbf{d}. \tag{7}
$$

Comparing (5) and (7) implies that $\mathbf{F}_w = (\mathbf{H}^T \mathbf{H})^{-1} \mathbf{H}^T$. To estimate a physically plausible reflectivity series, we could also incorporate more information about the reflectivity series into (6)

$$
\mathbf{r} = \underset{\mathbf{r}}{\operatorname{argmin}} \|\mathbf{H}\mathbf{r} - \mathbf{d}\|_2^2 + \lambda_r \mathcal{R}(\mathbf{r}) \tag{8}
$$

where $\mathcal{R}(\mathbf{r})$ is a regularization term that enhances some desired features in the reflectivity series and $\lambda_r$ is a regularization parameter that balances the importance of data fidelity and priori information about the reflectivity series.

57