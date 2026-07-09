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