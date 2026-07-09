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