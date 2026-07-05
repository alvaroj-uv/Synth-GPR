Other investigators have described the results of combining GPR technology with a different commercial EM-based system for detecting rebar, a handheld concrete pachometer, also known as covermeter, (Barrile and Pucinotti (2005)). They report diameter estimates with 12% error. This dual method, however lacks the advantage of GPR alone, which can be towed at vehicle speeds over concrete.

Recently, full-waveform inversion (FWI), in which the full waveforms of GPR traces are used, rather than peak arrival times, has been applied to the problem of buried pipe diameter (Jazayeri and Kruse (2016); Jazayeri et al. (2018); Liu et al. (2018)). FWI is shown to improve diameter estimations of water or air-filled PVC pipes and also to predict the pipe's infilling material permittivity.

In this paper, we test the FWI method for estimating rebar diameter. Because the FWI method requires a starting model, it begins with a ray-based estimate of rebar diameter. To optimize this initial estimate, we derive the mathematical expression for the hyperbolic pattern of a cylindrical target perpendicular to the GPR profile, considering both target diameter and transmitter-receiver offset. Second, we adapt the FWI approach from Jazayeri et al. (2018) to the problem of reinforced concrete. This approach requires the shape of the transmitted pulse (known as source wavelet or SW) as an input. We use Jazayeri et al. (2019)'s Sparse Blind Deconvolution (SBD) technique to calculate the SW. Finally, we explore the capabilities of the proposed method on one synthetic and two real data sets.

### 4.4 Method

#### 4.4.1 Analytical expression for travel times

The diameter of a diffracting cylinder affects the arrival time of the GPR signal and the general shape of the diffraction hyperbolas (although as described above this effect is small when the cylinder is small). Al-Nuaimy et al. (2004) and Shihab and Al-Nuaimy (2005) provide formulations that consider the radius of the target and are suitable for least squares approximations. However, for simplification, they treat the transmitter-receiver offset as negligible.

12