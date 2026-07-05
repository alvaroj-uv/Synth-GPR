Geophysical Journal International

Geophys. J. Int. (2023) 232, 504–522

Advance Access publication 2022 August 17

GJI Marine Geosciences and Applied Geophysics

https://doi.org/10.1093/gji/ggac319

# Full-waveform inversion of ground-penetrating radar data in frequency-dependent media involving permittivity attenuation

Tan Qin¹, Thomas Bohlen¹ and Niklas Allroggen²

¹Geophysical Institute, Karlsruhe Institute of Technology, 76187 Karlsruhe, Germany. E-mail: tan.qin@kit.edu

²Institute of Geosciences, University of Potsdam, 14476 Potsdam-Golm, Germany

Accepted 2022 August 3. Received 2022 July 1; in original form 2022 February 12

## SUMMARY

Full-waveform inversion (FWI) of ground-penetrating radar (GPR) data has received particular attention in the past decade because it can provide high-resolution subsurface models of dielectric permittivity and electrical conductivity. In most GPR FWIs, these two parameters are regarded as frequency independent, which may lead to false estimates if they strongly depend on frequency, such as in shallow weathered zones. In this study, we develop frequency-dependent GPR FWI to solve this problem. Using the τ-method introduced in the research of viscoelastic waves, we define the permittivity attenuation parameter to quantify the attenuation resulting from the complex permittivity and to modify time-domain Maxwell's equations. The new equations are self-adjoint so that we can use the same forward engine to back-propagate the adjoint sources and easily derive model gradients in GPR FWI. Frequency dependence analysis shows that permittivity attenuation acts as a low-pass filter, distorting the waveform and decaying the amplitude of the electromagnetic waves. The 2-D synthetic examples illustrate that permittivity attenuation has low sensitivity to the surface multioffset GPR data but is necessary for a good reconstruction of permittivity and conductivity models in frequency-dependent GPR FWI. As a comparison, frequency-independent GPR FWI produces more model artefacts and hardly reconstructs conductivity models dominated by permittivity attenuation. The 2-D field example shows that both FWIs reveal a triangle permittivity anomaly which proves to be a refilled trench. However, frequency-dependent GPR FWI provides a better fit to the observed data and a more robust conductivity reconstruction in a high permittivity attenuation environment. Our GPR FWI results are consistent with previous GPR and shallow-seismic measurements. This research greatly expands the application of GPR FWI in more complicated media.

**Key words:** Electromagnetic theory; Inverse theory; Waveform inversion.

## 1 INTRODUCTION

Ground-penetrating radar (GPR) plays an increasingly important role in near-surface surveys (Jol 2008). Full-waveform inversion (FWI) was first proposed by Tarantola (1984) for seismic reflection data, and then introduced to crosshole GPR data by Ernst et al. (2007b) and Kuroda et al. (2007). GPR FWI has been successfully applied to crosshole data (Ernst et al. 2007a; Meles et al. 2010; Oberröhrmann et al. 2013; Gueting et al. 2015) as well as to surface recordings (El Bouajaji et al. 2011; Busch et al. 2012; Lavoué et al. 2014; Liu et al. 2018). In the past decade, it has been shown that GPR FWI has great potential for reconstructing high-resolution subsurface models of electromagnetic (EM) material properties, namely dielectric permittivity and electrical conductivity (Klotzsche et al. 2019). In most GPR FWIs, these two parameters are assumed to be frequency independent, i.e. they are constant values over the main GPR bandwidth. However, many typical geological materials in the shallow subsurface are frequency-dependent to EM waves (Turner & Siggins 1994). In this case, GPR FWI may not reveal its full potential if the forward modelling cannot account for velocity dispersion and permittivity attenuation.

The time-domain modelling of EM waves requires solving Maxwell's equations involving convolution calculations that explain the frequency-dependent electrical properties. For replacing the convolution with the more efficient multiplication, Carcione (1996) used the Debye model and Kelvin–Voigt model to approximate the relaxation functions of the dielectric permittivity and electrical conductivity, respectively. Bergmann et al. (1998) further developed Carcione's approach in the time domain and performed the numerical modelling by the finite-difference time-domain (FDTD) method. Their Maxwell's equations are analogous to the viscoelastic (or viscoacoustic) equations with

© The Author(s) 2022. Published by Oxford University Press on behalf of The Royal Astronomical Society. This is an Open Access article distributed under the terms of the Creative Commons Attribution License (https://creativecommons.org/licenses/by/4.0/), which permits unrestricted reuse, distribution, and reproduction in any medium, provided the original work is properly cited.

504

Downloaded from https://academic.oup.com/gji/article/232/1/504/6670780 by KIT Library user on 25 October 2022

FWI of GPR data in frequency-dependent media 505

standard linear solid (SLS) mechanisms, as shown, for example in Blanch *et al.* (1995). These equations use similar physical models to characterize the frequency dependence of electrical parameters and seismic moduli (Carcione & Cavallini 1995). It implies that GPR FWI can refer to viscoelastic FWI already developed in the seismic community, such as Fabien-Ouellet *et al.* (2017) and Jiang (2019). However, Maxwell's equations differ from the viscoelastic equations because the complex permittivity and conductivity always occur in a combined form and both cause attenuation (Turner & Siggins 1994; Bradford 2007). In viscoelastic case, the magnitude of dispersion and attenuation of a single wave ($P$ or $S$ waves) can be described by a single parameter ($\tau_P$ or $\tau_S$), which corresponds to the case of considering only permittivity attenuation or conductivity attenuation in EM waves (Blanch *et al.* 1995).

In the last decade, most GPR FWIs still used frequency-independent sensitivity kernels when updating model parameters (Klotzsche *et al.* 2019). There are two reasons for this. One is that simultaneous reconstruction of permittivity and conductivity is already a challenging task in frequency-independent GPR FWI, while studies of frequency-dependent GPR FWI that require estimation of more parameters take a back seat. Another reason is that frequency-independent GPR FWI, when combined with source signal estimation, can handle weak permittivity attenuation environments where quality factor ($Q$) $\geq 20$ (Belina *et al.* 2012). In the study of Belina *et al.* (2012), since their model gradients were practically the same as those of the frequency-independent GPR FWI and the static conductivity was ignored, researchers did a permittivity-only inversion with a priori $Q$ model. To better image the realistic materials with $Q < 20$ and investigate crosstalk between multiple parameters, frequency-dependent GPR FWI must be developed.

FWI is also known as an inverse scattering problem in the microwave community. Winters *et al.* (2006) proposed the time-domain inverse scattering technique to estimate the frequency-dependent average dielectric properties, using a short relaxation time approximation in Debye scatterers. Based on their work, Papadopoulos & Rekanos (2011) introduced an auxiliary differential equation (ADE) with the polarization current density, which extended the feasibility of microwave imaging. Deng *et al.* (2021) reported the high-performance computation of EM FWI in the single-pole Debye model, using the theoretical basis of the inverse scattering technique. These studies suggested that we can similarly develop frequency-dependent GPR FWI. Nevertheless, they did not give an explicit measure of permittivity attenuation in EM wave propagation, which makes the inversion algorithm less intuitive than viscoelastic FWI involving seismic attenuation.

In this paper, we use the $\tau$-method, with reference to the viscoelastic waves (Blanch *et al.* 1995), to quantify the attenuation of EM waves caused by the complex permittivity. Based on this, we modify the time-domain Maxwell's equations proposed by Bergmann *et al.* (1998) and implement the frequency-dependent GPR FWI. With a frequency dependence analysis, we show how each model parameter affects EM wave propagation, including amplitude attenuation and velocity dispersion. Finally, we apply 2-D GPR FWI in the synthetic examples and field examples and compare the performance of the FWI considering and not considering permittivity attenuation. Since surface-based GPR plays an important role for characterizing near-surface targets, we perform a surface-based GPR FWI in this study to investigate the applicability and limitations of using reflected waves.

## 2 METHODOLOGY

### 2.1 Forward problem

The propagation of EM waves in heterogeneous media can be expressed by Maxwell's equations as follows:

$$
\begin{aligned}
-\partial_t \mathbf{B} - \nabla \times \mathbf{E} &= 0, \\
-\nabla \times \mathbf{H} + \partial_t \mathbf{D} + \mathbf{J}_c &= -\mathbf{J}_c,
\end{aligned}
\tag{1}
$$

with three generalized constitutive relations:

$$
\begin{aligned}
\mathbf{B} &= \mu \mathbf{H}, \\
\mathbf{D} &= \varepsilon * \mathbf{E}, \\
\mathbf{J}_c &= \sigma * \mathbf{E},
\end{aligned}
\tag{2}
$$

where $\mathbf{B}$ is the magnetic flux, $\mathbf{H}$ is the magnetic field, $\mathbf{D}$ is the electric displacement and $\mathbf{E}$ is the electric field. $\mathbf{J}_c$ is the conduction current density and $\mathbf{J}_c$ is the electric current sources. $\nabla$ is the Laplace operator, $\times$ is the curl operator and $*$ is the time convolution. The magnetic permeability $\mu$ is essentially frequency independent, while the dielectric permittivity $\varepsilon$ and electrical conductivity $\sigma$ are described as complex frequency-dependent quantities (Carcione 1996; Bergmann *et al.* 1998). The attenuation and dispersion processes of EM waves depend on the $\varepsilon$ and $\sigma$ of the media.

Substituting eq. (2) into eq. (1), Maxwell's equations become

$$
\begin{aligned}
-\mu \partial_t \mathbf{H} - \nabla \times \mathbf{E} &= 0, \\
-\nabla \times \mathbf{H} + \varepsilon * \partial_t \mathbf{E} + \sigma * \mathbf{E} &= -\mathbf{J}_c.
\end{aligned}
\tag{3}
$$

In order to solve eq. (3) explicitly in the time domain, we must calculate the convolutions $\varepsilon * \partial_t \mathbf{E}$ and $\sigma * \mathbf{E}$. We use the Debye model (eq. 4) to approximate the relaxation function of the permittivity in the time domain (Carcione 1996), i.e. the frequency-dependent function

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022

506 T. Qin, T. Bohlen and N. Allroggen

in the frequency domain.

$$\varepsilon(t) = \partial_t \Psi_t(t) \quad \text{with} \quad \Psi_t(t) = \varepsilon_s \left[ 1 - \frac{1}{L} \sum_{l=1}^L \left( 1 - \frac{\tau_{EI}}{\tau_{DI}} \right) e^{-t/\tau_{DI}} \right] H(t), \quad (4)$$

where $\tau_{EI}$ and $\tau_{DI}$ are the relaxation times of the electric field and displacement of the $l$th Debye model, respectively. $\tau_{EI} < \tau_{DI}$ for the $l$th mechanism. $\tau_{DI} = 1/(2\pi f_l)$ where $f_l$ is the relaxation frequency of the $l$th Debye peak and $L$ is the number of relaxation mechanisms. $H(t)$ is the Heaviside function. $\varepsilon_s$ is the static dielectric permittivity, corresponding to the permittivity in the frequency-independent media. Following the $\tau$-method proposed by Blanch *et al.* (1995), we define the permittivity attenuation $\tau_s = 1 - \tau_{EI}/\tau_{DI}$ as the attenuation level of the $l$th Debye model for EM waves. By doing so, $\Psi_t$ can be rewritten as

$$\Psi_t(t) = \varepsilon_s \left( 1 - \tau_s \frac{1}{L} \sum_{l=1}^L e^{-t/\tau_{DI}} \right) H(t). \quad (5)$$

In eq. (5), one can see that $\tau_s$ is independent of the $l$th Debye model, which means the same $\tau_s$ can be used for different Debye models. The newly defined variable is dimensionless ($0 \leq \tau_s < 1$) and more straightforward for identifying attenuation and dispersion caused by the complex permittivity. Using the Debye model, the convolution $\varepsilon * \partial_t \mathbf{E}$ becomes

$$\varepsilon(t) * \partial_t \mathbf{E} = \partial_t \Psi_t(t) * \partial_t \mathbf{E} = \varepsilon_s (1 - \tau_s) \partial_t \mathbf{E} + \varepsilon_s \tau_s \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{DI}} \mathbf{E} + \sum_{l=1}^L \mathbf{r}_l. \quad (6)$$

Due to space limitations in the main content, we omit the computational process of convolution (readers can find details of eqs 6, 7, 10, and 11 in Appendix A). We introduce an ADE with a memory variable $\mathbf{r}_l$ of the $l$th mechanism corresponding to $\mathbf{E}$:

$$\partial_t \mathbf{r}_l = - \frac{\varepsilon_s \tau_s}{L \tau_{DI}^2} \mathbf{E} - \frac{1}{\tau_{DI}} \mathbf{r}_l. \quad (7)$$

Note that the definition of $\mathbf{r}_l$ is slightly different from the memory variable in Carcione (1996) and Bergmann *et al.* (1998). Similar to viscoelastic wave equations described in Bohlen (2002), we incorporate $\varepsilon_s$ into $\mathbf{r}_l$. By doing so, we can easily develop self-adjoint wave equations for GPR FWI (shown in Section 2.2). If only one Debye model is used, the memory variable $\mathbf{r}_l$ is related to the polarization current density $\mathbf{J}$ used in the microwave imaging of Papadopoulos & Rekanos (2011) by

$$\mathbf{J} = \mathbf{r}_l + \frac{\Delta \varepsilon}{\tau_{DI}} \mathbf{E} \quad \text{with} \quad \Delta \varepsilon = \varepsilon_s \tau_s \text{ and } l = 1. \quad (8)$$

On the other hand, the relaxation function of the conductivity can be described by a Kelvin–Voigt type model (Pipkin 2012) as

$$\sigma(t) = \partial_t \Psi_\sigma(t) \quad \text{with} \quad \Psi_\sigma(t) = \sigma_s [H(t) + \tau_\sigma \delta(t)], \quad (9)$$

where $\tau_\sigma$ is the relaxation time including the out-of-phase component of conductivity, $\sigma_s$ is the static conductivity, and $\delta(t)$ is the Dirac function. Then, the convolution $\sigma * \mathbf{E}$ becomes

$$\sigma(t) * \mathbf{E} = \partial_t \Psi_\sigma(t) * \mathbf{E} = \sigma_s (\mathbf{E} + \tau_\sigma \partial_t \mathbf{E}). \quad (10)$$

Hence, we replace two convolutions with multiplications

$$\varepsilon(t) * \partial_t \mathbf{E} + \sigma(t) * \mathbf{E} = \varepsilon_\infty^e \partial_t \mathbf{E} + \sigma_\infty^e \mathbf{E} + \sum_{l=1}^L \mathbf{r}_l, \quad (11)$$

with the effective optical permittivity $\varepsilon_\infty^e$ and effective optical conductivity $\sigma_\infty^e$ as below:

$$\varepsilon_\infty^e = \varepsilon_s (1 - \tau_s) + \sigma_s \tau_\sigma, \quad \sigma_\infty^e = \sigma_s + \varepsilon_s \tau_s \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{DI}}. \quad (12)$$

The real effective permittivity and real effective conductivity with respect to the angular frequency $\omega$ are given by (Bergmann *et al.* 1998)

$$\begin{aligned} \varepsilon^e(\omega) &= \varepsilon_s \left( 1 - \tau_s \frac{1}{L} \sum_{l=1}^L \frac{\omega^2 \tau_{DI}^2}{1 + \omega^2 \tau_{DI}^2} \right) + \sigma_s \tau_\sigma, \\ \sigma^e(\omega) &= \sigma_s + \varepsilon_s \tau_s \frac{1}{L} \sum_{l=1}^L \frac{\omega^2 \tau_{DI}^2}{1 + \omega^2 \tau_{DI}^2}. \end{aligned} \quad (13)$$

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022

FWI of GPR data in frequency-dependent media

507

In fact, the effective optical parameters are the real effective parameters at infinite frequency. The attenuation factor $\alpha$, phase velocity $v$ and quality factor $Q$ are described as (Turner & Siggins 1994)

$$\alpha = \omega \left[ \frac{\mu \varepsilon^e(\omega)}{2} \left( \sqrt{1 + \tan^2 \delta} - 1 \right) \right]^{1/2},$$

$$v = \left[ \frac{\mu \varepsilon^e(\omega)}{2} \left( \sqrt{1 + \tan^2 \delta} + 1 \right) \right]^{-1/2},$$

$$Q = \tan^{-1} \delta, \tag{14}$$

where the loss tangent $\tan \delta = \sigma^e(\omega) / [\omega \varepsilon^e(\omega)]$. With $\tan \delta = 1$, we obtain the transition angular frequency $\omega_t = 2\pi f_t = \sigma^e(\omega_t) / \varepsilon^e(\omega_t)$ where $f_t$ is the transition frequency. In frequency-independent media where $\tau_e = 0$, $\sigma_\infty^e$ can be simplified to $\sigma_s$. Therefore the attenuation is determined by $\sigma_s$ alone, which is called conductivity attenuation. In frequency-dependent media, however, both $\sigma_s$ and $\tau_e$ contribute to attenuation. Based on eqs (7) and (11), we rewrite eq. (3) as

$$-\mu \partial_t \mathbf{H} - \nabla \times \mathbf{E} = 0,$$

$$-\nabla \times \mathbf{H} + \varepsilon_\infty^e \partial_t \mathbf{E} + \sigma_\infty^e \mathbf{E} + \sum_{l=1}^L \mathbf{r}_l = -\mathbf{J}_e,$$

$$\mathbf{E} + \frac{L \tau_{Dl}^2}{\varepsilon_s \tau_e} \partial_t \mathbf{r}_l + \frac{L \tau_{Dl}}{\varepsilon_s \tau_e} \mathbf{r}_l = 0, \quad l = 1, \dots, L. \tag{15}$$

We solve eq. (15) using the FDTD method of second order in time and fourth order in space. In the standard staggered grid of Yee (1966), the memory variable $\mathbf{r}_l$ locates at the same position of the electric field $\mathbf{E}$. The electrical parameters $\varepsilon_\infty^e$, $\varepsilon_s$, $\sigma_\infty^e$ and $\tau_e$ are averaged to the location of $\mathbf{E}$, while the magnetic parameter $\mu$ is averaged to the location of the magnetic field $\mathbf{H}$. The convolutional perfectly matched layer is included at the model boundary to absorb the outgoing waves (Roden & Gedney 2000).

Unlike eqs (6)–(8) in Papadopoulos & Rekanos (2011), eq. (15) uses the effective optical conductivity, resulting from different definitions of the polarization current density and memory variable (see eq. 8). Our modification in eq. (15) takes three advantages of the $\tau$-method (Blanch et al. 1995). First, we use one $\tau_e$ for all Debye models and set $\tau_{Dl}$ as a priori, which means less memory usage and computations in numerical modelling of EM waves than using $\tau_{Dl}$ and $\tau_{Dl}$ for $L$ Debye models. Second, if $\sigma_s \ll \sigma_\infty^e$, we can simply approximate a constant $Q$ by $Q \approx 2/\tau_e$. Thus, the attenuation is similar to a linear function of frequency and the simulator can account for the waveform distortion of EM waves (see Section 3 for an example). Third, we use only one $\tau_e$ in eqs (13) and (14) to quantify the magnitude of attenuation and dispersion introduced by complex permittivity, which is intuitive and reduces the number of parameters reconstructed by frequency-dependent GPR FWI in Section 2.2.

For convenience, we express eq. (15) in a matrix–vector formalism

$$\mathbf{M}_1 \partial_t \mathbf{u} + \mathbf{M}_2 \mathbf{u} - \mathbf{A} \mathbf{u} = \mathbf{s}, \tag{16}$$

with

$$\mathbf{u} = \left( H_x, H_y, H_z, E_x, E_y, E_z, r_{x1}, r_{y1}, r_{z1}, \dots, r_{xL}, r_{yL}, r_{zL} \right)^T,$$

$$\mathbf{s} = \left( 0, 0, 0, -J_{xx}, -J_{yy}, -J_{zz}, 0, 0, 0, \dots, 0, 0, 0 \right)^T,$$

$$\text{diag}(\mathbf{M}_1) = \left( -\mu, -\mu, -\mu, \varepsilon_\infty^e, \varepsilon_\infty^e, \varepsilon_\infty^e, \frac{L \tau_{Dl}^2}{\varepsilon_s \tau_e}, \frac{L \tau_{Dl}^2}{\varepsilon_s \tau_e}, \frac{L \tau_{Dl}^2}{\varepsilon_s \tau_e}, \dots, \frac{L \tau_{DL}^2}{\varepsilon_s \tau_e}, \frac{L \tau_{DL}^2}{\varepsilon_s \tau_e}, \frac{L \tau_{DL}^2}{\varepsilon_s \tau_e} \right),$$

$$\mathbf{M}_2 = \begin{pmatrix} 0_3 & 0_3 & 0_3 & \dots & 0_3 \\ 0_3 & \sigma_\infty^e I_3 & I_3 & \dots & I_3 \\ 0_3 & I_3 & \frac{L \tau_{Dl}}{\varepsilon_s \tau_e} I_3 & & \\ \dots & \dots & & \ddots & \\ 0_3 & I_3 & & & \frac{L \tau_{Dl}}{\varepsilon_s \tau_e} I_3 \end{pmatrix}, \quad \mathbf{A} = \begin{pmatrix} 0_3 & D & 0_3 & \dots & 0_3 \\ D & 0_3 & 0_3 & \dots & 0_3 \\ 0_3 & 0_3 & 0_3 & \dots & 0_3 \\ \dots & \dots & & \ddots & \\ 0_3 & 0_3 & & & 0_3 \end{pmatrix},$$

$$D = \begin{pmatrix} 0 & -\partial_z & \partial_y \\ \partial_z & 0 & -\partial_x \\ -\partial_y & \partial_x & 0 \end{pmatrix} = D_1 \partial_x + D_2 \partial_y + D_3 \partial_z, \quad D_i^* = D_i^T = -D_i,$$

$$D_1 = \begin{pmatrix} 0 & 0 & 0 \\ 0 & 0 & -1 \\ 0 & 1 & 0 \end{pmatrix}, \quad D_2 = \begin{pmatrix} 0 & 0 & 1 \\ 0 & 0 & 0 \\ -1 & 0 & 0 \end{pmatrix}, \quad D_3 = \begin{pmatrix} 0 & -1 & 0 \\ 1 & 0 & 0 \\ 0 & 0 & 0 \end{pmatrix}, \quad D^T = D,$$

$$D^* = (D_i \partial_i)^* = -D_i^* \partial_i = D_i \partial_i = D \quad \Rightarrow \quad \mathbf{A}^* = \mathbf{A}, \tag{17}$$

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022

508 T. Qin, T. Bohlen and N. Allroggen

where $0_3$ is the $3 \times 3$ zero matrix and $I_3$ the $3 \times 3$ unit matrix. The superscript * is the transpose conjugate operator which is equivalent to transpose operator $T$ for real variables. When deriving the transpose conjugate of A, we use the zero-valued boundary condition, i.e. equations 54 and 55 in Yang et al. (2016).

## 2.2 Inverse problem

The objective function $\Phi$ that we use in GPR FWI is

$$\Phi(\mathbf{m}) = \Phi(\mathbf{u}) = \frac{1}{2} ||R\mathbf{u}(\mathbf{m}) - \mathbf{d}^{\mathrm{obs}}||_2^2 = \frac{1}{2} ||\Delta\mathbf{d}||_2^2, \quad (18)$$

where the synthetic data are extracted from the forward wavefield $\mathbf{u}$ at the receiver position by the restriction operator $R$; $\Delta\mathbf{d} = R\mathbf{u}(\mathbf{m}) - \mathbf{d}^{\mathrm{obs}}$ is the residual between the synthetic data and observed data $\mathbf{d}^{\mathrm{obs}}$. The FWI seeks to iteratively reconstruct the model parameters $\mathbf{m}$ by minimizing $\Phi$ as follows:

$$\mathbf{m}_{k+1} = \mathbf{m}_k + \lambda \Delta\mathbf{m}_{k+1}, \quad (19)$$

$$\Delta\mathbf{m}_{k+1} = -\mathbf{P} \frac{\partial \Phi}{\partial \mathbf{m}} + \gamma \Delta\mathbf{m}_k, \quad (20)$$

where the step length $\lambda$ is calculated by line search (Pica et al. 1990). Considering the different sensitivities of model parameters to the objective function, we use an individual step length for each parameter (Ernst et al. 2007b). The model update direction for the $(k+1)$th iteration $\Delta\mathbf{m}_{k+1}$ is computed by the conjugate-gradient method, where $\gamma$ is the scale factor (Polak & Ribiere 1969) and $\mathbf{P}$ is the pre-conditioner (Plessix & Mulder 2004). We use a multiscale strategy to avoid cycle skipping in FWI (Bunks et al. 1995). In the following, we show how to calculate the model gradient $\partial\Phi/\partial\mathbf{m}$.

Due to that $\mathbf{M}_1$, $\mathbf{M}_2$ and $\mathbf{A}$ are self-adjoint, we obtain the adjoint-state equations as follows (Plessix 2006):

$$-\mathbf{M}_1 \partial_t \dot{\mathbf{u}} + \mathbf{M}_2 \dot{\mathbf{u}} - \mathbf{A} \dot{\mathbf{u}} = -R^* \Delta\mathbf{d},$$
$$\dot{\mathbf{u}} = \left( \hat{H}_x, \hat{H}_y, \hat{H}_z, \hat{E}_x, \hat{E}_y, \hat{E}_z, \hat{r}_{x1}, \hat{r}_{y1}, \hat{r}_{z1}, \dots, \hat{r}_{xL}, \hat{r}_{yL}, \hat{r}_{zL} \right)^T, \quad (21)$$

where the waveform residual $R^* \Delta\mathbf{d}$ is used as the adjoint sources for backpropagation and $\dot{\mathbf{u}}$ is the adjoint wavefield. In contrast to the forward problem, the computation of eq. (21) is done backward from the recording time $T$ to 0. Hence we reverse the time by substituting $t' = T - t$, $\dot{\mathbf{u}}'(t') = \dot{\mathbf{u}}(T - t)$ and $\Delta\mathbf{d}'(t') = \Delta\mathbf{d}(T - t)$ in the above equation and get the self-adjoint-state equations as below:

$$\mathbf{M}_1 \partial_t \dot{\mathbf{u}}' + \mathbf{M}_2 \dot{\mathbf{u}}' - \mathbf{A} \dot{\mathbf{u}}' = -R^* \Delta\mathbf{d}',$$
$$\dot{\mathbf{u}}' = \left( \hat{H}_x', \hat{H}_y', \hat{H}_z', \hat{E}_x', \hat{E}_y', \hat{E}_z', \hat{r}_{x1}, \hat{r}_{y1}, \hat{r}_{z1}, \dots, \hat{r}_{xL}, \hat{r}_{yL}, \hat{r}_{zL} \right)^T. \quad (22)$$

Then we cross-correlate the forward wavefield $\mathbf{u}$ and the back-propagating wavefield $\dot{\mathbf{u}}$ to compute the model gradient

$$\frac{\partial \Phi}{\partial \mathbf{m}} = \int_0^T \dot{\mathbf{u}}(t) \left( \frac{\partial \mathbf{M}_1}{\partial \mathbf{m}} \partial_t \mathbf{u}(t) + \frac{\partial \mathbf{M}_2}{\partial \mathbf{m}} \mathbf{u}(t) \right) dt$$
$$= \int_0^T \dot{\mathbf{u}}'(T - t) \left( \frac{\partial \mathbf{M}_1}{\partial \mathbf{m}} \partial_t \mathbf{u}(t) + \frac{\partial \mathbf{M}_2}{\partial \mathbf{m}} \mathbf{u}(t) \right) dt. \quad (23)$$

Eqs (22) and (23) indicate two advantages of our modification in eq. (15). One advantage is that we can use the same forward solver for the forward and back-propagating wavefield simulations without any additional programming works. Another advantage is that all model parameters are distributed at the diagonal positions of $\mathbf{M}_1$ and $\mathbf{M}_2$, which means that the form of model gradients is very simple (see Appendix B for details).

Theoretically, in eq. (23), $\mathbf{m}$ can be any model parameter of eq. (15). However, we are only interested in the electrical parameters $\mathbf{m} = (\varepsilon_{\infty}^e, \sigma_{\infty}^e, \varepsilon_s, \tau_s)$ in GPR FWI. According to eq. (12) and the chain rule, we convert the gradient of the objective function from the parameter class $\mathbf{m} = (\varepsilon_{\infty}^e, \sigma_{\infty}^e, \varepsilon_s, \tau_s)$ to $\mathbf{m}' = (\varepsilon_s', \sigma_s, \tau_s', \tau_s)$ where $\varepsilon_s' = \varepsilon_s$ and $\tau_s' = \tau_s$ (see Appendix B for details):

$$\frac{\partial \Phi}{\partial \mathbf{m}'} = \frac{\partial \Phi}{\partial \mathbf{m}} \frac{\partial \mathbf{m}}{\partial \mathbf{m}'} \quad (24)$$

In this study, we use the real effective permittivity $\varepsilon^e$ and real effective conductivity $\sigma^e$ at the reference angular frequency $\omega_0$ as the input and output parameters of GPR FWI, where $\omega_0$ is set as the peak frequency of the source wavelet. Thus we ensure the physical consistency of the results obtained by frequency-dependent GPR FWI and frequency-independent GPR FWI, similar to the correction for the phase velocity in viscoacoustic FWI (Kurzmann et al. 2013). In the following sections, $\varepsilon^e(\omega_0)$ and $\sigma^e(\omega_0)$ will be referred to as the permittivity $\varepsilon$ (or relative permittivity $\varepsilon_r$) and the conductivity $\sigma$ for convenience if not explicitly stated. In frequency-dependent GPR FWI, one can update the static parameters ($\varepsilon_s$ and $\sigma_s$) using the gradients calculated by eq. (24), or update the effective parameters ($\varepsilon$ and $\sigma$) by applying the chain rule again based on eq. (13) (see eq. B8 for details).

Downloaded from https://academic.oup.com/gj/article/2/32/1/504/6670780 by KIT Library user on 25 October 2022

FWI of GPR data in frequency-dependent media

509

![img-0.jpeg](img-0.jpeg)

Figure 1. (a) Radargrams generated by a shifted 50 MHz Ricker source in 1-D homogeneous media and obtained by the receiver 10 m offset away from the source. The traces are normalized by their maximum amplitudes. (b) Corresponding amplitude spectra. The spectra are divided by the maximum amplitude of the thick black line. The translucent grey area represents the amplitude spectrum of the source wavelet, and the thin dashed line marks the peak frequency. One relaxation mechanism is used when $\tau_{\varepsilon} = 0.2$ (the blue line).

### 3 FREQUENCY DEPENDENCE ANALYSIS

In order to analyse the effect of different model parameters on EM wave propagation, we make a comparison experiment using the 1-D analytical solution of EM wave in homogeneous media (Blanch et al. 1995). As shown in Fig. 1, we discuss three kinds of typical media in this section. All media have the same relative permittivity ($\varepsilon_{r} = 6$) so that the signals at the reference frequency propagate with the same phase velocity. The latter two attenuating media have the same conductivity ($\sigma = 2 \text{ mS m}^{-1}$) in order to generate the same attenuation level at the reference frequency. We take the wave propagation in a non-attenuating medium as a reference (the thick black line). One relaxation mechanism is employed in frequency-dependent medium where $\tau_{\varepsilon} = 0.2$ and $\sigma_{\varepsilon} = 0.1 \text{ mS m}^{-1}$. Thus, according to eq. (13), the permittivity attenuation $\tau_{\varepsilon}$ dominates the conductivity (95 per cent) and contributes to the permittivity slightly (10 per cent) at the reference frequency. We set the relaxation time of the conductivity $\tau_{\sigma} = 0$ s in this paper so that we can focus more on the effect of $\tau_{\varepsilon}$ on the data. The value of $\tau_{\varepsilon}$ is chosen to approximate a constant $Q (= 10)$ which has been observed in some geological materials (Turner & Siggins 1994).

Compared to the reference medium, the attenuating media lead to a significant decrease in amplitude in Fig. 1(b). We observe different waveform and amplitude decreases in the frequency-dependent medium (the blue line) where $\tau_{\varepsilon}$ works as a low-pass filter, with more attenuation at frequencies above the peak frequency and less attenuation in the other frequency ranges. This is presented as a shift of the amplitude spectrum towards lower frequencies in Fig. 1(b), corresponding to the waveform deformation in Fig. 1(a). In contrast, the conductivity attenuation medium scales the amplitude of different frequencies equally, without changing the waveform shape.

To find the reasons of these phenomena, we show the phase velocity $v$, attenuation factor $\alpha$ and quality factor $Q$ with respect to frequency in Figs 2(a)–(c). Those three characteristics are computed from the real effective parameters shown in Figs 2(d) and (e) through eq. (14). The reference medium has infinite $Q$ value, no attenuation, and a constant velocity. Along with the dominant frequency range of the source wavelet (25–80 MHz), the conductivity attenuation medium has a linear increase of the quality factor, almost the constant attenuation level, and similar velocity with the reference medium due to that the transition frequency ($\approx 6$ MHz) is much smaller than the peak frequency of the source wavelet (50 MHz). That results in almost identical travel time and amplitude changes of different frequency components in Fig. 1. Unlike the frequency-independent media, the frequency-dependent medium causes both phase velocity and attenuation factor to increase with frequency in the dominant frequency region, which is the reason for distorting the waveform and amplitude spectrum in Fig. 1. Although we use only one relaxation mechanism, the $Q$ approximated is close to the desired value. With more relaxation mechanisms, the $Q$ approximation can be further improved. As shown in Figs 2(d) and (e), dielectric permittivity and electrical conductivity are frequency-independent in the reference medium and conductivity attenuation medium and become frequency-dependent in the permittivity attenuation medium. When the frequency is greater than 25 MHz, the conductivity is proportional to the attenuation factor, and the permittivity is inversely proportional to the square of phase velocity.

### 4 INVERSION OF SYNTHETIC DATA

We use several synthetic examples of 2-D models ($x$–$z$ plane) to analyse the performance of frequency-dependent GPR FWI. Transverse magnetic (TM) mode waves are used in the simulation and inversion of GPR surface recordings. In frequency-independent media, there are wavefield components $H_{x}$, $H_{y}$ and $E_{y}$ and reconstructed model parameters $\varepsilon$ and $\sigma$. In frequency-dependent media, additional memory variable $r_{vl}$ and reconstructed model parameters $\tau_{\sigma}$ and $\tau_{\varepsilon}$ are added with $L = 1$. The magnetic permeability $\mu$ is constant and equal to its value of vacuum. We set $\tau_{\sigma} = 0$ s based on the analysis in the previous section.

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022

510 T. Qin, T. Bohlen and N. Allroggen

![img-1.jpeg](img-1.jpeg)

**Figure 2.** Frequency-dependent media characteristics. (a) Quality factor, (b) attenuation factor, (c) phase velocity, (d) real effective conductivity and (e) real effective permittivity. The translucent grey area represents the amplitude spectrum of the source wavelet, and the thin dashed line marks the peak frequency. The thin black line in (a) shows the desired $Q$ value ($Q = 10$). Note that $Q$ is infinite for the non-attenuating medium (the thick black line) and therefore not displayed in (a).

![img-2.jpeg](img-2.jpeg)

**Figure 3.** Models of the three-parameter synthetic example where all anomalies are spatially uncorrelated. The three columns are the true models, the frequency-dependent GPR FWI results and the frequency-independent GPR FWI results ($\varepsilon_r$ and $\sigma$), respectively. The red stars on the true model are the transmitters.

The EM model space shown in Fig. 3 is 10 m $\times$ 36 m, and the grid spacing is 0.1 m. The three-layer background parameters are set according to Table 1. As the 2-m-thick air layer above the ground is not updated during the inversion, we do not show it in the figures of this paper. The true model for the synthetic examples consists of the background model and triangular perturbations, where the permittivity perturbations are relatively weak, so that we can better study the reconstruction of the conductivity and permittivity attenuation models in the inversion. Receivers are placed on the ground at 0.2 m intervals to record the radargrams of the electric field component with a time sampling of 0.15 ns and a time window of 300 ns. Eighteen transmitters generate the electric field at 2 m intervals on the ground (see red stars in Fig. 3). The source is a shifted Ricker wavelet with a centre frequency of 50 MHz. For each source, the receivers record data with an offset of 1–20 m.

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022

FWI of GPR data in frequency-dependent media 511

We build a true model consisting of the background

|  Layer | Thickness (m) | ε_{r} (-) | σ (mS m^{-1}) | τ_{ε} (-)  |
| --- | --- | --- | --- | --- |
|  Air | 2 | 1 | 0 | 0  |
|  Soil | 6 | 6 | 2 | 0.1  |
|  Rock | 2 | 9 | 3 | 0.1  |

The observed data are simulated in the true model and are the same for the frequency-dependent GPR FWI and frequency-independent GPR FWI (τ$_{ε}$ = 0). The minimum wavelength of the EM waves observed in the soil layer is about 1 m.

We use the background model (Table 1) as the initial model to perform FWI. The model parameters are updated simultaneously in multiparameter inversion examples. Apart from the pre-conditioner shown in eq. (20), we also multiply the gradient by a user-defined taper to mitigate source and receiver artefacts. We use a multiscale strategy with five inversion stages and up to 15 iterations per stage. From the first stage to the fifth stage, we sequentially implement frequency band variations from 5 to 15, 25, 35, 50, and 80 MHz in a Butterworth bandpass filter. At the beginning of each stage, we apply the source-time function (STF) inversion (Groos *et al.* 2014). If the relative misfit change between the current iteration and the previous second iteration is less than 1 per cent, the inversion will switch to the next stage or stop if it is the last stage.

## 4.1 Uncorrelated model

### 4.1.1 Noise-free data

We build a true model consisting of the background model and several trench anomalies (triangles) spatially uncorrelated on each model. In Fig. 3, variations in the static parameters lead to anomalies in permittivity and conductivity models. To insulate the permittivity and conductivity models from permittivity attenuation anomalies, we adjust these static parameters at locations where τ$_{ε}$ anomalies exist. The strong crosstalks between ε$_{r}$, σ$_{r}$, and τ$_{ε}$ occur in the frequency-dependent GPR FWI results. In the conductivity model, we observe original conductivity anomaly and severe footprints generated by the anomalies of permittivity and τ$_{ε}$. Frequency-independent GPR FWI suffers even more from the crosstalks, which makes the original conductivity anomaly indistinguishable. In frequency-independent GPR FWI, more artefacts appear in the non-anomalous area of the permittivity and conductivity models because of the absence of permittivity attenuation. Although permittivity attenuation is weakly sensitive to the data, it is helpful for the correct reconstruction of the conductivity anomaly (the last trench) in the frequency-dependent GPR FWI.

To further investigate the performance of two FWIs, we compare the observed data and inverted data in Figs 4(a) and (b). In the observed data, the ground wave travels faster in the first source than in the last source due to the permittivity anomaly on the left side. The reflected wave of the first source propagates along the low permittivity attenuation anomaly (τ$_{ε}$ = 0) and shows a lower amplitude than that of the last source at an offset of 10–20 m, similar to the observation in Fig. 1(b). In GPR FWI, the STF inversion can provide an “effective” source wavelet that is low-pass filtered (Belina *et al.* 2012). Thus it can account for the frequency-dependent effects of EM waves in weak permittivity attenuation environments (Q ≥ 20 and τ$_{ε}$ ≤ 0.1). Nevertheless, after travelling through the high permittivity attenuation regions, such an ‘effective’ source may generate waveforms different from the observed data, e.g., the reflected wave with offsets greater than 10 m in Fig. 4(b). As a consequence, frequency-independent GPR FWI attributes the waveform differences to perturbations throughout the model space, resulting in some unwanted artefacts in Fig. 3. On the contrary, frequency-dependent GPR FWI can reconstruct trench anomalies in the permittivity and conductivity models and reduce artefacts due to its ability to describe permittivity attenuation. Frequency-dependent GPR FWI, therefore, agrees highly with the observed data. This example illustrates that the combination of frequency-independent GPR FWI and STF estimates can only partially explain the waveform distortions caused by permittivity decay. It is necessary to consider frequency-dependent GPR FWI when reconstructing the conductivity model.

### 4.1.2 Noise-contaminated data

In the synthetic example above, the observed data are free of noise. It is unrealistic and may lead us to overestimate the performance of the GPR FWI approaches. Therefore, starting from this section, we add Gaussian noise with a signal-to-noise ratio (SNR) of 20 dB, with respect to the strongest amplitude, to the observed data. As a result, the reflected waves in the observed data shown in Figs 4(c) and (d) are heavily disturbed and below the noise level after a 15 m offset. We repeat the synthetic example using noisy data and present the inversion results in Fig. 5.

Compared to Fig. 3, we see fewer model updates of the two FWIs in Fig. 5. It is reasonable as noise slows down the convergence of data misfits. On the one hand, the reconstructions of the four trenches more or less deteriorate. On the other hand, the crosstalks and artefacts are also suppressed. Consequently, frequency-independent GPR FWI shows clearer results of the conductivity model where the original conductivity anomaly becomes distinguishable. Fig. 4 also indicates that the existence of noise increases the difficulty of data fitting. In the last radargram, the two FWIs using noisy data have fewer differences in the waveform than those using noise-free data. To some extent,

Downloaded from https://academic.oup.com/gj/article/232/1/504/667/780 by KIT Library user on 25 October 2022

512 T. Qin, T. Bohlen and N. Allroggen

![img-3.jpeg](img-3.jpeg)

**Figure 4.** Data fitting of the three-parameter synthetic example where all anomalies are spatially uncorrelated. Gaussian noise (SNR = 20 dB) is added to the observed data in (c) and (d). (a and c) and (b and d) are the radargrams of the first and last sources, shown once every eight traces. Each trace is divided by the maximum amplitude of each trace of the observed data. The rectangular windows show the zoomed waveforms. A Butterworth bandpass filter (5–80 MHz in the fifth stage) is applied to the radargrams.

noise stabilizes frequency-independent GPR FWI and allows it to converge to better results than the noise-free case. Overall, frequency-dependent GPR FWI still possesses fewer data misfits and model artefacts than frequency-independent GPR FWI when the observed data are contaminated by noise.

## 4.2 Correlated model

### 4.2.1 Three-parameter model

In the true model of this example, the perturbations of the permittivity and conductivity models are located at the same position and have the same values in all trenches. However, the static permittivity and static conductivity in each trench are different due to the variations of the permittivity attenuation model. In Fig. 6, we see that frequency-dependent GPR FWI and frequency-independent GPR FWI have similar

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022

FWI of GPR data in frequency-dependent media

513

![img-4.jpeg](img-4.jpeg)

Figure 5. Models of the three-parameter synthetic example where all anomalies are spatially uncorrelated. Gaussian noise (SNR = 20 dB) is added to the observed data. The three columns are the true models, the frequency-dependent GPR FWI results and the frequency-independent GPR FWI results ($\varepsilon_r$ and $\sigma$), respectively.

![img-5.jpeg](img-5.jpeg)

Figure 6. Models of the three-parameter synthetic example where all anomalies are spatially correlated. Gaussian noise (SNR = 20 dB) is added to the observed data. The three columns are the true models, the frequency-dependent GPR FWI results and the frequency-independent GPR FWI results ($\varepsilon_r$ and $\sigma$), respectively.

performance in terms of reconstructing the permittivity model. The estimation of the conductivity perturbation deteriorates from left to right as permittivity attenuation increases. Besides, frequency-dependent GPR FWI shows more in-trench reconstructions than frequency-independent GPR FWI. In the frequency-independent GPR FWI results, the upper boundary of the last conductivity trench becomes discontinuous and only the two sides can be distinguished. On the contrary, frequency-dependent GPR FWI still reconstructs the four conductivity trenches with good resolution, although the first two trenches in the permittivity attenuation model are incorrectly estimated.

### 4.2.2 Two-parameter model

We perform another two tests to investigate the crosstalk of different parameters in the GPR FWI. Fig. 7 shows the same true models of $\varepsilon$ and $\tau_\varepsilon$ as Fig. 6. The static conductivity model is adjusted so that the conductivity model is unchanged. The increasing values of $\tau_\varepsilon$ from the left to the right trench means that the percentage of $\tau_\varepsilon$ in permittivity increases from 0 to 10 per cent. We observe heavy crosstalks between $\tau_\varepsilon$ and $\varepsilon$ in the results of frequency-dependent GPR FWI. The four permittivity attenuation trenches are described as high-value anomalies, and the four permittivity trenches are recovered to different degrees. For example, the last trench is reconstructed better than the first one, even

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022

514 T. Qin, T. Bohlen and N. Allroggen

![img-6.jpeg](img-6.jpeg)

Figure 7. Models of the two-parameter synthetic example where all anomalies are caused by the static permittivity $\varepsilon_s$ and permittivity attenuation $\tau_s$. Gaussian noise (SNR = 20 dB) is added to the observed data. The three columns represent the true models, the frequency-dependent GPR FWI results and the frequency-independent GPR FWI result ($\varepsilon_r$), respectively.

![img-7.jpeg](img-7.jpeg)

Figure 8. Models of the two-parameter synthetic example where all anomalies are caused by the static conductivity $\sigma_s$ and permittivity attenuation $\tau_s$. Gaussian noise (SNR = 20 dB) is added to the observed data. The three columns represent the true models, the frequency-dependent GPR FWI results and the frequency-independent GPR FWI result ($\sigma$), respectively.

though they have the same value in the true model. This should attribute to the more realistic dispersion and attenuation in the last trench. These differences also occur in the permittivity result of frequency-independent GPR FWI. Since the small effect of $\tau_s$ on the phase velocity (see Fig. 2c), the permittivity results obtained from frequency-dependent GPR FWI has only a slight improvement compared to that from frequency-independent GPR FWI (Fig. 7).

When it comes to the synthetic example of $\sigma$ and $\tau_s$ shown in Fig. 8, we adapt the static permittivity to make permittivity the same as the background values. Although four conductivity anomalies look the same in the true model, they are combinations of different static conductivity and permittivity attenuation. The percentage of $\tau_s$ in these conductivity anomalies increase from 0 in the first one to 75 per cent in the last one. We observe severe interference of conductivity on permittivity attenuation in the results of frequency-dependent GPR FWI, where all $\tau_s$ anomalies are reconstructed as high values. Similar to that shown in Fig. 6, it is difficult for frequency-independent GPR FWI to recover the conductivity anomalies dominated by permittivity attenuation. In the permittivity attenuation model reconstructed by frequency-dependent GPR FWI, the conductivity model introduces crosstalks that become weaker with depth (Fig. 8), while the permittivity model causes crosstalks around the trench boundaries and soil–rock interface (Fig. 7). It is due to different sensitivity kernels of permittivity and conductivity in FWI (Meles et al. 2011). Therefore, in Fig. 6, we observe a superposition of these effects when reconstructing three parameters simultaneously.

## 5 INVERSION OF FIELD DATA

### 5.1 Data acquisition and pre-processing

We conducted field measurements at the northeast corner of the gliding airfield in Rheinstetten, Germany. This test site is well known from previous GPR and seismic studies (Schaneng 2017; Wegscheider 2017; Pan et al. 2018, 2021; Wittkamp et al. 2019; Gao et al. 2020; Irnaka

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022

FWI of GPR data in frequency-dependent media 515

![img-8.jpeg](img-8.jpeg)

**Figure 9.** Models of the field data example in the Rheinstetten test site. The three columns are the initial models, the frequency-dependent GPR FWI results and the frequency-independent GPR FWI results, respectively. The white dashed triangle in the initial model outlines the target trench, known as the Ettlinger Line. The red stars are the transmitters, and the dense black triangles are the receivers of the 16th transmitter.

**Table 2.** Acquisition parameters of the surface GPR data (200 MHz) in the Rheinstetten test site and those used within the FWI.

|  Parameters | Raw | FWI  |
| --- | --- | --- |
|  Number of sources | 165 | 18  |
|  Traces per gather | 56–125 | 100–175  |
|  Transmitter spacing | ~ 0.2 m | 2 m  |
|  Receiver spacing | ~ 0.1 m | 0.04 m  |
|  Minimum offset | 0.2 m | 0.3 m  |
|  Maximum offset | 17 m | 8 m  |
|  Sample rate | 0.2 ns | 0.08 ns  |
|  Recording window | 200 ns | 164 ns  |

*et al.* (2022). It is covered by sediments consisting of gravel and sand from the Rhine river. The ground layer is composed of partially saturated soil. At the test site, a defensive “V” shaped trench named Ettlinger Line (dashed triangle in Fig. 9) was built in the early 17th century and has been refilled and is now completely flattened to the surface. The existence and shape of the Ettlinger Line have been delineated in detail via 3-D GPR migration imaging (Wegscheider 2017), 3-D Rayleigh-wave dispersion inversion (Schaneng 2017; Pan *et al.* 2018), 2-D joint elastic FWI of Rayleigh and Love waves (Wittkamp *et al.* 2019), 2-D viscoelastic FWI of Rayleigh waves (Gao *et al.* 2020), and 3-D viscoelastic FWI of the surface waves (Pan *et al.* 2021; Irnaka *et al.* 2022).

The surface GPR profile is positioned perpendicular to the Ettlinger Line. The two ends of the profile (from southwest to northeast) are in the same location as ‘C’ and ‘B’ in fig. 1(a) in Pan *et al.* (2018). The acquisition settings for the surface GPR data are listed in Table 2. Our GPR data were recorded using a single-channel pulseEKKO Pro GPR system equipped with a pulseEKKO Ultra receiver. The Ultra receiver stacked the records 256 times to obtain a higher SNR by reducing the random noise. The nominal centre frequency of the transmitter is 200 MHz. We deployed the transmitter–receiver orientation in HH mode to acquire TM wave data. The receiver was mounted on a sledge for smooth movement and tracked at the centimetre level by employing a real-time kinematic (RTK) positioning using a self-tracking total station as presented by Boniger & Tronicke (2010). To obtain multioffset GPR data for one source, we fixed the transmitter and moved the receiver towards the transmitter. Then we changed the transmitter location and moved the receiver away from the transmitter to produce the next gather. It took us two minutes to record one radargram and six hours for all 165 radargrams. Our measurements were slower than those of Lavoué (2014) who extracted hundreds of multioffset gathers from 15 common-offset gathers with an offset interval of 0.5 m. However, each trace in the multioffset GPR data used in Lavoué (2014) might be generated by a different transmitter-ground coupling. In contrast, our measurement had the same transmitter-ground coupling in one gather and had denser receiver intervals (~0.1 m).

In order to apply the FWI, we have to pre-process the GPR data first. The steps for data pre-processing are listed in Table 3, similar to those used in Domenzain *et al.* (2021). Due to the uneven walking speed of the worker when moving the sledge, the data we acquired has irregular trace spacing. To ensure a balanced illumination in the measurement area, we apply the data gridding, that is 2-D spline interpolation in the time-offset domain at regular trace spacing. Finally, we transform the data acquired in the 3-D world into 2-D line-source data because

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022

516 T. Qin, T. Bohlen and N. Allroggen

Table 3. Surface GPR data (200 MHz) pre-processing steps.

|  (1) | Data resampling in the frequency domain  |
| --- | --- |
|  (2) | Interpolation of clipped direct-arrival amplitudes  |
|  (3) | DC-shift removal and dewow  |
|  (4) | Bandpass filtering (5–400 MHz)  |
|  (5) | Bad traces removal and offset limitation  |
|  (6) | Data gridding in the time-offset domain  |
|  (7) | 3-D / 2-D transformation  |

we use a 2-D forward solver in GPR FWI. We use the transformation of the reflected waves to correct for phase and amplitude differences between the 3-D and 2-D data (Forbriger et al. 2014).

## 5.2 Data inversion

We build an initial model (7 m × 45.2 m with a grid spacing of 0.04 m) in Fig. 9, which does not show the air layer of 1 m thickness. The topographical variations along the survey line are minor and therefore ignored. The initial relative permittivity is 9 at the ground (the velocity of ground wave is 0.1 m ns⁻¹) and decreases slightly to 8 at a depth of 6 m. On the other hand, the initial conductivity is 6 mS m⁻¹ at the ground and decreases gradually to 2 mS m⁻¹ at a depth of 6 m. The initial permittivity attenuation is 0.1. We use similar inversion settings as the synthetic examples presented in the previous section, except that the frequency bands vary from 5 to 30, 40, 50, 70, and 100 MHz. These bands are chosen to avoid cycle skipping in GPR FWI since our initial model is relatively simple (Bunks et al. 1995). In frequency-dependent GPR FWI, the relaxation frequency of the Debye model fᵢ is 50 MHz and the reference angular frequency ω₀ = 2πfᵢ, ensuring that the conclusions we drew in Sections 3 and 4 are still applicable to the field data example. To save computational time, we select 18 gathers for FWI with a source interval of 2 m (see Table 2).

The reconstructed permittivity models of the two FWIs in Fig. 9 illustrate the presence of a triangular anomaly, the Ettlinger Line, which is in high agreement with the 3-D GPR migration results of Wegscheider (2017). On the right of the trench, we observe a strong permittivity contrast (a slightly right-tilted reflector) at 1.1–1.5 m depth, described as a low S-wave anomaly in the 3-D shallow-seismic FWI results of Pan et al. (2021) and Imaoka et al. (2022). Unlike the shallow-seismic FWI with a resolution of 1 m, GPR FWI has a much higher resolution (~0.25 m). Consequently, the reflector appears to be connected to the trench in the GPR FWI results, whereas their connection is more ambiguous in the shallow-seismic FWI results. One cannot observe the same reflector on the left side of the trench because the ground surface on this side was higher than on the right side and has been levelled [see schematics in fig. 3 in Imaoka et al. (2022)]. This implies that the reflector might be the original ground surface. Besides, both FWIs reveal a conductive layer near the ground and ranging from a thickness of 1.0 m on the left to 1.5 m on the right. More importantly, frequency-dependent GPR FWI reconstructs a permittivity attenuation model consistent with the permittivity model, where the Ettlinger Line is also visible.

The main differences between the two FWIs come from the right part of the highly conductive layer. This part is discontinuous and more similar to the permittivity model in frequency-independent GPR FWI. To understand these differences, we show the radargrams of the 16th source and the estimated source signals in Fig. 10. For both FWIs, the air and ground waves are difficult to fit because we use a 3-D / 2-D transformation of the reflected wave, and the line source cannot describe the radiation patterns and antenna-ground coupling in the real world. In the 16th radargram, the reflected waves become dominant at offsets greater than 2 m due to the strong permittivity contrast on the right side of the trench. Frequency-independent GPR FWI matches well to the reflection events with offsets shorter than 4 m, beyond 4 m its performance degrades. Frequency-dependent GPR FWI better fits the amplitude of reflection events at offsets greater than 4 m. It results from the high permittivity attenuation layer on the right of the trench, similar to the case in Fig. 4. The two FWIs have similar final data misfits (difference less than 1 per cent) due to strong decay characteristics of the surface recordings along the offset direction. Nevertheless, from the perspective of reflection fitting, frequency-dependent GPR FWI performs better and thus probably produces a more reliable conductivity model. Note that we acquired the first 11 radargrams on the first day and the last 7 radargrams on the second day. The estimated source signals of the first 11 sources are different from the last 7 sources in Fig. 10(b), probably due to coupling differences caused by slight near-surface moisture variations resulting from drying or wetting at night. However, the source signals used on the same day show similar waveform shapes and travel times, which indicates the stability of the two FWIs and source wavelet estimation.

## 6 DISCUSSION

In the examples of frequency dependence analysis and inversion, we ignore the relaxation time of conductivity (τₐ = 0 s) and use only one relaxation mechanism (L = 1) for costing purposes. The importance of considering τₐ > 0 s and L > 1 deserves further study. In the field example, the reconstructed permittivity attenuation model delineates the subsurface targets and provides a meaningful geological interpretation. Its high heterogeneous distribution also demonstrates the necessity of including it in the inversion. Based on our observation, we regard it still to be challenging to accurately estimate the permittivity attenuation model due to its weak sensitivity to the data and the crosstalk between multiple parameters. To better image the permittivity attenuation, two strategies are available. One strategy is to decouple the radiation patterns of the reconstructed parameters. It requires choosing a suitable parametrization so that different gradients have opposite

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022

FWI of GPR data in frequency-dependent media

517

![img-9.jpeg](img-9.jpeg)

Figure 10. (a) Data fitting of the 16th radargram of the field data example in the Rheinstetten test site, shown once every 20 traces. Each trace is divided by the maximum amplitude of each trace of the observed data. The rectangular window shows the zoomed waveforms. (b) Estimated source signals of two FWIs. The green and yellow lines mark the sources used on different days. A Butterworth bandpass filter (5–100 MHz in the fifth stage) is applied to the radargrams.

behaviour with respect to azimuth (Yao et al. 2018). Another strategy is to use the Hessian operator computed by Newton's method in optimization (Métivier et al. 2013; Operto et al. 2013; Gao et al. 2021). Truncated Newton method has been employed in frequency domain GPR FWI by Pinard et al. (2015). When it is introduced to the time domain GPR FWI, we have to find a balance between the elimination of crosstalk and the increase in computational cost, which needs further investigation.

Previous studies have shown the potential of joint inversion because other data can provide some complementary information to the GPR inversion (Linde et al. 2008; Domenzain et al. 2020; Qin et al. 2022). For example, the electrical resistivity (ER) data are sensitive to electrical conductivity. Therefore, the joint inversion of GPR and ER data may help to improve the reconstruction of conductivity (Domenzain et al. 2021). Note that the estimated conductivity is frequency-dependent in our GPR FWI, but frequency-independent in the ER inversion. Transformation of the two can be achieved by eq. (13), but depends on the reliability of the permittivity attenuation reconstruction, which requires further improvement in the future.

## 7 CONCLUSION

In this paper, we quantified permittivity attenuation for EM wave propagation simulator using the τ-method introduced from the seismic community, which not only saves memory and reduces computations in forward modelling but also simplifies the constant Q approximation and frequency-dependent GPR FWI. By defining the parameter ττ, we proposed a new form of time-domain Maxwell's equations to describe the propagation of EM waves in frequency-dependent media. These equations have two advantages in GPR FWI. The first one is their self-adjoint property, which allows performing frequency-dependent GPR FWI without changing the backpropagation engine. The second advantage is that the model gradients derived from these equations are fairly simple, ensuring as few modifications as possible to the existing frequency-independent GPR FWI code. Frequency dependence analysis revealed that, in the GPR spectrum range, the attenuation caused by the static conductivity is frequency-independent, while that caused by ττ is frequency-dependent. The permittivity attenuation acts as a low-pass filter and leads to waveform deformation and less amplitude decay of EM waves.

The 2-D synthetic examples confirmed the effectiveness and limitations of frequency-dependent GPR FWI. The spatially uncorrelated examples indicated that surface multioffset GPR data are weakly sensitive to permittivity attenuation compared to permittivity and conductivity. They also demonstrated that both frequency-dependent GPR FWI and frequency-independent GPR FWI suffer heavy crosstalk of different parameters. The spatially correlated examples showed that frequency-dependent GPR FWI works well in estimating the permittivity and conductivity models coupled with different permittivity attenuation levels, and frequency-independent GPR FWI produces comparable permittivity results as the dispersion effect is weak. Although combined with STF estimation, frequency-independent GPR FWI cannot handle the reconstruction of conductivity anomalies dominated by permittivity attenuation. In this case, frequency-dependent GPR FWI can provide more reliable conductivity results even if the permittivity attenuation models fail to be estimated and the observed data contain a

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022

518 T. Qin, T. Bohlen and N. Allroggen

degree of noise. These synthetic examples suggested the need for frequency-dependent GPR FWI in the presence of dispersion effects and variable attenuation.

When applying to field data acquired at the Rheinstetten test site, both frequency-dependent GPR FWI and frequency-independent GPR FWI successfully outlined the Ettlinger Line as a triangle permittivity anomaly. On the right of the trench, we found a slightly right-tilted layer which exhibits strong permittivity attenuation. Frequency-dependent GPR FWI showed better data fitting and more continuous conductivity structure in this region, and was likely to be more robust than frequency-independent GPR FWI. Previous GPR migration imaging and shallow-seismic FWIs have verified our GPR FWI results. Crosstalk mitigation and joint inversion with other geophysical approaches need to be studied in the future. The use of other models describing relaxation phenomena of permittivity and conductivity also deserves further investigation.

# ACKNOWLEDGMENTS

This work is financially supported by the China Scholarship Council (No. 201806260258). Tan Qin would like to thank Tilman Steinweg and Mark Wienöbst for their help in developing the WAVE-Toolbox. The authors sincerely thank Lars Houpt, Felix Bögelspacher, Leon Merkel, Michael Mayer, Hagen Steger, Roland Helfer, Philipp Koyan and the master students at Geophysical Institute, Karlsruhe Institute of Technology for their help in field data acquisition, and the editor Rene-Edouard Plessix, the reviewer Hansruedi Maurer and another anonymous reviewer for their constructive comments.

# DATA AVAILABILITY

An open-source software (GPL) package containing the source code, models and data used in this paper is provided in the WAVE-Toolbox (https://github.com/WAVE-Toolbox).

# REFERENCES

Belina, F., Irving, J., Ernst, J. & Holliger, K., 2012. Evaluation of the reconstruction limits of a frequency-independent crosshole georadar waveform inversion scheme in the presence of dispersion, J. Appl. Geophys., 78, 9–19.
Bergmann, T., Robertson, J.O. & Holliger, K., 1998. Finite-difference modeling of electromagnetic wave propagation in dispersive and attenuating media, Geophysics, 63(3), 856–867.
Blanch, J.O., Robertson, J.O. & Symes, W.W., 1995. Modeling of a constant Q: Methodology and algorithm for an efficient and optimally inexpensive viscoelastic technique, Geophysics, 60(1), 176–184.
Bohlen, T., 2002. Parallel 3-D viscoelastic finite difference seismic modelling, Comput. Geosci., 28(8), 887–899.
Boniger, U. & Tronicke, J., 2010. On the potential of kinematic GPR surveying using a self-tracking total station: Evaluating system crosstalk and latency, IEEE Trans. Geosci. Remote Sens., 48(10), 3792–3798.
Bradford, J.H., 2007. Frequency-dependent attenuation analysis of ground-penetrating radar data, Geophysics, 72(3), J7–J16.
Bunks, C., Saleck, F.M., Zaleski, S. & Chavent, G., 1995. Multiscale seismic waveform inversion, Geophysics, 60(5), 1457–1473.
Busch, S., van der Kruk, J., Bikowski, J. & Vereecken, H., 2012. Quantitative conductivity and permittivity estimation using full-waveform inversion of on-ground GPR data, Geophysics, 77(6), H79–H91.
Carcione, J. & Cavallini, F., 1995. On the acoustic-electromagnetic analogy, Wave Motion, 21(2), 149–162.
Carcione, J.M., 1996. Ground-penetrating radar: Wave theory and numerical simulation in lossy anisotropic media, Geophysics, 61(6), 1664–1677.
Deng, J., Røge, Y., Zhu, P., Hørkøe, A., Jiang, J. & Kofman, W., 2021. 3D time-domain electromagnetic full waveform inversion in Debye dispersive medium accelerated by multi-GPU paralleling, Comput. Phys. Commun., 265, 108002.
Domenzain, D., Bradford, J. & Mead, J., 2020. Joint inversion of full-waveform ground-penetrating radar and electrical resistivity data: Part 1, Geophysics, 85(6), H97–H113.
Domenzain, D., Bradford, J. & Mead, J., 2021. Joint full-waveform GPR and ER inversion applied to field data acquired on the surface, Geophysics, 87(1), 1–77.
El Bouajaji, M., Lanteri, S. & Yedlin, M., 2011. Discontinuous Galerkin frequency domain forward modelling for the inversion of electric permittivity in the 2D case, Geophys. Prospect., 59, 920–933 (Modelling Methods for Geophysical Imaging: Trends and Perspectives).
Ernst, J.R., Green, A.G., Maurer, H. & Holliger, K., 2007a. Application of a new 2D time-domain full-waveform inversion scheme to crosshole radar data, Geophysics, 72(5), J53–J64.
Ernst, J.R., Maurer, H., Green, A.G. & Holliger, K., 2007b. Full-waveform inversion of crosshole radar data based on 2-D finite-difference time-domain solutions of Maxwell's equations, IEEE Trans. Geosci. Remote Sens., 45(9), 2807–2828.
Fabien-Ouellet, G., Gloaguen, E. & Giroux, B., 2017. Time domain viscoelastic full waveform inversion, Geophys. J. Int., 209(3), 1718–1734.
Forbriger, T., Groos, L. & Schäfer, M., 2014. Line-source simulation for shallow-seismic data. Part 1: theoretical background, Geophys. J. Int., 198(3), 1387–1404.
Gao, L., Pan, Y. & Bohlen, T., 2020. 2-D multiparameter viscoelastic shallow-seismic full-waveform inversion: reconstruction tests and first field-data application, Geophys. J. Int., 222(1), 560–571.
Gao, L., Pan, Y., Rieder, A. & Bohlen, T., 2021. Multiparameter viscoelastic full-waveform inversion of shallow-seismic surface waves with a preconditioned truncated Newton method, Geophys. J. Int., 227(3), 2044–2057.
Groos, L., Schäfer, M., Forbriger, T. & Bohlen, T., 2014. The role of attenuation in 2D full-waveform inversion of shallow-seismic body and Rayleigh waves, Geophysics, 79(6), R247–R261.
Gueting, N., Klotzsche, A., van der Kruk, J., Vanderborgh, J., Vereecken, H. & Englert, A., 2015. Imaging and characterization of facies heterogeneity in an alluvial aquifer using GPR full-waveform inversion and cone penetration tests, J. Hydrol., 524, 680–695.
Irnaka, T., Brossier, R., Métivier, L., Bohlen, T. & Pan, Y., 2022. 3-D multi-component full waveform inversion for shallow-seismic target: Ettlingen line case study, Geophys. J. Int., 229(2), 1017–1040.
Jiang, H., 2019. Seismic imaging: strategies for visco-acoustic full waveform inversion, PhD thesis, Université Paris sciences et lettres.
Jol, H.M., 2008. Ground Penetrating Radar Theory and Applications, Elsevier.

Downloaded from https://academic.oup.com/gpl/article/232/1/504/6670780 by KIT Library user on 25 October 2022

FWI of GPR data in frequency-dependent media 519

Klotzsche, A., Vereecken, H. & van der Kruk, J., 2019. Review of cross-hole ground-penetrating radar full-waveform inversion of experimental data: recent developments, challenges, and pitfalls, Geophysics, 84(6), H13–H28.
Kuroda, S., Takeuchi, M. & Kim, H.J., 2007. Full-waveform inversion algorithm for interpreting crosshole radar data: a theoretical approach, Geosci. J., 11(3), 211–217.
Kurzmann, A., Przebindowska, A., Köhn, D. & Bohlen, T., 2013. Acoustic full waveform tomography in the presence of attenuation: a sensitivity analysis, Geophys. J. Int., 195(2), 985–1000.
Lavoué, F., 2014. 2D full waveform inversion of ground penetrating radar data: towards multiparameter imaging from surface data, PhD thesis, Université de Grenoble.
Lavoué, F., Brossier, R., Métivier, L., Garambois, S. & Virieux, J., 2014. Two-dimensional permittivity and conductivity imaging by full waveform inversion of multioffset GPR data: a frequency-domain quasi-Newton approach, Geophys. J. Int., 197(1), 248–268.
Linde, N., Tryggvason, A., Peterson, J.E. & Hubbard, S.S., 2008. Joint inversion of crosshole radar and seismic traveltimes acquired at the South Oyster Bacterial Transport Site, Geophysics, 73(4), G29–G37.
Liu, T., Klotzsche, A., Pondkule, M., Vereecken, H., Su, Y. & van der Kruk, J., 2018. Radius estimation of subsurface cylindrical objects from ground-penetrating-radar data using full-waveform inversion, Geophysics, 83(6), H43–H54.
Meles, G.A., Van der Kruk, J., Greenhalgh, S.A., Ernst, J.R., Maurer, H. & Green, A.G., 2010. A new vector waveform inversion algorithm for simultaneous updating of conductivity and permittivity parameters from combination crosshole/borehole-to-surface GPR data, IEEE Trans. Geosci. Remote Sens., 48(9), 3391–3407.
Meles, G.A., Greenhalgh, S.A., Green, A.G., Maurer, H. & Van der Kruk, J., 2011. GPR full-waveform sensitivity and resolution analysis using an FDTD adjoint method, IEEE Trans. Geosci. Remote Sens., 50(5), 1881–1896.
Métivier, L., Brossier, R., Virieux, J. & Operto, S., 2013. Full waveform inversion and the truncated Newton method, SIAM J. Sci. Comput., 35(2), B401–B437.
Oberröhrmann, M., Klotzsche, A., Vereecken, H. & van der Kruk, J., 2013. Optimization of acquisition setup for cross-hole: GPR full-waveform inversion using checkerboard analysis, Near Surf. Geophys., 11(2), 197–209.
Operto, S., Gholami, Y., Prieux, V., Ribodetti, A., Brossier, R., Métivier, L. & Virieux, J., 2013. A guided tour of multiparameter full-waveform inversion with multicomponent data: From theory to practice, Leading Edge, 32(9), 1040–1054.
Pan, Y., Schaneng, S., Steinweg, T. & Bohlen, T., 2018. Estimating S-wave velocities from 3D 9-component shallow seismic data using local Rayleigh-wave dispersion curves—A field study, J. Appl. Geophys., 159, 532–539.
Pan, Y., Gao, L. & Bohlen, T., 2021. Random-objective waveform inversion of 3D-9C shallow-seismic field data, J. geophys. Res., 126(9), e2021JB022036.
Papadopoulos, T.G. & Rekanos, I.T., 2011. Time-domain microwave imaging of inhomogeneous Debye dispersive scatterers, IEEE Trans. Antennas Propag., 60(2), 1197–1202.
Pica, A., Diet, J. & Tarantola, A., 1990. Nonlinear inversion of seismic reflection data in a laterally invariant medium, Geophysics, 55(3), 284–292.
Pinard, H., Garambois, S., Métivier, L., Dietrich, M. & Virieux, J., 2015. 2D frequency-domain full-waveform inversion of GPR data: Permittivity and conductivity imaging, in 2015 8th International Workshop on Advanced Ground Penetrating Radar (IWAGPR), pp. 1–4, IEEE.
Pipkin, A.C., 2012. Lectures on Viscoelasticity Theory, Vol. 7, Springer Science & Business Media.
Plessix, R.-E., 2006. A review of the adjoint-state method for computing the gradient of a functional with geophysical applications, Geophys. J. Int., 167(2), 495–503.
Plessix, R.-E. & Mulder, W., 2004. Frequency-domain finite-difference amplitude-preserving migration, Geophys. J. Int., 157(3), 975–987.
Polak, E. & Ribiere, G., 1969. Note on convergence of conjugate direction methods, Rev. Fr. Inform. Rech. Oper., 3(16), 35–43.
Qin, T., Bohlen, T. & Pan, Y., 2022. Indirect joint petrophysical inversion of synthetic shallow-seismic and multi-offset ground-penetrating radar data, Geophys. J. Int., 229(3), 1770–1784.
Roden, J.A. & Gedney, S.D., 2000. Convolution PML (CPML): an efficient FDTD implementation of the CFS–PML for arbitrary media, Microw. Opt. Technol. Lett., 27(5), 334–339.
Schaneng, S.P., 2017. Erstellung eines 3D Modells der Scherwellengeschwindigkeit im Bereich der Ettlinger Linie (Rheinstetten) aus der 1D Inversion der lokalen Dispersion von Rayleigh-Wellen [1D inversion of local Rayleigh wave dispersion curves to construct a local 3D S-wave velocity model of the Ettlinger Linie in Rheinstetten], Master's thesis, Karlsruhe Institute of Technology.
Tarantola, A., 1984. Inversion of seismic reflection data in the acoustic approximation, Geophysics, 49(8), 1259–1266.
Turner, G. & Siggins, A.F., 1994. Constant Q attenuation of subsurface radar pulses, Geophysics, 59(8), 1192–1200.
Wegscheider, S., 2017. Abbildung der Ettlinger Linie auf dem Segelflugplatz Rheinstetten mittels Georadar [Illustration of the Ettlinger line on the gliding airfield Rheinstetten by means of GPR], Master's thesis, Karlsruhe Institute of Technology.
Winters, D.W., Bond, E.J., Van Veen, B.D. & Hagness, S.C., 2006. Estimation of the frequency-dependent average dielectric properties of breast tissue using a time-domain inverse scattering technique, IEEE Trans. Antennas Propag., 54(11), 3517–3528.
Wittkamp, F., Athanasopoulos, N. & Bohlen, T., 2019. Individual and joint 2-D elastic full-waveform inversion of Rayleigh and Love waves, Geophys. J. Int., 216(1), 350–364.
Yang, P., Brossier, R., Métivier, L. & Virieux, J., 2016. A review on the systematic formulation of 3-D multiparameter full waveform inversion in viscoelastic medium, Geophys. J. Int., 207(1), 129–149.
Yao, G., Da Silva, N.V. & Wu, D., 2018. Sensitivity analyses of acoustic impedance inversion with full-waveform inversion, J. Geophys. Eng., 15(2), 461–477.
Yee, K., 1966. Numerical solution of initial boundary value problems involving Maxwell's equations in isotropic media, IEEE Trans. Antennas Propag., 14(3), 302–307.

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022

520 T. Qin, T. Bohlen and N. Allroggen

# APPENDIX A: CONVOLUTION CALCULATION

The convolution of the dielectric permittivity $\varepsilon$ and the electric field $\mathbf{E}$ is

$$\begin{aligned} \varepsilon(t) * \partial_t \mathbf{E} &= \partial_t \Psi_r(t) * \partial_t \mathbf{E} = \left\{ \partial_t \left[ \varepsilon_s \left( 1 - \tau_c \frac{1}{L} \sum_{l=1}^L e^{-t/\tau_{Dl}} \right) H(t) \right] \right\} * \partial_t \mathbf{E} \\ &= \left\{ \varepsilon_s \left[ \left( 1 - \tau_c \frac{1}{L} \sum_{l=1}^L e^{-t/\tau_{Dl}} \right) \delta(t) + \tau_c \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}} e^{-t/\tau_{Dl}} H(t) \right] \right\} * \partial_t \mathbf{E} \\ &= \varepsilon_s (1 - \tau_c) \partial_t \mathbf{E} + \left\{ \varepsilon_s \tau_c \frac{1}{L} \left[ \sum_{l=1}^L \frac{1}{\tau_{Dl}} e^{-t/\tau_{Dl}} H(t) \right] \right\} * \partial_t \mathbf{E} \\ &= \varepsilon_s (1 - \tau_c) \partial_t \mathbf{E} + \left\{ \varepsilon_s \tau_c \frac{1}{L} \partial_t \left[ \sum_{l=1}^L \frac{1}{\tau_{Dl}} e^{-t/\tau_{Dl}} H(t) \right] \right\} * \mathbf{E} \\ &= \varepsilon_s (1 - \tau_c) \partial_t \mathbf{E} + \left\{ \varepsilon_s \tau_c \frac{1}{L} \left[ \sum_{l=1}^L \frac{1}{\tau_{Dl}} e^{-t/\tau_{Dl}} \delta(t) - \sum_{l=1}^L \frac{1}{\tau_{Dl}^2} e^{-t/\tau_{Dl}} H(t) \right] \right\} * \mathbf{E} \\ &= \varepsilon_s (1 - \tau_c) \partial_t \mathbf{E} + \varepsilon_s \tau_c \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}} \mathbf{E} - \left[ \varepsilon_s \tau_c \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}^2} e^{-t/\tau_{Dl}} H(t) \right] * \mathbf{E} \\ &= \varepsilon_s (1 - \tau_c) \partial_t \mathbf{E} + \varepsilon_s \tau_c \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}} \mathbf{E} + \sum_{l=1}^L \mathbf{r}_l. \end{aligned} \tag{A1}$$

Therefore, we define the memory variable $\mathbf{r}_l$ of the $l$th mechanism corresponding to $\mathbf{E}$ as

$$\begin{aligned} \mathbf{r}_l &= - \left[ \frac{\varepsilon_s \tau_c}{L \tau_{Dl}^2} e^{-t/\tau_{Dl}} H(t) \right] * \mathbf{E}, \\ \partial_t \mathbf{r}_l &= - \left[ \frac{\varepsilon_s \tau_c}{L \tau_{Dl}^2} e^{-t/\tau_{Dl}} \delta(t) - \frac{\varepsilon_s \tau_c}{L \tau_{Dl}^2} e^{-t/\tau_{Dl}} H(t) \right] * \mathbf{E} \\ &= - \frac{\varepsilon_s \tau_c}{L \tau_{Dl}^2} \mathbf{E} + \left[ \frac{\varepsilon_s \tau_c}{L \tau_{Dl}^2} e^{-t/\tau_{Dl}} H(t) \right] * \mathbf{E} \\ &= - \frac{\varepsilon_s \tau_c}{L \tau_{Dl}^2} \mathbf{E} - \frac{1}{\tau_{Dl}} \mathbf{r}_l. \end{aligned} \tag{A2}$$

The convolution of the conductivity $\sigma$ and $\mathbf{E}$ is

$$\begin{aligned} \sigma(t) * \mathbf{E} &= \partial_t \Psi_\sigma(t) * \mathbf{E} \\ &= \partial_t \{ \sigma_s [H(t) + \tau_\sigma \delta(t)] \} * \mathbf{E} \\ &= \sigma_s [\delta(t) * \mathbf{E} + \tau_\sigma \delta(t) * \partial_t \mathbf{E}] \\ &= \sigma_s (\mathbf{E} + \tau_\sigma \partial_t \mathbf{E}). \end{aligned} \tag{A3}$$

We sum the two convolutions and get

$$\begin{aligned} \varepsilon(t) * \partial_t \mathbf{E} + \sigma(t) * \mathbf{E} &= \varepsilon_s (1 - \tau_c) \partial_t \mathbf{E} + \varepsilon_s \tau_c \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}} \mathbf{E} + \sum_{l=1}^L \mathbf{r}_l \\ &\quad + \sigma_s (\mathbf{E} + \tau_\sigma \partial_t \mathbf{E}) \\ &= [\varepsilon_s (1 - \tau_c) + \sigma_s \tau_\sigma] \partial_t \mathbf{E} \\ &\quad + \left[ \sigma_s + \varepsilon_s \tau_c \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}} \right] \mathbf{E} + \sum_{l=1}^L \mathbf{r}_l \\ &= \varepsilon_\infty^\sigma \partial_t \mathbf{E} + \sigma_\infty^\sigma \mathbf{E} + \sum_{l=1}^L \mathbf{r}_l, \end{aligned} \tag{A4}$$

where

$$\varepsilon_\infty^\sigma = \varepsilon_s (1 - \tau_c) + \sigma_s \tau_\sigma, \quad \sigma_\infty^\sigma = \sigma_s + \varepsilon_s \tau_c \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}}. \tag{A5}$$

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022

FWI of GPR data in frequency-dependent media

521

# APPENDIX B: GRADIENT CALCULATION

For consistency with Papadopoulos & Rekanos (2011), we present the gradients as the zero-lag cross-correlation of forward wavefield u and adjoint wavefield ũ in the following. Note that we actually replace ũ(t) in eq.(23) by ũ(T - t) which is given by the same forward solver. By doing so, the cross-correlation of ũ(t) and u(t) becomes the convolution of ũ(t) and u(t).

Thus, we obtain the gradients of the electrical parameters as follows:

$$\frac{\partial \Phi}{\partial \varepsilon_{\infty}^e} = \int_0^T \left( \hat{E}_x \partial_t E_x + \hat{E}_y \partial_t E_y + \hat{E}_z \partial_t E_z \right) dt,$$

$$\frac{\partial \Phi}{\partial \sigma_{\infty}^e} = \int_0^T \left( \hat{E}_x E_x + \hat{E}_y E_y + \hat{E}_z E_z \right) dt,$$

$$\frac{\partial \Phi}{\partial \varepsilon_s} = - \frac{L r_{\varepsilon\sigma}}{\varepsilon_s^2 \tau_e},$$

$$\frac{\partial \Phi}{\partial \tau_e} = - \frac{L r_{\varepsilon\sigma}}{\varepsilon_s \tau_e^2}, \tag{B1}$$

where

$$r_{\varepsilon\sigma} = \int_0^T \sum_{l=1}^L \tau_{Dl} (\tau_{Dl} r_{zl} + r_{zl}) dt,$$

$$r_{zl} = (\hat{r}_{xl} \partial_t r_{xl} + \hat{r}_{yl} \partial_t r_{yl} + \hat{r}_{zl} \partial_t r_{zl}),$$

$$r_{zl} = (\hat{r}_{xl} r_{xl} + \hat{r}_{yl} r_{yl} + \hat{r}_{zl} r_{zl}). \tag{B2}$$

Eq. (B2) can be simplified by the following equation, based on eq.(A2) where $\tau_{Dl}(\tau_{Dl} \partial_t \mathbf{r}_l + \mathbf{r}_l) = -\frac{\varepsilon_s \tau_e}{L} \mathbf{E}$:

$$r_{\varepsilon\sigma} = -\frac{\varepsilon_s \tau_e}{L} \int_0^T \sum_{l=1}^L (\hat{r}_{xl} E_x + \hat{r}_{yl} E_y + \hat{r}_{zl} E_z) dt. \tag{B3}$$

Then the gradient of $\varepsilon_s$ and $\tau_e$ are rewritten as:

$$\frac{\partial \Phi}{\partial \varepsilon_s} = \frac{1}{\varepsilon_s} \int_0^T \sum_{l=1}^L (\hat{r}_{xl} E_x + \hat{r}_{yl} E_y + \hat{r}_{zl} E_z) dt,$$

$$\frac{\partial \Phi}{\partial \tau_e} = \frac{1}{\tau_e} \int_0^T \sum_{l=1}^L (\hat{r}_{xl} E_x + \hat{r}_{yl} E_y + \hat{r}_{zl} E_z) dt, \tag{B4}$$

According to eq. (A5) and the chain rule, we convert the gradients of the objective function from the parameter class $\mathbf{m} = (\varepsilon_{\infty}^e, \sigma_{\infty}^e, \varepsilon_s, \tau_e)$ to $\mathbf{m}' = (\varepsilon_s', \sigma_s, \tau_e', \tau_\sigma)$ where $\varepsilon_s' = \varepsilon_s$ and $\tau_e' = \tau_e$.

$$\frac{\partial \Phi}{\partial \varepsilon_s'} = (1 - \tau_e) \frac{\partial \Phi}{\partial \varepsilon_{\infty}^e} + \tau_e \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}} \frac{\partial \Phi}{\partial \sigma_{\infty}^e} + \frac{\partial \Phi}{\partial \varepsilon_s},$$

$$\frac{\partial \Phi}{\partial \sigma_s} = \tau_\sigma \frac{\partial \Phi}{\partial \varepsilon_{\infty}^e} + \frac{\partial \Phi}{\partial \sigma_{\infty}^e},$$

$$\frac{\partial \Phi}{\partial \tau_e'} = -\varepsilon_s \frac{\partial \Phi}{\partial \varepsilon_{\infty}^e} + \varepsilon_s \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}} \frac{\partial \Phi}{\partial \sigma_{\infty}^e} + \frac{\partial \Phi}{\partial \tau_s},$$

$$\frac{\partial \Phi}{\partial \tau_\sigma} = \sigma_s \frac{\partial \Phi}{\partial \varepsilon_{\infty}^e}. \tag{B5}$$

For the reference angular frequency $\omega_0$, we have

$$\begin{cases} \varepsilon^e(\omega_0) = a\varepsilon_s + \sigma_s \tau_e \\ \sigma^e(\omega_0) = \sigma_s + b\varepsilon_s \end{cases} \Leftrightarrow \begin{cases} \varepsilon_s = [\varepsilon^e(\omega_0) - \sigma^e(\omega_0)\tau_e]/(a - b\tau_e) \\ \sigma_s = \sigma^e(\omega_0) - b\varepsilon_s \end{cases}, \tag{B6}$$

with

$$a = 1 - \tau_e \frac{1}{L} \sum_{l=1}^L \frac{\omega_0^2 \tau_{Dl}^2}{1 + \omega_0^2 \tau_{Dl}^2} = 1 - \tilde{a}\tau_e,$$

$$b = \tau_e \frac{1}{L} \sum_{l=1}^L \frac{\omega_0^2 \tau_{Dl}}{1 + \omega_0^2 \tau_{Dl}^2} = \tilde{b}\tau_e. \tag{B7}$$

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022

522 T. Qin, T. Bohlen and N. Allroggen

Alternatively, we can convert the gradients of the objective function from the parameter class $\mathbf{m}' = (\varepsilon_s', \sigma_s, \tau_s', \tau_\sigma)$ to $\mathbf{m}'' = (\varepsilon^\sigma, \sigma^\sigma, \tau_\sigma'', \tau_\sigma')$ where $\tau_\sigma'' = \tau_\sigma'$ and $\tau_\sigma'' = \tau_\sigma$.

$$\frac{\partial \Phi}{\partial \varepsilon^\sigma} = \frac{\partial \varepsilon_s'}{\partial \varepsilon^\sigma} \frac{\partial \Phi}{\partial \varepsilon_s'} + \frac{\partial \sigma_s}{\partial \varepsilon^\sigma} \frac{\partial \Phi}{\partial \sigma_s},$$

$$\frac{\partial \Phi}{\partial \sigma^\sigma} = \frac{\partial \varepsilon_s'}{\partial \sigma^\sigma} \frac{\partial \Phi}{\partial \varepsilon_s'} + \frac{\partial \sigma_s}{\partial \sigma^\sigma} \frac{\partial \Phi}{\partial \sigma_s},$$

$$\frac{\partial \Phi}{\partial \tau_\sigma''} = \frac{\partial \varepsilon_s'}{\partial \tau_\sigma''} \frac{\partial \Phi}{\partial \varepsilon_s'} + \frac{\partial \sigma_s}{\partial \tau_\sigma''} \frac{\partial \Phi}{\partial \sigma_s} + \frac{\partial \Phi}{\partial \tau_\sigma'},$$

$$\frac{\partial \Phi}{\partial \tau_\sigma''} = \frac{\partial \varepsilon_s'}{\partial \tau_\sigma''} \frac{\partial \Phi}{\partial \varepsilon_s'} + \frac{\partial \sigma_s}{\partial \tau_\sigma''} \frac{\partial \Phi}{\partial \sigma_s} + \frac{\partial \Phi}{\partial \tau_\sigma}, \quad (B8)$$

where

$$\frac{\partial \varepsilon_s'}{\partial \varepsilon^\sigma} = \frac{1}{a - b\tau_\sigma}, \quad \frac{\partial \sigma_s}{\partial \varepsilon^\sigma} = -b \frac{\partial \varepsilon_s'}{\partial \varepsilon^\sigma},$$

$$\frac{\partial \varepsilon_s'}{\partial \sigma^\sigma} = -\frac{\tau_\sigma}{a - b\tau_\sigma}, \quad \frac{\partial \sigma_s}{\partial \sigma^\sigma} = 1 - b \frac{\partial \varepsilon_s'}{\partial \sigma^\sigma},$$

$$\frac{\partial \varepsilon_s'}{\partial \tau_\sigma''} = \frac{\varepsilon^\sigma - \sigma^\sigma \tau_\sigma}{(a - b\tau_\sigma)^2} (\tilde{a} + \tilde{b}\tau_\sigma), \quad \frac{\partial \sigma_s}{\partial \tau_\sigma''} = -b \frac{\partial \varepsilon_s'}{\partial \tau_\sigma''},$$

$$\frac{\partial \varepsilon_s'}{\partial \tau_\sigma''} = \frac{b\varepsilon^\sigma - a\sigma^\sigma}{(a - b\tau_\sigma)^2}, \quad \frac{\partial \sigma_s}{\partial \tau_\sigma''} = -b \frac{\partial \varepsilon_s'}{\partial \tau_\sigma''}. \quad (B9)$$

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022