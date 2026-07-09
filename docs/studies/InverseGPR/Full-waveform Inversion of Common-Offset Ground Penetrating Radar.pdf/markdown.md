# Full-waveform Inversion of Common-Offset Ground Penetrating Radar (GPR) data

by

Sajad Jazayeri

A dissertation submitted in partial fulfillment
of the requirements for the degree of
Doctor of Philosophy
School of Geosciences
College of Arts and Sciences
University of South Florida

Major Professor: Sarah E. Kruse, Ph.D.
Juan Lorenzo, Ph.D.
Stephen McNutt, Ph.D.
Rocco Malservisi, Ph.D.
Glenn Thompson, Ph.D.

Date of Approval:
March 19, 2019

Keywords: Modeling, Full-waveform Inversion, Deconvolution, Ground Penetrating radar
(GPR), Reflectivity, Source wavelet, Sparsity.

Copyright © 2019, Sajad Jazayeri

# Dedication

This work is dedicated to my wife, Sanaz, who carried my baby boy while I was writing this, my parents, Farkhondeh and Hossein, and my brothers, Majid, Alireza and Mohammadreza. Thank you all for your unconditional endless support and for always being there for me. Love you all!

To Artin!

# Acknowledgments

This dissertation was completed with the generous advice and support of several people, most notably my adviser, Sarah Kruse, and my colleagues and friends Nasser Kazemi and Anja Klotzsche. I learned a lot from Stephen McNutt, Rocco Malservisi and Glenn Thompson at USF, thank you all. A special thanks to Juan Lorenzo for serving on my committee.

I would also like to acknowledge several colleagues who helped with this dissertation, data collection, pipe burial, etc. Sanaz Esmaeili greatly helped me debug my codes. Both Sanaz and Christine Downs assisted with data collection and digging for pipe burial. I acknowledge the great help and support of Tony Green for assistance implementing algorithms on the USF Research Computing cluster. Also, I'd like to thank Mark Rains for his continuous support.

Thank you to American Society of Civil Engineers (ASCE) for the 2017-2018 Trent R. Dames and William W. Moore Fellowship, the USF Geology Alumni Society for the 2019 Richard A. Davis Fellowship, and USF Office of Graduate Studies for the Dissertation Completion Fellowship.

## Table of Contents

|  List of Tables | iii  |
| --- | --- |
|  List of Figures | iv  |
|  Abstract | vii  |
|  1 Introduction | 1  |
|  1.1 Full waveform inversion for PVC pipe mapping | 3  |
|  1.2 Sparse Blind Deconvolution of Ground Penetrating Radar Data | 4  |
|  1.3 Reinforced structure mapping using FWI | 4  |
|  2 Improving estimates of buried pipe diameter and infilling material from ground-penetrating radar profiles with full-waveform inversion | 6  |
|  3 Sparse Blind Deconvolution of Ground Penetrating Radar Data | 7  |
|  4 Reinforced Concrete Mapping Using Full-Waveform Inversion of GPR Data | 8  |
|  4.1 abstract | 8  |
|  4.2 keyword | 8  |
|  4.3 Introduction | 8  |
|  4.4 Method | 12  |
|  4.4.1 Analytical expression for travel times | 12  |
|  4.5 Results | 16  |
|  4.5.1 Synthetic data, reinforced concrete | 16  |
|  4.5.2 Real data, case 1 | 20  |
|  4.5.3 Real data, case 2 | 22  |
|  4.6 Discussion and Conclusions | 25  |
|  5 Conclusion | 29  |
|  References | 32  |
|  Appendix I Improving estimates of buried pipe diameter and infilling material from ground-penetrating radar profiles with full-waveform inversion | 36  |
|  Appendix II Copyright permission from *Geophysics* for use of this manuscript in dissertation | 52  |

i

Appendix III Sparse Blind Deconvolution of Ground Penetrating Radar Data 55
Appendix IV Copyright permission from *IEEE* for use of this manuscript in dissertation 66

ii

## List of Tables

|  Table 1.1 | Average penetration depth vs the antenna frequency. Values adapted from http://www.geoscan.ca/ground-penetrating-radar-gpr.html | 1  |
| --- | --- | --- |
|  Table 4.1 | The true, ray-based estimated and FWI-estimated parameter values for the synthetic model shown in Figure 4.3. $x$ represents the horizontal location in $cm$, $y$ the depth in $cm$ and $d$ the diameter in $mm$. $\epsilon$ is the unit-less concrete relative permittivity and $\sigma$ is the concrete conductivity in $mS/m$. | 20  |
|  Table 4.2 | The true, ray-based and FWI-estimated parameter values for the experimental data collected using a GSSI 2.6 GHz antenna in the experiment shown in Figures 7-11. $x$ represents the horizontal location in $cm$, $y$ the depth in $cm$ and $d$ the diameter in $mm$. $\epsilon$ is unit-less concrete relative permittivity and $\sigma$ is concrete conductivity in $mS/m$. | 23  |
|  Table 4.3 | Real data - case 2. True and estimated positions and diameters of the bars. Rebar numbers start from the left side of the concrete slab shown in Figure 4.12. $x$ represents the horizontal location in $cm$, $y$ the depth in $cm$ and $d$ the diameter in $mm$. $\epsilon$ is unit-less concrete relative permittivity and $\sigma$ is concrete conductivity in $mS/m$. | 26  |

iii

## List of Figures

|  Figure 1.1 | The FWI flow chart. | 3  |
| --- | --- | --- |
|  Figure 4.1 | Synthetic GPR returns from four reinforcing bars embedded in concrete at depths ranging from 2.7 to 4 cm, as shown in Figure 4.3 assuming a 2.4 MHz antenna and source wavelet shown in Figure 4.4. Noise is added to the data to make the scenario more realistic. | 9  |
|  Figure 4.2 | Geometry for cylinder detection using ground-coupled common-offset GPR antennas. The cylinder size is exaggerated for clarity. | 13  |
|  Figure 4.3 | Cross section of the 3D geometry model for rebar in homogeneous concrete. Four different rebar are assumed at different depths. 10 cells of Perfectly Matched Layer (PML) on each side are added as absorbents to eliminate the boundary effects. | 17  |
|  Figure 4.4 | The source wavelet used to create the synthetic GPR data in Figure 4.1 from the model in Figure 4.3 is a Ricker wavelet derivative with 35° phase rotation. | 17  |
|  Figure 4.5 | Synthetic data from Figure 4.1 after background removal to eliminate the direct wave. Black boxes show sections of the data used to define the initial source wavelet for SBD. | 18  |
|  Figure 4.6 | Top. True source wavelet from the synthetic model (solid gray line); initial source wavelets estimated from the wavelets captured in the boxes shown in Figure 4.5 (solid black line); and source wavelet estimated from the SBD (dashed black line). Bottom. The estimated reflectivity model of the synthetic data from the SBD. The reflectivity model contains a range of values, the color scale has been flattened for clarity. | 19  |
|  Figure 4.7 | Construction of the concrete boxes with rebar. | 21  |
|  Figure 4.8 | Real data - case 1: schematic cross section of the experimental geometry. Three 19-*mm* rebar are buried at different depths. | 21  |
|  Figure 4.9 | Real data - case1, GPR B-scan from a 2.6 GHz antenna over the experiment shown in Figure 4.8. The three bars each produce a distinctive hyperbolic return. | 22  |

iv

Figure 4.10 Real data - case 1 (as in Figure 4.9) with background removed. Black boxes show sections of the data used to define the initial source wavelet for the SBD. 23

Figure 4.11 Real data - case 1: Top. Initial source wavelet estimated from the data in the boxes shown in Figure 4.10 (solid black line); source wavelet estimated from the SBD (dashed black line) for the 2.6 GHz antenna. Bottom. The estimated reflectivity model from the SBD. 24

Figure 4.12 Real data - case 2: Construction of the concrete box with seven 10-mm reinforcing bars at depths ranging from 0.5 to 15 cm. 25

Figure 4.13 Real data - case 2. GPR B-scan over seven rebar from 15 to 0.5 cm depth shown in Figure 4.12, using Sensors and Software 1 GHz antenna. Background removal is applied to mute the direct wave. 26

Figure 4.14 Real data - case 2: Top. Initial source wavelet estimated from the data (solid black line); source wavelet estimated from the SBD (dashed black line) for the 1 GHz antenna. Bottom. The estimated reflectivity model from the SBD. 27

v

# Abstract

Maintenance of aging buried infrastructure and reinforced concrete are critical issues in the United States. Inexpensive non-destructive techniques for mapping and imaging infrastructure and defects are an integral component of maintenance. Ground penetrating radar (GPR) is a widely-used non-destructive tool for locating buried infrastructure and for imaging rebar and other features of interest to civil engineers. Conventional acquisition and interpretation of GPR profiles is based on the arrival times of strong reflected/diffracted returns, and qualitative interpretation of return amplitudes. Features are thereby generally well located, but their material properties are only qualitatively assessed. For example, in the typical imaging of buried pipes, the average radar wave velocity through the overlying soil is estimated, but the properties of the pipe itself are not quantitatively resolved. For pipes on the order of the radar wavelength (<5-35 cm), pipe dimensions and infilling material remain ambiguous. Full waveform inversion (FWI) methods exploit the entire radar return rather than the time and peak amplitude. FWI can generate better quantitative estimates of subsurface properties. In recent decades FWI methods, developed for seismic oil exploration, have been adapted and advanced for GPR with encouraging results. To date, however, FWI methods for GPR data have not been specifically tuned and applied on surface collected common offset GPR data, which are the most common type of GPR data for engineering applications. I present an effective FWI method specifically tailored for common-offset GPR data. This method is composed of three main components, the forward modeling, wavelet estimation and inversion tools. For the forward modeling and iterative data inversion I use two open-source software packages, gprMax and PEST. The source wavelet, which is the most challenging component that guarantees the success of the method, is estimated with a novel Sparse Blind Deconvolution (SBD) algorithm that I have developed. The present dissertation indicates that

vi

with FWI, GPR can yield better quantitative estimates, for example, of both the diameters of small pipes and rebar and their electromagnetic properties (permittivity, conductivity). Also better estimates of electrical properties of the surrounding media (i.e. soil or concrete) are achieved with FWI.

vii

# 1. Introduction

Modern cities and countries demand constant infrastructure growth. Utilities are used for transferring water, sewage, oil, gas, telecommunication cables, power and many other vital components of modern life. Burying new utilities is challenging, especially in the areas lacking maps of existing utilities, often buried more than a few decades ago. Aging infrastructure also requires reliable monitoring. Therefore, non destructive testing and exploration tools are of great importance. Ground penetrating radar (GPR) is a widely used tool for the detection and location of buried utilities. Depending on the depth and sizes of buried features, different antenna frequencies should be selected for the detection procedure (Table 1.1). Higher frequency antennas have shallower depth of penetration, but better spatial resolution. Buried pipes generate characteristic diffraction hyperbolas in raw GPR data. Current methods for analyzing the shapes and timing of the diffraction hyperbolas are very effective for locating pipes, but less effective for determining the diameter of the pipes, particularly when the pipes are smaller than the radar wavelengths, typically a few tens of cms. Traditionally, once the utilities are located the vacuum excavators are used to dig a trench for visual examination of the size and material types, which is destructive.

Table 1.1: Average penetration depth vs the antenna frequency. Values adapted from http://www.geoscan.ca/ground-penetrating-radar-gpr.html

|  Antenna frequency (MHz) | Penetration depth range (m)  |
| --- | --- |
|  100 | 0-30  |
|  250 | 0-8  |
|  800 | 0-1.5  |
|  1600 | 0-0.45  |
|  2600 | 0-0.3  |

1

Traditionally, for GPR data analysis, the arrival times of the recorded returned signal are used for velocity and then depth estimation. With traditional GPR data analysis, it is straightforward to locate infrastructure targets, but difficult to resolve dimensions of small features and reliably determine their electromagnetic properties. If the electromagnetic properties could be accurately determined, precise geometry models and characteristics of pipe-filling material (especially for PVC and other non-metallic pipes) could be more accurately estimated. Current GPR limitations arise because interpretation is limited to identifying the arrival times of strong returns, and only qualitatively assessing variations in amplitudes. When only arrival times are used, objects smaller than $1/4 - 1/2$ of the radar wavelength can be reliably located but the dimensions are not resolved. This is the case for many GPR buried pipe surveys, and for virtually all rebar imaging.

The material properties of the target are difficult to quantitatively assess because the amplitude and waveform of GPR returns, even from simple targets, depend not only on the target properties but also the combined effects of the pulse transmission, antenna-ground coupling, and travel path effects through soil or concrete.

The data collected over utilities contain information about all these challenging effects, but extracting this information is very challenging. Full waveform inversion (FWI) is an optimization/inversion tool that has been around almost for three decades. Development was explicitly for seismic oil and gas exploration, since the method is computationally expensive. It requires a starting model of the subsurface which then update it in an iterative process in order to find the model that best fits the data (Figure 1.1). In GPR studies FWI has been used mainly on crosshole data (see chapter 2) and not on ground-coupled data. With new advanced FWI the entire waveform is used in the analysis, and the fell-wave path effects are implicitly or explicitly considered. As a result, much better estimates of target properties and dimensions can be derived.

This research presents an effective FWI method suitable for commercial type common offset ground-coupled GPR data. This state-of-the-art modeling technique, using a

2

![img-0.jpeg](img-0.jpeg)

Figure 1.1: The FWI flow chart.

computer-based iterative analysis, enables us to significantly improve the initial model given to the algorithm which is equivalent to generating better quantitative estimates of subsurface properties including electrical permittivity and conductivity structures and geometry properties of subsurface features.

Chapter 2 provides an FWI algorithm specifically tailored for the surface common-offset GPR data using two popular open sources packages with a deconvolution code to estimate the source wavelet shape. The effectiveness of the proposed method is tested on models with cylindrical targets, i.e. PVC pipes, embedded in soil. Chapter 3 introduces a novel sparse blind deconvolution (SBD) algorithm for estimating the transmitted wavelet shape. The second product of the developed SBD is a sparse representation of the subsurface reflectivity model. And finally chapter 4 utilizes the developed SBD algorithm in the FWI process to map reinforced structures.

### 1.1 Full waveform inversion for PVC pipe mapping

In Chapter 2, a full-waveform inversion (FWI) method is described for improving estimates of the diameter of a pipe and confirming the infilling material (air/water/etc.) for the simple case of an isolated diffraction hyperbola on a profile run perpendicular to a pipe

3

with antennas in broadside mode (parallel to the pipe). The technique described here can improve a good initial guess of pipe diameter (within 30-50% of the true value) to a better estimate (less than $\sim 8\%$ misfit). This method is developed by combining two freely available software packages with a deconvolution method for GPR effective source wavelet (SW) estimation. The FWI process is run with the PEST algorithm (Model-Independent Parameter Estimation and Uncertainty Analysis). PEST iteratively calls the gprMax software package for forward modeling of the GPR signal as the model for pipe and surrounding soil is refined.

## 1.2 Sparse Blind Deconvolution of Ground Penetrating Radar Data

In Chapter 3, we propose an effective method for sparse blind deconvolution (SBD) of ground penetrating radar (GPR) data. The SBD algorithm has no constraints on the phase of the wavelet, but the initial wavelet must be carefully captured from the data. The data are considered a convolution product of an unknown source wavelet and unknown sparse reflectivity series. The algorithm developed here is an alternating minimization technique that updates the reflectivity series and the wavelet iteratively. The reflectivity update is solved as an $\ell_2 - \ell_1$ problem with the alternating split Bregman iteration technique. The wavelet update is solved as an $\ell_2 - \ell_2$ problem with Wiener deconvolution. The algorithm converges to a local minimum. To increase the likelihood that convergence coincides with the desired local minimum, special steps are taken to provide a proper initial wavelet. Synthetic and real data examples show that both subsurface reflectivity series and wavelet (amplitude and phase) can be estimated efficiently. The SBD method presented appears robust and compares favourably to previous studies in its resistance to noise.

## 1.3 Reinforced structure mapping using FWI

In Chapter 4, we propose an effective full-waveform inversion (FWI) method for obtaining improved estimates of the properties of rebar embedded in concrete structures from surface-coupled common offset ground penetrating radar (GPR) data. We use a sparse blind deconvolution (SBD) technique to obtain the optimized source wavelet (necessary for

4

the FWI process) and a sparse representation of the subsurface reflectivity series. The ray-based analysis is then performed on the estimated reflectivity model (instead of collected GPR data) to define the initial geometry model. The initial model is then updated in an iterative FWI procedure. Results from this method on a synthetic data set and two real data cases show the FWI process significantly improves diameter and electrical property estimates over conventional ray-based methods. The improvement is found for two distinctive real data sets collected with different instruments.

5

## **2. Improving estimates of buried pipe diameter and infilling material from ground-penetrating radar profiles with full-waveform inversion**

Note to Reader:

This chapter has been previously published: S. Jazayeri, A. Klotzsche and S. Kruse, 2018, Improved resolution of pipes with full waveform inversion of common-offset GPR data using PEST; Geophysics, 83(4), H27-H41. DOI: 10.1190/geo2017-0617.1. See Appendix I for the PDF of the published document, Appendix II for the permission from the publisher.

6

### 3. Sparse Blind Deconvolution of Ground Penetrating Radar Data

Note to Reader:

This chapter has been previously published: S. Jazayeri, N. Kazemi, S. Kruse. (2019). Sparse Blind Deconvolution of Ground Penetrating Radar data. In: IEEE Transactions on Geoscience and Remote Sensing, Accepted. DOI: 10.1109/TGRS.2018.2886741. See Appendix III for the PDF of the published document, Appendix IV for the permission from the publisher.

7

## 4. Reinforced Concrete Mapping Using Full-Waveform Inversion of GPR Data $^{1}$

### 4.1 abstract

Full-waveform inversion (FWI) of surface-coupled common-offset GPR B-scans (profiles) over reinforced concrete improves estimates of rebar diameter over more conventional ray-based methods. The method applies a sparse blind deconvolution (SBD) technique to obtain the optimized source wavelet and a sparse representation of the subsurface reflectivity series. The ray-based analysis is then performed on the estimated reflectivity model to define the initial geometry model to start the FWI. Applying this method to a synthetic data set and two real data cases with 1 and 2.6 GHz antennas results in errors in the rebar diameter estimates of less than 11% for rebar with concrete cover 7.5 *cm* or less. These results compare favorably with methods that require additional instrumentation beyond conventional co-polarized GPR surveys. The synthetic model demonstrates that the SBD/FWI method also improves ray-based estimates of the concrete permittivity and conductivity.

### 4.2 keyword

Ground Penetrating Radar, Rebar, Reinforced Concrete, Utilities, Full-Waveform Inversion, Deconvolution, Sparsity

### 4.3 Introduction

Ground Penetrating Radar (GPR) is a safe, popular exploratory tool with many engineering applications. It uses high frequency electromagnetic (EM) waves to non-destructively image reinforced concrete structures (Al-Qadi and Lahouar (2005); Hugenschmidt et al.

---$^{1}$This chapter is prepared for submission to *Construction and Building Materials* journal as: S., Jazayeri, S. Kruse, M., Hassan, N., Yazdani and N. Diamanti (2019). Rebar mapping using Full- Waveform Inversion of Radar data. In: *Construction and Building Materials*, Elsevier.

8

![img-1.jpeg](img-1.jpeg)

Figure 4.1: Synthetic GPR returns from four reinforcing bars embedded in concrete at depths ranging from 2.7 to 4 cm, as shown in Figure 4.3 assuming a 2.4 MHz antenna and source wavelet shown in Figure 4.4. Noise is added to the data to make the scenario more realistic.

(2010); Alani et al. (2013)). The method is particularly well suited to mapping the positions of reinforcing bars. Data with high spatial density can be acquired at vehicle driving speeds, with obvious benefits for road and bridge deck monitoring (Benedetto and Pajewski (2015)).

GPR returns depend on the material properties of the concrete and reinforcing bars, specifically the dielectric constant (i.e. relative permittivity, defined as the ratio of the electrical permittivity of the media to that of free space) and electrical conductivity. Because reinforcing bars are distinctly different than surrounding concrete, they clearly reflect EM energy and generate characteristic hyperbolic returns on GPR profiles, or B-scans (e.g. Figure 4.1). The shape and position of the hyperbola on the GPR profile is controlled by the depth and properties of the rebar, as well as the overlying concrete properties.

The problem of locating the top of the rebar (both laterally and in depth below concrete surface) from the arrival times of the peaks in the hyperbolic GPR return is relatively straightforward and is widely applied. A best fit to the hyperbola arrival times is used to estimate the velocity of the wave in the overlying concrete and thereby estimate the depth of the rebar (e.g. Al-Qadi and Lahouar (2005)). This calculation, referred to as ray-based

9

analysis because it uses the travel times of selected ray paths, can be biased by human errors while fitting the hyperbolas and by noise (e.g. Sham and Lai (2016); Jazayeri et al. (2018)).

In contrast to the depth, the diameter of rebar is difficult to estimate when the rebar is small compared to the radar wavelength. With wavelengths greater than rebar diameter, the arrival times of the peak returns in the hyperbola are simply relatively insensitive to the diameter. Such is commonly the case in concrete investigations, where bar diameter may be 1 cm, while radar wavelength in concrete is 13 cm, for example for a 2.6 GHz antenna in concrete with a relative permittivity of 5. This leaves diameter estimations based on arrival times vulnerable to uncertainties in the material properties of the rebar and the overlying concrete, the shape of the pulse, and to noise in the data. In this paper we focus on a method for improving estimates of the diameters of reinforcing bars. Because this cannot be done without simultaneous estimates of the concrete properties and the GPR pulse, we describe those results as well.

A variety of methods have been examined to estimate diameter using more information from the total GPR returns. Migration is a process for collapsing the diffraction hyperbolas back to their originating point, which in theory could help resolve rebar diameter. However, in real problems, this method is not effective for improved diameter estimation (Soldovieri et al. (2011)). Soldovieri et al. (2006) propose a linear inverse scattering tomographic reconstruction algorithm in the frequency domain based on the Born Approximation. The authors claim satisfactory and reliable results in terms of localization, sizing and shape of the buried objects, but do not provide estimates of the errors in the method.

The amplitudes of the hyperbolic GPR returns can be sensitive to rebar diameter. Hasan and Yazdani (2016a) find an approximate linear relationship between the embedded rebar diameter and the maximum GPR amplitude. However, without knowledge of the source wavelet amplitude (which varies with instrument, concrete conditions, and surface contact) and concrete and rebar properties, the hyperbola peak amplitude cannot be related quantitatively to rebar diameter.

10

Several research groups have established experimental relationships between amplitude and frequency content of the hyperbolic returns and a variety of parameters, including the diameters and electromagnetic properties of reinforcing bars (Kalogeropoulos et al. (2011); Lai et al. (2012); Hasan and Yazdani (2016b)). The primary goal of these studies is to assess corrosion and deterioration in reinforced concrete. The problems of detecting bar diameter and corrosion are necessarily intertwined, as measured GPR returns depend on both the concrete they travel through and the rebar. Lai et al. (2012), Hasan and Yazdani (2016b) and Martino et al. (2016) report that the travel times, amplitudes, and frequency spectra of GPR returns change as corrosion progresses. We note that concrete deterioration effects can be linked with changes in diameter of the rebar as it undergoes through macrocell corrosion, but that significant deterioration (e.g. cracking, delamination) can occur in association with very small (less than 1 mm per year (Elsener (2002))) increases in bar diameter. Thus the focus of this paper is on resolving diameter for scenarios in which the dimensions of embedded bars are unknown, rather than resolving very small diameter changes associated with corrosion.

Researchers have also considered the amplitude ratios of the rebar returns from instrument setups with the transmitting and receiving antennas parallel each other (co-polarized), and setups with two antennas perpendicular to each other (cross-polarized) (Utsi and Utsi (2004), Leucci (2012)). Regressions are used to establish experimental relationships between rebar diameter and the amplitude ratios. Leucci (2012) claims an improvement on the method of Utsi and Utsi (2004) can generate diameter values with 6% error. Improved diameter estimates using cross-polarized antennas are also described by Zanzi and Arosio (2013), who investigate the effect of antenna polarity in rebar detection problems and also the qualitative relationships between the antenna frequency and the diameter. However, methods that require cross-polarized data are not readily available with typical commercial equipment that fixes the antenna pair in a co-polarized geometry. The amplitude ratio methods may also be sensitive to noise since absolute amplitude values are used.

11

Other investigators have described the results of combining GPR technology with a different commercial EM-based system for detecting rebar, a handheld concrete pachometer, also known as covermeter, (Barrile and Pucinotti (2005)). They report diameter estimates with 12% error. This dual method, however lacks the advantage of GPR alone, which can be towed at vehicle speeds over concrete.

Recently, full-waveform inversion (FWI), in which the full waveforms of GPR traces are used, rather than peak arrival times, has been applied to the problem of buried pipe diameter (Jazayeri and Kruse (2016); Jazayeri et al. (2018); Liu et al. (2018)). FWI is shown to improve diameter estimations of water or air-filled PVC pipes and also to predict the pipe's infilling material permittivity.

In this paper, we test the FWI method for estimating rebar diameter. Because the FWI method requires a starting model, it begins with a ray-based estimate of rebar diameter. To optimize this initial estimate, we derive the mathematical expression for the hyperbolic pattern of a cylindrical target perpendicular to the GPR profile, considering both target diameter and transmitter-receiver offset. Second, we adapt the FWI approach from Jazayeri et al. (2018) to the problem of reinforced concrete. This approach requires the shape of the transmitted pulse (known as source wavelet or SW) as an input. We use Jazayeri et al. (2019)'s Sparse Blind Deconvolution (SBD) technique to calculate the SW. Finally, we explore the capabilities of the proposed method on one synthetic and two real data sets.

### 4.4 Method

#### 4.4.1 Analytical expression for travel times

The diameter of a diffracting cylinder affects the arrival time of the GPR signal and the general shape of the diffraction hyperbolas (although as described above this effect is small when the cylinder is small). Al-Nuaimy et al. (2004) and Shihab and Al-Nuaimy (2005) provide formulations that consider the radius of the target and are suitable for least squares approximations. However, for simplification, they treat the transmitter-receiver offset as negligible.

12

![img-2.jpeg](img-2.jpeg)

Figure 4.2: Geometry for cylinder detection using ground-coupled common-offset GPR antennas. The cylinder size is exaggerated for clarity.

Here we relax the zero-offset assumption in the ray formulation. In commercial shielded instruments the transmitting and receiving antennas move together with a constant, but non-zero, offset. Figure 4.2 illustrates the problem. The transmitting (T) and receiving (R) antennas are respectively at distances d_T and d_R from the point of beam incidence on the rebar circumference (O') and are placed at x_T and x_R on ground, where |x_T - x_R| = δx is the antenna offset. The rebar with radius r is at horizontal location x and the top of it is at depth y below the surface. Since rebar are often metallic and can be considered as almost perfect electrical conductors, the point of incidence, O' at depth h ≥ y and at horizontal location x_0, plays a critical role in shaping the hyperbolic patterns.

Antennas used in rebar inspection generally have frequencies greater than 1 GHz (due to shallow burial depth and small rebar diameters) and are very small in size (less than several centimeters). Previous authors approximated d_T and d_R as O' leading to equation (4.1). However, for small targets this approximation may approach the time corrections associated with the target radius. Here d_T and d_R are considered explicitly. To calculate d_T and d_R requires O' and φ (the angle between the rebar center and the antenna center). φ is calculated via (4.2) and the depth and position of point O', h and x_0, are obtained via (4.3) and (4.4).

13

$$d = \sqrt{(x - x_T - \frac{\delta x}{2})^2 + (y + r)^2} - r \tag{4.1}$$

$$\phi = \arctan \frac{x - (x_T + \frac{\delta x}{2})}{y + r} \tag{4.2}$$

$$h = y + r(1 - \cos \phi) \tag{4.3}$$

$$x_0 = x - r \sin \phi \tag{4.4}$$

Finally, $d_T$ and $d_R$ are calculated using (4.5) and (4.6), respectively. Considering the medium around the rebar to be homogeneous with relative permittivity $\epsilon$, the two-way travel time of the EM pulse diffracted from rebar, $t_{TO'R}$, is obtained from (4.7), where $c$ is the speed of light in free space and $t_0$ is the effective time zero at which the pulse leaves the transmitter.

$$d_T = \sqrt{(x_0 - x_T)^2 + h^2} \tag{4.5}$$

$$d_R = \sqrt{(x_0 - x_T - \frac{\delta x}{2})^2 + h^2} \tag{4.6}$$

$$t_{TO'R} = \frac{d_T + d_R}{c / \sqrt{(\epsilon)}} + t_0 \tag{4.7}$$

The rebar diameter and rebar location can be calculated by finding the radius, position, and concrete permittivity that best fits the ray travel times in (4.7). However, the accuracy of this is limited if data are noisy or if hyperbola picking is performed inaccurately (Sham and Lai (2016); Jazayeri et al. (2018)). These values are thus used here as the initial estimates for the FWI process.

14

We note that full waveform inversion also requires an initial estimate of the concrete conductivity, and the rebar permittivity and conductivity. The initial concrete conductivity estimate is derived with the method of Jazayeri et al. (2018). The FWI process involves iterations with forward modeling of the wave propagation, which is done using the code gprMax (Warren et al. (2016)). The rebar is fixed as 'pec', or perfect electric conductor, in gprMax. The radar wave does not penetrate this medium and hence the medium does not have defined material properties. We note that this assumption would not be appropriate for corroded rebar. The initial estimates of all other properties are updated in the FWI process.

Because the FWI process aims to find the model that best fits the real data, the shape of the transmitted pulse must be considered. The effective pulse shape, or source wavelet can not be directly measured with ground-coupled antennas. Deconvolution strategies offer an alternative solution. Deconvolution methods that require no initial information of subsurface geometry are known as blind deconvolution. Recent developments in blind deconvolution enable us to handle even noisy data based on a sparsity assumption of subsurface reflectivities. Here we use the sparse blind deconvolution (SBD) algorithm from Jazayeri et al. (2019), described briefly below.

Data can be considered as a convolution product of the source wavelet and the subsurface reflectivity model, both unknown, plus additive noise. Fully blind deconvolutions that can solve for both unknowns are extremely computationally expensive. However if an initial estimate for the source wavelet can be captured from the data, the sparse reflectivity model can be estimated using an $\ell_2 - \ell_1$ norm problem solved by Split-Bregman algorithms (e.g. Jazayeri et al. (2019)). This process then can be taken into a two-step loop of updating the SW (by solving an $\ell_2 - \ell_2$ norm problem, the Wiener filter) and then the reflectivity model. If sufficient care is taken while selecting the initial SW, the final SW and reflectivity models are likely to be the global solutions for this minimization problem. (This requirement is loosely equivalent to a starting model in which the pulses differ by less than half a

15

wavelength from the true values (Meles et al. (2010)).) The final SW is fed into the FWI process.

The final reflectivity structure that comes out of the SBD can be considered as a model of data in which the effect of the pulse shape and much of the noise are removed. Therefore, the hyperbolas in the estimated reflectivity model are clear and are used to perform the ray-based analysis associated with equations 2-7. The ray-estimated rebar locations and diameters and concrete permittivity are used as the FWI starting model. Details on the FWI process are described in step 5 of Jazayeri et al. (2018).

### 4.5 Results

We evaluate the performance of the proposed method on one synthetic and two real data examples acquired with different instruments in different experiments.

#### 4.5.1 Synthetic data, reinforced concrete

For the synthetic test, we create 3D data with the first derivative of a Ricker wavelet with 35° phase rotation as the source wavelet (following Jazayeri et al. (2019, 2018)). The antenna is a Hertzian dipole with 3 cm transmitter-receiver offset and nominal frequency of 2.4 GHz. Four metallic rebars are placed at depths between 2.7 and 4 cm (see Table 4.1 and Figure 4.3) in uniform concrete. High and low frequency noise are added to the data with a Gaussian distribution of high-frequency noise centered at 3 GHz and peak value of 25% of the pulse amplitude, and lower frequency noise (1.5 MHz) added at a lower level (15% of pulse amplitude) (Figure 4.1). Parts of the diffracted signal, specifically for the rebar #4 are mixed with the direct wave. Realistic modeling of the direct wave is challenging due to the fact that it falls in the near-field zone. To avoid including the direct wave in the analysis, a background removal filter (an average trace removal across the whole profile) is applied to the data (Figure 4.5).

To define the initial source wavelet required for the SBD algorithm sections of data in proximity to the hyperbola apexes are carefully selected, time-shifted in order to maximize

16

![img-3.jpeg](img-3.jpeg)

Figure 4.3: Cross section of the 3D geometry model for rebar in homogeneous concrete. Four different rebar are assumed at different depths. 10 cells of Perfectly Matched Layer (PML) on each side are added as absorbents to eliminate the boundary effects.

![img-4.jpeg](img-4.jpeg)

Figure 4.4: The source wavelet used to create the synthetic GPR data in Figure 4.1 from the model in Figure 4.3 is a Ricker wavelet derivative with $35^{\circ}$ phase rotation.

17

![img-5.jpeg](img-5.jpeg)

Figure 4.5: Synthetic data from Figure 4.1 after background removal to eliminate the direct wave. Black boxes show sections of the data used to define the initial source wavelet for SBD.

the zero-lag cross-correlation, stacked and normalized (black boxes on Figure 4.5). This results in an initial wavelet whose general shape follows the true wavelet, but the amplitudes of the two positive parts of the signal are clearly under-estimated (Figure 4.6). The SBD process successfully modifies this initial wavelet to a wavelet closer to the true one, although some mismatch remains, presumably due to the effects of noise in the data. The final estimated reflectivity model (Figure 4.6) is a relatively clean representation of the data with the source wavelet removed. The hyperbolic portions of the reflectivity model are then used for the ray-based analysis to determine the initial model. At this stage horizontal locations of the targets are well estimated. However from the ray-based analysis alone, significant errors remain in the estimates of the rebar depth, relative permittivity and conductivity of the concrete and especially the rebar diameters (Table 4.1). On average, the diameter values are estimated with 73% error, with a minimum of 25% and a maximum of 124% error. Variability in the estimated diameters from ray-based analysis is associated with the random noise in the data, which confirms the sensitivity of ra-based results to noise.

The FWI process then improves the estimates of almost all parameters, particularly the diameter values (Table 4.1). The average error in the diameter after FWI is 9.7%, with a

18

![img-6.jpeg](img-6.jpeg)

Figure 4.6: Top. True source wavelet from the synthetic model (solid gray line); initial source wavelets estimated from the wavelets captured in the boxes shown in Figure 4.5 (solid black line); and source wavelet estimated from the SBD (dashed black line). Bottom. The estimated reflectivity model of the synthetic data from the SBD. The reflectivity model contains a range of values, the color scale has been flattened for clarity.

19

Table 4.1: The true, ray-based estimated and FWI-estimated parameter values for the synthetic model shown in Figure 4.3. $x$ represents the horizontal location in $cm$, $y$ the depth in $cm$ and $d$ the diameter in $mm$. $\epsilon$ is the unit-less concrete relative permittivity and $\sigma$ is the concrete conductivity in $mS/m$.

|  rebar# | True |   |   | Ray-based |   |   | FWI  |   |   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|   |  x | y | d | x | y | d | x | y | d  |
|  1 | 15 | 3.5 | 20 | 16.46 | 4.64 | 24.9 | 14.99 | 3.62 | 21.63  |
|  2 | 35 | 3.5 | 20 | 36.51 | 4.04 | 7.2 | 35.00 | 3.57 | 19.02  |
|  3 | 60 | 4 | 20 | 61.47 | 5.9 | 44.8 | 60.00 | 3.78 | 16.95  |
|  4 | 80 | 2.7 | 20 | 81.46 | 3.89 | 35.7 | 77.96 | 2.56 | 22.31  |
|  Parameter | True | Ray-based | FWI |   |   |   |   |   |   |
|  $\bar{\epsilon}_{concrete}$ | 5 | 3.89 | 4.77 |   |   |   |   |   |   |
|  $\sigma_{concrete}$ | 10 | 14.2 | 11.2 |   |   |   |   |   |   |

minimum of 4% and maximum of 15.2%. Since the FWI estimate for $\epsilon_{concrete}$ is improved over the ray-based value, depths are also more accurately estimated. The concrete conductivity estimate is similarly improved.

#### 4.5.2 Real data, case 1

A concrete block with length 137 $cm$, width 25 $cm$ and depth 15 $cm$ was constructed using normal weight concrete ($^{water}/_{cement}$ ratio of 0.4; maximum aggregate size of 19 $mm$ with a 28 day target compressive strength of 4000 $psi$) (Figure 4.7 in next page) Hasan and Yazdani (2016b). Three different standard 19 $mm$ ($^{3}/_{4}''$) rebar were embedded with different concrete covers (2.5, 5, 7.5 $cm$) (Figure 4.8). A ground-coupled 2.6 $GHz$ GSSI system was used to collect GPR B-scans perpendicular to rebar direction.

Initial basic processing of the collected data is required before FWI. A standard dewow filter and time-zero correction are applied first. Finally, high frequency noise was removed from the data using a simple low pass filter to remove the frequencies greater than 3.2 GHz.

As for the synthetic example, the returns from the least deep rebar (thinnest cover thickness) are mixed in the direct wave (Figure 4.9) and background removal is applied before SBD (Figure 4.10). The initial source wavelet for SBD is captured from the data (black boxes

20

![img-7.jpeg](img-7.jpeg)

Figure 4.7: Construction of the concrete boxes with rebar.

![img-8.jpeg](img-8.jpeg)

Figure 4.8: Real data - case 1: schematic cross section of the experimental geometry. Three 19-mm rebar are buried at different depths.

21

![img-9.jpeg](img-9.jpeg)

Figure 4.9: Real data - case1, GPR B-scan from a 2.6 GHz antenna over the experiment shown in Figure 4.8. The three bars each produce a distinctive hyperbolic return.

in Figure 4.10). The SBD process alters the shape of the initial wavelet, especially around the tail (Figure 4.11 top). The estimated reflectivity model used to define the initial model for the FWI is shown in Figure 4.11 bottom. From the ray-based analysis, the diameter values are estimated with 35% error, with a minimum of 25% and a maximum of 44% (Table 4.2).

The FWI significantly improves estimates of rebar depths, presumably due to a better $\varepsilon_{concrete}$ estimation. The average error for the estimated diameter values after FWI is 7.2%, with a minimum of 0.1% and a maximum of 11.1%. The conductivity estimate is altered significantly (Table 4.2).

### 4.5.3 Real data, case 2

Seven 10 mm rebar were embedded in a concrete slab, each at a different depth (Figure 4.12 and Table 4.3). Compared to the experiment in case 1, these rebar are approximately half the dimension, and buried over a greater depth range, from 0.5 to 15 cm. A common-offset B-scan was collected using the Noggin 1000 Sensors and Software system with 1 GHz

22

![img-10.jpeg](img-10.jpeg)

Figure 4.10: Real data - case 1 (as in Figure 4.9) with background removed. Black boxes show sections of the data used to define the initial source wavelet for the SBD.

Table 4.2: The true, ray-based and FWI-estimated parameter values for the experimental data collected using a GSSI 2.6 GHz antenna in the experiment shown in Figures 7-11. x represents the horizontal location in cm, y the depth in cm and d the diameter in mm.  \( \epsilon \)  is unit-less concrete relative permittivity and  \( \sigma \)  is concrete conductivity in mS/m.

|  rebar# | True |   |   | Ray-based |   |   | FWI  |   |   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|   |  x | y | d | x | y | d | x | y | d  |
|  1 | 15 | 2.5 | 19 | 15.34 | 2.2 | 14.3 | 15.02 | 2.42 | 17.02  |
|  2 | 45 | 5.0 | 19 | 44.51 | 4.14 | 27.34 | 45.05 | 5.02 | 19.02  |
|  3 | 76 | 7.5 | 19 | 74.47 | 6.9 | 12.0 | 75.5 | 7.61 | 16.89  |
|  Parameter | True | Ray-based | FWI |   |   |   |   |   |   |
|  \( \bar{\epsilon}_{concrete} \) | - | 5.11 | 4.77 |   |   |   |   |   |   |
|  \( \sigma_{concrete} \) | - | 8.22 | 14.09 |   |   |   |   |   |   |

23

![img-11.jpeg](img-11.jpeg)

Figure 4.11: Real data - case 1: Top. Initial source wavelet estimated from the data in the boxes shown in Figure 4.10 (solid black line); source wavelet estimated from the SBD (dashed black line) for the 2.6 GHz antenna. Bottom. The estimated reflectivity model from the SBD.

24

![img-12.jpeg](img-12.jpeg)

Figure 4.12: Real data - case 2: Construction of the concrete box with seven 10-mm reinforcing bars at depths ranging from 0.5 to 15 cm.

nominal frequency perpendicular to the rebar direction (Figure 4.13). Unlike the case 1 study, the hyperbolas overlap one another at their outer edges.

Similar to the previous case, a standard dewow filter and time-zero correction are applied on the data. High frequency noise, with frequencies greater than 1.6 GHz, is removed from the data using a simple low pass filter.

As for the previous test cases, the wavelet is carefully captured from the data and optimized through the SBD to estimate the source wavelet. The reflectivity model estimated from SBD is similarly used for the ray-based analysis. The ray-based and final FWI results are included in Table 4.3. On average the sizes estimated with the ray-based analysis have 61% error with a minimum of 30% and maximum of 162% error. After the FWI process the average size estimation error is 17% with a minimum of 3% and a maximum of 51% error. The highest errors are found for the deepest targets where amplitudes are lower and signal to noise ratio is poorest.

## 4.6 Discussion and Conclusions

We provide the mathematical expressions for cylindrical targets in common-offset GPR data assuming non-point diffractors and realistic antenna offset, in order to optimize estimates of cylindrical target diameter using ray-based analysis. Travel times for the ray-

25

Table 4.3: Real data - case 2. True and estimated positions and diameters of the bars. Rebar numbers start from the left side of the concrete slab shown in Figure 4.12. x represents the horizontal location in cm, y the depth in cm and d the diameter in mm.  \( \epsilon \)  is unit-less concrete relative permittivity and  \( \sigma \)  is concrete conductivity in mS/m.

|  rebar# | True |   |   | Ray-based |   |   | FWI  |   |   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|   |  x | y | d | x | y | d | x | y | d  |
|  1 | 15 | 15 | 10 | 14.9 | 16.8 | 26.2 | 14.9 | 14.6 | 15.1  |
|  2 | 30 | 10 | 10 | 29 | 9.4 | 17.7 | 29.5 | 9.8 | 12.8  |
|  3 | 45 | 7.5 | 10 | 45.1 | 8.2 | 14.2 | 45.1 | 7.6 | 9.7  |
|  4 | 60 | 5 | 10 | 60 | 5.5 | 13.0 | 60 | 5.2 | 10.3  |
|  5 | 75 | 2.5 | 10 | 75.4 | 3.1 | 5.5 | 75.3 | 2.6 | 8.9  |
|  6 | 90 | 1 | 10 | 89.7 | 0.5 | 15.1 | 90 | 0.9 | 10.4  |
|  7 | 105 | 0.5 | 10 | 104.9 | 0.0 | 15.9 | 105.1 | 0.2 | 10.6  |
|  Parameter | True | Ray-based | FWI |   |   |   |   |   |   |
|  \( \bar{\epsilon}_{concrete} \) | - | 6.56 | 5.98 |   |   |   |   |   |   |
|  \( \sigma_{concrete} \) | - | 28.45 | 19.72 |   |   |   |   |   |   |

![img-13.jpeg](img-13.jpeg)

Figure 4.13: Real data - case 2. GPR B-scan over seven rebar from 15 to 0.5 cm depth shown in Figure 4.12, using Sensors and Software 1 GHz antenna. Background removal is applied to mute the direct wave.

26

![img-14.jpeg](img-14.jpeg)

![img-15.jpeg](img-15.jpeg)

Figure 4.14: Real data - case 2: Top. Initial source wavelet estimated from the data (solid black line); source wavelet estimated from the SBD (dashed black line) for the 1 $GHz$ antenna. Bottom. The estimated reflectivity model from the SBD.

27

based analysis are estimated from the reflectivity series derived from a sparse blind deconvolution of the radar data. Output parameters from the ray-based analysis and an effective source wavelet estimated from the same deconvolution are used to create a starting model for full-waveform inversion of the radar data on reinforced concrete.

For a synthetic scenario and two experiments using different instruments over rebar with concrete cover ranging from 1 to 15 cm, the FWI significantly improves estimates of rebar diameter over the ray-based analyses. Errors in the final diameter estimates range from 0.1% to 11% for scenarios where the rebar depth is 7.5 cm or less. These errors are similar to values reported for other methods (6-12%) that require cross-polarized antennas or additional methods beyond GPR.

We note that all cases reported here assume uniform permittivity and conductivity in the concrete. The synthetic case demonstrates that the FWI improves estimates of both these parameters.

A key limitation in the method presented here is that it requires the GPR profile to be perpendicular to the rebar. Errors associated with this assumption are the topic of future investigation. Future research will also consider the effects of heterogeneity in the overlying concrete and relationships to corrosion status.

28

## 5. Conclusion

In Chapter 2, This paper introduces a new method for FWI of common-offset GPR data, particularly targeting the dimensions and infilling material of buried pipes. The method is designed to be used where clear isolated diffraction hyperbolas indicate the presence of a pipe, but pipe dimensions and filling may be unknown. The method consists of five main steps: GPR data processing, ray-based analysis to set a good initial model, 3D to 2D transformation of data, effective SW estimation, and full-waveform inversion. The method combines two freely available software packages: PEST, for the inversion, and gprMax for forward modeling of the GPR data.

This method is applied on a synthetic 3D dataset and two 800 MHz GPR profiles collected over a PVC pipe buried in clean sands. In the synthetic and water-filled and air-filled pipe field cases, good initial estimates of the depth and diameter of the pipe from the ray-based analysis are improved after FWI. The tests show that while the initial estimate of pipe diameter is within 30-50% of the true value, the inversion yields estimates with <8% error. For the field data, the requirement of a good starting model can in practice confirm or deny a starting assumption about the pipe-filling material.

Ray-based analysis is essential to set up the starting model, particularly to estimate the pipe location and average soil permittivity and conductivity. Although ray-based conductivity estimates are possible, improvement in the conductivity would require the SW to be updated after each iteration in the FWI procedure. Iterations on the SW during the FWI process, as in Busch et al. (2012; 2014), are beyond the scope of this study. The method in its present form is only effective for isolated hyperbolas, and assumes that GPR surveys

29

are conducted with broadside antenna geometry along profiles perpendicular to horizontal pipes. Furthermore, the soil is assumed to be locally homogenous.

In Chapter 3, the proposed sparse blind deconvolution method is tested on synthetic and simple field ground penetrating radar data. The method estimates the reflectivity model of the subsurface and the transmitted pulse shape efficiently and simultaneously without requiring any prior information from the subsurface or any assumption about the phase of the wavelet. The initial source wavelet estimate is made by extracting and averaging a subset of the data. The process then iteratively updates the reflectivity model and source wavelet.

The method is tested on datasets with cylindrical targets and different noise levels. High frequency noise alone is handled with the split Bregman algorithm parameters $$\alpha = 0.5$$ and $$\beta = 1$$ while scenarios with more low frequency noise and a complex pulse are better treated with $$\alpha = 0.01$$ to $$0.001$$ and $$\beta = 0.5$$. The hyperbolic shapes of the recorded signals are well recovered in the reflectivity models. In the synthetic models the initial wavelet estimate is improved upon, and the final wavelet estimate is a good fit to the true wavelet.

For ground penetrating radar studies, sparse blind deconvolution can be useful for image resolution enhancement and better understanding of the source wavelet. Both the estimated source wavelet and reflectivity model can be used in further advanced modeling procedures such as FWI.

Chapter 4 presents an effective full-waveform inversion method for the common-offset surface ground-penetrating radar data to model the rebars in reinforced concrete slabs. This presented method can be an effective way to improve the traditional analysis results. Traditional ray-based analysis either assumes the targets with hyperbolic returns to be point diffractors which will fail to provide any kind of information about the target size or would consider the non-point diffractor but still are very sensitive to the noise level in the data and therefore the estimated values can be highly biased. We have first provided the mathematical expressions of cylindrical targets in common-offset GPR data assuming non-point diffractors and realistic antenna offset. However, the models shown in this article show errors up to 200-

30

300% of the true diameter value using the ray-based analysis. The full-waveform inversion process can be used to improve the subsurface models from common-offset GPR data, however it requires an effective estimated wavelet. In this paper we have shown that the sparse blind deconvolution can effectively be used to define both the source wavelet and the subsurface reflectivity model. The initial model is then defined by performing the ray-based analysis on the estimated reflectivity model. On average the rebar sizes are estimated with around 1.5% error with this proposed. The numerical results suggest an improved estimate of permittivity and conductivity as well as diameters.

31

## References

Al-Nuaimy, W., Shihab, S., and Eriksen, A. (2004). Data fusion for accurate characterisation of buried cylindrical objects using GPR. In *Ground Penetrating Radar, 2004. GPR 2004. Proceedings of the Tenth International Conference on*, volume 1, pages 359–362. IEEE.

Al-Qadi, I. and Lahouar, S. (2005). Part 4: Portland cement concrete pavement: measuring rebar cover depth in rigid pavements with ground-penetrating radar. *Transportation Research Record: Journal of the Transportation Research Board*, (1907):80–85.

Alani, A. M., Aboutalebi, M., and Kilic, G. (2013). Applications of ground penetrating radar (GPR) in bridge deck monitoring and assessment. *Journal of Applied Geophysics*, 97:45–54.

Barrile, V. and Pucinotti, R. (2005). Application of radar technology to reinforced concrete structures: a case study. *NDT & E International*, 38(7):596–604.

Benedetto, A. and Pajewski, L. (2015). *Civil engineering applications of ground penetrating radar*. Springer.

Elsener, B. (2002). Macrocell corrosion of steel in concrete–implications for corrosion monitoring. *Cement and concrete composites*, 24(1):65–72.

Hasan, M. I. and Yazdani, N. (2016a). An experimental and numerical study on embedded rebar diameter in concrete using ground penetrating radar. *Chinese Journal of Engineering*, 2016.

32

Hasan, M. I. and Yazdani, N. (2016b). An experimental study for quantitative estimation of rebar corrosion in concrete using ground penetrating radar. *Journal of Engineering*, 2016.Hugenschmidt, J., Kalogeropoulos, A., Soldovieri, F., and Prisco, G. (2010). Processing strategies for high-resolution GPR concrete inspections. *NDT & E International*, 43(4):334–342.Jazayeri, S., Kazemi, N., and Kruse, S. (2019). Sparse blind deconvolution of ground penetrating radar data. *IEEE Transactions on Geoscience and Remote Sensing*, pages 1–10.Jazayeri, S., Klotzsche, A., and Kruse, S. (2018). Improving estimates of buried pipe diameter and infilling material from ground-penetrating radar profiles with full-waveform inversion. *GEOPHYSICS*, 83(4):H27–H41.Jazayeri, S. and Kruse, S. (2016). Full-waveform inversion of ground-penetrating radar (gpr) data using pest (fwi-pest method) applied to utility detection. In *SEG Technical Program Expanded Abstracts 2016*, pages 2474–2478. Society of Exploration Geophysicists.Kalogeropoulos, A., Van der Kruk, J., Hugenschmidt, J., Busch, S., and Merz, K. (2011). Chlorides and moisture assessment in concrete by gpr full waveform inversion. *Near Surface Geophysics*, 9(3):277–285.Lai, W.-L., Kind, T., Stoppel, M., and Wiggenhauser, H. (2012). Measurement of accelerated steel corrosion in concrete using ground-penetrating radar and a modified half-cell potential method. *Journal of Infrastructure Systems*, 19(2):205–220.Leucci, G. (2012). Ground penetrating radar: an application to estimate volumetric water content and reinforced bar diameter in concrete structures. *Journal of Advanced Concrete Technology*, 10(12):411–422.

33

Liu, T., Klotzsche, A., Pondkule, M., Vereecken, H., Su, Y., and van der Kruk, J. (2018). Radius estimation of subsurface cylindrical objects from ground-penetrating-radar data using full-waveform inversion. *Geophysics*, 83(6):H43–H54.Martino, N., Maser, K., Birken, R., and Wang, M. (2016). Quantifying bridge deck corrosion using ground penetrating radar. *Research in Nondestructive Evaluation*, 27(2):112–124.Meles, G. A., Van der Kruk, J., Greenhalgh, S. A., Ernst, J. R., Maurer, H., and Green, A. G. (2010). A new vector waveform inversion algorithm for simultaneous updating of conductivity and permittivity parameters from combination crosshole/borehole-to-surface gpr data. *IEEE Transactions on geoscience and remote sensing*, 48(9):3391–3407.Sham, J. F. and Lai, W. W. (2016). Development of a new algorithm for accurate estimation of GPR's wave propagation velocity by common-offset survey method. *NDT & E International*, 83:104–113.Shihab, S. and Al-Nuaimy, W. (2005). Radius estimation for cylindrical objects detected by ground penetrating radar. *Subsurface sensing technologies and applications*, 6(2):151–166.Soldovieri, F., Persico, R., Utsi, E., and Utsi, V. (2006). The application of inverse scattering techniques with ground penetrating radar to the problem of rebar location in concrete. *NDT & E International*, 39(7):602–607.Soldovieri, F., Solimene, R., Monte, L. L., Bavusi, M., and Loperte, A. (2011). Sparse reconstruction from GPR data with applications to rebar detection. *IEEE transactions on instrumentation and measurement*, 60(3):1070–1079.Utsi, V. and Utsi, E. (2004). Measurement of reinforcement bar depths and diameters in concrete. In *Ground Penetrating Radar, 2004. GPR 2004. Proceedings of the Tenth International Conference on*, pages 659–662. IEEE.

34

Warren, C., Giannopoulos, A., and Giannakis, I. (2016). gprmax: Open source software to simulate electromagnetic wave propagation for ground penetrating radar. *Computer Physics Communications*, 209:163–170.

Zanzi, L. and Arosio, D. (2013). Sensitivity and accuracy in rebar diameter measurements from dual-polarized GPR data. *Construction and Building Materials*, 48:1293–1301.

35

# **Appendix I. Improving estimates of buried pipe diameter and infilling material  
from ground-penetrating radar profiles with full-waveform inversion**

36

GEOPHYSICS, VOL. 83, NO. 4 (JULY-AUGUST 2018): P. H27–H41, 17 FIGS., 2 TABLES.
10.1199/G0202017-0617.1

Check for updates

# Improving estimates of buried pipe diameter and infilling material from ground-penetrating radar profiles with full-waveform inversion

Sajad Jazayeri¹, Anja Klotzsche², and Sarah Kruse¹

# ABSTRACT

Ground-penetrating radar (GPR) is a widely used tool for the detection and location of buried utilities. Buried pipes generate characteristic diffraction hyperbolas in raw GPR data. Current methods for analyzing the shapes and timing of the diffraction hyperbolas are very effective for locating pipes, but they are less effective for determining the diameter of the pipes, particularly when the pipes are smaller than the radar wavelengths, typically a few tens of centimeters. A full-waveform inversion (FWI) method is described for improving estimates of the diameter of a pipe and confirming the infilling material (air/water/etc.) for the simple case of an isolated diffraction hyperbola on a profile run perpendicular to a pipe with antennas in broadside mode (parallel to the pipe). The technique described here can improve a good initial guess of the pipe diameter (within 30%–50% of the true value) to a better estimate (less than approximately 8% misfit). This method is developed by combining two freely available software packages with a deconvolution method for GPR effective source wavelet estimation. The FWI process is run with the PEST algorithm (model-independent parameter estimation and uncertainty analysis). PEST iteratively calls the gprMax software package for forward modeling of the GPR signal as the model for the pipe and surrounding soil is refined.

# INTRODUCTION

Modern life depends on subsurface pipelines used to carry water, oil, gas, sewage, and other fluids. Civil engineering and construction industries face the challenge of maintaining and repairing existing pipelines as well as laying new pipes. Increasing demand

for new buried utilities increases the risk of damaging existing utilities (Lester and Bernold, 2007). As infrastructure ages, the demand for repairs and replacement requires knowledge of the locations and connectivities of multiple utility systems installed at different times, using different materials, in increasingly dense networks, in which records are often incomplete. In such scenarios, simply detecting a pipe at a given location may not be sufficient information. Ground-penetrating radar (GPR) resolution of not only the presence of the pipe but also the pipe diameter, pipe material, or pipe-filling material (e.g., air, water) could be a way to distinguish and map different generations or types of utilities.

GPR has become one of the primary tools of choice for mapping the locations of pipes in urban settings. The transmitting antenna emits an electromagnetic (EM) pulse that propagates into the subsurface. The EM pulse travels through the subsurface material, and it is reflected, scattered, and attenuated. The reflection or scattering occurs when the pulse encounters a subsurface inhomogeneity, in particular, soil heterogeneities or targets with contrasting dielectric properties (permittivity). (We note that the permittivity here is expressed as relative permittivity, which is the ratio of the material permittivity to the permittivity of free space.) The pulse attenuation is primarily controlled by the electrical conductivity of the soil. Reflected energy is recorded by the receiving antenna. The signal recorded at the receiving antenna contains a combination of the energy traveling in air and along the ground surface, reflected and refracted energy from soil inhomogeneities, buried targets (in this case, pipes), and noise. A buried pipe generates a characteristic diffraction hyperbola because of its shape and contrast in EM properties with the background soil. The diffraction hyperbolas of pipes in GPR profiles are sufficiently distinctive that they can be displayed and interpreted in real time; hence, GPR is widely used for on-the-spot utility detection.

GPR responses expected from underground utilities, drums, tanks, and cables have been described in the literature. Early modeling by Zeng and McMechan (1997) describes responses for a variety of utility scenarios, with air-filled, water-filled, and partially

Manuscript received by the Editor 14 September 2017; revised manuscript received 4 December 2017; published ahead of production 09 March 2018; published online 25 April 2018.

¹University of South Florida, School of Geosciences, Tampa, Florida, USA. E-mail: sjazayeri@mail.usf.edu; skruse@usf.edu.

²Institute of Bio- and Geosciences, Agrosphere (IBG-3), Forschungszentrum Jülich, Jülich, Germany. E-mail: a.klotzsche@fz-juelich.de.

© 2018 Society of Exploration Geophysicists. All rights reserved.

H27

Downloaded 01/15/19 to 131.247.224.4. Redistribution subject to SEG license or copyright; see Terms of Use at http://library.seg.org/

37

Downloaded 01/15/19 to 131.247.224.4. Redistribution subject to SEG license or copyright; see Terms of Use at http://library.seg.org/

H28

Jazayeri et al.

saturated pipes. Maierhofer et al. (2010) provide a workflow for the typical common-offset GPR data analysis procedures as well as modeling and imaging techniques common to rebar detection. Benedetto and Pajewski (2015) describe examples of GPR surveys in civil engineering, including pavement, bridges, tunnels and buildings, underground utilities, and voids.

The horizontal position of an underground pipe on a GPR profile is readily established as the location of the peak of the characteristic diffraction hyperbola (Figure 1). Inferring the depth to the top of the pipe requires knowledge of the average velocity structure of materials over the pipe. Loeffler and Bano (2004) study the impact of water content on the permittivity and therefore on GPR signals by simulations of cylindrical objects in the vadose zone. One way to derive the propagation velocity in the medium is by conducting a common-midpoint (CMP) or wide-angle reflection and refraction (WARR) survey, in which the spacing between the transmitter and receiver is progressively increased. Following methods derived for stacking seismic data, layer velocities can be determined by semblance analysis (Fisher et al., 1992; Grandjean et al., 2000; Liu and Sato, 2014; Liu et al., 2014). This method has the advantage of recovering information on how velocity varies with depth, but it requires surveys with systems that permit a variable offset between transmitter and receiver. Urban surveys require shielded antennas (to avoid reflections from surficial objects); most shielded systems cover a transmitter-receiver pair in a single shielded unit that does not lend itself to easy acquisition of CMP surveys. Alternatively, an average velocity can be determined from the shape and timing of the diffraction hyperbola that forms the GPR return from the pipe itself. So, in general, the pipe depth is estimated by finding the average velocity that best fits the measured hyperbola. However, Sham and Lai (2016) observe that the curve-fitting method is biased by human judgment. Grandjean et al. (2000), Booth et al. (2011), and Murray et al. (2007) describe the accuracy with which velocities, and hence depths of utilities, can be determined via both methods.

In this paper, we focus on how to extract additional information about pipes, beyond position and depth, from GPR profiles. The

![img-16.jpeg](img-16.jpeg)

Figure 1. A synthetic GPR profile for an air-filled PVC pipe. The inner diameter of the pipe is 40 cm with a wall thickness of 3 mm; the central frequency of the antenna is 800 MHz. In this case, distinct reflections from the top and bottom of pipe are observed; later, weaker arrivals are multiples.

pipe diameter affects GPR returns, most visibly when the radar wavelength is small compared with the pipe diameter and the pipe's permittivity is significantly different from the surrounding soil (Roberts and Daniels, 1996). In this case, distinct returns can be captured from the top and bottom of the pipe, as shown in Figure 1 (e.g., Zeng and McMechan, 1997). It is easier to capture the dimensions of water-filled pipes than air-filled pipes because the slow radar velocity in water delays the return from the bottom of the pipe by a factor of approximately nine over the equivalent air delay. In either case, when the pipe is narrow enough that the top and bottom returns overlap and interfere, extracting information on pipe diameter from the single hyperbola is challenging. Wincatujanagul et al. (2017) report no significant difference for the hyperbolic reflections for different rebar diameters. Diameter estimation based on fitting hyperbolas is clearly impacted by decisions about the phase of the pipe return selected for the fit (because one can choose either positive or negative phases; see Dou et al., 2017) and trade-offs made in wave velocity and pipe diameter selections. The hyperbola-fitting method also cannot provide any information about the pipe-filling material.

Ristic et al. (2009) present a method to estimate the radius of a cylindrical object and the wave propagation velocity from GPR data simultaneously based on the hyperbola fitting. In their method, the target radius is estimated by extracting the location of the apex of the hyperbola and the soil velocity that best fits the data for a point reflector, followed by finding an optimal soil velocity and target radius, using a nonlinear least-squares fitting procedure. This method is handicapped because the variability in the GPR source wavelet (SW) and local complexities in the soil's permittivity and conductivity structure affect the shape of the returned pulse. This in turn affects how the arrival times of diffracted returns are defined. These perturbations to the arrival time can be on the order of the changes expected with the changing cylinder diameter, making it difficult to distinguish the pipe diameter from the wavelet from the permittivity and conductivity complexities.

Other researchers have also investigated the complexities associated with pipe returns. For example, GPR can be applied for leakage detection from the pipes. Crocco et al. (2009) and Demirci et al. (2012) successfully detect water leakage from plastic pipes using GPR by applying microwave tomographic inversion and a back-projection algorithm, respectively. Ni et al. (2010) use a discrete wavelet transform (DWT) to filter and enhance GPR raw data to improve image quality. They find DWT to be advantageous in the detection of deeper pipes if shallower anomalies obscure the reflected signal from deeper targets, but they do not attempt to extract pipe diameter information. Jamming et al. (2014) present an approach for hyperbola recognition and pipe localization in radargrams, which use an iterative-directed shape-based clustering algorithm to recognize hyperbolas and identify groups of hyperbola reflections that belong to a single buried pipe.

Full-waveform inversion (FWI) can potentially provide high-resolution subsurface images because it uses information from the entire waveform. If achieved, FWI can improve on estimates of pipe diameter made from ray-based arrival time analysis, as in Ristic et al. (2009). Virieux and Operto (2009) provide an overview of the development of this technique for seismic data. FWI on GPR data is most commonly applied on crosshole GPR data to study aquifer material (e.g., Ernst et al., 2007; Klotzsche et al., 2010, 2012, 2013, 2014; Meles et al., 2010, 2012; Yang et al., 2013; Gueting et al.,

38

FWI of common-offset GPR using PEST

H29

2015, 2017; van der Kruk et al., 2015; Keskinen et al., 2017) or on frequency-domain air-launched GPR signals for a limited number of model parameters (Lambot et al., 2004; Tran et al., 2014; André et al., 2015; De Coster et al., 2016; Mahmoudzadeh Ardakani et al., 2016). Lavoué et al. (2014) use frequency domain FWI to image 2D subsurface electrical structures on multioffset GPR data. Kalogeropoulos et al. (2011) use FWI on surface GPR data to monitor chloride and moisture content in media. Busch et al. (2012, 2014) apply FWI on surface GPR data to characterize soil structure and to obtain conductivity and permittivity estimations. Busch et al. (2013) further apply FWI on surface GPR data to estimate hydraulic properties of a layered subsurface.

The method described in this paper builds on the previous work by applying the FWI method to the problem of pipe diameter and infilling material estimation. Multiple variables that influence the GPR diffraction hyperbola can be incorporated into the inversion process. Here, the method is assessed when the SW, average soil permittivity, pipe depth and horizontal position, pipe inner diameter, and pipe-filling material are optimized in the inversion. The method in its current state is only effective with diffraction(s) from one pipe, and it does not yet share the advantages of Ni et al. (2010) and Janning et al. (2014) methods that can distinguish multiple pipes.

We note that we are considering only an exceptionally simple case that provides a starting point for more thorough investigations. We only consider transects run perpendicular to a horizontal pipe with antennas in broadside mode (maintained parallel to the pipe and perpendicular to the transect). Polarization effects on surveys oblique to pipes will be quite different (e.g., Vilela and Romo, 2013).

## METHOD

The method presented here for determining a best-fitting pipe diameter and other parameters involves five main steps (Figure 2): (1) basic processing of the raw GPR data, (2) defining the starting model using the ray-based diffraction hyperbola analysis, (3) transformation of 3D data to 2D, (4) finding a good effective SW, and (5) an iterative inversion process that runs to a threshold criteria to find the pipe diameter that best fits the data. The starting model created in step 2 is defined using ray-based analysis of the data, whereby the average soil velocity and therefore electrical permittivity, soil electrical conductivity, pipe lateral location, and depth are estimated. In this workflow, the user must assume a permittivity of the pipe-filling material (e.g., a value expected for air, water, or sewage) and the pipe material (e.g., PVC) and pipe wall thickness. With these assumptions, a value for the electrical conductivity within the pipe and a starting estimate of the pipe diameter are also derived.

The inversion procedure in step 5 requires forward modeling of GPR wave propagation. Because forward modeling of 3D waves is computationally expensive, 2D forward modeling is used. This requires a 3D to 2D transformation on the data, accounting for the expected differences between the real source and a line source, and correcting the geometric spreading factor.

We note that the goals of the method described here are to improve the initial estimates of pipe diameter and pipe-filling material and soil permittivity. Estimating the conductivity of the pipe-filling material (or soil) would require further computational expense, in the form of updating the SW estimation (step 4) at each iteration of the inversion process in step 5. Here, the conductivity values are estimated from ray theory and then fixed during the inversion process. To eliminate errors caused by inaccurate conductivity values,

![img-17.jpeg](img-17.jpeg)

Figure 2. The inversion process flowchart. The critical steps prior to the PEST full waveform inversion (gray box) are (1) simple GPR data processing, (2) ray-based analysis to estimate the initial model, (3) 3D to 2D transformation, (4) source-wavelet correction(s); and (5) creation of a reasonably good initial model using the ray-based results and the estimated SW, starting the inversion.

Downloaded 01/15/19 to 131.247.224.4. Redistribution subject to SEG license or copyright; see Terms of Use at http://library.seg.org/

39

Downloaded 01/15/19 to 131.247.224.4. Redistribution subject to SEG license or copyright; see Terms of Use at http://library.seg.org/

H30

Jazayeri et al.

traces are individually normalized before misfit calculations in the inversion process. The pipe wall thickness estimate is also fixed in the inversion process, as typical values of a few mm put it below the GPR signal resolution.

1) Basic processing of raw GPR data: Some initial processing of the GPR data is essential for the inversion process to work (see Figure 2, step 1). A standard dewow filter and time-zero corrections (e.g., Cassidy, 2009) are followed by a high-cut frequency filter (2 GHz for examples in this paper). High-frequency noise removal is important because the forward models generated during the inversion process (described below, Figure 3) simulate "clean" data without such noise. In practice, additional data smoothing in the x and y (space and time) dimensions is found to help the inversion efficiency. The optimal window size for the xy filter appears to vary with individual data sets, and selection depends on the interpreter's experience. The combined effects of these processing steps on the signal amplitude, for all data presented here, are on average less than 1% through the traces. On the two noisiest traces, the average amplitude change is 4%. The data are not gained.

2) Defining the starting model using ray-based diffraction hyperbola analysis: The FWI and the effective SW estimation are impossible without a good initial model. We use ray-based analysis to estimate the initial parameters (Figure 2, step 2). First, traveltimes of the peak amplitudes of the diffraction hyperbola (from the top of pipe, if two are observed) are identified. Second, Radzevicius (2015)'s least-squares method is then used to estimate the average soil velocity, pipe depth, and lateral position that best fits the peak amplitude times, assuming the pipe to be a point diffractor and zero offset between antennas. If two distinct hyperbolas from the pipe top and pipe bottom are recognized, then the diameter is estimated from the rms average of the traveltime differences Δt for the peak amplitudes of returns from the pipe top and pipe bottom on traces in the diffraction hyperbola, where diameter = (v_filling/2)Δt_m, and v_filling is the velocity assumed for the pipe-filling material. The interpreter can assume the pipe to be water or air filled to estimate v_filling. If the resulting diameter appears unreasonable, an alternative filling medium can be considered (for most engineering utility scenarios, if distinct reflections from the top and bottom of the pipe are recorded with 800 MHz antennas, it is likely that the pipes are water filled). For instance, a 10 cm diameter water-filled pipe generates almost the same time interval between the hyperbolas off the pipe top and pipe bottom as a 90 cm diameter air-filled pipe. If no hyperbola from the pipe bottom can be recognized, interpreters must rely on their best guesses for the initial diameter based on knowledge of the site.

An average soil conductivity is estimated by a least-squares approach described in Appendix A. The maximum absolute amplitudes on the recorded hyperbola from the top of the pipe are used to find the best conductivity model that fits the data.

With isolated, clear diffraction hyperbolas and some knowledge about the expected target properties, it is possible to make sufficiently good starting models that the inversion can proceed successfully. Meles et al. (2012) indicate that successful inversion requires initial models return synthetic data pulses that are offset less than one-half wavelength from the measured traces. Ray-based analysis is critical for satisfying this criterion.

3) 3D to 2D transformation: To simulate 2D line-source generated waveforms that would be equivalent to those observed in the 3D data, a transformation is applied to the data (see Figure 2, step 3). This transformation is a prerequisite for the application of the 2D forward modeling in the inversion process, as noted for example by Ernst et al. (2007), Klotzsche et al. (2010, 2013), and Meles et al. (2012). We follow the method developed by Forbriger et al. (2014) to transform 3D shallow seismic data to 2D. Their method convolves data in the time domain with a √t⁻¹, where t is the traveltime, followed by an amplitude correction. The convolution provides a π/4 phase shift and corrects the geometric spreading difference between two and three dimensions.

4) SW estimation: The effective SW needs to be estimated once data are transformed to two dimensions (Figure 2, step 4). The shape and the amplitude of the SW depend on the instrument used, ground coupling, and the surficial soil permittivity and conductivity structure. As such, the user has little control over the wavelet form while collecting data. However, a good effective SW estimation is critical for the success of the inversion (inversion runs without the wavelet estimation step yield markedly poorer results or fail to converge). Ernst et al. (2007) and Klotzsche et al. (2010) propose a deconvolution approach to correct an initial estimate of an effective SW, for crosshole GPR data. An improved SW is obtained by deconvolving radar data with the impulse response of the earth in the area of investigation (Ernst et al., 2007; Klotzsche et al., 2010; Kalogeropoulos et al., 2011). We adapt this deconvolution approach for the use of common-offset data. The deconvolution is applied with the ray-based model and the observed data to correct the SW, and the process is then repeated a second time to yield a second corrected SW. Details of the procedure are described in Klotzsche et al. (2010).

The method requires an initial guess of the waveform. For the instrument and terrain conditions in the case studies presented here (a Mala Geosciences ProEx 800 MHz shielded antenna on partially saturated clean sands), we find that the fourth derivative of a Gaussian wavelet (second derivative of a Ricker wavelet) is effective. The efficiency of the FWI method is found to be highly dependent on the availability of an accurately corrected SW. The recovered SW is in turn dependent on the starting model (impulse response) of soil and pipe properties, and on the number of data traces and time window within traces used in the wavelet correction. Errors in the starting model propagate into the effective SW, and errors in the amplitude of the SW in particular can trade-off with errors in the conductivity model. Because the conductivity estimations in the FWI approach are highly dependent on the SW, a successful FWI analysis that aims to estimate the conductivity values requires the SW to be updated at each iteration of the FWI process. Busch et al. (2012, 2014) extend the deconvolution approach for surface WARR GPR data and combine it with a frequency-domain FWI for a horizontally layered media that better describes the sensitivity of the SW estimation to subsurface parameters. Thereby, Busch et al. (2012, 2014) combine the FWI and an effective SW update in terms of medium parameters and wavelet phase and amplitude. In contrast to common-offset data, WARR data provide more information about amplitude decay with changing offset and allow a better conductivity estimation.

40

FWI of common-offset GPR using PEST

H31

Adapting this approach to common-offset data is beyond the scope of this paper, and we thus expect errors associated with the SW amplitude estimation and the conductivities in the inversion process. We recognize this limitation in the method by eliminating soil conductivity as an inversion parameter (it remains fixed at the initial value), and reducing the impact of the soil conductivity on the inversion process by normalizing traces individually when calculating the cost (objective) functions at each inversion step.

5) FWI: As the fifth and final step, the GPR returns from the pipe are inverted to improve on the initial model of soil and pipe. In this paper, the inversion procedure is designed using two software packages that are freely available. The first, the PEST (model-independent parameter estimation and uncertainty analysis) package (Doherty, 2017), is used for inverting the data to find the best model parameters (Doherty, 2015). The second, gprMax 2D (Giannopoulos, 2005; Warren et al., 2016), is used to compute the GPR readings expected at each step as the model parameters are updated (Jazayeri and Kruse, 2016). Because small cell sizes are necessary for the inversion to accurately recover the pipe dimensions, a 3D forward model, although clearly preferable, was too computationally expensive for this study.

PEST, prepared by John Doherty and released in 1994, is a package developed for groundwater and surface-water studies (Doherty, 2017), but it can be linked to any forward-modeling problem. PEST uses the Gauss-Marquardt-Levenberg nonlinear estimation method (Doherty, 2010, 2015).

The relationship between the model parameters (e.g., pipe radius and soil permittivity) and the model-generated observation data (GPR returns) is represented by the model function **M** that maps the $n$-dimensional parameter space into $m$-dimensional space, where $m$ is the number of observational data points **d**. The term **M** should be differentiable with respect to all model parameters (Doherty, 2010). A set of parameters, $\mathbf{p}_0$ thus generate the model observations $\mathbf{d}_0$ (equation 1). Although generating another set of data $d$ from a **p** vector slightly different from $\mathbf{p}_0$, the Taylor expansion provides equation 2 as an approximation, where **J** is the **M**s Jacobian matrix:

$$\mathbf{d}_0 = \mathbf{M}(\mathbf{p}_0), \quad (1)$$

$$\mathbf{d} = \mathbf{d}_0 + \mathbf{J}(\mathbf{p} - \mathbf{p}_0). \quad (2)$$

The best fitting model is the one that produces the minimum of the cost function $\varphi$ (equation 3), where **d** is the real data collected and **Q** is an $m \times m$ diagonal weights matrix:

$$\varphi = (\mathbf{d} - \mathbf{d}_0 - \mathbf{J}(\mathbf{p} - \mathbf{p}_0))^T \mathbf{Q} (\mathbf{d} - \mathbf{d}_0 - \mathbf{J}(\mathbf{p} - \mathbf{p}_0)). \quad (3)$$

If **u** is denoted as the parameter upgrade vector, $\mathbf{u} = \mathbf{p} - \mathbf{p}_0$, it can be written as

$$\mathbf{u} = (\mathbf{J}^T \mathbf{Q} \mathbf{J})^{-1} \mathbf{J}^T \mathbf{Q} \mathbf{R}, \quad (4)$$

where **R** is the nonnormalized vector of residuals for the parameter set, $\mathbf{R} = \mathbf{d} - \mathbf{d}_0$.

This approach needs to be given a set of starting model parameters ($\mathbf{p}_0$), which will be updated to find the global minimum of the cost function ($\varphi$) in the time domain. The optimization process can benefit from adjusting equation 4 by adding a Marquardt parameter ($\alpha$). The new form of the upgrade vector can be rewritten as equation 5, where **I** is the $n \times n$ identity matrix:

$$\mathbf{u} = (\mathbf{J}^T \mathbf{Q} \mathbf{J} + \alpha \mathbf{I})^{-1} \mathbf{J}^T \mathbf{Q} \mathbf{R}. \quad (5)$$

For problems with parameters with greatly different magnitudes, terms in the Jacobian matrix can be vastly different in magnitude. The round-off errors associated with this issue can be eliminated through the use of an $n \times n$ diagonal scaling matrix **S**. The $i$th element of the scaling matrix is defined as

$$\mathbf{S}_{ii} = (\mathbf{J}^T \mathbf{Q} \mathbf{J})_{ii}^{-1/2}. \quad (6)$$

Finally, equation 6 can be rewritten as

$$\mathbf{S}^{-1} \mathbf{u} = ((\mathbf{J} \mathbf{S})^T \mathbf{Q} \mathbf{J} \mathbf{S} + \alpha \mathbf{S}^T \mathbf{S})^{-1} (\mathbf{J} \mathbf{S})^T \mathbf{Q} \mathbf{R}. \quad (7)$$

The largest element of $\alpha \mathbf{S}^T \mathbf{S}$ is often denoted as the Marquardt Lambda ($\lambda$), and it can be specified to help control the parameter upgrade vector **u** and optimize the upgrade process.

To start the inversion, PEST makes an initial call to gprMax to compute the initial GPR data set expected from the starting model $\mathbf{p}_0$ with the corrected SW (Figure 2, step 5). The Marquardt $\lambda$ value is set to 20, and PEST computes the initial cost function $\varphi$. Then, a lower $\lambda$ value is set and the cost function is recalculated. This process is repeated until a minimum cost function is found. If a lower cost function is not observed by $\lambda$ reduction, a higher lambda will be tested. Parameters **p** are then updated using the $\lambda$ value that yields the minimum cost function, and the next iterations starts, with gprMax called again from PEST to compute the new corresponding GPR readings $\mathbf{d}_0$. PEST then computes the residuals **R** between the updated model and real data. The next iteration starts with the best Marquardt $\lambda$ from the previous iteration. If, in the next iteration, a lower cost function is not achieved, a new vector of updated parameters will nevertheless be tested. This process continues until the step at which a lower cost function is not found after $N$ iterations. The $N$ in this process was set to six. The user can also specify upper and lower bounds for the parameters **p**. In this study, the relative permittivity is restricted between 1 and 90, and pipe diameters are bounded between 0 and 20 cm.

A concern in any inversion process is that the algorithm leads to a local minimum rather than the global minimum solution. For the real data, we cannot unambiguously identify the global minimum. To avoid local minima trapping, we follow, to the extent possible, the recommendation described above that the initial synthetic data set is offset less than a half wavelength from the measured data (e.g., Meles et al., 2012; Klotzsche et al., 2014). Then to qualitatively assess the likelihood that our results presented represent a local minimum, we run the inversion process with multiple sets of initial model parameters $\mathbf{p}_0$, and compute the cost function $\varphi$ at the conclusion of each run. The selection of initial models is described below. Runs that terminate with variable best-fit parameters **p** and differing cost functions $\varphi$ are suggestive of termination at local minima.

Downloaded 01/15/19 to 131.247.224.4. Redistribution subject to SEG license or copyright; see Terms of Use at http://library.seg.org/

41

Downloaded 01/15/19 to 131.247.224.4. Redistribution subject to SEG license or copyright; see Terms of Use at http://library.seg.org/

H32

Jazayeri et al.

## RESULTS AND DISCUSSION

### Synthetic model

This inversion method is evaluated by creating a 3D synthetic model of a PVC pipe filled with fresh water and buried 35 cm in homogeneous semi-dry sand (Figure 3a; Table 1). The model is used to generate synthetic 3D GPR readings. The GPR data set (Figure 3c) is created assuming a common-offset survey with an 800 MHz antenna set with 14 cm spacing between transmitter and receiver. Every 5 cm, a pulse is transmitted and received, with 12 traces in total. The synthetic waveform is a fourth derivative of the Gaussian waveform, similar to those of some commercial systems (Figure 3b). The cell size in the gprMax 3D forward model is 1 × 1 × 1 mm.

The ray-based analysis is applied to the synthetic GPR data (Figure 3c) assuming the pipe to be water filled. The ray-based analysis estimates the diameter with 15% error (Table 1). In contrast, an air-filling assumption results in an approximately 10%–30% error in diameter estimation. Lateral position and soil average permittivity and conductivity are well-estimated using the ray-based analysis (Table 1). The 3D to 2D transformation is applied, and the transformed data are then treated as the “observed data” in the inversion process.

A uniform soil permittivity, a uniform effective soil conductivity, a uniform effective in-filling conductivity, and the pipe lateral position and depth are set following the methods described above. Therefore, the unknown parameters in the inversion process are defined to be uniform soil and pipe-filling permittivities, pipe depth,

![img-18.jpeg](img-18.jpeg)

![img-19.jpeg](img-19.jpeg)

![img-20.jpeg](img-20.jpeg)

Figure 3. (a) Model geometry for a PVC pipe containing fresh water embedded in semi-dry sand. The pipe inner and outer diameter are 10 and 10.6 cm, respectively. The colored cross sections show the part of the model over which the antenna has moved. (b) The 800 MHz fourth derivative Gaussian wavelet assumed for the GPR signal. (c) The GPR profile produced by synthesizing readings every 5 cm across the model. The circles show the arrival-time picks used in the ray-based inversion. The white lines show the arrival-time curves predicted form the ray-based inversion parameters.

Table 1. The correct, initial guess, and inverted parameter values for the synthetic model. Pipe diameter estimate is significantly improved by the inversion process. Soil conductivity and pipefilling conductivity are fixed to the ray-based results during FWI.

|  Case | Parameter | Correct value | Ray-based estimation | FWI result with the ray-based results as the starting model | Estimation error (%)  |
| --- | --- | --- | --- | --- | --- |
|  Synthetic model of the water-filled pipe | Relative permittivity of the soil | 5 | 5.1 | 5.09 | 1.8  |
|   |  Electrical conductivity of the soil (mS/m) (fixed) | 2 | 2.3 | — | —  |
|   |  Relative permittivity of pipe-filling material (water) | 80 | 80 | 78.5 | 2.25  |
|   |  Electrical conductivity of pipe-filling material (water) (mS/m) | 1 | 2.5 | — | —  |
|   |  X (center of the pipe) (cm) | 50 | 49.95 | 49.95 | 0.1  |
|   |  Depth of the top of the pipe (cm) | 35 | 33.65 | 35.08 | 0.23  |
|   |  Pipe wall thickness (mm) (fixed) | 3 | — | — | —  |
|   |  Pipe inner diameter (cm) | 10 | 11.5 | 10.12 | 1.2  |
|   |  Pipe relative permittivity (PVC) (fixed) | 3 | — | — | —  |
|   |  Pipe electrical conductivity (mS/m) (PVC) (fixed) | 10 | — | — | —  |

42

Downloaded 01/15/19 to 131.247.224.4. Redistribution subject to SEG license or copyright; see Terms of Use at http://library.seg.org/

FWI of common-offset GPR using PEST

H33

and inner diameter. In this scenario, the pipe is assumed to be known to be constructed with PVC of typical wall thickness (3 mm), and the pipe permittivity and conductivity are set to values appropriate for PVC (see Table 1). To mimic the inversion process in which the SW is not known, an initial guess of a Ricker wavelet is applied as the SW (Figure 4) and a synthetic 2D model is generated using the ray-based estimated model and the Ricker wavelet. For the wavelet estimation, the direct air and ground wave are excluded. With the deconvolution method, the model SW is corrected (see Figure 4, the first corrected SW). The synthetic data are again calculated with the first corrected wavelet. At the last step of the SW correction, the wavelet is deconvolved again using the second synthetic data and the observed data (e.g., Klotzsche et al., 2010). In this process, the symmetric Ricker shape wavelet is altered to a nonsymmetric form closer to the real wavelet.

Because the ray-based results are good approximations of the "true" model parameters, Figure 5 illustrates that the effective SW correction alone produces a good fit between the hyperbola from the top of the pipe of the observed and modeled GPR traces. The inversion procedure for the soil and pipe properties and dimensions then brings improved alignment of the bottom of pipe diffraction returns (Figure 5) and reduces errors (Table 1). For instance, the ray theory estimated the pipe inner diameter to be 11.5 cm, whereas the FWI process improved this estimate model parameter to 10.12 cm (1.2% error). The estimated depth also shows an improvement after the FWI process.

To study the effect of the initial value selection on the FWI results, the FWI process was run 22 times for this case, in each case varying the permittivity of the pipe filling material and pipe diameter as initial model parameters. In each case, the effective SW is computed with the model medium properties. The initial values were specified in 15 cases by randomly varying values in a Gaussian distribution around the best fit inversion results of Table 1 with a standard deviation of 50% of the ray-based result and then in seven cases by randomly assigning more extreme outliers to selected parameters (a comprehensive examination of all five inversion parameters was computationally not feasible and is outside the scope of this paper). Figure 6 summarizes the changes in cost function from the initial value to the final inversion value for all runs, for the pipe inner diameter (Figure 6a) and the pipe-filling relative permittivity (Figure 6b). Note that only the first and last steps of the inversion process are shown as the tail and tip of the arrows; the successive changes in parameters through multiple iterations are not shown.

![img-21.jpeg](img-21.jpeg)

Figure 4. The real SW used to create 3D model (black), initial SW used in the synthetic model (gray); the first (light dashed gray), and second corrected effective SW pulse (dark dashed gray). The amplitudes are normalized.

![img-22.jpeg](img-22.jpeg)

Figure 5. Comparison of observed true synthetic GPR traces (black), the GPR traces predicted from the initial model and corrected SW (dashed), and the GPR traces predicted from the final inverted model (gray). Traces are normalized individually.

![img-23.jpeg](img-23.jpeg)

![img-24.jpeg](img-24.jpeg)

Figure 6. Cost function values associated with the initial guess (tail of arrow) and the inversion output (tip of the arrow) for 22 runs. Note that in each run, the initial values of the other variables in the inversion also vary. (a) The cost function changes with the inner pipe diameter. The dashed gray line marks the true (simulated) 10 cm pipe inner diameter. (b) The cost function changes with the infilling relative permittivity. The dashed gray line marks the true pipe filling relative permittivity of 80. With starting values of pipe diameter within a factor of two of the correct value, the inversion improves the estimate of the pipe diameter. The bold gray arrows show the inversion run with starting parameters from the ray-based analysis, listed in Table 1.

43

Downloaded 01/15/19 to 131.247.224.4. Redistribution subject to SEG license or copyright; see Terms of Use at http://library.seg.org/

H34

Jazayeri et al.

Figure 6a shows that the diameter estimates are improved for all starting values within a factor of two of the true value. Many initial models converge at a 1–2 mm overestimate of the pipe diameter, but the ray-based analysis starting model yields a final diameter only 0.12 mm greater than the true value, a difference less than the 1 mm cell size in the forward models. From Figure 6b, it can be concluded that inversions starting with significantly lower initial assigned in-filling relative permittivity values (<50) and initial pipe diameters that differed from the true diameter by more than 50% failed to reach within 10% of the true value. Lower initial pipe-filling relative permittivities (≤50) also significantly increased the time for convergence. We defer more detailed discussion of starting models to the more realistic field case studies described below.

The synthetic model results above show that this FWI method is effective for improving estimates of pipe dimensions in highly idealized conditions. The effects of realistic soil heterogeneities are missing. In the following section, results of the method in real-world but well-controlled scenarios are presented.

### Case studies of PVC pipe in well-sorted sands

The inversion method was tested with GPR profiles run across a buried PVC pipe of known position and dimensions. The field tests were run in the Geopark of the University of South Florida in Tampa, Florida, USA (Vacher, 2017). There, the uppermost 1–2 m consist of well-sorted loose sand over progressively more silty and clay-rich layers (e.g., Bumpus and Kruse, 2014).

In mid-May 2016, several reconnaissance GPR profiles were collected to find an area with few tree roots and low degree of soil disturbance. Once a preferred location was found, a trench was excavated to bury a PVC pipe (Figure 7). The selected PVC pipe has an outer diameter of 8.2 cm and a wall thickness of 3 mm, and it was placed so that the top of the pipe lay 35 cm below the ground surface. One end of the horizontal PVC pipe was closed with a PVC lid, and the other end was connected to another vertical pipe through a 90° PVC elbow. The “L”-shaped pipe was designed to enable researchers to fill the pipe with liquids (Figures 7a, 7b, and 8). Once the burial depth of the top of the pipe was confirmed to be the same at the elbow location and the lid, the trench was refilled. Before refilling with the native sand, the sand was sieved to remove small

tree roots. Attempts were made to make sure that the soil was as uniformly distributed as possible above the pipe to increase the chances of receiving clear diffracted hyperbolas.

Two subsequent GPR surveys were performed. The first was run on the empty, air-filled pipe on the same day the pipe was buried. The second was run almost six weeks later, in late July 2016. Although the soil was quite dry on the day of the July survey, there had been heavy rains in the six weeks since the pipe was installed, so it is assumed that the soil over the trench had settled and compacted to a degree more similar to undisturbed neighboring soil. For this second survey, the pipe was completely filled with fresh water. In this paper, we discuss the July water-filled pipe survey first because the data interpretation is more straightforward.

### Case study 1: Water-filled pipe

After the pipe was filled with water, as illustrated in Figure 8, a grid of 15 parallel profiles was acquired, with 5 cm spacing between profiles (a subset is shown in Figure 9). All profiles were run in a north–south direction, perpendicular to the pipe that was laid in an east–west direction. A Mala-ProEx system with 800 MHz shielded antennas was used. The spacing between traces along each profile was set to 8.5 mm and was controlled by an odometer wheel that

![img-25.jpeg](img-25.jpeg)

Figure 8. Schematic sketch of the pipe buried in sand. The moderate gray color shows the water level in the pipe.

a)

![img-26.jpeg](img-26.jpeg)

b)

![img-27.jpeg](img-27.jpeg)

c)

![img-28.jpeg](img-28.jpeg)

Figure 7. (a) The L-shaped PVC pipe in the hole in sand. (b) The elbow part of the pipe showing the burial depth of 35 cm for the top of the horizontal part. (c) After filling the hole, the vertical part is visible that enables filling the pipe. The horizontal part of the pipe is aligned between the pink flags.

44

FWI of common-offset GPR using PEST

H35

Downloaded 01/15/19 to 131.247.224.4. Redistribution subject to SEG license or copyright; see Terms of Use at http://library.seg.org/

![img-29.jpeg](img-29.jpeg)

Figure 9. Profiles of the water-filled pipe buried in sand. The left-most left plot is closest to the pipe elbow; the right-most right plot is closest to the lid. Diffracted hyperbolas are recorded from the top and bottom of the pipe, at all locations. The arrow shows the profile used for FWI.

Table 2. Sample inversion results for air- and water-filled pipes. Ray-based analysis results are used as the initial values in the FWI. Soil conductivity and pipe-filling conductivity are fixed to the ray-based results during FWI.

|  Case | Parameter | Correct value | Ray-based estimation | FWI result with the ray-based results as the starting model | Estimation error (%)  |
| --- | --- | --- | --- | --- | --- |
|  Water-filled pipe | Relative permittivity of the soil | — | 5.822 | 5.85 | —  |
|   |  Electrical conductivity of the soil (mS/m) (fixed) | — | 3.2 | — | —  |
|   |  X (center of the pipe) (m) | 1.09 | 1.088 | 1.09 | 0  |
|   |  Depth of the top of the pipe (cm) | 35 | 33.55 | 34.84 | 0.46  |
|   |  Pipe wall thickness (mm) (Fixed) | 3 | — | — | —  |
|   |  Pipe inner diameter (cm) | 7.6 | 6.8 | 7.59 | 0.13  |
|   |  Relative permittivity of the pipe-filling material (water) | — | 80 | 74 | —  |
|   |  Effective electrical conductivity of pipe-filling material (water) (mS/m) (fixed) | — | 0.02 | — | —  |
|   |  Pipe relative permittivity (PVC) (fixed) | — | 3 | — | —  |
|   |  Pipe electrical conductivity (mS/m) (PVC) (fixed) | — | 1 | — | —  |
|  Air-filled pipe | Relative permittivity of soil | — | 4.52 | 4.6 | —  |
|   |  Electrical conductivity of soil (mS/m) (fixed) | — | 4.23 | — | —  |
|   |  X (center of the pipe) | 1.09 | 1.095 | 1.092 | 0.18  |
|   |  Depth of the top of the pipe (cm) | 35 | 34.7 | 34.8 | 0.57  |
|   |  Pipe wall thickness (mm) (fixed) | 3 | — | — | —  |
|   |  Pipe inner diameter (cm) | 7.6 | Between 3 and 30 | 8.18 (starting value = 12) | 7.6  |
|   |  Relative permittivity of the pipe-filling material (air) | 1 | 1 | 1 | 0  |
|   |  Effective electrical conductivity of the pipe-filling material (air) (mS/m) (fixed) | 0 | — | — | —  |
|   |  Pipe relative permittivity (PVC) (fixed) | — | 3 | — | —  |
|   |  Pipe electrical conductivity (mS/m) (PVC) (fixed) | — | 1 | — | —  |

45

Downloaded 01/15/19 to 131.247.224.4. Redistribution subject to SEG license or copyright; see Terms of Use at http://library.seg.org/

H36

Jazayeri et al.

![img-30.jpeg](img-30.jpeg)

Figure 10. Profile over the water-filled pipe, direct wave excluded. The first strong return between 7 and 10 ns is the reflection from the top of the pipe; the second return between 12 and 15 ns is from the bottom of the pipe. The latest weak return between 17 and 19 ns is a multiple. The circles show the arrival time picks used in the ray-based inversion. The white lines show the arrival time curves predicted from the ray-based inversion parameters.

![img-31.jpeg](img-31.jpeg)

Figure 11. The initial and corrected effective SWs. The second corrected SW has an overall shape similar to the fourth Gaussian derivative, but it is not symmetric.

![img-32.jpeg](img-32.jpeg)

![img-33.jpeg](img-33.jpeg)

![img-34.jpeg](img-34.jpeg)

Figure 12. (a) Observed data (black) and initial synthetic data (gray) comparison. (b) The same plot after SW correction; the first reflected signals fit better than the previous model. (c) The same plot after the FWI process. A generally good fit between the observed and modeled data is observed. Traces are normalized individually.

was calibrated on site. The 80 traces centered on the hyperbola were selected to use in the inversion process. The water-filled pipe produces sharp hyperbolas in all the GPR profiles.

For a water-filled pipe, distinct reflections from the top and bottom of pipe are anticipated if the pipe diameter is greater than approximately half the radar wavelength. For this scenario, a wavelength of approximately 4 cm is expected; the pipe diameter of 7.6 cm is almost twice this value. Clear hyperbolas are indeed observed from top and bottom of the pipe in all 15 profiles. The central profile marked by the arrow in Figure 9 has one of the cleanest pipe returns recorded, and it was selected for the FWI.

From the selected profile, the closest 80 traces to the pipe were extracted for the FWI (Figure 9). The optimal data range and trace spacing for inversion is site dependent and outside the scope of this paper. The ray-based analysis was performed on the selected data set (Table 2) followed by the 3D to 2D transformation. Figure 10 presents the 80 traces after basic filtering, including a 4 ns dewow filter, a time-zero correction, a high-cut 1600 MHz frequency filter, an average xy filter with a 3 x 3 window size (this subjectively chosen window size smooths the data slightly, does not generally affect amplitudes on average by more than 1%, and improves the

performance of the inversion process), and a 3D to 2D transformation.

We found that the inversion procedure yields better results if the direct wave arrivals are excluded when computing the residuals vector R (equation 4). The direct arrivals are excluded as shown in Figure 10.

The ray-based analysis was used to create an initial model to start the inversion. Because two diffraction hyperbolas are observed, we used the liquid-filled assumption for the pipe. The ray theory starting estimates are listed in Table 2. Conductivity values were fixed during FWI, and traces were individually normalized in the cost function calculations. Ray theory estimates the diameter with approximately 10% error if a good infilling permittivity is chosen (Table 2). The permittivity, conductivity, and the wall thickness of the pipe itself (PVC) were assumed to be known and fixed to the actual values.

After setting the initial model parameters as described above, the initial synthetic GPR data were computed assuming a cell size of 1 x 1 mm in the gprMax 2D forward models and a fourth derivative of the Gaussian wavelet as the SW. Using the deconvolution method, the SW was corrected twice (Figure 11). This wavelet is similar to that obtained for other data sets using a similar instrument from the same manufacturer (Klotzsche et al., 2013).

Neither the shape of the first reflected signals from the top of the pipe nor the second reflected signals from the bottom of the pipe are modeled acceptably with the initial guess parameters because the shape of the SW has not been corrected (see Figure 12a). After the SW correction (Figure 12b), the reflections from the bottom of the pipe are still poorly fit because the initial model

46

FWI of common-offset GPR using PEST

H37

still misestimates the pipe diameter. After 17 iterations, the model and observed data fit is far superior (Figure 12c).

The inversion process maintains values for pipe-filling material that are close to the expected values for fresh water (see Table 2). The depth and pipe diameter are recovered to within 1% of their known values.

To investigate the sensitivity of the inversion algorithm to the initial values, the FWI process was run 20 times for the water-filled pipe case, similar to the process described above for the synthetic model. Figure 13 summarizes the changes in cost function from the initial value to the final inversion value for the 20 runs, for the pipe inner diameter (Figure 13a) and the pipe-filling relative permittivity (Figure 13b).

Figure 13 illustrates that models with initial pipe diameters between 5 and 10 cm converge to within 1 cm of the 7.6 cm correct value. Models with more widely different starting values end up at local minima of the cost function.

Case study 2: Air-filled pipe

On the same day that the pipe was buried, GPR profiles were collected using the 800 MHz antenna with the same settings as the previous section, but the pipe was empty. An air-filled pipe should produce weaker reflections and a shorter time gap between the upper and lower returns. Presumably, also the sand covering the pipe was less uniformly compacted and drier on the day of burial than six weeks later, and thus we expect more "background noise" and a longer incoming wavelength in this case. These factors combine to make the FWI in this case more challenging, designed to illustrate the efficiency of this technique in a more complex case.

A GPR profile (Figure 14) was selected for the inversion procedure at the same location of the inverted profile in case study 1. Comparing Figures 10 and 14 illustrates the expected effects of water versus air and soil compaction. The air-filled pipe produces less pronounced and overlapping diffraction hyperbolas. There is also some scattered energy recorded before the hyperbolas, as anticipated due to heterogeneity in the sand. Using the ray-based scheme, the average sand relative permittivity was estimated to be 4.52, i.e., an average velocity of almost 0.14 m/ns, indicating that the sand was much dryer at the time of this survey than at the time of the later survey over the water-filled pipe. The depth and the lateral location of the pipe are well-estimated from the ray-based analysis (Table 2). Because there is just one hyperbola recorded from the pipe, the diameter and pipe-filling conductivity estimation are challenging. Traditional hyperbola fitting anticipates the pipes within diameter of 3–30 cm to be a fit to these data. Because the starting model parameters should be provided for FWI, the initial diameter of the pipe is set to 12 cm for the sample run. We can guess that the pipe is filled with air, and the appropriate permittivity and conductivities are assigned.

The 3D to 2D transformation, effective SW estimation (Figure 15), and inversion procedure and assumptions are identical to those described for the water-filled pipe. Similar to two previous cases, the unknowns assigned to the inversion procedure are the

pipe position, pipe diameter, and soil and pipe-filling permittivities. Initial parameter values for a sample run are listed in Table 2, and the inversion results are presented in Figure 16.

The final model after FWI is an improved but clearly imperfect fit to the real data, with the inverted parameter values listed in Table 2. Misfits are presumably caused in part by unmodeled soil heterogeneities. The pipe dimension is recovered with 8% error.

![img-35.jpeg](img-35.jpeg)

Figure 13. Cost function values associated with the initial guess (tail of arrow) and inversion output (tip of the arrow) for 20 runs. Note that in each run, the initial values of the other variables in the inversion also vary. The thick gray arrows belong to the inversion starting from the ray-based analysis listed in Table 2. (a) The cost function changes with the inner pipe diameter. The dashed gray line marks the known 7.6 cm pipe inner diameter. With starting values of pipe diameter within 50% of the correct value, the inversion improves the estimate of the pipe diameter. (b) The cost function changes with infilling relative permittivity.

![img-36.jpeg](img-36.jpeg)

Figure 14. The GPR profile over the air-filled pipe, direct wave excluded. A primary reflection from the top of the pipe is observed between 6 and 9 ns. Dewow, zero-time correction, band pass, and average xy filters are applied with the same settings as for the water-filled pipe (Figure 10). Data are transformed to two dimensions. The circles show the arrival-time picks used in the ray-based inversion. The white line shows the arrival-time curves predicted from the ray-based inversion parameters.

Downloaded 01/15/19 to 131.247.224.4. Redistribution subject to SEG license or copyright; see Terms of Use at http://library.seg.org/

47

Downloaded 01/15/19 to 131.247.224.4. Redistribution subject to SEG license or copyright; see Terms of Use at http://library.seg.org/

![img-37.jpeg](img-37.jpeg)

Figure 15. The initial and corrected effective SWs for the air-filled pipe.

![img-38.jpeg](img-38.jpeg)

Figure 16. (a) Observed data (black) and initial synthetic data (gray) comparison. (b) The same plot after the SW correction. The reflected signals are a better fit. (c) The same plot after the FWI process.

![img-39.jpeg](img-39.jpeg)

Figure 17. Cost function values associated with the initial guess (tail of the arrow) and the inversion output (tip of arrow) for 20 runs. The thick gray arrows belong to the inversion included in Table 2. (a) The cost function changes with the inner pipe diameter. The dashed gray line marks the known 7.6 cm pipe inner diameter. (b) The cost function changes with the infilling relative permittivity. The dashed gray line marks one as the relative permittivity of air. The inversion process clearly targets local minima if the initial estimate of pipe-filling permittivity is poor.

To investigate the quality of inversion results and assess local minima of the cost function, 20 different models were run with different starting parameters (permittivity of pipe filling and diameter and depth). The SW was estimated for each of the tests separately. Figure 17 summarizes the changes in the cost function from the initial value to the final inversion value for the 20 runs, for the pipe inner diameter (Figure 17a) and the pipe-filling relative permittivity (Figure 17b).

Because of the interference (overlap) in returns between the top of the pipe and the bottom of the pipe in the air-filled case, models that started with initial diameters significantly too large or too small fail to account for the overlap and yield SWs that look dramatically different from those of the better models. This in turn yields unsatisfactory inversion results, underscoring the importance of the initial model. These tests for the air-filled case suggest that the initial models with diameters within 30% of the true diameter are consistently improved in the inversion process.

## DISCUSSION

In these simple field tests, the pipe diameter estimates are significantly improved when the initial guess is within approximately 50% of the true value for the water-filled pipe with distinct returns from the top and bottom, and within approximately 30% of the true value for the air-filled pipe. With the good initial guess, inversion generally proceeds to within 1 cm or less of the true value (in this case to <8% error). This is an improvement over the traditional ray-based scheme, in which the diameter is estimated by trial-and-error fit of the observed hyperbola to the expected arrival times for returns over pipes of varying sizes. As described in the "Introduction" section, the trial-and-error fit for the air-filled pipe case (inner diameter 7.6 cm) yielded reasonable results for diameters ranging from 3 to 30 cm.

This method in its current form is thus suitable for improving good starting estimates of the pipe diameter in simple cases with isolated diffraction hyperbolas. Examination of model runs such as those shown in Tables 1 and 2 and Figure 13 shows that the initially good pipe diameter estimates are also typically slightly improved in the inversion. Conductivity values are fixed to the ray-based analysis results, for the reasons described for previous cases above. To obtain conductivities, the SW could be updated during the FWI following a process similar to Busch et al. (2012, 2014).

The method described here shares the conclusions of Meles et al. (2012) that starting model estimates must be sufficiently good such that

48

FWI of common-offset GPR using PEST

H39

synthetic data pulses are offset less than a half wavelength from the measured traces. For the clean synthetic data, this criteria can be met with a model that assumes a permittivity within 50% of the correct value, and the inversion proceeds toward a permittivity closer to the correct value. For the field data case in which two diffracted hyperbolas are recorded, ray theory can provide good starting model parameters for the FWI process. In the cases of gas-filled pipes (or very narrow liquid-filled cylinders, such as tree roots) that are likely to generate just one diffraction hyperbola, the ray theory fails to provide good starting models; in this case, the best judgment of the user must be used to set the initial model parameters. In this sense, a successful inversion confirms the initial guess, whereas a failure to converge or a small reduction in cost function suggests a poor starting model.

## CONCLUSION

This paper introduces a new method for FWI of common-offset GPR data, particularly targeting the dimensions and infilling material of buried pipes. The method is designed to be used in which clear isolated diffraction hyperbolas indicate the presence of a pipe, but pipe dimensions and filling may be unknown. The method consists of five main steps: GPR data processing, ray-based analysis to set a good initial model, 3D to 2D transformation of data, effective SW estimation, and FWI. The method combines two freely available software packages: PEST for the inversion and gprMax for forward modeling of the GPR data.

This method is applied on a synthetic 3D data set and two 800 MHz GPR profiles collected over a PVC pipe buried in clean sands. In the synthetic and water-filled and air-filled pipe field cases, good initial estimates of the depth and diameter of the pipe from the ray-based analysis are improved after FWI. The tests show that although the initial estimate of pipe diameter is within 30%–50% of the true value, the inversion yields estimates with < 8% error. For the field data, the requirement of a good starting model can, in practice, confirm or deny a starting assumption about the pipe-filling material.

Ray-based analysis is essential to set up the starting model, particularly to estimate the pipe location and average soil permittivity and conductivity. Although ray-based conductivity estimates are possible, improvement in the conductivity would require the SW to be updated after each iteration in the FWI procedure. Iterations on the SW during the FWI process, as in Busch et al. (2012, 2014), are beyond the scope of this study.

The method in its present form is only effective for isolated hyperbolas, and it assumes that GPR surveys are conducted with broadside antenna geometry along profiles perpendicular to horizontal pipes. Furthermore, the soil is assumed to be locally homogeneous. Relaxation of these conditions is the subject of ongoing research.

## ACKNOWLEDGMENTS

The authors are very grateful to J. van der Kruk for very constructive comments, S. Esmaeili and C. Downs for field assistance, D. Voytenko and N. Voss for their introduction to PEST, A. Giannopoulos and C. Warren for their help with gprMax, and A. Green for assistance implementing algorithms on the USF Research Computing cluster. S. Busch, G. Tsofias, B. Schneider, and three

anonymous reviewers gave productive reviews that greatly improved the manuscript.

## APPENDIX A

### RAY BASED ANALYSIS TO ESTIMATE CONDUCTIVITY VALUES

Assuming homogeneous soil, the amplitude of the GPR wave decays due to geometric spreading and soil attenuation. The combination of these two effects can be described with wave amplitude proportional to $e^{-\alpha r}/r$ in 3D media, in which the attenuation term $\alpha$ can be described as

$$\alpha = \frac{\sigma}{2} \sqrt{\frac{\mu}{\varepsilon}}, \tag{A-1}$$

where $\sigma$ is the soil conductivity, $\mu$ is the magnetic permeability, and $\varepsilon$ is the mean absolute electrical permittivity of the soil.

To estimate the conductivity of the soil, the peak amplitudes of the first pipe diffraction hyperbola arrivals are picked and used in a least-squares inversion for the attenuation term, and thereby the soil conductivity. Assuming far-field amplitudes, a uniform antenna radiation pattern, and a uniform reflection coefficient from all parts of the pipe, the amplitude $A$ of the wave having traveled a distance $r$ is expressed as

$$A = A_0 \frac{e^{-\alpha r}}{r}, \tag{A-2}$$

where $A_0$ is a constant. The term $e^{-\alpha r}$ can be replaced the first two terms of its Taylor series expansion, $1 + \alpha r$, leaving $A = A_0(1/(e^{\alpha r})r) \approx A_0(1/(1 + \alpha r)r)$. Rearranging,

$$\left(\frac{1}{A_0}\right)Ar + \left(\frac{\alpha}{A_0}\right)Ar^2 = 1. \tag{A-3}$$

By picking the peak amplitude and computing the travel distance for each trace in the diffraction hyperbola, the Jacobian matrix $\mathbf{J}$ is created. Then, the unity vector $\mathbf{I}$ and parameter vector $\mathbf{p}$ are calculated via

$$\mathbf{J} = \begin{bmatrix} A_1 r_1 & A_1 r_1^2 \\ \vdots & \vdots \\ A_n r_n & A_n r_n^2 \end{bmatrix}; \quad \mathbf{p} = \begin{bmatrix} p_1 \\ p_2 \end{bmatrix}; \quad \mathbf{I} = \begin{bmatrix} 1 \\ \vdots \\ 1 \end{bmatrix}. \tag{A-4}$$

The parameter vector $\mathbf{p}$ can be estimated with the least-squares solution ($\mathbf{p} = (\mathbf{J}^T \mathbf{J})^{-1} \mathbf{J}^T \mathbf{I}$) of these systems using equation A-4. The attenuation term $\alpha$ is estimated as

$$\alpha = p_2/p_1. \tag{A-5}$$

We note that the simplifying assumptions about far-field amplitudes, radiation patterns, and uniform scattering are not strictly valid in real scenarios. However, tests showed that more complicated models did not yield conductivity estimates that consistently produced better inversion results.

Downloaded 01/15/19 to 131.247.224.4. Redistribution subject to SEG license or copyright; see Terms of Use at http://library.seg.org/

49

Downloaded 01/15/19 to 151.247.224.4. Redistribution subject to SEG license or copyright, see Terms of Use at http://library.seg.org/

H40

Jazayeri et al.

# REFERENCES

André, F., M. Jonard, and S. Lambot, 2015, Non-invasive forest litter characterization using full-wave inversion of microwave radar data: IEEE Transactions on Geoscience and Remote Sensing, 53, 828–840, doi: 10.1109/TGRS.2014.2328776.
Benedetto, A., and L. Pajewski, 2015, Civil engineering applications of ground penetrating radar: Springer Transactions in Civil and Environmental Engineering.
Booth, A., R. A. Clark, and T. Murray, 2011, Influences on the resolution of GPR velocity analyses and a Monte Carlo simulation for establishing velocity precision: Near Surface Geophysics, 9, 399–411, doi: 10.3997/1873-0604.2011019.
Bumpus, P. B., and S. Kruse, 2014, Case history: Self-potential monitoring for hydrologic investigations in urban covered-karst terrain: Geophysics, 79, no. 6, B231–B242, doi: 10.1190/geo2013-0354.1.
Busch, S., J. van der Kruk, J. Bikowski, and H. Vereecken, 2012, Quantitative conductivity and permittivity estimation using full-waveform inversion of on-ground GPR data: Geophysics, 77, no. 6, H79–H91, doi: 10.1190/GEO2012-0045.1.
Busch, S., J. van der Kruk, and H. Vereecken, 2014, Improved characterization of fine-texture soils using on-ground GPR full-waveform inversion: IEEE Transactions on Geoscience and Remote Sensing, 52, 3947–3958, doi: 10.1109/TGRS.2012.2278297.
Busch, S., L. Wehrmüller, J. A. Huisman, C. M. Steelman, A. L. Endres, H. Vereecken, and J. Kruk, 2013, Coupled hydrogeophysical inversion of time-lapse surface GPR data to estimate hydraulic properties of a layered subsurface: Water Resources Research, 49, 8480–8494.
Cassidy, N. J., 2009, Ground penetrating radar data processing, modelling and analysis, in Harry, M. J., ed., Ground penetrating radar: theory and applications, Elsevier, 141–176.
Crocco, L., G. Prisco, F. Soloveiri, and N. J. Cassidy, 2009, Early-stage leaking pipes GPR monitoring via microwave tomographic inversion: Journal of Applied Geophysics, 67, 270–277.
De Coster, A., A. P. Tran, and S. Lambot, 2016, Fundamental analyses on layered media reconstruction using GPR and full-wave inversion in near-field conditions: IEEE Transactions on Geoscience and Remote Sensing, 54, 5143–5158, doi: 10.1109/TGRS.2016.2556062.
Deminici, S., E. Yigit, I. H. Eskidemir, and C. Ozdemir, 2012, Ground penetrating radar imaging of water leaks from buried pipes based on back-projection method: NDT&E International, 47, 35–42.
Doherty, J., 2010, PEST model-independent parameter estimation user manual, 5th ed.: Watermark Numerical Computing.
Doherty, J., 2015, Calibration and uncertainty analysis for complex environmental models, PEST: Complete theory and what it means for modelling the real world: Watermark Numerical Computing.
Doherty, J., 2017, PEST, http://www.pesthomepage.org/, accessed 1 August 2017.
Dou, Q., L. Wei, D. R. Magee, and A. G. Cohn, 2017, Real-time hyperbola recognition and fitting in GPR data: IEEE Transactions on Geoscience and Remote Sensing, 55, 51–62.
Ernst, J. R., A. G. Green, H. Maurer, and K. Holliger, 2007, Application of a new 2D time-domain full-waveform inversion scheme to crosshole radar data: Geophysics, 72, no. 5, J53–J64, doi: 10.1190/1.2761848.
Fisher, S. C., R. R. Stewart, and H. M. Jol, 1992, Processing ground penetrating radar (GPR) data: CREWES Research Report 4, 11–2–11–22.
Forberger, T., L. Groos, and M. Schafer, 2014, Line-source simulation for shallow-seismic data, Part 1: Theoretical background: Geophysical Journal International, 198, 1387–1404, doi: 10.1093/gj/ggu199.
Giannopoulos, A., 2005, Modelling ground penetrating radar by GprMax: Construction and Building Materials, 19, 755–762, doi: 10.1016/j.conbuildmat.2005.06.007.
Grandjean, G., J. C. Goury, and A. Binti, 2000, Evaluation of GPR techniques for civil-engineering applications: study on a test site: Journal of Applied Geophysics, 45, 141–156.
Guering, N., A. Klotzsche, J. van der Kruk, J. Vanderborgh, H. Vereecken, and A. Englert, 2015, Imaging and characterization of facies heterogeneity in an alluvial aquifer using GPR full-waveform inversion and cone penetration tests: Journal of Hydrology, 524, 680–695, doi: 10.1016/j.jhydrol.2015.03.030.
Guering, N., T. Vienken, A. Klotzsche, J. van der Kruk, J. Vanderborgh, J. Caers, H. Vereecken, and A. Englert, 2017, High resolution aquifer characterization using crosshole GPR full-waveform tomography: Comparison with direct-push and tracer test data: Water Resources Research, 53, 49–72, doi: 10.1002/2016WR019496.
Janning, R., A. Busche, T. Horvath, and L. Schmidt-Thieme, 2014, Buried pipe localization using an iterative geometric clustering on GPR data: Artificial Intelligence Review, 42, 403–425, doi: 10.1007/s10462-013-9410-2.
Jazayeri, S., and S. Kruse, 2016, Full-waveform inversion of ground-penetrating radar (GPR) data using pest (PWI-pest method) applied to utility detection: 86th Annual International Meeting, SEG, Expanded Abstracts, 2474–2478, doi: 10.1190/sega2016-13878165.1.
Kalogeropoulos, A., J. van der Kruk, J. Hugenchmidt, S. Busch, and K. Metz, 2011, Chlorides and moisture assessment in concrete by GPR full-waveform inversion: Near Surface Geophysics, 9, 277–285, doi: 10.3997/1873-0604.2010064.
Keskinen, J., A. Klotzsche, M. C. Loomis, J. Moreau, J. van der Kruk, K. Holliger, L. Stemmerik, and L. Nielsen, 2017, Full-waveform inversion of crosshole GPR data: Implications for porosity estimation in chalk: Journal of Applied Geophysics, 140, 102–116, doi: 10.1016/j.japgeo.2017.01.001.
Klotzsche, A., J. van der Kruk, J. Bradford, and H. Vereecken, 2014, Detection of spatially limited high-porosity layers using crosshole GPR signal analysis and full-waveform inversion: Water Resources Research, 50, 6966–6985, doi: 10.1002/2013WR015177.
Klotzsche, A., J. van der Kruk, N. Linde, J. A. Doersch, and H. Vereecken, 2013, 3-D characterization of high-permeability zones in a gravel aquifer using 2-D crosshole GPR full-waveform inversion and waveguide detection: Geophysical Journal International, 195, 932–944, doi: 10.1093/gj/ggt275.
Klotzsche, A., J. van der Kruk, G. A. Meles, J. A. Doersch, H. Maurer, and N. Linde, 2010, Full-waveform inversion of crosshole ground penetrating radar data to characterize a gravel aquifer close to the Thur River, Switzerland: Near Surface Geophysics, 8, 631–646, doi: 10.3997/1873-0604.2010054.
Klotzsche, A., J. van der Kruk, G. Meles, and H. Vereecken, 2012, Crosshole GPR full-waveform inversion of waveguides acting as preferential flow paths within aquifer systems: Geophysics, 77, no. 4, H57–H62, doi: 10.1190/geo2011-0458.1.
Lambot, S., E. C. Slob, I. van den Bosch, B. Stockbroeckx, and M. Van-closster, 2004, Modeling of ground-penetrating radar for accurate characterization of subsurface electric properties: IEEE Transactions on Geoscience and Remote Sensing, 42, 2555–2568, doi: 10.1109/TGRS.2004.834800.
Lavoué, F., R. Brossier, L. Métivier, S. Garambos, and J. Vireux, 2014, Two-dimensional permittivity and conductivity imaging by full-waveform inversion of multioffset GPR data: A frequency-domain quasi-Newton approach: Geophysical Journal International, 197, 248–268, doi: 10.1093/gj/ggt528.
Lester, J., and L. E. Bernold, 2007, Innovative process to characterize buried utilities using ground penetrating radar: Automation in Construction, 16, 546–555, doi: 10.1016/j.autcon.2006.09.004.
Liu, H., and M. Sato, 2014, In situ measurement of pavement thickness and dielectric permittivity by GPR using an antenna array: NDT&E International, 64, 65–71, doi: 10.1016/j.nd168.2014.03.001.
Liu, H., X. Xie, K. Takahashi, and M. Sato, 2014, Groundwater level monitoring for hydraulic characterization of an unconfined aquifer by common mid-point measurements using GPR: JEEQ, 19, 259–268, doi: 10.2113/EEQ19.4.xx.
Loeffler, O., and M. Bano, 2004, Ground penetrating radar measurements in a controlled vadose zone: Influence of the water content: Vadose Zone Journal, 3, 1082–1092.
Mahmoudzadeh Ardakani, M. R., D. C. Jacques, and S. Lambot, 2016, A layered vegetation model for GPR full-wave inversion: IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing, 9, 18–28, doi: 10.1109/JSTARS.2015.2418093.
Maierhofer, C., H. Reinhardt, and G. Dobmann, 2010, Non-destructive evaluation of reinforced concrete structures, Volume 1: Detection processes and standard test methods, 1st ed.: Woodhead Publishing Limited.
Meles, G. A., S. A. Greenhalgh, J. Van der Kruk, A. G. Green, and H. Maurer, 2012, Taming the non-linearity problem in GPR full-waveform inversion for high contrast media: Journal of Applied Geophysics, 78, 31–43, doi: 10.1016/j.japgeo.2011.12.001.
Meles, G. A., J. Van der Kruk, S. A. Greenhalgh, J. R. Ernst, H. Maurer, and A. G. Green, 2010, A new vector waveform inversion algorithm for simultaneous updating of conductivity and permittivity parameters from combination crosshole/borehole-to-surface GPR data: IEEE Transactions on Geosciences and Remote Sensing, 48, 3391–3407, doi: 10.1109/TGRS.2010.2046670.
Murray, T., A. Booth, and D. M. Rippin, 2007, Water-content of glacier-ice: Limitations on estimates from velocity analysis of surface ground-penetrating radar surveys: JEEQ, 12, 87–99.
Ni, S., Y. Huang, K. Lo, and D. Lin, 2010, Buried pipe detection by ground penetrating radar using the discrete wavelet transform: Computers and Geotechnics, 37, 440–448.
Radzevicin, S., 2015, Least-squares curve fitting for velocity and time zero: Presented at the 8th IWAGPR.
Ristic, A. V., D. Petrovacki, and M. Govedarica, 2009, A new method to simultaneously estimate the radius of a cylindrical object and the wave propagation velocity from GPR data: Computers & Geosciences, 35, 1620–1630.

50

FWI of common-offset GPR using PEST

H41

Roberts, R. L., and J. J. Daniels, 1996, Analysis of GPR polarization phenomena: JEEG, 1, 139–157.
Sham, J. F. C., and W. W. L. Lai, 2016, Development of a new algorithm for accurate estimation of GPR's wave propagation velocity by common-offset survey method: NDT&E International, 83, 104–113.
Tran, A. P., F. André, and S. Lambot, 2014, Validation of near-field ground-penetrating radar modeling using full-wave inversion for soil moisture estimation: IEEE Transactions on Geoscience and Remote Sensing, 52, 5483–5497, doi: 10.1109/TGRS.2013.2289952.
Vacher, L., School of Geosciences, University of South Florida, 2017, USF GeoPark, history of the GeoPark, http://hennaest.forest.usf.edu/main/depts/geosci/facilities/geopark.aspx, accessed 1 August 2017.
van der Kruk, J., N. Gueting, A. Klotzsche, G. He, S. Rudolph, C. von Hebel, X. Yang, L. Weihermiller, A. Mester, and H. Vereecken, 2015, Quantitative multi-layer electromagnetic induction inversion and full-waveform inversion of crosshole ground penetrating radar data: Journal of Earth Science, 26, 844–850, doi: 10.1007/s12583-015-0610-3.
Villela, A., and J. M. Romo, 2013, Invariant properties and rotation transformations of the GPR scattering matrix: Journal of Applied Geophysics, 90, 71–81.
Virtieux, J., and S. Operto, 2009, An overview of full-waveform inversion in exploration geophysics: Geophysics, 74, no. 6, WCC1–WCC26, doi: 10.1190/1.3238367.
Warren, C., A. Giannopoulos, and I. Giannakis, 2016, gprMax: Open source software to simulate electromagnetic wave propagation for Ground Penetrating Radar: Computer Physics Communications, 209, 163–170, doi: 10.1016/j.cpc.2016.08.020.
Wiwatrojanagul, P., R. Sahamitmongkol, S. Tangtermisirikul, and N. Kham-semanan, 2017, A new method to determine locations of rebars and estimate cover thickness of RC structures using GPR data: Construction and Building Materials, 140, 257–273.
Yang, X., A. Klotzsche, G. Meles, H. Vereecken, and J. van der Kruk, 2013, Improvements in crosshole GPR full-waveform inversion and application on data measured at the Boise Hydrogeophysics Research Site: Journal of Applied Geophysics, 99, 114–124, doi: 10.1016/j.jappgeo.2013.08.007.
Zeng, X., and G. McMechan, 1997, GPR characterization of buried tanks and pipes: Geophysics, 62, 797–806, doi: 10.1190/1.1444189.

Downloaded 01/15/19 to 131.247.224.4. Redistribution subject to SEG license or copyright; see Terms of Use at http://library.seg.org/

51

# Appendix II. Copyright permission from *Geophysics* for use of this manuscript  
in dissertation

52

Copyright Clearance Center

1/25/19, 6:30 PM

Copyright

Clearance

Center

Note: Copyright.com supplies permissions but not the copyrighted content itself.

1

PAYMENT

2

REVIEW

3

CONFIRMATION

### Step 3: Order Confirmation

Thank you for your order! A confirmation for your order will be sent to your account email address. If you have questions about your order, you can call us 24 hrs/day, M-F at +1.855.239.3415 Toll Free, or write to us at info@copyright.com. This is not an invoice.

Confirmation Number: 11785977

Order Date: 01/25/2019

If you paid by credit card, your order will be finalized and your card will be charged within 24 hours. If you choose to be invoiced, you can change or cancel your order until the invoice is generated.

### Payment Information

Sajad Jazayeri

sjazayeri@mail.usf.edu

+1 (813) 362-9299

Payment Method: n/a

### Order Details

### Geophysics

Order detail ID: 71781869

Order License Id: 4516150683801

ISSN: 0016-8033

Publication Type: Journal

Volume:

Issue:

Start page:

Publisher: SOCIETY OF EXPLORATION GEOPHYSICISTS,

Author/Editor: SOCIETY OF PETROLEUM GEOPHYSICISTS ; SOCIETY OF EXPLORATION GEOPHYSICISTS

Permission Status: ☑ Granted

Permission type: Republish or display content

Type of use: Thesis/Dissertation

Hide details

Requestor type

Author of requested content

Format

Print, Electronic

Portion

chapter/article

The requesting person/organization

Sajad Jazayeri

Title or numeric reference of the portion(s)

Chapter 2

Title of the article or chapter the portion is from

Improving estimates of buried pipe diameter and infilling material from ground-penetrating radar profiles with full-waveform inversion

Editor of portion(s)

N/A

Author of portion(s)

Sajad Jazayeri

https://www.copyright.com/confirmColCartPurchase.do?operation=confirmPurchase

Page 1 of 2

53

Copyright Clearance Center

1/25/19, 6:30 PM

|  **Volume of serial or monograph** | 83  |
| --- | --- |
|  **Issue, if republishing an article from a serial** | 4  |
|  **Page range of portion** |   |
|  **Publication date of portion** | July-August 2018  |
|  **Rights for** | Main product  |
|  **Duration of use** | Life of current edition  |
|  **Creation of copies for the disabled** | no  |
|  **With minor editing privileges** | no  |
|  **For distribution to** | Worldwide  |
|  **In the following language(s)** | Original language of publication  |
|  **With incidental promotional use** | no  |
|  **Lifetime unit quantity of new product** | Up to 499  |
|  **Title** | High-resolution modeling of common-offset GPR data using Full-waveform Inversion  |
|  **Institution name** | University of South Florida  |
|  **Expected presentation date** | Apr 2019  |

**Note:** This item will be invoiced or charged separately through CCC's **RightsLink** service. More info

**$ 0.00**

**Total order items: 1**

**This is not an invoice.**

**Order Total: 0.00 USD**

https://www.copyright.com/confirmCoiCartPurchase.do?operation=confirmPurchase

Page 2 of 2

54

### **Appendix III. Sparse Blind Deconvolution of Ground Penetrating Radar Data**

55

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING

1

# Sparse Blind Deconvolution of Ground Penetrating Radar Data

Sajad Jazayeri, Nasser Kazemi, and Sarah Kruse

Abstract—We propose an effective method for sparse blind deconvolution (SBD) of ground penetrating radar data. The SBD algorithm has no constraints on the phase of the wavelet, but the initial wavelet must be carefully captured from the data. The data are considered a convolution product of an unknown source wavelet and unknown sparse reflectivity series. The algorithm developed here is an alternating minimization technique that updates the reflectivity series and the wavelet iteratively. The reflectivity update is solved as an $\ell_2 - \ell_1$ problem with the alternating split Bregman iteration technique. The wavelet update is solved as an $\ell_2 - \ell_2$ problem with Wiener deconvolution. The algorithm converges to a local minimum. In order to increase the likelihood so that convergence coincides with the desired local minimum, special steps are taken to provide a proper initial wavelet. Synthetic and real data examples show that both subsurface reflectivity series and wavelet (amplitude and phase) can be estimated efficiently. The SBD method presented appears robust and compares favorably to previous studies in its resistance to noise.

Index Terms—Deconvolution, ground penetrating radar (GPR), reflectivity, source wavelet, sparsity.

# I. INTRODUCTION

DECONVOLUTION is a popular deblurring technique used in signal and image processing, with applications in photography, remote sensing, astronomy, medical imaging, geophysics, and more [1], [2]. When successfully applied to blurry or distorted matrices, the result is a clearer image with more details. In geophysics, particularly in exploration seismology, the goal of deconvolution is higher resolution subsurface images [3]. Deconvolution works by removing the signature of the propagated waveform. Ideally, what is left is a representation of the subsurface pattern of reflection coefficients, which present a high-resolution subsurface image [4].

Deconvolution of ground penetrating radar (GPR) data is used to estimate the reflectivity series [5]–[13], to produce a higher resolution subsurface image or a clean reflectivity series that can be used for ray-based travel-time analysis. GPR deconvolution is also used to extract the shape of the transmitted pulse [14]–[16], for use in modeling procedures

Manuscript received April 27, 2018; revised August 10, 2018 and September 23, 2018; accepted November 18, 2018. (Corresponding author: Sajad Jazayeri.)

S. Jazayeri and S. Kruse are with the School of Geosciences, University of South Florida, Tampa, FL 33620 USA (e-mail: sjazayeri@mail.usf.edu; skruse@usf.edu).

N. Kazemi is with the Department of Chemical and Petroleum Engineering, University of Calgary, Calgary, AB T2N 1N4, Canada (e-mail: nasser.kazeminojadeh@ucalgary.ca).

Digital Object Identifier 10.1109/TGRS.2018.2886741

such as full-waveform inversion (FWI). Factors such as antenna-ground coupling and Earth's filtering effects due to soil's characteristics alter the shape of the wavelet [10], which make it challenging to estimate the waveform and reflectivity series.

The widely used Wiener deconvolution [17], [18] has some disadvantages when applied to GPR data. Wiener deconvolution assumes that the reflectivity series has an ideal statistical property, i.e., it is white noise, and the wavelet has a minimum phase characteristics [17], [18]. However, Ricker [19] shows that due to the earth filtering, the average wavelet is different from the near-source signature. We show, here, that when using the Wiener deconvolution method, we can only estimate a smooth reflectivity series and a residual wavelet; any difference between the actual wavelet and its minimum phase equivalent remains untouched in the recovered reflectivity series. Fortunately, a body of literature shows the possibility of estimating nonminimum phase wavelets by imposing a sparsity constraint instead of a white noise assumption (i.e., Gaussian distribution) on the reflectivity series [20]–[25].

The alternative deconvolution method is referred to as sparse blind deconvolution (SBD). A sparsity assumption is imposed on the matrix of reflection coefficients. The process begins "blindly" in that it is formulated to start without requiring a starting model of reflection coefficients, or without a starting model for the source wavelet. The sparsity assumption is well adapted to enhancing the resolution of thin layers and isolated buried objects. The method thus holds promise particularly for both layered geological features and engineering, archeological, or tree root applications where finite objects produce distinctive returns within a background of soil structure. Few studies have applied a sparsity assumption while performing deconvolution on GPR data [26], [27]. The method presented by Chahine et al. [26] improves image resolution in the presence of thin layers by sparsity maximization in the reflectivity series with results similar to spiking deconvolution. Their method requires a minimum phase wavelet and is sensitive to noise. Li [27] introduces an alternating iterative method to solve the nonconvex optimization problem, with a threshold maximum for the reflector amplitudes to avoid trapping the solution in local minima. Tested only on synthetic data, Li's algorithm struggles to recover the shape and the phase of the source wavelet in the presence of noise.

In this paper, we propose an alternating SBD method targeting GPR data, which may be more robust in the presence of noise. The algorithm estimates both the wavelet and the

0196-2892 © 2019 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission. See http://www.ieee.org/publications_standards/publications/rights/index.html for more information.

56

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

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

4

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING

![img-40.jpeg](img-40.jpeg)

Fig. 1 Synthetic 1-GHz 3-D GPR model of a profile run perpendicular over three cylinders with 1.2-GHz noise and 500-MHz noise. Black boxes contain trace segments used for initial wavelet estimation. Traces are computed for 7 ns; the earliest portions of the traces containing the direct wave arrivals are removed from the analysis.

simplifies to

\[
\mathbf {w} = \underset {\mathbf {w}} {\operatorname{argmin}} \left\| \mathbf {R w} - \mathbf {d} \right\| _ {2} ^ {2} + \lambda_ {\infty} \| \mathbf {w} \| _ {2} ^ {2} \tag {18}
\]

which is an \(\ell_2 - \ell_2\) problem and has a closed-form solution

\[
\mathbf {w} = (\mathbf {R} ^ {T} \mathbf {R} + \lambda_ {\infty} \mathbf {I}) ^ {- 1} \mathbf {R} ^ {T} \mathbf {d} \tag {19}
\]

where I is the identity matrix.

At this point, we stress that the alternating minimization technique is a local minimization approach and special steps must be taken to initialize the unknown variables w and r. The initial estimation of the wavelet is of particular importance and discussed further below.

## II. METHODOLOGY

The proposed SBD method has two stages, the initialization and the main optimization. Our main optimization algorithm is an alternating minimization technique. Because we begin with (17) (updating the reflectivity with wavelet fixed), we require the formulation of an initial wavelet. The main algorithm then solves the general SBD equation (15) or (16) by defining the two subproblems for reflectivity and wavelet expressed in (17) and (18), respectively.

### A. Algorithm Initialization

The proposed algorithm is a local minimizer and, therefore, sensitive to the initial wavelet. For the ground-coupled GPR scenarios considered here, the method is successful when we obtain the initial wavelet from the data. To estimate the initial wavelet, windowed portions of several traces near the apex of the hyperbolic events in the data are averaged, as shown, for example, in the black squared windows in Fig. 1. The windowed traces are first shifted relative to one another to maximize the zero-lag cross correlation. Then, the shifted traces are stacked and normalized to provide the initial wavelet. We note the initial wavelet is estimated in this fashion from the data in both synthetic and real data examples.

### B. Main Optimization

This section describes the alternating minimization technique. First, we illustrate updating the reflectivity series by the alternating split Bregman algorithm for solving (17) and then updating the wavelet by solving (19).

1) Updating Reflectivity With the Alternating Split Bregman Algorithm: Bregman iteration regularization is based on the Bregman distance and solves a constrained optimization problem with a general form of

\[
\mathbf {r} = \underset {\mathbf {r}} {\operatorname{argmin}} \mathcal {C} _ {1} (\mathbf {r}) \quad \text { s.t. } \mathcal {C} _ {2} (\mathbf {r}) = 0 \tag {20}
\]

with  \( C_{1} \)  and  \( C_{2} \)  convex,  \( C_{2} \)  differentiable, and  \( \arg\min_{\mathbf{r}} C_{2}(\mathbf{r}) = 0 \) . The Bregman distance of functional  \( C_{1} \)  between two points  \( r_{1} \)  and  \( r_{2} \)  is defined as

\[
B D _ {\mathcal {C} _ {1}} ^ {\mathrm{R}} \left(\mathbf {r} _ {1}, \mathbf {r} _ {2}\right) = \mathcal {C} _ {1} \left(\mathbf {r} _ {1}\right) - \mathcal {C} _ {1} \left(\mathbf {r} _ {2}\right) - \langle \mathbf {g}, \mathbf {r} _ {1} - \mathbf {r} _ {2} \rangle \tag {21}
\]

where \(\mathbf{g} \in \partial \mathcal{C}_1(\mathbf{r}_2)\) is a subgradient of \(\mathcal{C}_1\) at the \(\mathbf{r}_2\) point. Bregman iterative regularization solves the problem stated in (20) by a sequence of convex problems

\[
\mathbf {r} = \underset {\mathbf {r}} {\operatorname{argmin}} \mathcal {C} _ {1} (\mathbf {r}) - \left\langle \mathbf {g} ^ {k}, \mathbf {r} \right\rangle + \lambda \mathcal {C} _ {2} (\mathbf {r}) \tag {22}
\]

and

\[
\mathbf {g} ^ {k + 1} = \mathbf {g} ^ {k} - \lambda \nabla \mathcal {C} _ {2} (\mathbf {r} ^ {k + 1}) \tag {23}
\]

with \(k = 0,1,2,\ldots\) the iteration number, \(\lambda >0\), \(\nabla\) is the gradient operator, and \(\mathbf{g}^{k + 1}\in \partial \mathcal{C}_1(\mathbf{r}^{k + 1})\). To take advantage of the Bregman iteration, we need to rewrite (17) with a similar format to that in (20)

\[
\left\{\mathbf {r}, \mathbf {t} _ {1} \right\} = \underset {\mathbf {r}, \mathbf {t} _ {1}} {\operatorname{argmin}} \left\| \mathbf {t} _ {1} \right\| _ {2} ^ {2} + \lambda_ {r} \| \mathbf {r} \| _ {1} \text {s.t.} \mathbf {t} _ {1} - (\mathbf {H r} - \mathbf {d}) = 0 \tag {24}
\]

with \(\mathbf{t}_1 = \mathbf{H}\mathbf{r} - \mathbf{d}\). Comparing (24) and (20) reveals that \(\mathcal{C}_1(\mathbf{r},\mathbf{t}_1) = ||\mathbf{t}_1||_2^2 +\lambda_r||\mathbf{r}||_1\) and \(\mathcal{C}_2(\mathbf{r},\mathbf{t}_1) = \mathbf{t}_1 - (\mathbf{H}\mathbf{r} - \mathbf{d})\). Using the new \(\mathcal{C}_1\) and \(\mathcal{C}_2\) functionals and defining \(\mathbf{t}_2 = \mathbf{r}\), we derive the simplified Bregman iterations (for detailed derivations see [39]) as

\[
\begin{array}{l} \left\{\mathbf {r} ^ {k + 1}, \mathbf {t} _ {1} ^ {k + 1}, \mathbf {t} _ {2} ^ {k + 1} \right\} = \underset {\mathbf {r}, \mathbf {t} _ {1}, \mathbf {t} _ {2}} {\operatorname{argmin}} \| \mathbf {t} _ {1} \| _ {2} ^ {2} + \lambda_ {r} \| \mathbf {t} _ {2} \| _ {1} \\ + \frac {\alpha}{2} \mathbf {t} _ {1} - (\mathbf {H r} - \mathbf {y}) - \mathbf {g} _ {1} ^ {k} \\ + \frac {\beta}{2} \mathbf {t} _ {2} - \mathbf {r} - \mathbf {g} _ {2} ^ {k} \begin{array}{c c} 2 & \\ 2 & \end{array} \tag {25} \\ \end{array}
\]

\[
\mathbf {g} _ {1} ^ {k + 1} = \mathbf {g} _ {1} ^ {k} - \mathbf {t} _ {1} ^ {k + 1} - (\mathbf {H r} ^ {k + 1} - \mathbf {y}) \tag {26}
\]

\[
\mathbf {g} _ {2} ^ {k + 1} = \mathbf {g} _ {2} ^ {k} - \mathbf {t} _ {2} ^ {k + 1} - \mathbf {r} ^ {k + 1} \tag {27}
\]

with \(\mathbf{g}_1^0 = \mathbf{g}_2^0 = \mathbf{0}\) and \(\alpha, \beta > 0\). The final step is to solve (25). Goldstein and Osher [39] show that (25) can be divided into three sub-problems where

\[
\mathbf {r} ^ {k + 1} = \underset {\mathbf {r}} {\operatorname{argmin}} \frac {\alpha}{2} \mathbf {t} _ {1} ^ {k} - (\mathbf {H r} - \mathbf {y}) - \mathbf {g} _ {1} ^ {k} + \frac {\beta}{2} \mathbf {t} _ {2} ^ {k} - \mathbf {r} - \mathbf {g} _ {2} ^ {k} \tag {28}
\]

\[
\mathbf {t} _ {1} ^ {k + 1} = \underset {\mathbf {d}} {\operatorname{argmin}} \frac {\alpha}{2} \| \mathbf {d} - (\mathbf {H r} ^ {k + 1} - \mathbf {y}) - \mathbf {g} _ {1} ^ {k} \| + \| \mathbf {d} \| _ {2} ^ {2} \tag {29}
\]

\[
\mathbf {t} _ {2} ^ {k + 1} = \underset {\mathbf {d}} {\operatorname{argmin}} \frac {\beta}{2} \mathbf {d} - \mathbf {H r} ^ {k + 1} - \mathbf {g} _ {2} ^ {k} + \lambda_ {r} \| \mathbf {d} \| _ {1}. \tag {30}
\]

59

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

JAZAYERI et al.: SBD OF GPR DATA

5

Equations (28) and (29) have closed-form solutions

$$\mathbf{r}^{k+1} = \mathbf{P}^{-1} \left( \alpha \mathbf{H}^T \mathbf{t}_1^k - \mathbf{g}_1^k + \mathbf{y} + \beta \mathbf{t}_2^k - \mathbf{g}_2^k \right) \tag{31}$$

and

$$\mathbf{t}_1^{k+1} = \frac{\mathbf{H} \mathbf{r}^{k+1} - \mathbf{y} + \mathbf{g}_1^k}{1 + \frac{\alpha}{\alpha}} \tag{32}$$

where $\mathbf{P} = \alpha \mathbf{H}^T \mathbf{H} + \beta \mathbf{I}$ and $\mathbf{I}$ is the identity matrix. Finally, in the case of (30), Goldstein and Osher argue that a single-iteration update is enough to approximate the solution. Accordingly, the single-iteration solution of (30) is defined as

$$\mathbf{t}_2^{k+1} = \text{prox}_{\frac{\alpha}{\alpha}} (\mathbf{r}^{k+1} + \mathbf{g}_2^k) \tag{33}$$

where prox is a proximity operator and is defined as $\text{prox}_r(\mathbf{a}) = \text{sign}(\mathbf{a}) \odot \max(|\mathbf{a}| - r, 0)$ and $\odot$ is the Hadamard product. At this point by using (31)–(33) along with (26) and (27), we finalize the alternating split Bregman algorithm (Algorithm 1).

Algorithm 1 Alternating Split Bregman Algorithm as a Minimizer of 24 in the Time Domain

Require: d, H, $\lambda_r$, $\alpha$, $\beta$
Initialize: $k = 0, \mathbf{t}_1^0 = \mathbf{t}_2^0 = \mathbf{g}_1^0 = \mathbf{g}_1^0 = \mathbf{0}$
while $\|\mathbf{r}^k - \mathbf{r}^{k-1}\|_2^2 > tol$ do
$\mathbf{r}^{k+1} = \mathbf{P}^{-1} (\alpha \mathbf{H}^T [\mathbf{t}_1^k - \mathbf{g}_1^k + \mathbf{y}] + \beta [\mathbf{t}_2^k - \mathbf{g}_2^k])$
$\mathbf{t}_1^{k+1} = \frac{\mathbf{H} \mathbf{r}^{k+1} - \mathbf{y} + \mathbf{g}_1^k}{1 + \frac{\alpha}{\alpha}}$
$\mathbf{t}_2^{k+1} = \text{prox}_{\frac{\alpha}{\alpha}} (\mathbf{r}^{k+1} + \mathbf{g}_2^k)$
$\mathbf{g}_1^{k+1} = \mathbf{g}_1^k - [\mathbf{t}_1^{k+1} - (\mathbf{H} \mathbf{r}^{k+1} - \mathbf{y})]$
$\mathbf{g}_2^{k+1} = \mathbf{g}_2^k - [\mathbf{t}_2^{k+1} - \mathbf{r}^{k+1}]$
$k \leftarrow k + 1$
end while
return $\mathbf{r} = \mathbf{r}^k$

Algorithm 1 can efficiently solve (24). However, close inspection of the algorithm shows the matrix $\mathbf{P}$ has a block diagonal structure with each block being a Toeplitz matrix that can be diagonalized in the frequency domain. Accordingly, the update of $\mathbf{r}^{k+1}$ step can be formulated as a Wiener deconvolution in the frequency domain without any direct inversion of the $\mathbf{P}$ matrix. Hence, we formulate the alternating split Bregman algorithm in the frequency domain to decrease the computational cost of the algorithm. To do so, the Fourier equivalent of variables is defined as $\hat{\mathbf{w}} = \mathcal{F}\mathbf{w}$, $\hat{\mathbf{r}} = \mathcal{F}\mathbf{r}$, where $\mathcal{F}$ is a Fourier transform operator with $\mathcal{F}_{m,n} = \exp(-i2\pi mn/N)$, $i = -1, m, n = 0, 1, 2, \dots, N-1$, and the inverse Fourier transform is $\mathcal{F}^{-1} = (1/N)\mathcal{F}$, where indicates the complex conjugate. Using these Fourier pairs, we can write $\mathbf{H} = \mathcal{F}^{-1}\mathbf{H}_f\mathcal{F}$ where $\mathbf{H}_f$ is a diagonal matrix with $J$ matrices built from $\text{diag}(\hat{\mathbf{w}})$ where $\text{diag}(\cdot)$ reshapes the vector to a diagonal matrix. Now, we have all the ingredients to formulate the alternating split Bregman algorithm in the frequency domain (Algorithm 2).

2) Updating the Wavelet: To update the wavelet, we need to solve (18), which has the closed-form solution shown in (19). Equation (19) can also be solved in the frequency domain since

Algorithm 2 Alternating Split Bregman Algorithm as a Minimizer of 24 in the Frequency Domain

Require: d, $\mathbf{H}_f$, $\hat{\mathbf{w}}$, $\lambda_r$, $\alpha$, $\beta$
Define: $\mathbf{D} = \text{diag}(\frac{1}{\alpha(\|\mathbf{H}_f\|^2 + \beta)})$
Initialize: $k = 0, \mathbf{t}_1^0 = \mathbf{t}_2^0 = \mathbf{g}_1^0 = \mathbf{g}_1^0 = \mathbf{0}$
while $\|\hat{\mathbf{r}}^k - \hat{\mathbf{r}}^{k-1}\|_2^2 > tol$ do
$\hat{\mathbf{r}}^{k+1} = \mathbf{D} (\alpha \mathbf{H}_f \mathcal{F} [\mathbf{t}_1^k - \mathbf{g}_1^k + \mathbf{y}] + \beta \mathcal{F} [\mathbf{t}_2^k - \mathbf{g}_2^k])$
$\mathbf{t}_1^{k+1} = \frac{\mathcal{F}^{-1} \mathbf{H}_f \hat{\mathbf{r}}^{k+1} - \mathbf{y} + \mathbf{g}_1^k}{1 + \frac{\alpha}{\alpha}}$
$\mathbf{t}_2^{k+1} = \text{prox}_{\frac{\alpha}{\alpha}} (\mathcal{F}^{-1} \hat{\mathbf{r}}^{k+1} + \mathbf{g}_2^k)$
$\mathbf{g}_1^{k+1} = \mathbf{g}_1^k - [\mathbf{t}_1^{k+1} - (\mathcal{F}^{-1} \mathbf{H}_f \hat{\mathbf{r}}^{k+1} - \mathbf{y})]$
$\mathbf{g}_2^{k+1} = \mathbf{g}_2^k - [\mathbf{t}_2^{k+1} - \mathcal{F}^{-1} \hat{\mathbf{r}}^{k+1}]$
$k \leftarrow k + 1$
end while
return $\mathbf{r} = \mathbf{t}_2^k$

the matrix $\mathbf{R}$ has a Toeplitz structure and can be diagonalized in the frequency domain

$$\mathbf{w} = \mathcal{F}^{-1} \left[ \frac{J_{j-1}}{J_{j-1}} \hat{\mathbf{r}}_j \odot \hat{\mathbf{d}}_j \right] \tag{34}$$

where $\hat{\mathbf{r}} = J_{j-1} \hat{\mathbf{r}}_j \odot \hat{\mathbf{r}}_j$, $\odot$ is the Hadamard product, and $\hat{\mathbf{r}}_j$ and $\hat{\mathbf{d}}_j$ are the Fourier pairs of reflectivity and data in trace $j$, respectively.

### C. SBD Algorithm

After defining the initialization step and the main optimization workflow for updating the reflectivity series and the wavelet, we can finalize the SBD algorithm. We use the more efficient frequency domain methods. Algorithm 3 shows the steps.

Algorithm 3 SBD Algorithm

Require: d, L, $\lambda_r$, $\lambda_w$, $\alpha$, $\beta$
Define initial wavelet [using Algorithm initialization]: $\mathbf{w}^0$
k=0
while $\|\mathbf{H}\mathbf{r} - \mathbf{d}\|_2^2 > tol$ do
Update $\mathbf{H}^k$ using $\mathbf{w}^k$
Update reflectivity [using Algorithm 2]
$\mathbf{r}^{k+1} = \text{argmin} \|\mathbf{H}^k \mathbf{r} - \mathbf{d}\|_2^2 + \lambda_r \|\mathbf{r}\|_1$
Update $\mathbf{R}^{k+1}$ using $\mathbf{r}^{k+1}$
Update wavelet [using (34)]
$\mathbf{w}^{k+1} = \text{argmin} \|\mathbf{R}^{k+1} \mathbf{w} - \mathbf{d}\|_2^2 + \lambda_w \|\mathbf{w}\|_2^2$
$k \leftarrow k + 1$
end while
return $\mathbf{r} \leftarrow \mathbf{r}^k, \mathbf{w} \leftarrow \mathbf{w}^k$

### III. PARAMETER SELECTION

In this section, we describe our parameter selection strategies. The main parameters are length of wavelet $L$, regularization parameter for reflectivity update $\lambda_r$, and regularization

60

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

6

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING

parameter for wavelet update $\lambda_w$. The length of the wavelet, $L$, is defined subjectively as a full wavelength, which may include a “tail” over which the pulse amplitudes converge to zero (examples are shown in results below).

The choice of regularization parameter $\lambda_r$ has a significant impact on the estimated reflectivities. If the noise level $\delta$ is known, Pareto curves can be used to define $\lambda_r$ [40], [41]. Alternatively, the minimizer of the generalized cross-validation (GCV) score [42] can be used for selecting the regularization parameter

$$\mathrm{GCV}(\lambda_r) = \frac{\|\mathbf{H} \mathbf{r}_{\lambda_r} - \mathbf{d}\|_2^2}{(N - C \times \|\mathbf{r}_{\lambda_r}\|_0)^2} \tag{35}$$

where $\|\cdot\|_0$ is an $\ell_0$ norm that counts the number of nonzero elements, $C$ is an stabilizing parameter [43], and $\mathbf{r}_{\lambda_r}$ is the solution of (17) to a specific regularization parameter $\lambda_r$. A range of different parameters are tested and the minimizer of the GCV score is selected as the optimum $\lambda_r$. The GCV score method has the advantage of not requiring any prior information about the noise level so is used for real-data cases. Our tests on synthetic data show that the $\lambda_r$ values estimated from the Pareto curve and the GCV score are similar.

For the wavelet update, we need to define the optimum $\lambda_w$ parameter. Again, we make use of GCV score. The score for the Wiener deconvolution formulation of the wavelet estimation [2], [44] is defined as

$$\mathrm{GCV}(\lambda_w) = \frac{\|\mathbf{R} \mathbf{w}_{\lambda_w} - \mathbf{d}\|_2^2}{\left(N - C \times \sum_{k=0}^{N-1} \frac{(c_k k)^2}{(\lambda_k k)^2 + \lambda_w}\right)^2} \tag{36}$$

where $\mathbf{w}_{\lambda_w}$ is the solution of (18) to a specific regularization parameter $\lambda_w$. The $\alpha, \beta > 0$ are the split Bregman tradeoff parameters. We find that the recommended values of $\alpha = 0.5$, $\beta = 1$ from Gholami and Sacchi [2] work well for GPR data with Gaussian noise. High values make the numerical problem unstable. Our tests show that in data sets with high-amplitude low-frequency noise (typical for some GPR data) $\alpha = 0.001 - 0.01$, $\beta = 1$ produce optimal reflectivity and wavelet models.

### IV. NUMERICAL RESULTS

Synthetic data sets with two different noise levels and a field data set incorporating cylindrical objects (pipes and tree roots) buried in soil are considered for performance evaluation of the proposed method.

#### A. Synthetic Data, Cylindrical Objects Model, and Low Noise Level

The first model uses a mixed-phase GPR wavelet with 1-GHz (Hertzian dipole antenna with a transmitter-receiver offset of 3 cm) system response over three cylinders with different sizes and depths embedded in a homogeneous soil (see Table I for details). Cylinders have higher velocities than the background soil. Synthetic data are created with the software package gprMax [45] in 3-D. Noise is added to the modeled data, with a Gaussian distribution of high-frequency noise centered at 1.2 GHz and the peak value of 15% of the pulse amplitude, and lower frequency noise (500 MHz) added

TABLE I
OBJECT AND SOIL CHARACTERISTICS FOR SYNTHETIC DATA SHOWN IN
FIG. 1. INFORMATION ABOUT THE ANTENNA AND SPLIT BRIEGMAN PARAMETERS IS INCLUDED IN THE BOTTOM HALF

|  Object | Depth (cm) | Diameter (cm) | Relative Permittivity  |
| --- | --- | --- | --- |
|  Left | 19 | 2 | 7  |
|  Middle | 21 | 6 | 8  |
|  Right | 17 | 4 | 10  |
|  Soil |  |  | 5  |
|  Antenna Frequency (GHz) | Time Window (ns) | $\alpha$ | $\beta$  |
|  1 | 7 | 0.5 for case 1 and 0.001 for case 2 | 1 for case 1 and 0.5 for case 2  |

![img-41.jpeg](img-41.jpeg)

![img-42.jpeg](img-42.jpeg)

Fig. 2. Results from the deconvolution of the synthetic data shown in Fig. 1. (Top) True synthetic, initial, and final estimated wavelets. The graph shows the full length (3.7 ns) of the assumed wavelet. (Bottom) Estimated reflectivity model.

at a lower level (10% of pulse amplitude) (Fig. 1). To avoid the complexity of the direct wave, we applied a background removal filter to mute the direct wave. To estimate the initial wavelet, five traces around the apex of each hyperbolic event (seen in black boxes in Fig. 1) are selected, time-shifted to maximize zero-lag cross correlation, stacked and finally normalized [Fig. 2 (top)].

After seven iterations of the main loop of the algorithm, the model converges to the desired minimum, resulting in a final wavelet [red dashed line in Fig. 2 (top)] very close to the true wavelet [black line in Fig. 2 (top)] and a favorable sparse estimate of the reflectivity model [Fig. 2 (bottom)].

61

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

JAZAYERI et al.: SBD OF GPR DATA

7

![img-43.jpeg](img-43.jpeg)

Fig. 3. Estimated data from SBD for the cylinders model with high-frequency noise and moderate low-frequency noise. Comparison with Fig. 1 shows the noise is reduced.

![img-44.jpeg](img-44.jpeg)

Fig. 4. Synthetic 1-GHz 3-D GPR model over buried cylinders as given in Fig. 1, but with higher levels of low-frequency noise. Black boxes indicate trace segments used for initial wavelet estimation. Early direct wave arrivals are removed before analysis.

The polarity, location, and shape of the hyperbolic returns from the cylinders are extremely well recovered. The low-frequency random noise triggers very few sparse isolated reflectors. The data estimated from the convolution product of the final wavelet and the reflectivity model are shown in Fig. 3. Comparing this result with the original data in Fig. 1 shows the proposed SBD algorithm is an efficient method for reducing the level of high-frequency noise. It should also be noted that a higher resolution image of the estimated reflectivity models is obtained after SBD compared to the collected data as the impact of the transmitted pulse is erased from the data. The estimated reflectivity model is an ideal model that can be used in traditional curve fitting to identify the geometry and location of the reflecting objects.

### B. Synthetic Data, Cylindrical Objects Model, and High Noise Level

To create a somewhat more realistic case, a higher level of low-frequency noise (30% of pulse amplitude with 100–600-MHz frequency range) is added to the previously described model (Fig. 4). Such low-frequency noise, typical of many GPR data sets, is much more challenging to remove than high-frequency noise. We find that with the selection of

![img-45.jpeg](img-45.jpeg)

![img-46.jpeg](img-46.jpeg)

Fig. 5. Results from the deconvolution of the noisier synthetic data shown in Fig. 4. (Top) True, initial, and final estimated wavelets using the same split Bregman parameters $\alpha = 0.5$ and $\beta = 1$, which were used in the lower noise case in Fig. 2. (Bottom) Estimated reflectivity model of the cylinders. Random spikes caused by the low-frequency noise could make it challenging to identify the hyperbolic reflector.

$\alpha = 0.5$ and $\beta = 1$, the SBD fails to remove much of the noise and the reconstructed reflectivity model clearly suffers (Fig. 5). Here, the location and the shape of the hyperbolic reflectors are well recovered, but the reflectivity model could be difficult to interpret against the background noise. The estimated wavelet also suffers from the noise, especially at the tail of the pulse, where the amplitude fails to converge rapidly to zero (orange dashed pulse in Fig. 5).

To do a better job at reducing the low-frequency noise, a range of the split Bregman tradeoff parameters were tested. We find that for GPR data with high levels of low-frequency noise, $\alpha = 0.01$ to 0.001 and $\beta = 0.5$ are more successful in noise reduction and optimal reflectivity and wavelet recovery. Fig. 6 is obtained with $\alpha = 0.001$ and $\beta = 0.5$ ($\alpha = 0.01$ produces almost the same results). Comparison of Figs. 5 and 6 clearly illustrates the importance of the selection of the split Bregman tradeoff parameters. The shape of the estimated wavelet in both cases is generally similar, but the estimated source wavelet in Fig. 6 is much closer to the true wavelet, especially in the tail. Some sparse random reflectors remain in the model, presumably due to the similarity between the noise and the pulse frequencies at those locations.

### C. Real Data

A Mala ProEX system with an 800-MHz shielded antenna pair was used to gather a common-offset profile over an 8-cm-diameter metallic pipe buried in the sand (at distance

62

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

8

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING

![img-47.jpeg](img-47.jpeg)

![img-48.jpeg](img-48.jpeg)

![img-49.jpeg](img-49.jpeg)

![img-50.jpeg](img-50.jpeg)

Fig. 6. (Top) True, initial, and estimated wavelets as given in Fig. 5, but with split Bregman tradeoff parameters $\alpha = 0.001$ and $\beta = 0.5$. (Bottom) Estimated reflectivity model of the cylinders is much less noisy, compared to Fig. 5.

Fig. 8. (Top) Initial and final estimated wavelets for the data set shown in Fig. 7 with $\alpha = 0.5$ and $\beta = 1$. (Bottom) Corresponding estimated reflectivity model. The reflectivity image contains more complexity than desired.

![img-51.jpeg](img-51.jpeg)

Fig. 7. GPR transect over a metallic pipe (0.75 m along profile) and tree roots (2.1 and 3.0 m) in sand. A low-pass (2 GHz) filter has been applied to reduce high-frequency noise. The direct wave arrival has been cropped from the top of the time axis. No gains are applied. Black boxes contain trace segments used in the initial wavelet calculation.

approximately 0.75 m along the GPR profile shown in Fig. 7). Two other distinctive hyperbolic patterns are seen in the data; these are created by tree roots. High-frequency noise is removed from the data by a simple low-pass filter removing frequencies greater than 2 GHz. Soil heterogeneities generate additional radar returns, especially visible around 6-ns two-way travel time.

Similar to the synthetic models, a background removal is applied and the computation of the initial wavelet does not

use the direct wave (before 4 ns, not shown). This is because the direct wave varies along the transect due to variations in soil moisture, surface roughness, and antenna-ground coupling (Fig. 7). This first arrival also falls in the near field of the antenna, and compensation for near-field effects is beyond the scope of this paper (in such settings, it would likely be more effective to estimate the optimum wavelet and reflectivities for each individual transmitter location separately, rather than estimating one best-fit wavelet for the whole data set, a topic also beyond the scope of this paper).

The initial wavelet is calculated by time shifting, stacking, and finally normalizing a few traces around the apex of each hyperbolic event shown in boxes in Fig. 7 (similar to the synthetic case). As for the “noisier” synthetic case, selection of the split Bregman parameters strongly influences results. Comparing Figs. 8 and 9, setting $\alpha = 0.001$ and $\beta = 0.5$ reduces the number of estimated reflectors ($\alpha = 0.01$ provided almost the same reflectivity and wavelet model as $\alpha = 0.001$.) In this latter case (Fig. 9), the hyperbolic shapes of the pipe and roots reflectors are recovered well with fewer reflectors placed earlier than 6 ns and later than the hyperbola arrivals. We stress that in this particular case, recovering the reflectivity model of cylindrical objects was the desired target, rather than soil heterogeneity. The overall shape of the source wavelet recovered with both parameter selections is similar (Figs. 8 and 9), but the latter model yields fewer noncylindrical target reflectors. We find that limiting the source wavelet length to just

63

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

JAZAYERI et al.: SBD OF GPR DATA

9

![img-52.jpeg](img-52.jpeg)

![img-53.jpeg](img-53.jpeg)

Fig. 9. (Top) Initial and final estimated wavelets for the data set shown in Fig. 7 with α = 0.001 and β = 0.5 (α = 0.01 provides very similar models). (Bottom) Corresponding estimated reflectivity model. The additional peak in the early part of the wavelet allows parts of the complexity in the data to be shifted from the reflectivity series to the wavelet.

![img-54.jpeg](img-54.jpeg)

Fig. 10. Wiener deconvolution reflectivity series for the real data in Fig. 7. The signature of the source wavelet is reduced but the reflectivity series still shows the residual wavelet, i.e., the difference between the actual wavelet and its minimum phase equivalent.

the main cycle (i.e., <4 ns length) generates an undesirable train of hyperbolas in the estimated reflectivity model.

Finally, we compare the performance of the SBD algorithm (Fig. 9) with Wiener deconvolution (Fig. 10). Wiener deconvolution assumes that the wavelet has minimum phase and that the reflectivity series is white noise. These assumptions are not satisfied in real-world GPR data, and as a result, the Wiener deconvolution is less effective at removing the effect of the

wavelet from the data. Although the recovered reflectivity series (Fig. 10) shows more focused events than the original data (Fig. 7), the series is smooth and lacks the high-resolution features present in the SBD reflectivity series (Fig. 9).

## V. CONCLUSION

The proposed SBD method is tested on synthetic and simple field GPR data. The method estimates the reflectivity model of the subsurface and the transmitted pulse shape efficiently and simultaneously without requiring any prior information from the subsurface or any assumption about the phase of the wavelet. The initial source wavelet estimate is made by extracting and averaging a subset of the data. The process then iteratively updates the reflectivity model and source wavelet. The method is tested on data sets with cylindrical targets and different noise levels. High-frequency noise alone is handled with the split Bregman algorithm parameters α = 0.5 and β = 1, while scenarios with more low-frequency noise and a complex pulse are better treated with α = 0.01 to 0.001 and β = 0.5. The hyperbolic shapes of the recorded signals are well recovered in the reflectivity models. In the synthetic models, the initial wavelet estimate is improved upon, and the final wavelet estimate is a good fit to the true wavelet.

For GPR studies, SBD can be useful for image resolution enhancement and better understanding of the source wavelet. Both the estimated source wavelet and reflectivity model can be used in further advanced modeling procedures such as FWI. Compensation for near-field signal propagation effects is a subject of future research.

## ACKNOWLEDGMENT

The authors would like to thank S. Esmaeili for assistance in making plots, and A. Ebrahimi for guidance and constructive discussions. They would also like to thank three anonymous reviewers and the associate editor who gave constructive reviews that greatly improved this paper.

## REFERENCES

[1] F. Sroubek and P. Milanfar, "Robust multichannel blind deconvolution via fast alternating minimization," IEEE Trans. Image Process., vol. 21, no. 4, pp. 1687-1700, Apr. 2012.

[2] A. Gholami and M. D. Sacchi, "A fast and automatic sparse deconvolution in the presence of outliers," IEEE Trans. Geosci. Remote Sens., vol. 50, no. 10, pp. 4105-4116, Oct. 2012.

[3] G. P. Angeleri, "A statistical approach to the extraction of the seismic propagating wavelet," Geophys. Prospecting, vol. 31, no. 5, pp. 726-747, 1983.

[4] R. E. Sheriff and L. P. Geldart, Exploration Seismology. Cambridge, U.K.: Cambridge Univ. Press, 1995.

[5] J. Xia, E. K. Franssen, R. D. Miller, T. V. Weis, and A. P. Byrnes, "Improving ground-penetrating radar data in sedimentary rocks using deterministic deconvolution," J. Appl. Geophys., vol. 54, nos. 1-2, pp. 15-33, 2003.

[6] N. Economou, A. Validis, H. Hamdan, G. Kritikakis, N. Andronikidis, and K. Dimitriadis, "Time-varying deconvolution of GPR data in civil engineering," Nondestruct. Test Eval., vol. 27, no. 3, pp. 285-292, 2012.

[7] N. Economou and A. Validis, "GPR data time varying deconvolution by kurtosis maximization," J. Appl. Geophys., vol. 81, pp. 117-121, Jun. 2012.

[8] I. Abdel-Qader, V. Krause, F. Abu-Amara, and O. Abudayyeh, "Comparative study of deconvolution algorithms for GPR bridge deck imaging," WSEAS Trans. Signal Process., vol. 10, no. 1, pp. 9-20, 2014.

64

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

10

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING

[9] V. Krause, “Blind source separation for feature detection and segmentation in ground penetrating radar (GPR) Imaging of concrete bridge decks for nondestructive condition assessment,” Dept. Elect. Comput. Eng., Western Michigan Univ., Kalamazoo, MI, USA, 2015.

[10] C. Schmelzbach and E. Huber, “Efficient deconvolution of ground-penetrating radar data,” IEEE Trans. Geosci. Remote Sens., vol. 53, no. 9, pp. 5209–5217, Sep. 2015.

[11] S. Zhao, P. Shangguan, and I. L. Al-Qadi, “Application of regularized deconvolution technique for predicting pavement thin layer thicknesses from ground penetrating radar data,” NDT E Int., vol. 73, pp. 1–7, Jul. 2015.

[12] D. Arosio, “Rock fracture characterization with GPR by means of deterministic deconvolution,” J. Appl. Geophys., vol. 126, pp. 27–34, Mar. 2016.

[13] J. Xiao and L. Liu, “Permalrost subgrade condition assessment using extrapolation by deterministic deconvolution on multifrequency GPR data acquired along the Qinghai-Tibet railway,” IEEE J. Sel. Topics Appl. Earth Observ. Remote Sens., vol. 9, no. 1, pp. 83–90, Jan. 2016.

[14] J. R. Ernst, A. G. Green, H. Maurer, and K. Holliger, “Application of a new 2D time-domain full-waveform inversion scheme to crosshole radar data,” Geophysics, vol. 72, no. 5, pp. 353–364, 2007.

[15] A. Klotzsche, J. van der Kruk, G. A. Melex, J. Doetsch, H. Maurer, and N. Linde, “Full-waveform inversion of cross-hole ground-penetrating radar data to characterize a gravel aquifer close to the Thur River, Switzerland,” Near Surf. Geophys., vol. 8, no. 6, pp. 635–649, 2010.

[16] S. Jazayeri, A. Klotzsche, and S. Kruse, “Improving estimates of buried pipe diameter and infilling material from ground-penetrating radar profiles with full-waveform inversion,” Geophysics, vol. 83, no. 4, pp. H27–H41, 2018, doi: 10.1190/geo2017-0617.1.

[17] N. Levinson, “The Wiener (root mean square) error criterion in filter design and prediction,” Stud. Appl. Math., vol. 25, nos. 1–4, pp. 261–278, Apr. 1946.

[18] E. A. Robinson, “Predictive decomposition of seismic traces,” Geophysics, vol. 22, no. 4, pp. 767–778, 1957.

[19] N. Ricker, “The form and laws of propagation of seismic wavelets,” Geophysics, vol. 18, no. 1, pp. 10–40, 1953.

[20] R. A. Wiggins, “Minimum entropy deconvolution,” Geosuplication, vol. 16, nos. 1–2, pp. 21–35, 1978.

[21] M. D. Sacchi and T. J. Ulrych, “Nonminimum-phase wavelet estimation using higher order statistics,” Lead. Edge, vol. 19, no. 1, pp. 80–83, 2000.

[22] K. F. Kaaresen and T. Taxi, “Multichannel blind deconvolution of seismic signals,” Geophysics, vol. 63, no. 6, pp. 2093–2107, 1998.

[23] N. Kazemi and M. D. Sacchi, “Sparse multichannel blind deconvolution,” Geophysics, vol. 79, no. 5, pp. V143–V152, 2014.

[24] N. Kazemi, E. Bougajum, and M. D. Sacchi, “Surface-consistent sparse multichannel blind deconvolution of seismic signals,” IEEE Trans. Geosci. Remote Sens., vol. 54, no. 6, pp. 3200–3207, Jun. 2016.

[25] N. Kazemi, “Blind deconvolution with Toeplitz-structured sparse total least squares algorithm,” in Proc. 50th EAGE Conf. Exhib., 2018, doi: 10.3997/2214-4609.201800882.

[26] K. Chahine, V. Baltazari, Y. Wang, and X. Dérobert, “Blind deconvolution via sparsity maximization applied to GPR data,” Eur. J. Environ. Civil Eng., vol. 15, no. 4, pp. 575–586, 2011.

[27] L. Li, “Sparsity-promoted blind deconvolution of ground-penetrating radar (GPR) data,” IEEE Geosci. Remote Sens. Lett., vol. 11, no. 8, pp. 1330–1334, Aug. 2014.

[28] E. A. Robinson and S. Treitel, Geophysical Signal Analysis, vol. 263. Upper Saddle River, NJ, USA: Prentice-Hall, 1980.

[29] A. Osen, B. G. Secrest, L. Amundsen, and A. Reitan, “Wavelet estimation from marine pressure measurements,” Geophysics, vol. 63, no. 6, pp. 2108–2119, 1998.

[30] R. L. Brown, W. McElhattan, and D. J. Santiago, “Wavelet estimation: An interpretive approach,” Lead. Edge, vol. 7, no. 12, pp. 16–19, 1988.

[31] E. Bianco, “Geophysical tutorial: Well-tie calculus,” Lead. Edge, vol. 33, no. 6, pp. 674–677, 2014.

[32] O. Shalvi and E. Weinstein, “New criteria for blind deconvolution of nonminimum phase systems (channels),” IEEE Trans. Inf. Theory, vol. 36, no. 2, pp. 312–321, Mar. 1990.

[33] D. R. Velis, “Stochastic sparse-spike deconvolution,” Geophysics, vol. 73, no. 1, pp. R1–R9, 2007.

[34] H. W. J. Debeye and V. P. Riel, “L$_{p}$-norm deconvolution,” Geophys. Prospecting, vol. 38, no. 4, pp. 381–403, 1990.

[35] J.-L. Starck, F. Murtagh, and J. M. Fadili, Sparse Image and Signal Processing: Wavelets, Curvelets, Morphological Diversity. Cambridge, U.K.: Cambridge Univ. Press, 2010.

[36] A. Repetti, M. Pham, L. Duval, E. Chouzenoux, and J.-C. Pesquet, “Euclid in a taxicab: Sparse blind deconvolution with smoothed $t_1/t_2$ regularization,” IEEE Signal Process. Lett., vol. 22, no. 5, pp. 539–543, May 2015.

[37] I. Selesnick, “Sparse deconvolution (an MM algorithm),” Connexions, 2012. [Online]. Available: https://goo.gl/mGDx7m

[38] M. A. T. Figueiredo, R. D. Nowak, and S. J. Wright, “Gradient projection for sparse reconstruction: Application to compressed sensing and other inverse problems,” IEEE J. Sel. Topics Signal Process., vol. 1, no. 4, pp. 586–597, Dec. 2007.

[39] T. Goldstein and S. Osher, “The split Bregman method for L1-regularized problems,” SIAM J. Imag. Sci., vol. 2, no. 2, pp. 323–343, 2009.

[40] G. Hennenfent, E. van den Berg, M. P. Friedlander, and F. J. Herrmann, “New insights into one-norm solvers from the Pareto curve,” Geophysics, vol. 73, no. 4, pp. A23–A26, 2008.

[41] D. O. Pérez, D. R. Velis, and M. D. Sacchi, “High-resolution prestack seismic inversion using a hybrid FISTA least-squares strategy,” Geophysics, vol. 78, no. 5, pp. R185–R195, 2013.

[42] G. Wabba, “The approximate solution of linear operator equations when the data are noisy,” Adv. Appl. Probab., vol. 8, no. 2, pp. 222–223, 1976.

[43] D. J. Cummins, T. G. Felloon, and D. Nychka, “Confidence intervals for nonparametric curve estimates: Toward more uniform pointwise coverage,” J. Amer. Stat. Assoc., vol. 96, no. 453, pp. 233–246, 2001.

[44] A. Ebrahimi, A. Gholami, and M. Nabi-Bidhendi, “Sparsity-based GPR blind deconvolution and wavelet estimation,” J. Ind. Geophys. Union, vol. 21, no. 1, pp. 7–12, 2017.

[45] C. Warren, A. Giannopoulos, and I. Giannakis, “gprMax: Open source software to simulate electromagnetic wave propagation for ground penetrating radar,” Comput. Phys. Commun., vol. 209, pp. 163–170, Dec. 2016.

![img-55.jpeg](img-55.jpeg)

Sajad Jazayeri received the B.Sc. degree in physics from Razi University, Kermanshah, Iran, in 2007, and the M.Sc. degree in geophysics from the University of Tehran, Tehran, Iran, in 2009. He is currently pursuing the Ph.D. degree with the Geophysics Group, University of South Florida, Tampa, FL, USA.

Since 2014, he has been with the School of Geosciences, University of South Florida. His research interests include full-waveform inversion, and modeling and imaging of geophysical data.

![img-56.jpeg](img-56.jpeg)

Nasser Kazemi received the B.Sc. degree in geology from the University of Tabriz, Tabriz, Iran, in 2007, the M.Sc. degree in geophysics from the University of Tehran, Tehran, Iran, in 2010, and the Ph.D. degree in geophysics from the University of Alberta, Edmonton, AB, Canada, in 2017.

From 2012 to 2017, he was with the Signal Analysis and Imaging Group, University of Alberta, where he was involved in seismic depth imaging and seismic signal processing. He also briefly collaborated with the Statoil ASA Research Group, Trondheim,

Norway, in 2014. In 2017, he joined the University of Calgary, Calgary, AB, Canada, as a Post-Doctoral Associate Researcher. He is the point person for integrating seismic and seismic-while-drilling imaging with the development and production workflows. His research interests include the signal analysis and seismic imaging.

Dr. Kazemi was a recipient of Canada First Research Excellence Fund Fellowship, University of Calgary.

![img-57.jpeg](img-57.jpeg)

Sarah Kruse is currently a Professor with the School of Geosciences, University of South Florida, Tampa, FL, USA. He is involved in ground penetrating radar applied to void detection, sinkhole hazards, and engineering targets. Her research interests include near-surface geophysics.

65

# **Appendix IV. Copyright permission from *IEEE* for use of this manuscript in  
dissertation**

66

Rightslink® by Copyright Clearance Center

1/10/19, 1:39 PM

RightsLink®

![img-58.jpeg](img-58.jpeg)

**Title:** Sparse Blind Deconvolution of Ground Penetrating Radar Data
**Author:** Sajad Jazayeri
**Publication:** Geoscience and Remote Sensing, IEEE Transactions on
**Publisher:** IEEE
**Date:** Dec 31, 1969
Copyright © 1969, IEEE

Logged in as:
Sajad Jazayeri
Account #:
3001390487

LOGOUT

### Thesis / Dissertation Reuse

**The IEEE does not require individuals working on a thesis to obtain a formal reuse license, however, you may print out this statement to be used as a permission grant:**

*Requirements to be followed when using any portion (e.g., figure, graph, table, or textual material) of an IEEE copyrighted paper in a thesis:*

1) In the case of textual material (e.g., using short quotes or referring to the work within these papers) users must give full credit to the original source (author, paper, publication) followed by the IEEE copyright line © 2011 IEEE.
2) In the case of illustrations or tabular material, we require that the copyright line © [Year of original publication] IEEE appear prominently with each reprinted figure and/or table.
3) If a substantial portion of the original paper is to be used, and if you are not the senior author, also obtain the senior author's approval.

*Requirements to be followed when using an entire IEEE copyrighted paper in a thesis:*

1) The following IEEE copyright/ credit notice should be placed prominently in the references: © [year of original publication] IEEE. Reprinted, with permission, from [author names, paper title, IEEE publication title, and month/year of publication]
2) Only the accepted version of an IEEE copyrighted paper can be used when posting the paper or your thesis on-line.
3) In placing the thesis on the author's university website, please display the following message in a prominent place on the website: In reference to IEEE copyrighted material which is used with permission in this thesis, the IEEE does not endorse any of [university/educational entity's name goes here]'s products or services. Internal or personal use of this material is permitted. If interested in reprinting/republishing IEEE copyrighted material for advertising or promotional purposes or for creating new collective works for resale or redistribution, please go to http://www.ieee.org/publications_standards/publications/rights/rights_link.html to learn how to obtain a License from RightsLink.

If applicable, University Microfilms and/or ProQuest Library, or the Archives of Canada may supply single copies of the dissertation.

BACK

CLOSE WINDOW

Copyright © 2019 Copyright Clearance Center, Inc. All Rights Reserved. Privacy statement, Terms and Conditions. Comments? We would like to hear from you. E-mail us at customercare@copyright.com

https://s100.copyright.com/AppDispatchServlet#formTop

Page 1 of 2

67

Rightslink® by Copyright Clearance Center

1/10/19, 1:39 PM

https://s100.copyright.com/AppDispatchServlet#formTop

Page 2 of 2

68