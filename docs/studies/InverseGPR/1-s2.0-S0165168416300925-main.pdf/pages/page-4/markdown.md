M. Sun et al. / Signal Processing 132 (2017) 272–283

275

Table 1

RMSE on curve fitting with Gaussian and exponential functions.

|  RMSE %(s₁/s₂) Frequency | Model | |s(f)| = sₖ × exp(-b̄f) | s(f)| = sₖ × exp(-bf²)  |
| --- | --- | --- | --- | --- | --- | --- |
|  [0.5, 1.5] | GHz | 0.0290/0.371 | 0.0307/0.179  |
|  [0.5, 2.5] | GHz | 0.0906/1.04 | 0.0433/0.257  |
|  [0.5, 3.5] | GHz | 0.171/1.94 | 0.0605/0.324  |
|  [0.5, 6.5] | GHz | 0.463/5.63 | 0.170/0.346  |
|  [0.5, 8.5] | GHz | 0.698/7.99 | 0.270/0.355  |
|  [0.5, 10.5] | GHz | 0.983/9.88 | 0.367/0.323  |

results of the Gaussian and exponential functions. It can be noticed that, the Gaussian fitting is generally in good agreement with radar data in the whole frequency band, but for the exponential fitting, significant deviations can be found, particularly for large frequency bands. We assess the performance of the curve fitting by Root Means Square Errors (RMSE), as shown in Table 1. The results are in agreement with the above figures, the Gaussian fitting is more precise than the exponential fitting.

### 3. Signal model

In the previous section, the frequency behaviour of interface roughness has been studied by using PILE method. In this paper, we focus on the first two or three top layers of roadway, the whole thickness (of the roadway) is about 6–13 cm. Indeed, in our study, we focus on pavements which are composed of an UTAS (1–3 cm thickness) and a base course (5–10 cm thickness). For pavement materials, according to the data provided in [28], the conductivity usually ranges within the interval [10⁻³; 10⁻²] S/m. Thus, the media considered in this paper are assumed to be low-loss media. Moreover, the pavement permittivity remains constant within the GPR bandwidth and generally ranges between 4 and 8. Thus, the considered media are low-loss and non-dispersive media. In addition, the dispersivity of the medium can be neglected [29], if the surface medium is slightly lossy. For flat pavements, the backscattered echoes can be simply considered as time-shifted and attenuated copies of the transmitted signal [9,12,21,30]. For a rough pavement, a new signal model is presented with roughness for non-dispersive media and without considering the conductivity as follows:

$$r(f_i) = \sum_{k=1}^{K} e(f_i) s_k w_k(f_i) \exp(-j2\pi f_i t_k) + n(f_i) \tag{1}$$

where

- K is the number of interfaces;
- e(fᵢ) is the radar pulse at frequency fᵢ;
- sₖ represents the reflection coefficient of the kth scattered echo with flat interfaces, which is independent of fᵢ;
- n(fᵢ) is an additive white Gaussian noise, with zero mean and variance σ²;
- wₖ(fᵢ) represents the frequency behaviour of the kth scattered echo at frequency fᵢ = f₁ + (i - 1)Δf and i = 1, 2...N, N being the number of used frequencies; f₁ is the lowest frequency of the studied frequency band and Δf is the frequency step.

Eq. (1) can be written in the following vector form:

$$\mathbf{r} = \mathbf{A}\mathbf{A}\mathbf{s} + \mathbf{n} \tag{2}$$

with the following notation definitions:

- r = [r(f₁)r(f₂)...r(fₙ)]ᵀ is the (N × 1) received signal vector, called observation vector, which may represent either the Fourier transform of the GPR signal or the measurements from a step frequency radar; the superscript T denotes the transpose operator;
- Λ = diag(e(f₁), e(f₂), ..., e(fₙ)) is a (N × N) diagonal matrix, whose diagonal elements are the Fourier transform e(f) of the radar pulse e(t);
- A = [a(t₁)a(t₂)... a(tₖ)] is called the (N × K) mode matrix;
- a(tₖ) = [exp(-2jσf₁tₖ)wₖ(f₁)exp(-2jσf₂tₖ)wₖ(f₂)...exp(-2jσfₙtₖ)wₖ(fₙ)]ᵀ is the mode vector;
- s = [s₁s₂...sₖ]ᵀ is the (K × 1) vector of echoes amplitudes in the case of flat interfaces;
- n = [n(f₁)n(f₂)...n(fₙ)]ᵀ is the (N × 1) noise vector, with variance matrix σ²I;

According to signal model (2) and assuming that the noise is independent of the echoes, the covariance matrix Y can be written as:

$$\begin{array}{l} \mathbf{Y} = E(\mathbf{r}\mathbf{r}^H) = \mathbf{A}\mathbf{A}E(\mathbf{s}\mathbf{s}^H)\mathbf{A}^H\mathbf{A}^H + E(\mathbf{n}\mathbf{n}^H) \\ = \mathbf{A}\mathbf{A}\mathbf{S}\mathbf{A}^H\mathbf{A}^H + \sigma^2\mathbf{I} \tag{3} \end{array}$$

where E(·) denotes the ensemble average, S is the K × K dimensional covariance matrix of the source vector s and I is an identity matrix. In the following, the data are divided by the pulse, thus the new observation vector r' can be written as r' = Λ⁻¹r = As + Λ⁻¹n = As + b, where b is the new noise vector after division. Thus, the new covariance matrix R₀ can be written as:

$$\mathbf{R}_0 = E(\mathbf{r}\mathbf{r}^H) = \mathbf{A}^{-1}\mathbf{Y}\mathbf{A}^{-H} = \mathbf{A}\mathbf{S}\mathbf{A}^H + \sigma^2\mathbf{S} \tag{4}$$

with

$$\mathbf{S} = \mathbf{A}^{-1}\mathbf{A}^{-H} = diag\left(\frac{1}{|e(f_1)|^2}, \frac{1}{|e(f_2)|^2}, \dots, \frac{1}{|e(f_N)|^2}\right) \tag{5}$$

In practice, the correlation between echoes degrades the subspace algorithm's performance. In this situation, preprocessing methods like spatial smoothing technique are used to obtain a new covariance matrix of restored rank. This kind of techniques only works on uniform linear frequency behaviours [31]. As the frequency behaviour of backscattered echoes w(f) can have an arbitrary frequency behaviour, methods like spatial smoothing technique cannot be used directly. In order to solve this problem, we propose to interpolate the frequency behaviour of backscattered echoes into a uniform linear. Then, the spatial smoothing technique can be applied. This kind of algorithms is called interpolated spatial smoothing technique [32,33]. By using interpolation, a new covariance matrix can be written as follows:

$$\mathbf{R} = \mathbf{B}\mathbf{A}\mathbf{S}\mathbf{A}^H\mathbf{B}^H + \sigma^2\mathbf{B}\mathbf{S}\mathbf{B}^H \tag{6}$$