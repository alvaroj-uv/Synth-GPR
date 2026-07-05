remote sensing

MDPI

Article

# Full-Waveform Inversion of Two-Parameter Ground-Penetrating Radar Based on Quadratic Wasserstein Distance

Kai Lu 1, Yibo Wang 2,3,*, Heting Han 2,3, Shichao Zhong 4 and Yikang Zheng 2,3

1 MNR Key Laboratory of Polar Science, Polar Research Institute of China, Shanghai 200062, China; lukai@pric.org.cn
2 Key Laboratory of Petroleum Resource Research, Institute of Geology and Geophysics, Chinese Academy of Sciences, Beijing 100029, China; hetinghan@mail.iggcas.ac.cn (H.H.); zhengyk@mail.iggcas.ac.cn (Y.Z.)
3 University of Chinese Academy of Sciences, Beijing 100049, China
4 Yangtze Delta Region Academy of Beijing Institute of Technology, Jiaxing 314019, China; zhongshichao16@bit.edu.cn
* Correspondence: wangyibo@mail.iggcas.ac.cn

Abstract: Full-waveform inversion (FWI) is one of the most promising techniques in current ground-penetrating radar (GPR) inversion methods. The least-squares method is usually used, minimizing the mismatch between the observed signal and the simulated signal. However, the cycle-skipping problem has become an urgent focus of this method because of the nonlinearity of the inversion problem. To mitigate the issue of local minima, the optimal transport problem has been introduced into full-waveform inversion in this study. The Wasserstein distance derived from the optimal transport problem is defined as the mismatch function in the FWI objective function, replacing the L2 norm. In this study, the Wasserstein distance is computed by using entropy regularization and the Sinkhorn algorithm to reduce computational complexity and improve efficiency. Additionally, this study presents the objective function for dual-parameter full-waveform inversion of ground-penetrating radar, with the Wasserstein distance as the mismatch function. By normalizing with the Softplus function, the electromagnetic wave signals are adjusted to meet the non-negativity and mass conservation assumptions of the Wasserstein distance, and the convexity of the method has been proven. A multi-scale frequency-domain Wasserstein distance full-waveform inversion method based on the Softplus normalization approach is proposed, enabling the simultaneous inversion of relative permittivity and conductivity from ground-penetrating radar data. Numerical simulation cases demonstrate that this method has low initial model dependency and low noise sensitivity, allowing for high-precision inversion of relative permittivity and conductivity. The inversion results show that it, in particular, significantly improves the accuracy of conductivity inversion.

Keywords: Wasserstein distance; optimal transport distance; relative permittivity and conductivity; full-waveform inversion

Citation: Lu, K.; Wang, Y.; Han, H.; Zhong, S.; Zheng, Y. Full-Waveform Inversion of Two-Parameter Ground-Penetrating Radar Based on Quadratic Wasserstein Distance. Remote Sens. 2024, 16, 4146. https://doi.org/10.3390/rs16224146

Academic Editor: Roberto Orosei

Received: 9 October 2024

Revised: 26 October 2024

Accepted: 30 October 2024

Published: 7 November 2024

Copyright: © 2024 by the authors. Licensee MDPI, Basel, Switzerland. This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution (CC BY) license (https://creativecommons.org/licenses/by/4.0/).

## 1. Introduction

Ground-penetrating radar (GPR) is an efficient, non-destructive geophysical method used for near-surface investigation. GPR works in the way of emitting high-frequency electromagnetic waves into the ground by transmitting antenna and receiving the reflected waves from subsurface structures by receiving antenna. This allows for imaging of shallow subsurface structures and electromagnetic properties. GPR inversion refers to the process of reconstructing the subsurface distribution of electrical parameters, such as relative permittivity and conductivity, from GPR observational data. The inversion result is crucial for analyzing and interpreting subsurface structures and has significant implications for engineering applications. Currently, common methods used in GPR inversion imaging include tomography [1,2], common midpoint (CMP) velocity analysis [3], full-waveform

Remote Sens. 2024, 16, 4146. https://doi.org/10.3390/rs16224146

https://www.mdpi.com/journal/remotesensing