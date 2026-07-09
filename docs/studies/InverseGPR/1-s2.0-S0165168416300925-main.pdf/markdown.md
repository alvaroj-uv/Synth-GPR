Signal Processing 132 (2017) 272–283

Contents lists available at ScienceDirect

Signal Processing

journal homepage: www.elsevier.com/locate/sigpro

# Estimation of time delay and interface roughness by GPR using modified MUSIC

Meng Sun a, Cédric Le Bastard b,a, Nicolas Pinel c, Yide Wang a, Jianzhong Li a,d,* Jingjing Pan a, Zhiwen Yu d

a Institut d’ Electronique et Télécommunications de Rennes (IETR), LUNAM Université, Université de Nantes, UMR CNRS, 6164, Rue Christian Pauc, BP 50609, Nantes 44306, France

b Cerema (Centre for Expertise and Engineering on Risks, Environment, Mobility, Urban and Country Planning), 23 Avenue de l’Amiral Chauvin, BP 69, 49136 Les Ponts de Cé, France

c Alyotech, 2 Rue Antoine Becquerel, 35700 Rennes, France

d South China University of Technology, Guangzhou 510641, People’s Republic of China

ARTICLE INFO

Article history:

Received 29 January 2016

Received in revised form

11 April 2016

Accepted 28 May 2016

Available online 11 June 2016

Keywords:

Ground Penetrating Radar (GPR)

Time-Delay Estimation (TDE)

Roughness

Modified MUSIC

Method of Moments (MoM)

Maximum Likelihood method (MLE)

ABSTRACT

In civil engineering, roadway structure evaluation is an important application which can be carried out by ground penetrating radar. In this paper, firstly a signal model taking into account the influence of interfaces roughness (surface and interlayer) is proposed. In order to estimate the time delay and interface roughness, we propose a method composed of 2 steps: 1) a modified MUSIC algorithm is proposed for time delay estimation; 2) the interface roughness is estimated by using Maximum Likelihood method (MLE) with the estimated time delays. The proposed algorithms are tested on data obtained by a method of moments (MoM). Numerical examples are provided to demonstrate the performance of the proposed algorithm.

© 2016 Elsevier B.V. All rights reserved.

1. Introduction

Ground penetrating radar (GPR) is widely used as a non destructive testing technique for road pavement survey [1–6], particularly for the measurement of different layer thicknesses. In road pavement survey, the road layers are assumed to be horizontally stratified [7]. Useful information about the vertical structure of the roadway can then be extracted from radar profiles by means of echo detection and amplitude estimation [8–11]. Echo detection provides the time-delay estimation (TDE) associated with each interface, while amplitude estimation allows retrieving the wave speed within each layer. In this paper, we focus on the practical case when the backscattered echoes are overlapped [12,13], which means that the thickness is smaller than the wavelength in the medium. In this case, high resolution and super-resolution methods [14–17] (or subspace methods) can be used to estimate the time delays of echoes and then to measure the small pavement thicknesses (with estimated permittivity). However,

these methods assume that the interfaces of the layers are flat. For decimetre-scale GPR wavelengths (in the air), this assumption can be held, but for an ultra-wide band radar, this is no longer suitable. The influence of interface roughness and heterogeneous of medium must then be analysed [13,18,19]. In this paper, only the interface roughness is discussed. For large frequency bands, the case of a heterogeneous medium case can be considered as a homogeneous medium with an equivalent permittivity. The heterogeneity medium will be studied in future work. The interface roughness is characterized by a particular frequency signature of echoes amplitudes, which is decreasing with frequency. In this paper, we propose to firstly estimate the time delays and then the interface roughness with an ultra-wideband GPR. In the following, the media are assumed to be lossless [20,21]. Roughness parameter is important for road safety, like pavement skid resistance analysis, and for analysing the inside of the pavement, especially to detect the cracks or debondings by highlighting the disaggregation of interface materials.

In [19,20], this kind of work has already been carried out, but the frequency behaviour coming from the roughness has been simply approximated by an exponential function (using a curve fitting method). In this situation, the high resolution methods can easily be applied for parameters estimation (time delays and

* Corresponding author at: Institut d’ Electronique et Télécommunications de Rennes (IETR), LUNAM Université, Université de Nantes, UMR CNRS, 6164, Rue Christian Pauc, BP 50609, Nantes 44306, France.

E-mail address: jianzhong.li@etu.univ-nantes.fr (J. Li).

http://dx.doi.org/10.1016/j.sigpro.2016.05.029

0165-1684/© 2016 Elsevier B.V. All rights reserved.

M. Sun et al. / Signal Processing 132 (2017) 272–283

273

roughness). Nevertheless, it is suitable only for narrow band (less than 2 GHz). With the widening of the frequency band, the curve fitting error will increase rapidly, which may bring errors to the interface roughness estimation. In order to reduce the errors coming from the curve fitting, we propose a modified MUSIC algorithm which can take into account several possible frequency behaviours, more adaptable for ultra-wideband GPR. Like in [19,20], we also focus on the estimation of time delays and interface roughness. Unlike the methods in [19,20], the proposed method allows estimating the time delays without knowing the frequency behaviour from roughness. Then, the roughness parameter is estimated by MLE [22] with the estimated time delays from the modified MUSIC algorithm. This step uses a model of which the roughness frequency behaviour is approximated as a Gaussian function. The performance of the proposed algorithm is tested on data simulated from PILE method [13,23–25], which is based on the MoM.

This paper is organised as follows. Section 2 gives the simulation results of the scattering of EM waves from random rough interfaces, and studies the frequency behaviour of the backscattered echoes. In Section 3, the radar data model and preprocessing methods are presented. In Section 4, a modified MUSIC algorithm is proposed to estimate the time delays without knowing the frequency behaviour. Moreover, the roughness parameters are estimated by MLE [22]. Simulation results and a discussion on the performance of the proposed algorithm are given in Section 5. Finally, conclusions and perspectives are drawn.

# 2. Rough pavement scattering model

In order to give some ideas about the scattering from a rough pavement, a realistic simulation of a typical thin asphalt road structure (pavement layer) is considered. The rigorous electromagnetic method PILE (propagation inside layer expansion) [23,25] based on the MoM, provides simulation data that allows showing the influence of the interface roughness on the backscattered echoes of stratified media. The simulation parameters are chosen to match the air-coupled radar configuration at vertical incidence that is used for pavement survey at traffic speed; the probing scope is assumed to be limited to the first two layers of the pavement structure. The considered pavement structure is an Ultra-Thin Asphalt Surfacing (UTAS), which is made of a layer medium $\Omega_2$ with mean thickness $H = 20$ mm. For the rolling band (or base band) corresponding to the medium $\Omega_3$, it has the same composition as the medium $\Omega_2$, see Fig. 1. We assume that $\Omega_2$ and

$\Omega_2$ are homogeneous media for a normal incidence angle ($\theta_i = 0$ in Fig. 1) and the frequency band under study is $[0.5, 10.5]$ GHz. For the considered media, their relative permittivity $\varepsilon_r$ typically ranges between 4 and 8. Moreover, in this paper, the media are assumed to be lossless. For the simulations, we take $\varepsilon_{r2} = 4.5$ and $\varepsilon_{r3} = 7$. The two rough interfaces $\Sigma_A$ and $\Sigma_B$ are assumed to have a Gaussian height probability density function and an exponential height autocorrelation function [26,27]. For $\Sigma_A$, the RMS height $\sigma_{hA}$ is about 0.6 – 1 mm, and the correlation length $L_{cA}$ is about 5–10 mm [26,27]. For $\Sigma_B$, the RMS height $\sigma_{hB}$ and the correlation length $L_{cB}$ are greater than those of $\Sigma_A$. It is assumed that the antenna radiates a vertically polarized plane wave in far field of probed pavement (in practice, the antenna is about 400 mm above the rough surface). The typical width of a probed surface antenna footprint is about 300 – 500 mm. In the simulations, we consider surfaces of length $L = 2400$ mm, illuminated by a Thorsos beam (the Thorsos beam is a tapered plane wave, whose tapering has a Gaussian shape; the tapering is used to reduce the incident field to near zero at the edges of the surface realisations and thereby to reduce edge effects to negligible levels) of attenuation parameter $g = L/8$. The two rough interfaces are sampled with a sampling step $\Delta x = Re(\lambda_2)/8$, where $\lambda_2$ is the wavelength inside $\Omega_2$ with $\lambda_2 = \lambda_0/\sqrt{\varepsilon_{r2}}$ ($\lambda_0$ is the wavelength in vacuum) and $Re(\dots)$ is the real part. We take an incident wave with normal incidence ($\theta_i = 0$), and then calculate the first two scattered echoes $s_1$ and $s_2$ from the scattered field.

In order to investigate the influence of interface roughness on the backscattered echoes, a rough pavement is tested, with roughness parameters $\sigma_{hA} = 1.0$ mm, $L_{cA} = 6.4$ mm, $\sigma_{hB} = 2.0$ mm, $L_{cB} = 15$ mm. According to the selected parameters, PILE method provides the first two backscattered echoes $s_1$ and $s_2$ at each frequency over the frequency band $f \in [0.5, 10.5]$ GHz, with sampling step $\Delta f = 0.1$ GHz. Simulated data were obtained by a Monte Carlo process with 100 independent realizations. Two models are presented: an exponential shape and a Gaussian shape. For doing so, a curve fitting is made by using least squares method to estimate the parameters of the model. In [19,20], the exponential shape $|s(f)| = s_k \times \exp(-\bar{b}f)$ with roughness parameter $\bar{b}$ of the scattered echo amplitude is studied. In this paper, we introduce a Gaussian shape $|s(f)| = s_k \times \exp(-bf^2)$ with a different roughness parameter $b$; where $s_k$ is the amplitude of the considered backscattered echo in the flat pavement.

Curve fittings are made with radar data from PILE in 3 narrow bands ($f \in [0.5, 1.5]$ GHz, $f \in [0.5, 2.5]$ GHz, $f \in [0.5, 3.5]$ GHz) and 3 large bands ($f \in [0.5, 6.5]$ GHz, $f \in [0.5, 8.5]$ GHz, $f \in [0.5, 10.5]$ GHz). Figs. 2 and 3 give the frequency behaviour of

![img-0.jpeg](img-0.jpeg)

Fig. 1. Rough Pavement Configuration.

274

M. Sun et al. / Signal Processing 132 (2017) 272–283

![img-1.jpeg](img-1.jpeg)

Fig. 2. Frequency behaviour of echoes with curve fitting results in [0.5, 1.5] GHz, [0.5, 2.5] GHz and [0.5, 3.5] GHz.

![img-2.jpeg](img-2.jpeg)

Fig. 3. Frequency behaviour of echoes with curve fitting results in [0.5, 6.5] GHz, [0.5, 8.5] GHz and [0.5, 10.5] GHz.

the backscatter echoes. We can notice that the amplitudes of the backscattered echoes are decreasing when the frequency increases, especially for the second echo. Thus, the influence of the

interface roughness cannot be neglected any more, the frequency behaviour of the echoes should be considered in radar data processing. In addition, Figs. 2 and 3 also show the curve fitting

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

276

M. Sun et al. / Signal Processing 132 (2017) 272–283

![img-3.jpeg](img-3.jpeg)

Fig. 4. Pseudo-spectrum of MUSIC for time delay estimation with SNR=30 dB, the three time delays are 1 ns, 1.3 ns and 1.6 ns.

where B is a transformation matrix of interpolation (the details of the interpolation are provided in Appendix A). In the following section, a modified MUSIC algorithm is proposed and applied for TDE. This method assumes that the noise is a Gaussian white noise. To ensure this condition, like in [20], the noise covariance matrix should be removed. As the radar pulse (measured by the echo backscattered from a metallic plane) and the transformation matrix B are known, and the noise variance σ² is estimated by the propagator method [34], the new noise free covariance matrix R can be written as follows:

$$\mathbf{R} = \mathbf{BASA}^H\mathbf{B}^H + 0 \times \mathbf{I} \approx \mathbf{R} - \hat{\sigma}^2\mathbf{B}\Sigma\mathbf{B}^H \tag{7}$$

where δ² is the estimated noise variance. Then, the spatial smoothing preprocessing technique can be applied [35]. The SSP technique estimates the modified covariance matrix RSSP as follows [35]:

$$\mathbf{R}_{SSP} = \frac{1}{M} \sum_{k=1}^{M} \mathbf{R}_k \tag{8}$$

where Rk is the kth sub-band of the covariance matrix R, N frequencies, M overlapping sub-bands of length L are considered. N, M and L are related to one another by:

$$N = L + M - 1$$

### 4. Time delay and interface roughness estimation

When the interface roughness is taken into account, high resolution algorithms like MUSIC or ESPRIT cannot be used directly in theory, due to the unknown frequency behaviour wh(f) of the echoes. Therefore, we propose a modified MUSIC algorithm to estimate the time delays, and then MLE is used to estimate the interface roughness.

### 4.1. Modified music algorithm

In this section, a modified MUSIC algorithm is proposed, which allows estimating only the time delays. The mode vector a can be written as follows:

$$\begin{array}{l} \mathbf{a}(t) = [\exp(-2j\pi f_1 t)\hat{w}(f_1)\exp(-2j\pi f_2 t)\hat{w}(f_2) \\ \quad \dots \exp(-2j\pi f_L t)\hat{w}(f_L)]^T \\ = \text{diag}\{\exp(-2j\pi f_1 t), \exp(-2j\pi f_2 t) \\ \quad \dots, \exp(-2j\pi f_L t)\}[\hat{w}(f_1)\hat{w}(f_2)\dots\hat{w}(f_L)]^T \\ = \tilde{\mathbf{A}}\mathbf{k} \end{array}$$

where $$\tilde{\mathbf{A}} = \text{diag}\{\exp(-2j\pi f_1 t), \exp(-2j\pi f_2 t), \dots, \exp(-2j\pi f_L t)\}$$ and $$\mathbf{k} = [\hat{w}(f_1)\hat{w}(f_2)\dots\hat{w}(f_L)]^T$$ with $$\hat{w}(f)$$ the frequency behaviour of the backscattered echoes after interpolation. k is a real vector.

The pseudo-spectrum of MUSIC can be written as:

$$P(t) = \left[ \min_k \left\{ \frac{\mathbf{k}^H\tilde{\mathbf{A}}^H\mathbf{U}_N\mathbf{U}_N^H\tilde{\mathbf{A}}\mathbf{k}}{\mathbf{k}^H\tilde{\mathbf{A}}^H\tilde{\mathbf{A}}\mathbf{k}} \right\} \right]^{-1} \tag{9}$$

where UN is the L × (L − K) noise matrix whose columns are the L − K noise eigenvectors. Referring to [36], P(t) is equal to the minimum generalized eigenvalue λmin of $$\tilde{\mathbf{A}}^H\mathbf{U}_N\mathbf{U}_N^H\tilde{\mathbf{A}}$$ and $$\tilde{\mathbf{A}}^H\tilde{\mathbf{A}}$$, satisfying (with kmin the corresponding generalized eigenvector):

$$\tilde{\mathbf{A}}^H\mathbf{U}_N\mathbf{U}_N^H\tilde{\mathbf{A}}\mathbf{k}_{min} = \lambda_{min}\tilde{\mathbf{A}}^H\tilde{\mathbf{A}}\mathbf{k}_{min} = \lambda_{min}\mathbf{k}_{min} \tag{10}$$

The pseudo-spectrum of MUSIC can also be written as the reciprocal of the minimum eigenvalue of real{$$\tilde{\mathbf{A}}^H\mathbf{U}_N\mathbf{U}_N^H\tilde{\mathbf{A}}$$} [36,37]:

$$P(t) = \frac{1}{\lambda_{min}(t)} \tag{11}$$

By using (11), we need only to search the spectrum in the time domain without knowing the influence of the frequency behaviour. Nevertheless, it has a false peak in the middle of two true values. For example, when two echoes are considered, we assume that t₁ and t₂ (t₂ > t₁) are the time delays of the echoes, then we can prove that t₃ = (t₂ - t₁)/2 is also a solution of λmin(t) = 0 (the proof is given in Appendix B). In [37], based on the characteristics of λmin(t) corresponding to the false time delay and the true time delays, they propose a new pseudo-spectrum of MUSIC to cancel the false time delay, which can be expressed as follows:

$$P(t) = 10 \log_{10} \left\{ \frac{\lambda_1(t)}{\lambda_2(t)} \right\} \tag{12}$$

where λk(t) is the kth eigenvalue of real{$$\tilde{\mathbf{A}}^H\mathbf{U}_N\mathbf{U}_N^H\tilde{\mathbf{A}}$$}, and λL(t) ≥ λL−1(t) ≥ ... ≥ λ1(t). Still, the above method only works for the case of two echoes. Indeed, for the case where the number of echoes is superior to 2, Eq. (12) does not work. For example, when a true time delay has the same value as a false one, this true time delay will also be cancelled. From Appendix B, we show that the number of zero eigenvalues of real{$$\tilde{\mathbf{A}}^H\mathbf{U}_N\mathbf{U}_N^H\tilde{\mathbf{A}}$$} corresponding to the true time delay is odd, and to the false time delay, this number is even. Based on the above characteristics, we propose a generalized pseudo-spectrum for modified MUSIC as follows:

M. Sun et al. / Signal Processing 132 (2017) 272–283

277

![img-4.jpeg](img-4.jpeg)

Fig. 5. RRMSE on the estimated roughness parameter $b_1 = 1.10 \times 10^{-3} \text{ GHz}^{-2}$ ($\sigma_{hA} = 0.5 \text{ mm}$, $L_{cA} = 6.4 \text{ mm}$) against first time delay $T_1 = 1 \text{ ns}$ in a noiseless environment by MLE.

$$P(t) = \begin{cases} \frac{\lambda_2(t)}{\lambda_1(t)} \frac{\lambda_4(t)}{\lambda_3(t)} \cdots \frac{\lambda_{L-1}(t)}{\lambda_{L-2}(t)} & L = 2n + 1 \\ \frac{\lambda_2(t)}{\lambda_1(t)} \frac{\lambda_4(t)}{\lambda_3(t)} \cdots \frac{\lambda_L(t)}{\lambda_{L-1}(t)} & L = 2n \end{cases} \tag{13}$$

where $n = 0, 1, 2 \dots$ and $L$ can be an odd or even number. The pseudo-spectrums of MUSIC in (11), (12) and (13) are shown in Fig. 4. In the simulation, 3 time delays (1 ns, 1.3 ns and 1.6 ns) are considered, the second time delay is in the middle of the other two time delays. In order to make a better comparison between the three pseudo-spectrums, an amplitude normalization is made in Fig. 4. Modified MUSIC in (11) obtains two false peaks at 1.15 ns and 1.45 ns. By using (12), the two false peaks are removed, but also the second time delay. Only the proposed method (13) can successfully remove the false time delays and keep the true time delays. Thus, Eq. (13) is used in the following of the paper.

### 4.2. MLE for roughness parameter estimation

For the frequency behaviour of backscattered echoes, it has been found in the previous section that the frequency behaviour $w(f)$ can be approximated by a Gaussian function for ultra wide band radar. It enables a parametrization of the frequency variations for data modelling. We assume that the frequency behaviour can be expressed as $w_k(f_i) = \exp(-b_k f_i^2)$, where $b_k$ is the roughness parameter of the $k$th interface. For flat interfaces, $b_k = 0$. This parameter can be calculated by MLE [22] with estimated time delays, the details of the calculation are given in Appendix C. We should notice that the roughness parameters are very sensitive to the bias of the estimated time delay, especially when the roughness parameters are very small, as shown in Fig. 5 (only the first

layer is considered). Note that when the value of $T_1$ is not the true value, the relative-root-mean-square error (RRMSE) on roughness parameter $b_1$ increases drastically.

### 5. Simulations and discussion

In the simulations, the performance of the modified MUSIC and MLE is tested on the data provided by PILE method. The simulated data represent the radar backscattered signal at nadir from a rough pavement made of two rough interfaces separating homogeneous media. The studied pavement structure is made of a layer of UTAS with a relative permittivity equal to 4.5 overlying a base band with a relative permittivity equal to 7. We consider two scattered echoes corresponding to the time delays 1 ns and 1.3 ns, which corresponds to thickness of the first layer of approximately 20 mm and the second layer is infinite. In the simulations, four pavements are studied (the rough interfaces are assumed to have a Gaussian height probability density function and an exponential height autocorrelation function) [26,27] with different root mean square heights $\sigma_h$, correlation lengths $L_h$ and conductivities of the layers $\delta$:

- Case 1. $\sigma_{hA} = 1.0 \text{ mm}$, $L_{cA} = 6.4 \text{ mm}$, $\sigma_{hB} = 2.0 \text{ mm}$, $L_{cB} = 15 \text{ mm}$, lossless media.
- Case 2. $\sigma_{hA} = 1.0 \text{ mm}$, $L_{cA} = 6.4 \text{ mm}$, $\sigma_{hB} = 2.5 \text{ mm}$, $L_{cB} = 15 \text{ mm}$, lossless media.
- Case 3. $\sigma_{hA} = 1.5 \text{ mm}$, $L_{cA} = 6.4 \text{ mm}$, $\sigma_{hB} = 3.0 \text{ mm}$, $L_{cB} = 15 \text{ mm}$, lossless media.
- Case 4. $\sigma_{hA} = 1.0 \text{ mm}$, $L_{cA} = 6.4 \text{ mm}$, $\sigma_{hB} = 2.0 \text{ mm}$, $L_{cB} = 15 \text{ mm}$, low-loss media ($\delta_A = 5 \times 10^{-3} \text{ S/m}$, $\delta_B = 10^{-2} \text{ S/m}$).

When the frequency band is 0.5 – 3.5 GHz, with 0.05 GHz

![img-5.jpeg](img-5.jpeg)

Fig. 6. Case 1, Pseudo-spectrum of MUSIC for time delay estimation with SNR=20 dB, the two time delays are 1 ns and 1.3 ns in grey dashed line, slightly overlapped.

278

M. Sun et al. / Signal Processing 132 (2017) 272–283

![img-6.jpeg](img-6.jpeg)

Fig. 7. Case 2, Pseudo-spectrum of MUSIC for time delay estimation with SNR=20 dB, the two time delays are 1 ns and 1.3 ns in grey dashed line, slightly overlapped.

![img-7.jpeg](img-7.jpeg)

Fig. 8. Case 3, Pseudo-spectrum of MUSIC for time delay estimation with SNR=20 dB, the two time delays are 1 ns and 1.3 ns in grey dashed line, slightly overlapped.

![img-8.jpeg](img-8.jpeg)

Fig. 9. Case 1, Pseudo-spectrum of MUSIC for time delay estimation with SNR=20 dB, the two time delays are 1 ns and 1.3 ns in grey dashed line, non-overlapped.

frequency step (61 frequency samples), the echoes are slightly overlapped. When the frequency band is 0.5 – 6.5 GHz, with 0.1 GHz frequency step (61 frequency samples), the echoes are non-overlapped. The covariance matrix is estimated from 1000 independent snapshots. The interpolated SSP technique is used to reduce the cross-correlation between the echoes and the number of sub-bands (M) is equal to 20. The signal-to-noise ratio (SNR) is defined as the ratio between the powers of the second echo and noise variance. In the first simulation, a fixed SNR=20 dB is used for three different rough pavements.

Figs. 6–10 show the pseudo-spectrums of modified MUSIC. Two peaks corresponding to the time delays of the first two scattered echoes are well estimated. Simulation results demonstrate that the

proposed algorithm can handle cases where both echoes are either overlapped or non-overlapped and for either lossless or low-loss media. The roughness parameters could also be estimated by using the MLE with the estimated time delays (see Figs. 11–15). Table 2 gives the results of estimated time delays ($\hat{t}_k$) and estimated roughness parameters ($\hat{b}_k$). We compare the estimated frequency behaviours with the data from PILE in Figs. 11–15. From the frequency behaviour of the four different cases, it is shown that the expressions of the echoes are in agreement with the data from PILE for various roughness parameters with either lossless media or low-loss media.

Then, in the second simulation, we evaluate the performance of

M. Sun et al. / Signal Processing 132 (2017) 272–283

279

![img-9.jpeg](img-9.jpeg)

Fig. 10. Case 4, Pseudo-spectrum of MUSIC for time delay estimation with SNR=20 dB, the two time delays are 1 ns and 1.3 ns in grey dashed line, slightly overlapped, low-loss media.

![img-10.jpeg](img-10.jpeg)

Fig. 11. Case 1, Expression for frequency behaviour of backscattered echoes by using estimated roughness parameter versus frequency behaviour of backscattered echoes from radar data, slightly overlapped.

![img-11.jpeg](img-11.jpeg)

Fig. 12. Case 2, Expression for frequency behaviour of backscattered echoes by using estimated roughness parameter versus frequency behaviour of backscattered echoes from radar data, slightly overlapped.

modified MUSIC, which is assessed with a Monte-Carlo process of 500 independent runs of the algorithm with independent noise snapshots and from the RRMSE of the evaluated parameter as follows:

$$RRMSE(z) = \frac{\sqrt{\frac{1}{U} \sum_{j=1}^{U} \left( \hat{z}_j - z \right)^2}}{z}, \tag{14}$$

where $\hat{z}_j$ denotes the estimated parameter for the $j$th run of the

algorithm, and $z$ the true value. In the simulation, the parameter $z$ can represent either the first ($t_1$) or the second ($t_2$) time delay. Only case 1 is considered. In the time delay estimation, as expected, it can be seen that the RRMSE is continuously decreasing when the SNR increases. Fig. 16 shows that the proposed method gives relatively good performances in TDE.

In the third simulation, the performance of the proposed method is tested on a pavement which is composed of 3 rough interfaces (four layers). The simulation parameters of the pavement are chosen as follows: the permittivities of first three layers

280

M. Sun et al. / Signal Processing 132 (2017) 272–283

![img-12.jpeg](img-12.jpeg)

Fig. 13. Case 3, Expression for frequency behaviour of backscattered echoes by using estimated roughness parameter versus frequency behaviour of backscattered echoes from radar data, slightly overlapped.

![img-13.jpeg](img-13.jpeg)

Fig. 14. Case 1, Expression for frequency behaviour of backscattered echoes by using estimated roughness parameter versus frequency behaviour of backscattered echoes from radar data, non-overlapped.

![img-14.jpeg](img-14.jpeg)

Fig. 15. Case 4, Expression for frequency behaviour of backscattered echoes by using estimated roughness parameter versus frequency behaviour of backscattered echoes from radar data, slightly overlapped, low-loss media.

are $\epsilon_{r2} = 4.5$, $\epsilon_{r3} = 7$ and $\epsilon_{r4} = 9$, respectively; we consider three backscattered echoes corresponding to the first three time delays 1 ns, 1.3 ns and 1.7 ns, which corresponds to a thickness of the second layer as approximately 20 mm, of the third layer as approximately 23 mm and of the fourth layer as infinite; the roughness parameters of three rough interfaces are chosen as follows: $b_1 = 1.60 \times 10^{-3} \text{ GHz}^{-2}$, $b_2 = 1.70 \times 10^{-2} \text{ GHz}^{-2}$ and $b_3 = 3.00 \times 10^{-2} \text{ GHz}^{-2}$, which are obtained from the signal model

in Eq. (1). Figs. 17 and 18 present the pseudo-spectrum of the modified MUSIC and the frequency behaviour of the backscattered echoes for a rough pavement with 3 layers. It can be seen that the three peaks corresponding to the time delays of the first three scattered echoes are well estimated (estimated time delays are $\hat{t}_1 = 0.999$ ns, $\hat{t}_2 = 1.302$ ns and $\hat{t}_3 = 1.705$ ns). Furthermore, the estimated frequency behaviours of backscattered echoes are in relatively good agreement with the data from signal model

M. Sun et al. / Signal Processing 132 (2017) 272–283

281

Table 2
Estimated time delays and roughness parameters by modified MUSIC and MLE.  \( \hat{t}_{k} \)  and  \( \hat{b}_{k} \)  represent estimated time delays and estimated roughness parameters, respectively.

|  Parameter | Case1 overlapped | Case2 overlapped | Case3 overlapped | Case1 non-overlapped | Case1 overlapped with low-loss media  |
| --- | --- | --- | --- | --- | --- |
|  \( \hat{t}_{1} \) (ns) | 1.000 | 1.000 | 0.999 | 1.000 | 1.000  |
|  \( \hat{t}_{2} \) (ns) | 1.299 | 1.302 | 1.301 | 1.302 | 1.306  |
|  \( \hat{b}_{1} \) (GHz\( ^{-2} \)) | \( 1.96 \times 10^{-3} \) | \( 2.69 \times 10^{-3} \) | \( 4.40 \times 10^{-3} \) | \( 1.41 \times 10^{-3} \) | \( 3.52 \times 10^{-3} \)  |
|  \( \hat{b}_{2} \) (GHz\( ^{-2} \)) | \( 1.52 \times 10^{-2} \) | \( 2.49 \times 10^{-2} \) | \( 4.02 \times 10^{-2} \) | \( 1.60 \times 10^{-2} \) | \( 1.76 \times 10^{-2} \)  |

![img-15.jpeg](img-15.jpeg)

Fig. 16. Simulation 2, RRMSE on the estimated time delay \( t_k \), (\( k = 1, 2 \)) vs. SNR after 500 Monte-Carlo simulations for case 1, slightly overlapped.

![img-16.jpeg](img-16.jpeg)

Fig. 17. Simulation 3, Pseudo-spectrum of MUSIC for time delay estimation with SNR=20 dB, the three time delays are 1 ns, 1.3 ns and 1.7 ns in grey dashed line.

![img-17.jpeg](img-17.jpeg)

Fig. 18. Simulation 3, Expression for frequency behaviour of backscattered echoes by using estimated roughness parameter versus frequency behaviour of backscattered echoes from radar data.

282

M. Sun et al. / Signal Processing 132 (2017) 272–283

(estimated roughness parameters are $\hat{b}_1 = 1.50 \times 10^{-3} \text{ GHz}^{-2}$, $\hat{b}_2 = 1.83 \times 10^{-2} \text{ GHz}^{-2}$ and $\hat{b}_3 = 2.93 \times 10^{-2} \text{ GHz}^{-2}$).

## 6. Conclusion

In this paper, we have studied time delays and interface roughness estimation with coherent backscattered echoes. After applying the interpolated spatial smoothing technique to decorrelate the received echoes, we propose a modified MUSIC algorithm, which is able to estimate the time delays without knowing the frequency behaviour from roughness. Then, the influence of the interface roughness is estimated by MLE. These algorithms are applied to evaluate the pavement. The performance of the proposed algorithms is tested on data from MoM. The proposed algorithms show good performance for time delays and interface roughness estimation. In perspective, the proposed method will be extended to dispersive media (soils or hydraulic concretes).

## Acknowledgment

The authors would like to thank the China Scholarship Council (No. 201306150010) and the grant of Science and Technology Planning Project of Guangdong (No. 2015A050502011) for funding part of this work. This work may contribute to COST Action TU1208 "Civil Engineering Applications of Ground Penetrating Radar".

## Appendix A.

The mode vector can be written as:

$$\begin{array}{l} \mathbf{a}(t_k) = [\exp(-2j\pi f_1 t_k)w_k(f_1)\exp(-2j\pi f_2 t_k)w_k(f_2) \\ \quad \dots \exp(-2j\pi f_N t_k)w_k(f_N)]^T \\ = diag\{w_k(f_1), w_k(f_2) \dots w_k(f_N)\} \\ \quad [\exp(-2j\pi f_1 t_k), \exp(-2j\pi f_2 t_k) \dots \exp(-2j\pi f_N t_k)]^T \\ = \mathbf{C}\bar{\mathbf{a}} \end{array}$$

The frequency behaviour $w(f)$ depends on the RMS height $\sigma_h$ and the correlation length $L_h$, thus matrix $\mathbf{C}$ also changes with $\sigma_h$ and $L_h$, it can be expressed as $\mathbf{C}(\sigma_h, L_h)$. We propose to interpolate $w(f)$ into a uniform linear frequency behaviour. The procedure is as follows:

- Define a set of $\sigma_h = \{\sigma_{h1}, \sigma_{h2} \dots \sigma_{hC}\}$ and a set of $L_h = \{L_{h1}, L_{h2} \dots L_{hP}\}$;
- Compute the model vectors associated with the set $\sigma_h$ and $L_h$, and arrange them into a matrix form as follows: $\mathbf{C}_r = [\mathbf{C}(\sigma_{h1}, L_{h1})\mathbf{C}(\sigma_{h2}, L_{h2}) \dots \mathbf{C}(\sigma_{h3}, L_{hP})\mathbf{C}(\sigma_{h4}, L_{h4}) \dots \mathbf{C}(\sigma_{hC}, L_{hP})]$;
- Decide where to place the "virtual elements" of the interpolation matrix $\mathbf{C}_r = [\hat{\mathbf{C}}(\sigma_{h1}, L_{h1})\hat{\mathbf{C}}(\sigma_{h2}, L_{h2}) \dots \hat{\mathbf{C}}(\sigma_{h3}, L_{hP})\hat{\mathbf{C}}(\sigma_{h4}, L_{h4}) \dots \hat{\mathbf{C}}(\sigma_{hC}, L_{hP})]$, $\hat{\mathbf{C}}(\sigma_h, L_h)$ has a uniform linear frequency behaviour.
- Find the transformation matrix $\mathbf{B}$ by a least squares solution of $\mathbf{B}\mathbf{C}_r = \mathbf{C}_r$. The "best" interpolation matrix $\mathbf{C}_r$ is the one which will minimize $\|\mathbf{B}\mathbf{C}_r - \mathbf{C}_r\|^2$.

## Appendix B.

In this appendix, we present why a false peak exists. Only the case of two echoes is presented, but the same calculation can be carried out when the number of echoes is superior to 2. We assume $t_1$ and $t_2$ are the time delays of two echoes ($t_1 < t_2$) and define $t_3 = (t_1 + t_2)/2$, $\Delta t = (t_2 - t_1)/2$, $\Phi(t) = \hat{\mathbf{A}}^H(t)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t)$. By

definition, the rank of $\mathbf{U}_h\mathbf{U}_h^H$ is $L-2$, it has always 2 zero eigenvalues with 2 eigenvectors, $\mathbf{a}^H(t)\mathbf{U}_h\mathbf{U}_h^H\mathbf{a}(t)$ is real valued. Following the subspace principle, we have 2 equalities:

- $\mathbf{a}^H(t)\mathbf{U}_h\mathbf{U}_h^H\mathbf{a}(t) = \mathbf{k}^T\hat{\mathbf{A}}^H(t)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t)\mathbf{k} = \mathbf{k}^T\Phi(t)\mathbf{k} = 0$, for $t = t_1$ or $t_2$.
- $\mathbf{k}^T\Phi(t)\mathbf{k} \neq 0$, for $t \neq t_1$ or $t_2$.

Then we can have the following 3 situations:

case 1: $t = t_1$ and $t_2$. When $t = t_1$ or $t_2$, $\mathbf{a}^H(t)\mathbf{U}_h\mathbf{U}_h^H\mathbf{a}(t) = \mathbf{k}^T\hat{\mathbf{A}}^H(t)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t)\mathbf{k} = \mathbf{k}^T\Phi(t)\mathbf{k} = 0$. $\Phi(t)$ has 2 zero eigenvalues with 2 eigenvectors and $\mathbf{k}$ is a real eigenvector. For $t = t_1$, we can see also:

$$\begin{array}{l} \mathbf{k}^T\hat{\mathbf{A}}^H(t_2 - t_1)\hat{\mathbf{A}}^H(t_1)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t_1)\hat{\mathbf{A}}(t_2 - t_1)\mathbf{k} \\ = \mathbf{k}_{10}^H\hat{\mathbf{A}}^H(t_1)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t_1)\mathbf{k}_{10} = \mathbf{k}^T\hat{\mathbf{A}}^H(t_2)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t_2)\mathbf{k} \end{array}$$

where $\mathbf{k}_{10} = \hat{\mathbf{A}}(t_2 - t_1)\mathbf{k}$ is another eigenvector. Similarly, $\mathbf{k}_{20} = \hat{\mathbf{A}}(t_1 - t_2)\mathbf{k}$ is the second eigenvector for $t = t_2$. $\mathbf{k}_{10}$ and $\mathbf{k}_{20}$ are complex valued and not collinear with $\mathbf{k}$, any non-zero coefficients linear combination of $\mathbf{k}$ and $\mathbf{k}_{10}$ or $\mathbf{k}$ and $\mathbf{k}_{20}$ is complex valued. Therefore, $\Phi(t)$ has only one real eigenvector ($\mathbf{k}$) corresponding to one single zero eigenvalue, and $real\{\mathbf{k}^T\Phi(t)\mathbf{k}\} = \mathbf{k}^T real\{\Phi(t)\}\mathbf{k} = 0$, only one solution for $t_1$ or $t_2$. Thus, the number of zero eigenvalue of $real\{\Phi(t_1)\}$ and $real\{\Phi(t_2)\}$ is 1.

case 2: $t \neq t_1$, $t_2$ and $t_3$. $\Phi(t)$ has 2 zero eigenvalues, we can find easily 2 non-linearly correlated eigenvectors $\mathbf{k}_1$ and $\mathbf{k}_2$ corresponding to the zero eigenvalues:

$$\mathbf{k}_1^H\Phi(t)\mathbf{k}_1 = \mathbf{k}_1^H\hat{\mathbf{A}}^H(t)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t)\mathbf{k}_1 = 0$$

$$\mathbf{k}_2^H\Phi(t)\mathbf{k}_2 = \mathbf{k}_2^H\hat{\mathbf{A}}^H(t)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t)\mathbf{k}_2 = 0$$

where $\mathbf{k}_1 = \hat{\mathbf{A}}(t_1 - t)\mathbf{k}$ and $\mathbf{k}_2 = \hat{\mathbf{A}}(t_2 - t)\mathbf{k}$. Due to $t \neq t_1$, $t_2$ and $t_3$, $\mathbf{k}_1$ and $\mathbf{k}_2$ are complex and non-linearly correlated. For these values of $t$, we can show that any linear combination of $\mathbf{k}_1$ and $\mathbf{k}_2$ will always be complex valued. $\Phi(t)$ has no real eigenvector corresponding to zero eigenvalue. Then, $\mathbf{k}^T\Phi(t)\mathbf{k} \neq 0$, $real\{\mathbf{k}^T\Phi(t)\mathbf{k}\} = \mathbf{k}^T real\{\Phi(t)\}\mathbf{k} \neq 0$, which means $real\{\Phi(t)\}$ is full rank, there is no zero eigenvalue.

case 3: $t = t_3$. When $t = t_1$ and $t_2$, We have:

$$\mathbf{k}^T\Phi(t_1)\mathbf{k} = \mathbf{k}^T\hat{\mathbf{A}}^H(t_1)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t_1)\mathbf{k} = 0$$

$$\mathbf{k}^T\Phi(t_2)\mathbf{k} = \mathbf{k}^T\hat{\mathbf{A}}^H(t_2)\mathbf{U}_h\mathbf{U}_h^H\hat{\mathbf{A}}(t_2)\mathbf{k} = 0$$

which are equivalent to

$$\mathbf{U}_h^H\hat{\mathbf{A}}(t_1)\mathbf{k} = 0$$

$$\mathbf{U}_h^H\hat{\mathbf{A}}(t_2)\mathbf{k} = 0$$

For $t = t_3$, any linear combination of above equations leads $\mathbf{U}_h^H\hat{\mathbf{A}}(t_1)\mathbf{k} + \alpha\mathbf{U}_h^H\hat{\mathbf{A}}(t_2)\mathbf{k} = \mathbf{U}_h^H\hat{\mathbf{A}}(t_3)(\hat{\mathbf{A}}^H(\Delta t) + \alpha\hat{\mathbf{A}}(\Delta t))\mathbf{k} = 0$. Only when $\alpha$ is equal to 1 or $-1$, $\hat{\mathbf{A}}^H(\Delta t) + \alpha\hat{\mathbf{A}}(\Delta t)$ is a pure real or imaginary matrix.

For $\alpha = 1$, $\mathbf{U}_h^H\hat{\mathbf{A}}(t_3)(\hat{\mathbf{A}}^H(\Delta t) + \hat{\mathbf{A}}(\Delta t))\mathbf{k} = 2\mathbf{U}_h^H\hat{\mathbf{A}}(t_3)real\{\hat{\mathbf{A}}(\Delta t)\}\mathbf{k} = 2\mathbf{U}_h^H\hat{\mathbf{A}}(t_3)\mathbf{k}_3$. For $\alpha = -1$, $\mathbf{U}_h^H\hat{\mathbf{A}}(t_3)(\hat{\mathbf{A}}^H(\Delta t) - \hat{\mathbf{A}}(\Delta t))\mathbf{k} = 2\mathbf{U}_h^H\hat{\mathbf{A}}(t_3)imag\{\hat{\mathbf{A}}(\Delta t)\}\mathbf{k} = 2\mathbf{U}_h^H\hat{\mathbf{A}}(t_3)\mathbf{k}_4$. Therefore, $\mathbf{k}_1^H\Phi(t_3)\mathbf{k}_3 = \mathbf{k}_1^H\Phi(t_3)\mathbf{k}_4 = 0$ with $\mathbf{k}_3 = real\{\hat{\mathbf{A}}(\Delta t)\}\mathbf{k}$ and $\mathbf{k}_4 = imag\{\hat{\mathbf{A}}(\Delta t)\}\mathbf{k}$. In addition, $\mathbf{a}^H(t)\mathbf{U}_h\mathbf{U}_h^H\mathbf{a}(t)$ is always real valued, thus, $t_3$ is a solution of $\lambda_{\min}(t) = 0$ and $real\{\Phi(t_3)\}$ only two zero eigenvalues with corresponding eigenvectors $\mathbf{k}_3$ and $\mathbf{k}_4$. When the number of echoes is superior to 2, the number of zero eigenvalues of $real\{\Phi(t)\}$ corresponding to the true time delay is odd. For false time delay, this number is even.

## Appendix C.

In this appendix, we present MLE for the roughness parameters estimation. The time delays are estimated ($\hat{t}_k$ is the $k$th estimated

M. Sun et al. / Signal Processing 132 (2017) 272–283

283

time delay) and the noise being a Gaussian white noise with zero mean and variance $\sigma^2$. Referring to Eq. (1), the joint probability density function for all observations can be calculated:

$$f(\mathbf{r}, b_k) = \frac{1}{(\pi \sigma^2)^N} \exp \left\{ - \frac{\sum_{i=1}^N |r(f_i) - \sum_{k=1}^K s_k e(f_i) \exp(-j2\pi f_i \hat{t}_k - b_k f_i^2)|^2}{\sigma^2} \right\}$$

In practice, MLE is obtained by maximizing a log-likelihood function $L(\mathbf{r}, b_k)$ instead of the joint density function $f(\mathbf{r}, b_k)$ as follows:

$$L(\mathbf{r}, b_k) = \ln f(\mathbf{r}, b_k)$$

$$= - \frac{\sum_{i=1}^N |r(f_i) - \sum_{k=1}^K s_k e(f_i) \exp(-j2\pi f_i \hat{t}_k - b_k f_i^2)|^2}{\sigma^2} - N \ln(\pi \sigma^2)$$

The optimal estimation (for the roughness parameters $b_k$) is obtained by finding the solution of $\frac{d(\mathbf{r}, b_k)}{db_k} = 0$.

# References

[1] A.P. Annan, N. Diamanti, J.D. Redman, S.R. Jackson, Ground-penetrating radar for assessing winter roads, Geophysics 81 (2016) WA101–WA109.

[2] A. Benedetto, L. Pajewski, Civil Engineering Applications of Ground Penetrating Radar, Springer International Publishing, Switzerland, 2015.

[3] A.S. Venkatachalam, X. Xu, D. Huston, T. Xia, Development of a new high speed dual-channel impulse ground penetrating radar, IEEE J. Sel. Top. Appl. Earth Obs. Remote. Sens. 7 (2014) 753–760.

[4] D.H. Chen, F. Hong, W. Zhou, P. Ying, Estimating the hotmix asphalt air voids from ground penetrating radar, NDT E Int. 68 (2014) 120–127.

[5] H. Liu, M. Sato, In situ measurement of pavement thickness and dielectric permittivity by GPR using an antenna array, NDT E Int. 64 (2014) 65–71.

[6] J. Lee, C. Nguyen, T. Scullion, A novel, compact, low-cost, impulse ground-penetrating radar for nondestructive evaluation of pavement, IEEE Trans. Instrum. Meas. 53 (2004) 1502–1509.

[7] T. Saarenketo, T. Scullion, Road evaluation with ground penetrating radar, J. Appl. Geophys. 43 (2000) 119–138.

[8] S. Lee, E. Millos, R. Greiner, J. Rossiter, A. Venetsanopoulos, On the machine analysis of radar signals for ice profiling, Signal Process. 18 (1989) 371–386.

[9] U. Spagnolini, V. Rampa, Multitarget detection/tracking for monostatic ground penetrating radar: application to pavement profiling, IEEE Trans. Geosci. Remote. Sens. 37 (1) (1999) 383–394.

[10] I.L. Al-Qadi, S. Lahouar, Measuring layer thickness with GPR-theory to practice, Constr. Build. Mater. 19 (10) (2005) 763–772.

[11] S. Lahouar, I.L. Al-Qadi, Automatic detection of multiple pavement layers from GPR data, NDT E Int. 41 (2) (2008) 69–81.

[12] C. Le Bastard, V. Baltazart, Y. Wang, J. Saillard, Thin-pavement thickness estimation using GPR with high-resolution and super resolution methods, IEEE Trans. Geosci. Remote. Sens. 45 (2007) 2511–2519.

[13] N. Pinel, C. Le Bastard, V. Baltazart, C. Bourlier, Y. Wang, Influence of layer roughness for road survey by ground penetrating radar at nadir: theoretical study, IET Radar, Sonar Navig. 5 (2011) 650–656.

[14] K. Luo, A. Manikas, Superresolution multitarget parameter estimation in MIMO radar, IEEE Trans. Geosci. Remote. Sens. 51 (6) (2013) 3683–3693.

[15] D. Kurrant, E. Fear, Technique to decompose near-field reflection data generated from an object consisting of thin dielectric layers, IEEE Trans. Antennas

Propag. 60 (8) (2012) 3684–3692.

[16] C. Le Bastard, V. Baltazart, Y. Wang, Modified ESPRIT (M-ESPRIT) algorithm for time delay estimation in both any noise and any radar pulse context by a GPR radar, Signal Process. 90 (2010) 173–179.

[17] K. Chahine, V. Baltazart, Y. Wang, Interpolation-based matrix pencil method for parameter estimation of dispersive media in civil engineering, Signal Process. 90 (2010) 2567–2580.

[18] N. Pinel, C. Le Bastard, C. Bourlier, M. Sun, Asymptotic modeling of coherent scattering from random rough layers: application to road survey by GPR at nadir, Int. J. Antennas Propag. (2012), Article ID 874840.

[19] M. Sun, N. Pinel, C. Le Bastard, V. Baltazart, A. Ilhamouten, Y. Wang, Time delay and interface roughness estimation by subspace algorithms for pavement survey by radar, Surf. Geophys. 13 (2015) 279–287.

[20] M. Sun, C. Le Bastard, N. Pinel, Y. Wang, J. Li, Road surface layers geometric parameters estimation by ground penetrating radar using estimation of signal parameters via rotational invariance techniques method, IET Radar, Sonar Navig. 10 (2016) 603–609.

[21] L. Qu, Q. Sun, T. Yang, L. Zhang, Y. Sun, Time-delay estimation for ground penetrating radar using ESPRIT with improved spatial smoothing preprocessing, IEEE Geosci. Remote. Sens. Lett. 11 (2014) 1315–1319.

[22] A. Schatzberg, A.J. Devaney, A.J. Witten, Estimating target location from scattered field data, Signal Process. 40 (1994) 227–237.

[23] N. Déchamps, N. De Beaucoudrey, C. Bourlier, S. Toutain, Fast numerical method for electromagnetic scattering by rough layered interfaces: propagation-inside-layer expansion method, J. Opt. Soc. Am. A 23 (2006) 359–369.

[24] C. Bourlier, G. Kubické, N. Déchamps, Fast method to compute scattering by a buried object under a randomly rough surface: PILE combined with FB-SA, J. Opt. Soc. Am. A 5 (2009) 260–263.

[25] C. Bourlier, C. Le Bastard, V. Baltazart, Generalization of PILE method to the EM scattering from stratified subsurface with rough interlayers: application to the detection of debondings within pavement structure, IEEE Trans. Geosci. Remote. Sens. 53 (2015) 4104–4115.

[26] F. Koudogbo, P.F. Combes, H.J. Mametsa, Numerical and experimental validations of IEM for bistatic scattering from natural and manmade rough surfaces, Progress. Electromagn. Res. 46 (2004) 203–244.

[27] E. Li, K. Sarabandi, Low grazing incidence millimeter-wave scattering models and measurements for various road surfaces, IEEE Trans. Antennas Propag. 47 (1999) 851–861.

[28] C. Fauchard, Utilisation de radars très hautes fréquences: application à lausculation non destructive des chaussées, PhD thesis, University of Nantes, France, 2001.

[29] D. Daniel, Ground Penetrating Radar, 2nd edn, IEE Press, London, 2004.

[30] X. Li, R. Wu, An efficient algorithm for time delay estimation, IEEE Trans. Signal Process. 46 (1998) 2231–2235.

[31] M. Sun, C. Le Bastard, Y. Wang, N. Pinel, Time delay estimation using ESPRIT with extended improved spatial smoothing techniques for radar signals, IEEE Geosci. Remote. Sens. Lett. 13 (2016) 73–77.

[32] B. Friedlander, A.J. Weiss, Direction finding using spatial smoothing with interpolated arrays, IEEE Trans. Aerosp. Electron. Syst. 28 (1982) 574–587.

[33] A.J. Weiss, B. Friedlander, performance analysis of spatial smoothing with interpolated arrays, IEEE Trans. Signal Process. 41 (1993) 1881–1892.

[34] S. Marcos, J. Sanchez-Araujo, Méthodes linéaires haute résolution pour l'estimation de directions d'arrivée de sources performances asymptotiques et complexité, Trait. Du. Signal 14 (1997) 99–116.

[35] T.J. Shan, M. Wax, T. Kailath, On spatial smoothing for direction-of-arrival estimation of coherent signals, IEEE Trans. Acoust., Speech Signal Process. 33 (1985) 806–811.

[36] F. Ge, D. Shen, Y. Peng, V.O.K. Li, Super-resolution time delay estimation in multipath environments, IEEE Trans. Circuits Syst. 54 (2007) 1977–1986.

[37] F. Ge, Q. Wan, X. Wang, Y. Peng, Frequency estimation of the sinusoidal signals with lowpass envelopes based on the eigenanalysis, in: Proceedings of the IEEE Radar Conference, 2002, pp. 453–458.