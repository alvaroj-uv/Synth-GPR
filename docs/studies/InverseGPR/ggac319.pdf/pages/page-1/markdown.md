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