Engineering Research Express

INCLUSIVE PUBLISHING TRUSTED SCIENCE

PURPOSE-LED PUBLISHING

PAPER • OPEN ACCESS

# Electromagnetic echo characteristics of soil–rock mixtures based on gprMax forward analysis

To cite this article: Yangzhou Feng et al 2025 Eng. Res. Express 7 045123

View the article online for updates and enhancements.

# You may also like

- Numerical simulation of ground penetrating radar based on advanced prediction of adverse geological bodies Shaojie Li and Rongming Hu
- The Effect of Ground Penetrating Radar (GPR) Image Reflection on Different Pipes and Soil
Nur Haafizhah Binti Mohd Kamal, Zulkaraini Mat Amin and Nurafifah Binti Mohamad
- GPR geophysical method as a remediation tool to determine zones of high penetration resistance of soil
A Akinsunmade, S Tomecka-Sucho, P Kiebasa et al.

This content was downloaded from IP address 200.14.70.213 on 17/06/2026 at 19:20

IOP Publishing

Eng. Res. Express 7 (2025) 045123

https://doi.org/10.1088/2631-8695/ae1a38

# Engineering Research Express

[Check for updates]

# OPEN ACCESS

RECEIVED

2 June 2025

REVISED

26 September 2025

ACCEPTED FOR PUBLICATION

31 October 2025

PUBLISHED

10 November 2025

Original content from this work may be used under the terms of the Creative Commons Attribution 4.0 licence.

Any further distribution of this work must maintain attribution to the author(s) and the title of the work, journal citation and DOI.

[O]

# PAPER

# Electromagnetic echo characteristics of soil-rock mixtures based on gprMax forward analysis

Yangzhou Feng $^{1}$, Mingming Jing $^{1}$, Ning An $^{1}$, Yulong Qin $^{1}$, Fan Wang $^{1}$, Yongqiang Tian $^{1}$, Zhihe Cheng $^{2}$  and Junfeng Du $^{2,*}$

$^{1}$ State Grid Gansu Power Company, Lanzhou, Gansu 730000, People's Republic of China
$^{2}$ School of Civil Engineering, Harbin Institute of Technology, Harbin, Heilongjiang, People's Republic of China
* Author to whom any correspondence should be addressed.

E-mail: junfeng150090@163.com

Keywords: soil-rock mixtures, electromagnetic characteristics, echo characteristics, forward modeling

# Abstract

The objective of this study was to explore the electromagnetic wave reflection characteristics of soil-rock mixtures. Using the FDTD-based gprMax software, we developed numerical models incorporating multiple survey lines to analyze the impacts of three factors—dielectric constant, conductivity, and water content—on electromagnetic echo characteristics through forward modeling with a focus on wave forms and the electromagnetic wave propagation process were examined to gain deeper insights. Results showed that the propagation time of an electromagnetic wave increased with increasing dielectric constant; meanwhile, when the dielectric constant remained unchanged, changes in conductivity did not impact the reflected waveform, radar wave propagation time, or directly coupled wave, though increased conductivity decreased the amplitude of the reflected wave. The echo characteristics were pronounced in water-rich areas, observing high values of instantaneous amplitude. These findings provide a reference for advancing ground-penetrating radar applications in nondestructive testing and enhancing forward modeling accuracy.

# 1. Introduction

Ground-penetrating radar (GPR) is an essential technology in geophysical exploration, water conservancy project, civil engineering, and environmental research, with significant potential in geological mapping, fault detection, and tunnel lining assessment [1-3]. A GPR can detect objects by identifying changes in their electromagnetic properties, typically including dielectric constant, conductivity, magnetic permeability, and magnetic loss factor [4-6]. By analyzing GPR signal waveforms, we can identify the amplitudes and time variations of received echoes and thus determine the approximate locations, structural shapes, and burial depths of subsurface objects [7-10]. GPRs are widely used to assess the distribution of soil-rock mixtures and shape and thickness of strata, contributing considerably to the advancement of engineering construction and geological survey projects and enhancing the overall understanding of the subsurface conditions.

Ground-penetrating radar (GPR) numerical modeling encompasses a variety of techniques, each with distinct features and applications. Ray-tracing methods simulate wave propagation by depicting the paths of electromagnetic waves as they encounter interfaces and obstacles. The finite element method (FEM) discretizes the target region into segments, enabling localized analysis of complex structures, while the method of moments (MoM) derives from the integral form of functional theory [11]. The finite-difference time-domain (FDTD) method has gained prominence for its ability to discretize Maxwell's equations in both space and time, making it particularly suitable for modeling complex subsurface geometries and associated wave phenomena [12]. Within this context, GprMax stands out as an open-source simulation tool tailored for GPR applications. Initially developed by Antonis Giannopoulos at the University of Edinburgh in 1996, it employs FDTD as its core algorithm to effectively simulate electromagnetic wave propagation in complicated environments [13]. Later, Warren reimplemented the software using Python and Cython to support more detailed and

© 2025 The Author(s). Published by IOP Publishing Ltd

IOP Publishing

Eng. Res. Express 7 (2025) 045123

Y Feng et al

![img-0.jpeg](img-0.jpeg)
Figure 1. Yee grid [19]. Reproduced from [21, 22]. CC BY 4.0.

sophisticated modeling requirements [14]. On the application side, Zhu [15] conducted forward modeling using GprMax2D to systematically analyze the GPR image characteristics of typical unfavorable geological bodies during tunnel construction, interpreting field measurement data with the aid of simulation results. Feng [16] proposed a hybrid algorithm combining the finite-element time-domain (FETD) method with FDTD for high-fidelity simulation of GPR responses to lining defects in tunnels. Yang [17] derived a CPML ADI FDTD scheme to enhance computational efficiency, while Lin [18] employed FDTD for both forward modeling and back-projection imaging to achieve non-destructive detection and evaluation of tunnel lining defects. To further improve imaging accuracy, Lv [19] introduced a reverse time migration (RTM) algorithm for GPR data. In a related study, Luo [20] investigated the GPR response patterns of voids in urban infrastructure, revealing the influence of void size relative to signal wavelength on B-scan features and thereby improving the identification accuracy of voids in complex underground environments.

In summary, numerous researchers have made substantial contributions to GPR forward modeling and are continuing to improve and optimize GPR forward modeling techniques and enhance their effectiveness and accuracy in complex geological environments. However, challenges remain in GPR detection. For instance, heterogeneous media can lead to substantial electromagnetic scattering and energy loss, which can reduce the resolution of GPR signals. In addition, interference from soil-rock mixtures may affect the detection and localization of subsurface objects. This study investigates the effects of factors—conductivity, dielectric constant, and water content—on radar signals in soil-rock mixtures and uses the FDTD-based open-source software gprMax for the GPR forward modeling of these factors with the aim of identifying relevant patterns.

# 2. Theory of the FDTD method

# 2.1. Basic FDTD equations

To model electromagnetic wave propagation in space, KS Yee [12] introduced a grid, as shown in figure 1, which converts Maxwell's equations into difference equations by assuming that the propagation properties at different locations in the modeled area are the same and remain unchanged over time.

$$
\frac {\partial \vec {H}}{\partial t} = - \frac {1}{\mu} \nabla \times \vec {E} - \frac {\rho}{\mu} \vec {H} \tag {1}
$$

$$
\frac {\partial \vec {E}}{\partial t} = - \frac {1}{\varepsilon} \nabla \times \vec {H} - \frac {\sigma}{\varepsilon} \vec {H} \tag {2}
$$

In equations (1) and (2),  $\rho$  is the magnetic relativity used to calculate the magnetic loss and  $\sigma$  is the electric conductivity of the medium.

In the Cartesian coordinate system, we have

$$
\frac {\partial E _ {z}}{\partial y} - \frac {\partial E _ {y}}{\partial z} = - \mu \frac {\partial H _ {x}}{\partial t} \tag {3}
$$

$$
\frac {\partial E _ {x}}{\partial z} - \frac {\partial E _ {z}}{\partial x} = - \mu \frac {\partial H _ {y}}{\partial t} \tag {4}
$$

$\frac{\partial E_{y}}{\partial x}-\frac{\partial E_{x}}{\partial y}=-\mu\frac{\partial H_{z}}{\partial t}$ (5)
$\frac{\partial H_{z}}{\partial y}-\frac{\partial H_{y}}{\partial z}=\varepsilon\frac{\partial E_{x}}{\partial t}+\sigma E_{x}$ (6)
$\frac{\partial H_{x}}{\partial z}-\frac{\partial H_{z}}{\partial x}=\varepsilon\frac{\partial E_{y}}{\partial t}+\sigma E_{y}$ (7)
$\frac{\partial H_{y}}{\partial x}-\frac{\partial H_{x}}{\partial y}=\varepsilon\frac{\partial E_{x}}{\partial t}+\sigma E_{z}$ (8)

In equations (3)--(8), $\sigma$ is the electric conductivity (S/m); $\mu$ is the magnetic permeability (H/m); $\varepsilon$ is the dielectric constant (F/m); t is time (s); $E_{x}$, $E_{y}$, and $E_{z}$ are electric field intensity components (V/m); and $H_{x}$, $H_{y}$, and $H_{z}$ are magnetic field intensity components (A/m).

### 2.2. Stability and dispersion of solution

According to electromagnetic principles, in lossy media, the phase velocity of an electromagnetic wave is a function of frequency. Using the Yee difference algorithm to perform FDTD calculations, the curl equations in Maxwell's equations are converted from partial differential equations into explicit difference equations [12]. The phase velocity of the electromagnetic pulse wave varies with the temporal discretization interval $\Delta t$ and spatial discretization intervals $\Delta x$, $\Delta y$, and $\Delta z$. As the number of iterations increases, numerical dispersion may occur. To ensure the stability of the numerical solution, the temporal discretization interval $\Delta t$ and spatial discretization intervals $\Delta x$, $\Delta y$, and $\Delta z$ must satisfy specific conditions to keep numerical dispersion within minimal bounds [19].

Taflove conducted extensive research on the Yee difference grid algorithm and established the limiting condition between the temporal interval $\Delta t$ and spatial intervals $\Delta x$, $\Delta y$, and $\Delta z$ [19].

$\Delta t\leqslant\frac{1}{c\sqrt{\frac{1}{(\Delta x)^{2}}+\frac{1}{(\Delta y)^{2}}+\frac{1}{(\Delta z)^{2}}}}$ (9)

In equation (9) [12], c is the speed of light in vacuum (m/s) [19].

To simplify computations, the Yee grid is usually divided uniformly with a discrete spatial step of $\Delta x=\Delta y=\Delta z$. Equation (10) [12] can then be simplified by the equation (9) [12], as shown below:

$\Delta t\leqslant\frac{\Delta l}{c\sqrt{3}}$ (10)

To reduce numerical dispersion, spatial steps are usually set to less than $\lambda/10$, where $\lambda$ is the electromagnetic wavelength, to increase the stability of the numerical solution [12].

### 2.3. Selection of the excitation source

Common excitation sources include Gaussian pulse, sine wave, and Ricker wavelet. In this study, Ricker wavelet is selected as the excitation source, which is suitable for detecting subsurface media with varying dielectric constants [12]. The mathematical expression for the Ricker wavelet is shown in equation (11) [12].

$s(t)=(1-2\pi^{2}f_{0}^{2}(t-t_{0})^{2})e^{(-\pi^{2}f_{0}^{2}(t-t_{0})^{2})}$ (11)

where $f_{0}$ is the central frequency and $t_{0}$ is the time at the center of the waveform. After Fourier transformation, we have equation (12) [12].

$F(f)=\frac{2f^{2}}{\sqrt{\pi}f_{m}^{2}}e^{-\frac{f^{2}}{f_{m}^{2}}}$ (12)

## 3. Forward modeling

### 3.1. Forward modeling of soil--rock mixtures

By writing a Python script, irregular rocks were generated, and the #geometry_objects_read command in gprMax was used to load the script file for modeling rocks. This script controls parameters such as the number of rocks and their radii, thereby allowing the control of the pixel percentage of rocks in the space and thus the setting of different soil--rock ratios (30%, 50%, and 70%). An example of generated rocks is shown in figure 2.

IOP Publishing

Eng. Res. Express 7 (2025) 045123

Y Feng et al

![img-1.jpeg](img-1.jpeg)
Figure 2. Schematic of randomly generated rocks [19]. Reproduced from [22], CC BY 4.0.

![img-2.jpeg](img-2.jpeg)
Figure 3. Schematic of the model [19]. Reproduced from [22], CC BY 4.0.

A geoelectric model was constructed by incorporating rocks into a layered structure consisting of an upper air layer, a 3-m-thick intermediate soil-rock mixture layer, and a lower rock layer. The rock sizes ranging randomly from 4 to  $50~\mathrm{cm}$ . A point source emitting a Ricker wavelet was used as the excitation source. The transmitting and receiving antennas were spaced  $0.3\mathrm{m}$  apart, and simulations were conducted at antenna frequencies of 50, 100, 200, and  $400\mathrm{MHz}$  with an amplitude scaling factor of 1. In accordance with previous studies, the computational cost of forward modeling increases with grid resolution. To maintain a balance between accuracy and efficiency, the grid cell size was set to  $0.005\mathrm{m}$ . Both soil and rock were treated as nonmagnetic materials, with a magnetic permeability of  $1\mathrm{Hm}^{-1}$  and a magnetic loss factor of zero. The finalized geoelectric model, illustrated in figure 3, was employed to investigate the typical GPR response characteristics of soil-rock mixtures containing randomly distributed rocks.

# 3.2. Data processing

Time-gain calibration is nonlinear. After performing time-gain calibration, the form of the signal changes considerably. Generally, the electromagnetic wave energy follows an exponential change pattern. Therefore, an exponential gain function is chosen, as shown in equation (13).

$$
y = a ^ {x} - 0. 5 \tag {13}
$$

In equation (13),  $\mathbf{x}$  is the sampling rate or time.

For  $a = 1.3$ , the gain function plot is shown in figure 4.

The presence of the direct wave is a common issue in the analysis of ground-penetrating radar (GPR) data. This wave refers to the signal that travels directly from the transmitting to the receiving antenna without interacting with subsurface media, and it often appears as the strongest and most energetic component in GPR records. Its high amplitude can easily mask weaker reflections from underground targets. Therefore, the removal of the direct wave is essential for accurately interpreting subsurface features. This processing step not

only helps to emphasize meaningful reflections but also contributes to noise suppression and improvement of the signal-to-noise ratio, thereby enhancing the detection sensitivity of GPR to subtle underground structures.

## Forward modeling and analysis

### Impact of dielectric constant on echo characteristics l

To study the impact of the dielectric constant on the reflections of GPR waves, dielectric conductivity was set to a constant, with conductivity being set to 0 and magnetic permeability to 1. The dielectric constant was then set to 4, 8, 12, 16, 20, 24, 28, and 32. The geoelectric model with different parameter settings was forward simulated in gprMax to generate the echo curves of the associated radar waves, as shown in figure 5.

Figure 5 show that with other parameters, such as conductivity, remaining unchanged, variations in the dielectric constant remarkably impact the echoes of radar waves. The dielectric constant, an indicator of a material's ability to store electric energy, can considerably affect electromagnetic wave propagation. An increase in the dielectric constant value increases the propagation time of the electromagnetic wave in the medium. In addition, the amplitude of the reflected wave is positively correlated with the dielectric constant due to changes in the reflection coefficient, which increases with the dielectric constant, thereby enhancing the reflected wave. By contrast, a surface directly coupled wave (which propagates directly along the surface of a medium without penetrating the medium) behaves in an opposite manner: its amplitude decreases as the dielectric constant increases. These dynamics highlight the crucial role of the dielectric constant in shaping the behavior of an electromagnetic wave: impacting its propagation time and the amplitudes of reflected and surface directly coupled waves.

### Impact of conductivity on echo characteristics

To study the impact of conductivity on radar wave reflections, the dielectric constant was set to a constant (25) and magnetic permeability was set to 1. Conductivity was increased at a step of 0.004 from 0--0.004, 0.008, 0.012, 0.016, 0.020, and 0.028 S m^{-1}. These values were input into the forward model to generate eight echo curves of the associated radar waves, as shown in figure 6.

Figure 5 show that with other parameters, such as the dialectic constant and magnetic permeability, remaining unchanged, variations in conductivity remarkably impact the echoes of radar waves. When only conductivity changes, the waveform, propagation time, and directly coupled wave remain unaffected, indicating that these properties are inherently robust to changes in conductivity. However, the amplitude of the reflected wave is highly sensitive to changes in conductivity. An increase in conductivity decreases the reflected wave amplitude due to the enhanced absorption of the electromagnetic wave by the medium, which intensifies with increasing conductivity, thereby reducing the reflected wave amplitude. Conversely, a decrease in conductivity increases the reflected wave amplitude due to the decreased absorptive capacity of the medium. In a high-conductivity medium, electromagnetic wave is more scattered, increasing the attenuation and interference of the detection signal and decreasing the resolution. By contrast, in a low-conductivity medium, electromagnetic wave experiences less attenuation and interference, thereby resulting in a higher resolution.

IOP Publishing

Eng. Res. Express 7 (2025) 045123

Y Feng et al

![img-3.jpeg](img-3.jpeg)
(a)  $30\%$

![img-4.jpeg](img-4.jpeg)
(b)  $50\%$

![img-5.jpeg](img-5.jpeg)
(c)  $70\%$
Figure 5. Radar single-channel waveforms of varied dielectric constant at a soil-rock ratio.

# 4.3. Impact of water content on echo characteristics

To verify the enhanced radar signal in the soil-rock mixture, direct waves were removed from the forward modeling results of the radar signals for different water contents (9%, 12%, 15%, 18%, 21%, and 24%), and the results are shown in figure 7.

IOP Publishing

Eng. Res. Express 7 (2025) 045123

Y Feng et al

![img-6.jpeg](img-6.jpeg)
(a)  $30\%$

![img-7.jpeg](img-7.jpeg)
(b)  $50\%$

![img-8.jpeg](img-8.jpeg)
(c)  $70\%$
Figure 6. Radar single-channel waveforms of varied conductivity at a soil-rock ratio.

Figure 7 shows changes in radar electromagnetic waves as they penetrate the soil-rock mixture. Waveforms become increasingly chaotic, and their amplitudes decline, indicating energy attenuation in the complex geological medium. Although the upper boundary between soil and rock is distinguishable, the lower boundary

IOP Publishing

Eng. Res. Express 7 (2025) 045123

Y Feng et al

![img-9.jpeg](img-9.jpeg)
(a)  $9\%$

![img-10.jpeg](img-10.jpeg)
(b)  $12\%$

![img-11.jpeg](img-11.jpeg)
(c)  $15\%$

![img-12.jpeg](img-12.jpeg)
(d)  $18\%$

![img-13.jpeg](img-13.jpeg)
(e)  $21\%$

![img-14.jpeg](img-14.jpeg)
(f)  $24\%$
Figure 7. Radar signal gain processing for soil-rock mixtures with different water contents.

![img-15.jpeg](img-15.jpeg)
(a)  $9\%$

![img-16.jpeg](img-16.jpeg)
(b)  $12\%$

![img-17.jpeg](img-17.jpeg)
(c)  $15\%$

![img-18.jpeg](img-18.jpeg)
(d)  $18\%$

![img-19.jpeg](img-19.jpeg)
(e)  $21\%$

![img-20.jpeg](img-20.jpeg)
(f)  $24\%$
Figure 8. Spectra of soil-rock mixtures with different water contents.

appears blurred, characterized by random disturbances and 'noise.' The reduced signal clarity can be attributed to the scattering of the GPR wave in the soil-rock mixture. This scattering disrupts the coherence of the GPR wave, reducing the SNR and consequently the GPR echo resolution. This underscores the inherent challenges associated with interpreting GPR signals in soil-rock mixtures and highlights the need for advanced signal processing techniques to improve signal clarity and interpretability.

The spectra of channel 35 corresponding to red lines in the above grayscale images of the radar signal are shown in figure 8. As shown figure 8, as the water content in the soil-rock mixture increases, the echo characteristics become more pronounced.

IOP Publishing

Eng. Res. Express 7 (2025) 045123

Y Feng et al

# 5. Conclusions

GPRs, as a nondestructive detection technology, enable the three-dimensional profiling of objects and have broad application prospects in areas, such as landslides and tunnel lining inspections. In this study, we developed a soil-rock mixture model with multiple survey lines, investigated the impacts of the dielectric constant, conductivity, water content on the echo characteristics through forward modeling, and analyzed the patterns of echo images with a focus on waveforms and electromagnetic wave propagation to draw the following conclusions:

(1) In a soil-rock mixture, a change in the dielectric constant leads to a variation in the reflection coefficient at the interface, and the propagation time of an electromagnetic wave increases with increasing dielectric constant value and decreases with decreasing dielectric constant value;

(2) When the dielectric constant remains unchanged, changes in conductivity do not impact the reflected waveform, propagation time of the radar wave, or directly coupled wave, though increased conductivity decreases the amplitude of the reflected wave.

(3) As the water content increases, the echo characteristics become more pronounced. The echo characteristics are pronounced in water-rich areas, exhibiting high values of instantaneous amplitude. The dielectric constants of water-rich areas are higher than those of dry soil or rock, leading to stronger reflections at interfaces between materials with different water contents.

# Acknowledgments

This work is supported by the Tibet Autonomous Region Major Science and Technology Special Project (No. XZ202402ZD0008).

# Data availability statement

All data that support the findings of this study are included within the article (and any supplementary files).

# References

[1] Xintu S 2020 Application of High Density Resistivity Method and Ground Penetrating Radar in Typical Engineering Detection (Jilin University)

[2] Zhaorong Z et al 2022 Study on effect model and field solid test of cavity detection in tunnel lining with GPR Chinese Journal of Geotechnical Engineering 44 132-7

[3] Daniels J J 1989 Fundamentals of ground penetrating radar Symp. on the Application of Geophysics to Engineering and Environmental Problems Proc. 62-142

[4] Yiqun C and Baixun X 2005 On the status and development of ground penetrating radar Chinese Journal of Engineering Geophysics 2 149-55

[5] Xingqiang X et al 2022 Study on the dielectric properties and dielectric constant model of laterite Frontiers in Earth Science 10 1035692

[6] Zamanian M and Shahandashti M 2022 Investigation of relationship between geotechnical parameters and electrical resistivity of sandy soils Construction Research Congress 2022 686-95

[7] Zonghui L, Heng W and Dong Z 2015 Application of spectrum inversion method to detection of tunnel lining with GPR Chinese Journal of Geotechnical Engineering 37 711-7

[8] Zonghui L, Maomao L and Dong Z 2019 Identification method of typical karst bad geology based on ground penetrating radar attribute analysis Soil and Rock Mechanics 40 3282-90

[9] Hongfei Z, Xiaojun C and Pan G 2009 Research on forward simulation of GPR map of tunnel lining cavity Rock and Soil Mechanics 30 2810-4

[10] Lixun L, Shikun D and Mi R 2010 Application of ground penetrating radar in tunnel construction advance detection Chinese Journal of Engineering Geophysics 7 201-6

[11] Jansky K G 1933 Radio waves from outside the solar system Nature 132 66-66

[12] Yee K 1966 Numerical solution of initial boundary value problems involving Maxwell's equations in isotropic media IEEE Trans. Antennas Propag. 14 302-7

[13] Giannakis I, Giannopoulos A and Warren C 2015 A realistic FDTD numerical modeling framework of ground penetrating radar for landmine detection IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing 9 37-51

[14] Warren C, Giannopoulos A and Giannakis I 2016 gprMax: open source software to simulate electromagnetic wave propagation for ground penetrating radar Comput. Phys. Commun. 209 163-70

[15] Yunfeng Z, Qiren W and Guowen D 2016 Forward simulation of tunnel geological prediction based on GPRMAX and analysis of measured data Computing Techniques for Geophysical and Geochemical Exploration 38 185-90

[16] Deshan F, Xun W and Bin Z 2018 Specific evaluation of tunnel lining multi-defects by all-refined GPR simulation method using hybrid algorithm of FETD and FDTD Constr. Build. Mater. 185 220-9

[17] Daoxue Y, Kui Z and Peng Z 2019 Application of ground penetrating radar in underground coal mine (in Chinese) Int. J. Rock Mech. Min. Sci. Geomech. Abstr. 33 A233

IOP Publishing

Eng. Res. Express 7 (2025) 045123

Y Feng et al

[18] Chunjin L et al 2020 Forward modelling and GPR imaging in leakage detection and grouting evaluation in tunnel lining KSCE J. Civ. Eng. 24 278–94
[19] Yuzeng L, Honghua W and Junbo G 2020 Application of GPR reverse time migration in tunnel lining cavity imaging Appl. Geophys. 17 277–84
[20] Tess X.H L, Wallace W.L L and Antonios G 2020 Forward modelling on GPR responses of subsurface air voids Tunnelling Underground Space Technol. 103 103521
[21] Ning A et al 2024 Study on the impact of physical characteristics of soil-rock composite medium on its relative permittivity based on laboratory experiments Front. Earth Sci. 12 1342003
[22] Yulong Q 2023 Deep learning-based inverse analysis of GPR data for landslide hazards Front. Earth Sci. 11 1340484