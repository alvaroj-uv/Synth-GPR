Computers & Geosciences 137 (2020) 104422

![img-0.jpeg](img-0.jpeg)

Contents lists available at ScienceDirect

Computers and Geosciences

journal homepage: www.elsevier.com/locate/cageo

![img-1.jpeg](img-1.jpeg)

Research paper

# 3D modeling of ground-penetrating radar data across a realistic sedimentary model

Philipp Koyan *, Jens Tronicke

Universität Potsdam, Institut für Geowissenschaften, Karl-Liebknecht-Straße 24-25, 14476 Potsdam, Germany

ARTICLE INFO

Keywords:

Applied geophysics
Ground-penetrating radar
3D modeling

ABSTRACT

Ground-penetrating radar (GPR) is an established geophysical tool to explore a wide range of near-surface environments. Today, the use of synthetic GPR data is largely limited to 2D because 3D modeling is computationally more expensive. In fact, only recent developments of modeling tools and powerful hardware allow for a time-efficient computation of extensive 3D data sets. Thus, 3D subsurface models and resulting GPR data sets, which are of great interest to develop and evaluate novel approaches in data analysis and interpretation, have not been made publicly available up to now.

We use a published hydrofacies data set of an aquifer-analog study within fluvio-glacial deposits to infer a realistic 3D porosity model showing heterogeneities at multiple spatial scales. Assuming fresh-water saturated sediments, we generate synthetic 3D GPR data across this model using novel GPU-acceleration included in the open-source software gprMax. We present a numerical approach to examine 3D wave-propagation effects in modeled GPR data. Using the results of this examination study, we conduct a spatial model decomposition to enable a computationally efficient 3D simulation of a typical GPR reflection data set across the entire model surface. We process the resulting GPR data set using a standard 3D structural imaging sequence and compare the results to selected input data to demonstrate the feasibility and potential of the presented modeling studies. We conclude on conceivable applications of our 3D GPR reflection data set and the underlying porosity model, which are both publicly available and, thus, can support future methodological developments in GPR and other near-surface geophysical techniques.

1. Introduction

Ground-penetrating radar (GPR) is a standard geophysical tool increasingly employed in various archeological, engineering, environmental, and geological applications (Knight, 2001; Bristow and Jol, 2003; Daniels, 2004; Lai et al., 2018). Within the field of GPR, synthetic data sets and the underlying models play an important role as they can serve, for example, to formulate suitable target-specific acquisition strategies (e.g., Samet et al., 2017; Liu et al., 2018), to reference novel data processing and analysis routines including data inversion (e.g., Paasche and Tronicke, 2007; Klotzsche et al., 2010), or to study GPR response to different saturation scenarios within sedimentary deposits (e.g., Kowalsky et al., 2001). In the seismic community, 3D models and resulting synthetic data sets are widely used; for example, the famous Marmousi model and its variants or the SEG/EAGE 3D salt and overthrust models (Versteeg, 1994; Aminzadeh et al., 1997) are actively utilized references to test and evaluate novel methodological ideas (e.g., Yang et al., 2014; Boehm et al., 2016; Métivier et al., 2016). However, up to now there are no publicly available reference models and data sets for GPR.

To simulate GPR data, numerous implementations typically relying on the Finite-Difference Time-Domain (FDTD) method have been proposed and continuously developed throughout the past decades (e.g., Bergmann et al., 1998; Irving and Knight, 2006; Millington and Cassidy, 2010). The open-source software gprMax (Warren et al., 2016) is a well-established and well-maintained tool, which delivers a highly flexible FDTD scheme to model GPR data. The computational effort to tackle FDTD modeling problems in a 3D fashion is highly demanding (especially regarding calculation time). Thus, the most recent development within gprMax can be considered as a quantum leap, because the software now features a GPU modeling engine (Warren et al., 2018). For the first time, the resulting speed-up allows time-efficient modeling of 3D GPR reflection data sets with typical constant-offset geometries (commonly consisting of thousands of single source positions) across 3D models comprising several millions of cells without the need of high-performance computing resources.

In sedimentary environments, high-resolution 3D GPR images facilitate a deeper understanding of depositional processes, tectonic activity

* Corresponding author.

E-mail addresses: koyan@uni-potsdam.de (P. Koyan), Jens@Geo.uni-potsdam.de (J. Tronicke).

https://doi.org/10.1016/j.cageo.2020.104422

Received 21 June 2019; Received in revised form 21 January 2020; Accepted 29 January 2020

Available online 3 February 2020

0098-3004/© 2020 Elsevier Ltd. All rights reserved.

P. Koyan and J. Tronicke

Computers and Geosciences 137 (2020) 104422

or the hydrogeological settings at a field site (e.g., Neal, 2004). However, throughout the whole range of sedimentological applications, the use of 3D GPR modeling (e.g., to improve near-surface characterization strategies) has not kept pace with the steady development of modeling tools and technologies. Hence, the publicly available hydrofacies data set resulting from an aquifer-analog study within a gravel quarry near the village of Herten in SW-Germany (Bayer et al., 2011; Comunian et al., 2011) poses an ideal basis to perform 3D GPR modeling across a realistic sedimentary environment. This data set comprises hydrogeological data (including porosity and hydraulic conductivity) and facies models, respectively, which describe heterogeneities within a volume of $16 \times 10 \times 7$ m (length $\times$ width $\times$ depth) dominated by sandy and gravelly fluvio-glacial deposits.

In this study, we make use of the novel GPU engine in gprMax to generate extensive 3D GPR data across a realistic 3D sedimentary model. Therefore, we use the Herten data set to derive a porosity model showing realistic variations down to the sub-facies scale. Assuming fresh-water saturated sediments, this porosity model then is translated into a model comprising fundamental electrical subsurface parameters. After introducing our modeling setup, we propose an approach to examine 3D effects in synthetic GPR data. Considering the results of this examination study, we conduct a spatial model decomposition in order to perform a computationally efficient 3D modeling of a typical GPR reflection data set across the entire model surface. To analyze this data set, we apply a standard 3D GPR processing sequence including the analysis of a synthetic common-midpoint experiment and evaluate our results by a direct comparison to the input model. Finally, we present our conclusions and discuss the further use of our synthetic GPR reflection data set and our porosity model, which are both publicly available (Koyan and Tronicke, 2019).

## 2. Data base and model preparation

In this section, we introduce and present the Herten data set. Furthermore, we outline the derivation of our porosity model and its transformation into the electrical parameter models which are used as input for modeling 3D GPR data.

### 2.1. Hydrofacies and porosity model

As starting point, we use a high-resolution 3D hydrofacies data set resulting from an aquifer-analog study within fluvio-glacial deposits. Here, we only give a brief overview of the steps performed to obtain this data set and summarize the most striking sedimentary features therein. For a detailed description of the underlying field work, the mapping procedure, and the sedimentological interpretation, we refer to Bayer et al. (2011). A precise portrayal of the applied 3D geostatistical modeling is presented by Comunian et al. (2011).

The 3D data set comprises hydrogeological properties and their spatial distributions within a well-described gravel quarry near the village of Herten (SW-Germany). There, mainly poorly to well-sorted sand and gravel sequences formed in a braided-river regime characterize the subsurface. The data set originates from six parallel digitized outcrop images with a lateral distance of 2 m between individual images. Supported by sedimentary mapping performed during excavation (Bayer, 2000), these images are interpreted in terms of lithological facies resulting in six 16 m wide rasterized 2D facies sections. These sections cover a depth range of 7 m and show a resolution of 0.05 m. Laboratory measurements of facies-specific hydrogeological properties including porosity $\Phi$ and hydraulic conductivity $K$ lead to a subdivision of the mapped lithological facies into 10 different variants, termed hydrofacies. Comunian et al. (2011) use these 2D hydrofacies sections to perform geostatistical modeling resulting in 3D realizations of the local subsurface architecture with a resolution of 0.05 m in all spatial dimensions which these authors provide as supplementary material.

![img-2.jpeg](img-2.jpeg)

Fig. 1. 3D view across the Herten hydrofacies model used as starting point in this work ('Realization 1' of Comunian et al., 2011). Details on the hydrofacies code are provided in Table 1.

In Fig. 1, we visualize the 3D hydrofacies model used in this work ('Realization 1' of Comunian et al., 2011) and also introduce our coordinate system. The hydrofacies code is based on a convention from Bayer et al. (2011) compiled from Keller (1996) and Heinz and Aigner (2003). In Table 1, we support the understanding of this model by a brief description of the different hydrofacies including their representative porosity values and the associated porosity ranges as compiled by Bayer et al. (2011). Combining the representative porosity values and the 3D hydrofacies model yields a representative 3D porosity model for the Herten site of which we show a typical 2D slice at $y = 6$ m in Fig. 2a. Figs. 1 and 2a illustrate that the local subsurface exhibits a highly heterogeneous 3D architecture showing numerous sedimentary features on the cm- to m-scale including corresponding porosity variations.

Referring to Figs. 1 and 2a, we discuss the most prominent sedimentary features and the associated porosity variations. The model is capped by typical accretionary structures down to a depth of $-1$–$2$ m. These structures are formed by a thin, continuous gravel layer with a sand-rich matrix (sGcm) showing the overall smallest porosity values embedded in a minimally less condensed facies with a cobble-rich matrix (cGcm). Directly underneath, we identify cut-and-fill sequences showing an alteration of highly porous, gently dipping open-framework gravels (Gcg,o and sGcg,o) and less porous sand-gravel mixtures (mainly sGcm,b). A comparable depositional structure can be found at depths around 4 m (up to $x \approx 12$ m) where it overlays an up to 1 m thick body accommodating the globally most porous well-sorted gravels and sands (GS-x and S-x). In the deeper parts of the model, beneath the well-sorted sand-gravel body and the cut-and-fill sequences, the model again exhibits typical accretionary structures dominated by the least porous, matrix-supported gravels (Gcm and its variants). In this context, we observe thin, partially discontinuous and (sub)-horizontal to gently dipping layers which locally exhibit a sequentially graded bedding. These layers include highly porous open-framework gravels (Gcg,o and its variants) as well as small portions of the most porous, well-sorted sands (S-x). This results in local high-wavenumber, high-magnitude porosity variations in the lowermost parts of the model.

The representative porosity model in Fig. 2a shows considerable multi-scale and multi-magnitude variations. However, up to now we assume that each hydrofacies shows uniform properties throughout the entire model and therefore is characterized by a single representative porosity value. To generate a more realistic porosity distribution in view of modeling realistic GPR data, we upgrade the representative porosity model (Fig. 2a) by introducing heterogeneities at the sub-facies scale. As no deterministic information on the spatial distribution and correlation of heterogeneities within each hydrofacies are available, we

2

P. Koyan and J. Trunicke

Computers and Geosciences 137 (2020) 104422

Table 1
Description of hydrofacies code used in Fig. 1 as well as representative porosity values and associated ranges (Bayer et al., 2011). Porosity ranges marked by * assumed for this work (no data provided).

|  Hydrofacies code | Description (details) | Porosity Φ (range)  |
| --- | --- | --- |
|  Gcm | Poorly sorted, matrix-supported gravel (normal) | 0.17 (± 0.07)  |
|  cGcm | Poorly sorted, matrix-supported gravel (cobble-rich) | 0.15 (± 0.01)  |
|  sGcm | Poorly sorted, matrix-supported gravel (sand-rich) | 0.13 (± 0.04)  |
|  Gcg,o | Alternating gravel (matrix-free, clast-supported open framework, coarse-fine pebbles) | 0.26 (± 0.02)  |
|  cGcg,o | Alternating gravel (cobbles-coarse pebbles, open framework) | 0.26 (± 0.02)  |
|  sGcg,o | Alternating gravel (granules/sand, open framework) | 0.23 (± 0.01)*  |
|  sGcm,b | Alternating gravel (bimodal basal sub-unit with sand matrix) | 0.22 (± 0.01)*  |
|  fGcm,b | Alternating gravel (bimodal basal sub-unit with silt/clay matrix) | 0.20 (± 0.01)*  |
|  GS-x | Well sorted gravel (and coarse sand) | 0.27 (± 0.07)  |
|  S-x | Pure, well sorted sand | 0.36 (± 0.04)  |

take advantage of the fact that a wide range of petrophysical properties within sedimentary deposits shows fractal characteristics (e.g., Walden and Hosken, 1985; Desbarats and Bachu, 1994). To consider this, we use the popular exponential covariance model characterized by a commonly observed ratio between vertical and horizontal correlation length of 1:10 (e.g., Gelhar, 1993) to simulate an independent, spatially correlated 3D random field with a Gaussian probability density function for each of the 10 hydrofacies. We perform the numerical realization utilizing the turning bands algorithm of Emery and Lantuéjoul (2006) allowing for an efficient calculation of such random fields. We scale the 10 resulting 3D random fields using the porosity ranges listed in Table 1 and add the results to the representative porosity model (Fig. 2a) considering the spatial appearance of the respective hydrofacies. In the following, we limit the precision of this porosity model to three decimal places. Thus, we restrict the number of different porosity values in the model and therefore the amount of different property values in the resulting electrical parameter models which is a prerequisite for an efficient GPR modeling procedure (Section 3). In Fig. 2b, we visualize our resulting porosity model at the same 2D slice as in Fig. 2a. Fig. 3 illustrates the associated porosity distribution for the entire 3D model as hydrofacies-specific histogram plots. These plots are normalized to the total number of porosity values and give an impression of the relative portions of the individual hydrofacies found in the model. Analyzing Figs. 2b and 3 illustrates that the porosity values within each hydrofacies now exhibit a commonly observed spatial correlation structure, and are also characterized by a Gaussian distribution whose mean value, standard deviation, and minimum/maximum values depend on the associated representative porosity value and range as listed in Table 1.

### 2.2. Electrical parameter models and discretization

Fundamental electrical properties affecting the propagation of electromagnetic waves are (1) the dielectric permittivity $\varepsilon = \varepsilon_r\varepsilon_0$, where $\varepsilon_r$ is the material dependent dielectric constant and $\varepsilon_0$ the dielectric permittivity of free space, (2) the electrical resistivity $\rho$, (3) the magnetic loss $\sigma^*$, and (4) the magnetic permeability $\mu = \mu_r\mu_0$, where $\mu_r$ and $\mu_0$ are the material dependent relative magnetic permeability and the magnetic permeability of free space, respectively. Due to the absence of magnetic materials in our model, we fix the magnetic permeability to the value of free space (i.e., $\mu_r = 1$) and assume no magnetic loss (i.e., $\sigma^* = 0$). For this modeling study being a first attempt toward modeling extensive 3D GPR data, we use first-order realistic media; i.e., we basically assume frequency-independent electrical parameters. Furthermore, we only consider fresh-water saturated sediments. This allows us to use standard two-component mixture models without any further assumptions on the material characteristics (not available for the Herten field site) to translate our porosity model (Fig. 2b) into $\varepsilon_r$ and $\sigma$, respectively (e.g., Tronicke and Holliger, 2005). More specifically, we obtain a model of $\varepsilon_r$ using the two-component formulation of the complex refractive index model (CRIM; e.g., Roth et al., 1990; Zakri et al., 1998):

$$\varepsilon_r = \left( (1 - \Phi) \sqrt{\varepsilon_{r,m}} + \Phi \sqrt{\varepsilon_{r,m}} \right)^2. \tag{1}$$

![img-3.jpeg](img-3.jpeg)

![img-4.jpeg](img-4.jpeg)

![img-5.jpeg](img-5.jpeg)

![img-6.jpeg](img-6.jpeg)

Fig. 2. Typical 2D profile slices at $\gamma = 6$ m of (a) porosity model with representative values from Table 1, (b) our porosity model including spatially correlated heterogeneities at the sub-facies scale, (c) GPR velocity model derived from (b) assuming fresh-water saturated sediments, and (d) electrical resistivity model derived from (b) assuming fresh-water saturated sediments.

3

P. Koyan and J. Tronicke

Computers and Geosciences 137 (2020) 104422

![img-7.jpeg](img-7.jpeg)

Fig. 3. Hydrofacies-specific porosity values as histogram plots illustrating the porosity distribution for the entire 3D model after adding spatially correlated heterogeneities at the sub-facies scale. Plots are normalized to the total number of porosity values in our model.

Here, $\epsilon_{r,w}$ is the dielectric constant of the dry matrix and $\epsilon_{r,w}$ that of fresh water, which we set to typical values of 6.9 and 80, respectively (e.g., Kowalsky et al., 2001). To obtain a model of $\rho$, we use a formulation of the well-known Archie's equation for fresh-water saturated media (Archie, 1942):

$$\rho = \rho_w \left( \frac{a}{d^m} \right). \quad (2)$$

Here, we set the electrical resistivity of the fresh water $\rho_w$ to a typically observed value of 25 $\Omega$m, and use for the empirical parameters $a$ and $m$ average values for unconsolidated sand of 0.88 and 1.37, respectively (Schön, 1998). For a better hands-on interpretation in terms of GPR wave propagation, we translate $\epsilon_r$ into GPR velocity $v$ using $v = c_0/\sqrt{c_1}$ with $c_0$ being the speed of light in vacuum. In Fig. 2c, we show a selected 2D slice of the resulting 3D GPR velocity model. In Fig. 2d, we visualize the same 2D slice in terms of electrical resistivity as calculated using Eq. (2). The electrical parameter distributions predominantly show GPR velocity values between 0.07 and 0.085 $m/s$ and electrical resistivity values between 150 and 350 $\Omega$m. Within the most porous well-sorted sands and gravels (S-x, GS-x) and the least porous matrix-supported gravels (Gcm and its variants), we observe extreme values down to $v \approx 0.06$ $m/s$ and $\rho \approx 80$ $\Omega$m and up to $v \approx 0.095$ $m/s$ and $\rho \approx 500$ $\Omega$m, respectively. Comparable values and associated variations of electrical properties are commonly observed in similar fresh-water saturated environments (e.g., Klotzsche et al., 2010; Hamann and Tronicke, 2014) and thus, we consider that our electrical parameter models closely resemble a typical sedimentary subsurface scenario.

The model discretization is a fundamental property of input models for FDTD GPR modeling. A rule-of-thumb typically applied to obtain adequate modeling results is that the discretization should be around ten times smaller than the smallest wavelength of the propagating electromagnetic wave field (Kunz and Luebbers, 1993). This wavelength depends on the minimum GPR velocity and the maximum frequency of the propagating waves, which is approximately 2–3 times as high as the nominal center frequency $f_c$ of a typical broad-band GPR signal. For the chosen saturation scenario, we observe GPR velocities down to $\sim 0.06$ $m/s$ (compare Fig. 2c). For our modeling study, we choose a nominal center frequency $f_c = 100$ MHz typically employed in comparable sedimentological field applications (e.g., Beres et al., 1995). Thus, we determined a discretization of 0.025 m in all spatial dimensions for the given modeling situation, which has been realized in every model presented in this work (starting with a nearest neighbor interpolated version of the hydrofacies model as shown in Fig. 1).

### 3. 3D GPR modeling

In this section, we briefly introduce the modeling tool gprMax as well as the key input parameters for 3D GPR modeling based on the subsurface scenario described in Section 2.2. Furthermore, we discuss a numerical approach to examine 3D effects within modeled GPR data and present the modeling strategy used to produce our synthetic 3D GPR reflection data set.

#### 3.1. Modeling software and basic parameters

gprMax is open-source software to simulate the propagation of electromagnetic waves using the Finite-Difference Time-Domain (FDTD) method (Warren et al., 2016). This software is employed in a diverse range of applications; for example, to study GPR wave propagation in lossy environments (Loewer and Igel, 2016), to investigate the potential of GPR for landmine detection (Giannakis et al., 2016), or as a forward solver to inverse problems like full-waveform inversion of cross-hole GPR data (van der Kruk et al., 2018). Due to the nature of FDTD modeling schemes, especially 3D simulations require extensive computational resources in terms of processing time. A recent development within gprMax tackles this problem as the software now offers the possibility to model on graphics processing units (GPUs) within NVIDIA's CUDA-framework. As a result, calculations are now performed up to 30 times faster compared to a multi-core desktop CPU using OpenMP parallelization (Warren et al., 2018). For the first time, this allows to model large and thus complex 3D GPR data sets consisting of thousands of single traces based on 3D subsurface models with millions of cells on a well-equipped work station without the need of costly high-performance computing resources. Here, we exploit this GPU-acceleration using gprMax v.3.1.4 to perform extensive 3D GPR modeling using our realistic model of subsurface sedimentary heterogeneities.

In the following, we introduce the key modeling parameters used in this work, whereas study-specific parameters are introduced where applied. As input, we set up a 3D model comprising the distributions of $\epsilon_r$ and the electrical conductivity $\sigma = 1/\rho$ associated with the distributions of $v$ and $\rho$ shown in Fig. 2c–d. As discussed in Section 2.2, our model shows a discretization of 0.025 m and we assume $\sigma^* = 0$ and $\mu_r = 1$. Above the subsurface model, we insert an air layer (i.e., a material with $\epsilon_r = 1$, $\sigma = 0$, $\sigma^* = 0$, and $\mu_r = 1$) with a thickness of 0.5 m. The thickness of the Perfectly Matched Layers (PMLs), which realize the absorbing boundary conditions, is set to 0.25 m in all spatial dimensions.

Up to now, no realistic antenna model with our desired nominal center frequency (i.e., $f_c = 100$ MHz) is available in gprMax. Hence, we assume a Hertzian dipole source, polarized perpendicular to the inline ($x$) direction, emitting a Ricker wavelet with unit amplitude. Considering both, our GPR velocity distribution (Fig. 2c) and the maximum depth of the model, we infer a time window of $t = 200$ ns. The sampling interval $\Delta t \approx 0.048$ ns directly results from the model discretization considering the 3D stability condition for the FDTD method. We place all GPR sources/receivers on the air-subsurface boundary. For modeling GPR profiles, we realize a constant-offset GPR reflection geometry commonly employed in sedimentological applications, with a source-receiver offset of 0.5 m and an inline trace spacing of 0.05 m.

#### 3.2. Examination of 3D effects

Having at hand both, a realistic 3D model of sedimentary heterogeneities and a modeling software allowing for efficient calculation of 3D electromagnetic wave fields, offers an up to now unique possibility to study 3D effects. Here, the term 3D effects comprises any phenomena related to energy originating from out-of-plane of a GPR profile acquired with a typical 2D constant-offset geometry. The following numerical approach allows us to assess and evaluate such 3D effects.

4

P. Koyan and J. Tronicke

Computers and Geosciences 137 (2020) 104422

![img-8.jpeg](img-8.jpeg)

Fig. 4. Modeling setup used to examine 3D effects in our simulated GPR data. Here, we display the case $\Delta y_{3D} = 2$ m at the study location $x/y = 5/5$ m in terms of GPR velocity; i.e., 3D structures extend 2 m in $y$ direction to each side of a GPR profile located in the center part of the model sub-cuboid. Air layer and PMLs not shown for simplicity. (For interpretation of the references to color in this figure legend, the reader is referred to the web version of this article.)

First, we select three locations in our model at $x/y = 5/5$, $8/6$, $10/4$ m around which we extract 3D sub-cuboids from the model with a size of $8 \times 8 \times 7$ m ($x, y, z$). In the center of each sub-cuboid, we place a GPR profile with a length of 1 m (i.e., 21 traces), which is oriented along the $x$ direction (Fig. 4). This results in a minimum distance of 4 m in $y$ direction between any GPR source/receiver and the boundary of the model domain enclosing each sub-cuboid. We start with modeling GPR data across these sub-cuboids fully containing 3D structures over a distance of $\Delta y_{3D} = 4$ m in $y$ direction. Then, we iteratively decrease the extent of 3D structures to each side of the GPR profile (i.e., $\Delta y_{3D}$) by steps of 0.25 m while keeping each model domain at constant size of $8 \times 8 \times 7$ m. For each step, we fill the remaining cells using replicates of the respective outermost 2D ($x-z$) planes where 3D structures are found. This is repeated for each sub-cuboid until reaching the 2.5D case ($\Delta y_{3D} = 0$); i.e., a 3D model domain only comprising the 2D subsurface structures found directly beneath the GPR profile. In Fig. 4, we illustrate this procedure by showcasing the modeling setup for the sub-cuboid around the study location $x/y = 5/5$ m for $\Delta y_{3D} = 2$ m; i.e., the case in which 3D structures, here shown in terms of GPR velocity, extend 2 m on each side of the GPR profile (air layer and PMLs not shown for simplicity).

To assess 3D effects in the modeled GPR profiles, we evaluate root mean square (rms) amplitudes. At each of the three locations and for every $\Delta y_{3D}$, we calculate the rms amplitude of each trace in a 170 ns time window (starting at 30 ns to suppress any effects related to high-energy direct arrivals), and average the resulting 21 rms values of each GPR profile. Fig. 5 shows these averaged rms values calculated for each simulated GPR profile as a function of $\Delta y_{3D}$ at every of the three locations. To ease the interpretation, the mean rms values are normalized to the according value calculated for $\Delta y_{3D} = 4$ m at each study location (i.e., the associated sub-cuboid completely contains 3D structures).

When analyzing Fig. 5, we see that our modeled GPR data exhibit 3D effects. At each study location, this becomes clear as for $\Delta y_{3D}$ larger than $\sim 1.5$ m, the normalized mean rms values show a high stability (i.e., no significant deviations compared to the case $\Delta y_{3D} = 4$ m), whereas with decreasing $\Delta y_{3D}$ these values show a considerable scatter with deviations up to $\sim 25$ % related to 3D effects absent in the underlying GPR data. Hence, for the given subsurface model and GPR

![img-9.jpeg](img-9.jpeg)

Fig. 5. Examination of 3D effects at three study locations. Mean rms amplitude values of each GPR profile as a function of $\Delta y_{3D}$. Values are normalized to the according rms value observed for $\Delta y_{3D} = 4$ m at each study location.

parameter configuration we conclude that (1) simulating GPR data in a 3D fashion is indispensable to fully capture 3D wave-propagation phenomena, and (2) the major source of reflected energy present in the GPR data extends $\sim 1.5$ m in crossline direction of a GPR profile.

### 3.3. Modeling strategy

To formulate a suitable strategy for modeling our extensive 3D GPR reflection data set, we consider the findings from Section 3.2 as well as the required RAM (commonly a limiting factor on GPUs) and calculation time, which both depend on the number of cells in a model domain. Accordingly, we decompose the full 3D model into three separate, equally sized sub-cuboids. These include the full $x$ and $z$ dimensions of the model and range from $y = 0-6$ m, $2-8$ m and $4-10$ m; i.e., the sub-cuboids show an overlap of 4 m in $y$ direction. Using these sub-cuboids, we model a total of 51 GPR profiles along the full $x$ dimension and with a crossline trace spacing of 0.2 m from $y = 0-4$ m, between $y = 4-6$ m, and from $y = 6-10$ m, respectively. Thus, we assure a minimum distance of 2 m in $y$ direction between the GPR profiles and the border of 3D structures within each sub-cuboid wherever applicable. Consequently, considering the analyses of Fig. 5, we assume that our modeled GPR data show a maximum of 3D character though using three separate model sub-cuboids. To assure that each GPR source/receiver is located at an adequate distance from every domain border, we additionally pad the sub-cuboids in the horizontal directions by 0.5 m (where necessary) using replicates of the outermost 2D ($x-z$ and $y-z$) planes.

A result of this modeling strategy is the uni-dimensional reduction in model domain size which, in turn, linearly decreases the calculation time. Moreover, our strategy ensures that each of the three sub-cuboids fits onto a single GPU RAM and enables us to use three NVIDIA GPUs (1x GeForce GTX1070, 2x Tesla K80, hosted by different workstations) to split the calculation tasks (i.e., one model sub-cuboid per GPU). The simultaneous use of three GPUs again decreases the overall calculation time significantly. Consequently, the complete simulation task comprising a total of 15810 traces has been performed within approximately one month. In Table 2, we sum up the key parameters characterizing our 3D GPR reflection data set, which we obtain by merging the three data sets individually simulated across the model sub-cuboids.

Common field practice is to complement constant-offset GPR data sets by performing experiments with a common-midpoint (CMP) geometry at selected locations. An analysis of GPR reflections observed within a CMP gather yields an estimate of the subsurface GPR velocity model which then, for example, can be used for migration of the corresponding constant-offset GPR reflection data set. Thus, we simulate a

5

P. Koyan and J. Tronicke

Computers and Geosciences 137 (2020) 104422

a)

![img-10.jpeg](img-10.jpeg)

b)

![img-11.jpeg](img-11.jpeg)

c)

![img-12.jpeg](img-12.jpeg)

Fig. 6. Typical 2D profile slices at y = 6 m of (a) unprocessed 3D GPR reflection data set, (b) 3D processed GPR depth image, and (c) same as (b) with GPR velocity model (Fig. 2c) as transparent overlay.

CMP gather with a center location at x/y = 8/8 m across the according 3D model sub-cuboid ranging from y = 4–10 m. This CMP gather is modeled along the x direction with a trace interval of 0.05 m and shows a maximum source-receiver offset of 5 m.

#### 4. Results and interpretation

In this section, we present and interpret the results of our 3D GPR modeling exercise based on a realistic sedimentary subsurface scenario (Fig. 2c–d) and discuss some of many conceivable applications

6

P. Koyan and J. Trunicke

Computers and Geosciences 137 (2020) 104422

Table 2
Key parameters describing our simulated 3D GPR reflection data set, which comprises a total of 15810 traces (51 profiles, 310 traces each).

|  Parameter | Value  |
| --- | --- |
|  Input model size (x, y, z) | 16 × 10 × 7 m  |
|  Input model discretization | 0.025 m  |
|  Sampling interval | ~0.048 ns  |
|  Time window | 200 ns  |
|  Nominal center frequency | 100 MHz  |
|  Source-receiver offset | 0.50 m  |
|  Inline trace spacing | 0.05 m  |
|  Crossline trace spacing | 0.20 m  |

when having at hand both, a realistic 3D subsurface model and the corresponding modeled GPR reflection data.

In Fig. 6a, we show a representative 2D slice of the unprocessed 3D GPR data (along the same profile shown in Fig. 2). This modeling result reveals that the multi-scale and multi-magnitude heterogeneities within the underlying electrical parameter fields result in GPR data with a realistic appearance and character. Beyond the high-energetic direct arrivals dominating travel times up to ~30 ns, we notice a large variety of commonly observed reflection patterns ranging from (semi-)continuous reflection structures to complex diffraction and interference phenomena.

To provide a typical GPR depth image (as expected in a corresponding field study), we apply a standard 3D GPR processing sequence including time zero correction, removal of direct arrivals, frequency filtering, 3D Kirchhoff migration and amplitude scaling (e.g., Allroggen et al., 2015; Schennen et al., 2016). As an example for the further use of our 3D model and following common field practice, we generated a CMP gather (Section 3.3) to estimate a subsurface GPR velocity model for our Kirchhoff migration. Fig. 7a–b illustrate the result of a reflection-based spectral velocity analysis and the underlying modeled CMP gather, respectively. Hence, considering typical uncertainties of such analyses (e.g., Hamann et al., 2013), we conclude that a constant GPR velocity of  \( 0.085 \, m/s \)  characterizes the subsurface velocity field. This is in well agreement with the GPR velocities present in the model (compare Fig. 2c) and thus, this constant velocity is used to perform the 3D Kirchhoff migration and the time-to-depth conversion of our data.

From the resulting 3D GPR depth image we extract the same profile shown in Fig. 6a and present it in Fig. 6b. To emphasize the 3D character of the GPR depth image, we visualize it in Fig. 8 using the same perspective display chosen for the hydrofacies model shown in Fig. 1. Comparing unprocessed and processed data reveals that diffracted energy (visible as hyperbolic events in Fig. 6a) has been collapsed and spatial positions of reflections have been corrected in the course of 3D migration. In the GPR depth image, we clearly recognize sedimentary structures such as the shallow accretionary elements (hydrofacies sGcm embedded within Gcm) imaged by a slightly undulating reflection, or the cut-and-fill sequences in the central part of the model (shown in yellow and green colors in Fig. 1) marked by gently dipping reflection patterns striking in y direction. Although a detailed interpretation of these results is beyond the scope of this work, we highlight the unique possibility to obtain a deeper understanding on the relations between subsurface structures within a realistic sedimentary scenario and the resultant reflection patterns in GPR images. To demonstrate this, we show in Fig. 6c the GPR depth slice of Fig. 6b together with the input GPR velocity model (equivalent to Fig. 2c) as transparent overlay. Fig. 6c emphasizes that (1) our GPR data are in good agreement with the input model, and (2) especially shallow, large-scale features like (semi-)horizontal interfaces as well as dipping structures (e.g., above, within, and beneath the cut-and-fill sequences) have been accurately imaged according to their depth, shape, dip, and spatial extend (compare Figs. 1 and 8). Though, (3) we also notice effects of decreasing resolution with increasing depth inherent for the GPR method. This can be observed at features whose extend is beyond local GPR resolution; for

![img-13.jpeg](img-13.jpeg)

Fig. 7. (a) Result of a reflection-based spectral velocity analysis of (b) synthetic CMP gather with a center location at x/y = 8/8 m modeled along the x direction. (For interpretation of the references to color in this figure legend, the reader is referred to the web version of this article.)

![img-14.jpeg](img-14.jpeg)

Fig. 8. 3D view across processed GPR depth image. For comparability, we use the same perspective display chosen for the hydrofacies model in Fig. 1.

example, in regions where small-scale GPR velocity variations evoked by high-wavenumber, high-magnitude porosity variations (Section 2.1) occur. Those features are repeatedly found in the deeper parts of the model and produce complex interference phenomena which, in turn, entail fragmentary reflection patterns, and thus complicate a standard reflection-based interpretation.

## 5. Conclusions

We have demonstrated the viability of modeling extensive 3D GPR data based on a realistic sedimentary subsurface scenario. We used

7

P. Koyan and J. Tronicke

Computers and Geosciences 137 (2020) 104422

publicly available hydrofacies data from an aquifer-analog study to infer a realistic, high-resolution 3D porosity model, which exhibits heterogeneities down to the sub-facies scale. Recent developments within open-source electromagnetic modeling software gprMax (now including time-efficient GPU-accelerated solvers) allowed us to extensively model 3D GPR data across such a large and realistic sedimentary model for the first time. We have proposed a numerical approach to obtain a deeper understanding of 3D effects in modeled GPR data. The results of this study have been considered when performing a spatial decomposition of the model in order to enable a computationally efficient 3D modeling of an extensive GPR reflection data set. The application of a standard 3D GPR processing sequence including the analysis of a 3D modeled common-midpoint experiment provided a realistic, high-resolution structural depth image. Our results are in good agreement with the input model thus demonstrating the feasibility and the potential of our modeling studies.

The subsurface model exhibits a large variety of realistic sedimentary features at different spatial scales. This includes thin, quasi-continuous interfaces as well as dipping layer sequences showing subtle to strong electrical parameter contrasts. Especially at greater depths, the resulting GPR reflection data show numerous fragmented reflection elements and interference patterns which make them, together with the model, a challenging and thus ideal target and reference to test and evaluate novel (3D) GPR processing and interpretation methods. For example, this may include the evaluation of amplitude scaling strategies, filtering, migration, or deconvolution algorithms as well as benchmarking innovative techniques aiming at a quantitative amplitude interpretation (e.g., to infer geophysical subsurface parameters), or the investigation of different interpretation approaches of structural GPR images. The provided porosity model can form a basis to generate complementary data sets using different GPR frequencies and source types, acquisition geometries (as indicated by our CMP example), and/or using additional geophysical exploration methods (electrical resistivity tomography, electromagnetic induction etc.) to formulate and reference approaches of an integrated geophysical interpretation. Moreover, this subsurface model can be adjusted and perturbed in a study-specific manner; for example, to explore different saturation scenarios (e.g., when combined with realistic subsurface flow models), to investigate effects of higher-order realistic media (e.g., by incorporating frequency-dependent properties using a Debye relaxation model), or to study the detectability of objects such as unexploded ordnance (UXO) or utility pipes buried within a realistic sedimentary background. In conclusion, we expect our 3D modeling studies as well as our publicly available GPR reflection data set and porosity model to pose a beneficial input to the research community.

### Data and computer code availability

Data associated with this article as well as basic Matlab and python code to read and visualize these data can be found at http://dx.doi.org/10.17632/by3yh79hx4.1, an open-source online data repository hosted at Mendeley Data (Koyan and Tronicke, 2019). The 3D GPR modeling presented in this work has been performed using gprMax v.3.1.4, an open-source electromagnetic modeling software (Warren et al., 2016, 2018) which can be found at https://github.com/gprmax/gprMax.

### Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

### CRediT authorship contribution statement

**Philipp Koyan:** Formal analysis, Investigation, Methodology, Visualization, Writing - original draft, Writing - review & editing. **Jens Tronicke:** Conceptualization, Methodology, Supervision.

### Acknowledgments

The authors would like to thank Marco Ende for providing additional computational resources to speed up the calculations. Additionally, we want to thank three anonymous reviewers for their helpful suggestions and comments. This work has been funded by the Deutsche Forschungsgemeinschaft (DFG), Germany under grant TR512/10-1.

### References

Allroggen, N., Tronicke, J., Delock, M., Böniger, U., 2015. Topographic migration of 2D and 3D ground-penetrating radar data considering variable velocities. Near Surface Geophys. 13 (3), 253–259. http://dx.doi.org/10.3997/1873-0604.2014037.
Aminzadeh, F., Brac, J., Kunz, T., 1997. 3D Salt and overthrust models. In: SEG/EAGE Modeling Series, No 1: Distribution CD of Salt and Overthrust Models.
Archie, G.E., 1942. The electrical resistivity log as an aid in determining some reservoir characteristics. Trans. AIME 146 (01), 54–62. http://dx.doi.org/10.2118/942054-G.
Bayer, P., 2000. Aquifer-Analog-Studie in großkläutischen "braided-river" Ablagerungen: Sedimentäre/hydrogeologische Wandkartierung und Kalibrierung von Georadarmessungen. In: Diploma Mapping Campaign. Universität Tübingen.
Bayer, P., Huggenberger, P., Renard, P., Comunian, A., 2011. Three-dimensional high resolution fluvio-glacial aquifer analog: Part 1: Field study. J. Hydrol. 405 (1–2), 1–9. http://dx.doi.org/10.1016/j.jhydrol.2011.03.038.
Beres, M., Green, A., Huggenberger, P., Hatzmeyer, H., 1995. Mapping the architecture of glaciofluvial sediments with three-dimensional georadar. Geology 23 (12), 1087–1090. http://dx.doi.org/10.1130/0091-7613(1995)023<1087:MTAOGS>2.3.CO;2.
Bergmann, T., Robertson, J.O., Holliger, K., 1998. Finite-difference modeling of electromagnetic wave propagation in dispersive and attenuating media. Geophysics 63 (3), 856–867. http://dx.doi.org/10.1190/1.1444396.
Boehm, C., Hanzich, M., de la Puente, J., Fichtner, A., 2016. Wavefield compression for adjoint methods in full-waveform inversion. Geophysics 81 (6), R385–R397. http://dx.doi.org/10.1190/GE02015-0653.1.
Bristow, C.S., Jol, H.M. (Eds.), 2003. Ground penetrating radar in sediments. Geological Society, Special Publications, 211, London.
Comunian, A., Renard, P., Straubhaar, J., Bayer, P., 2011. Three-dimensional high resolution fluvio-glacial aquifer analog - Part 2: Geostatistical modeling. J. Hydrol. 405 (1–2), 10–23. http://dx.doi.org/10.1016/j.jhydrol.2011.03.037.
Daniels, D., 2004. Ground penetrating radar. In: Radar, Sonar, Navigation, and Avionics Series, Institution of Electrical Engineers.
Desbarats, A., Bachu, S., 1994. Geostatistical analysis of aquifer heterogeneity from the core scale to the basin scale: A case study. Water Resour. Res. 30 (3), 673–684. http://dx.doi.org/10.1029/93WR02980.
Emery, X., Lantuéjou, C., 2006. TBSIM: A computer program for conditional simulation of three-dimensional Gaussian random fields via the turning bands method. Comput. Geosci. 32 (10), 1615–1628. http://dx.doi.org/10.1016/j.cageo.2006.03.001.
Gelhar, L.W., 1993. Stochastic Subsurface Hydrology. Prentice-Hall.
Giannakis, I., Giannopoulos, A., Warren, C., 2016. A realistic FOTO numerical modeling framework of ground penetrating radar for landmine detection. IEEE J. Sel. Top. Appl. Earth Obs. Remote Sens. 9 (1), 37–51. http://dx.doi.org/10.1109/JSTARS.2015.2468597.
Hamann, G., Tronicke, J., 2014. Global inversion of GPR traveltimes to assess uncertainties in CMP velocity models. Near Surface Geophys. 12 (4), 505–514. http://dx.doi.org/10.3997/1873-0604.2014005.
Hamann, G., Tronicke, J., Steelman, C.M., Endres, A.L., 2013. Spectral velocity analysis for the determination of ground-wave velocities and their uncertainties in multi-offset GPR data. Near Surface Geophys. 11 (2), 167–176. http://dx.doi.org/10.3997/1873-0604.2012038.
Heinz, J., Aigner, T., 2003. Hierarchical dynamic stratigraphy in various Quaternary gravel deposits, Rhine glacier area (SW Germany): Implications for hydrostratigraphy. International Journal of Earth Sciences 92 (6), 923–938. http://dx.doi.org/10.1007/s00531-003-0359-2.
Irving, J., Knight, R., 2006. Numerical modeling of ground-penetrating radar in 2-D using MATLAB. Comput. Geosci. 32 (9), 1247–1258. http://dx.doi.org/10.1016/j.cageo.2005.11.006.
Keller, B., 1996. Lithofacies-Codes für die Klassifikation von Lockergeteinen. Mitt. Schweiz. Ges. Boden Felsmechanik 132, 5–12.
Klotzsche, A., van der Kruk, J., Meles, G.A., Doetsch, J., Maurer, H., Linde, N., 2010. Full-waveform inversion of cross-hole ground-penetrating radar data to characterize a gravel aquifer close to the Thur River, Switzerland. Near Surface Geophys. 8 (6), 635–649. http://dx.doi.org/10.3997/1873-0604.2010054.
Knight, R., 2001. Ground penetrating radar for environmental applications. Ann. Rev. Earth Planetary Sci. 29, 229–255. http://dx.doi.org/10.1146/annurev.earth.29.1.229.
Kowalsky, M.B., Dietrich, P., Teutsch, G., Rubin, Y., 2001. Forward modeling of ground-penetrating radar data using digitized outcrop images and multiple scenarios of water saturation. Water Resour. Res. 37 (6), 1615–1625. http://dx.doi.org/10.1029/2001WR900015.

8

P. Koyan and J. Tronicke

Computers and Geosciences 137 (2020) 104422

Koyan, P., Tronicke, J., 2019. [dataset] A synthetic 3D ground-penetrating radar (GPR) data set across a realistic sedimentary model. Mendeley Data http://dx.doi.org/10.17632/by3yh79hx4.1.
van der Kruk, J., Liu, T., Mozaffari, A., Gueting, N., Klotzsche, A., Vereecken, H., Warren, C., Giannopoulos, A., 2018. GPR Full-waveform inversion, recent developments, and future opportunities. In: 17th International Conference on Ground Penetrating Radar (GPR), Rapperswil, Switzerland. IEEE, http://dx.doi.org/10.1109/ICGPR.2018.8441667.
Kunz, K.S., Luebbers, R.J., 1993. Finite Difference Time Domain Method for Electromagnetics. CRC Press.
Lai, W.W.-L., Dérobert, X., Annan, P., 2018. A review of ground penetrating radar application in civil engineering: a 30-year journey from locating and testing to imaging and diagnosis. NDT and E Int. 96, 58–78. http://dx.doi.org/10.1016/j.ndteint.2017.04.002.
Liu, B., Zhang, C., Xu, S., Zhang, Q., Li, S., Li, Y., Zhang, F., Nie, L., 2018. Forward modelling and imaging of ground-penetrating radar in tunnel ahead geological prospecting. Geophys. Prospect. 66 (4), 784–797. http://dx.doi.org/10.1111/1365-2478.12613.
Loewer, M., Igel, J., 2016. FDTD simulation of GPR with a realistic multi-pole debye description of lossy and dispersive media. In: 16th International Conference on Ground Penetrating Radar, GPR, Hong Kong, China. http://dx.doi.org/10.1109/ICGPR.2016.7572599.
Métivier, L., Brossier, R., Mérigot, Q., Oudet, E., Virieux, J., 2016. An optimal transport approach for seismic tomography: Application to 3D full waveform inversion. Inverse Problems 32, http://dx.doi.org/10.1088/0266-5611/32/11/115008.
Millington, T.M., Cassidy, N.J., 2010. Optimising GPR modelling: A practical, multi-threaded approach to 3D FDTD numerical modelling. Comput. Geosci. 36 (9), 1135–1144. http://dx.doi.org/10.1016/j.cageo.2009.12.006.
Neal, A., 2004. Ground-penetrating radar and its use in sedimentology: Principles, problems and progress. Earth Sci. Rev. 66 (3–4), 261–330. http://dx.doi.org/10.1016/j.earscirev.2004.01.004.
Paasche, H., Tronicke, J., 2007. Cooperative inversion of 2D geophysical data sets: A zonal approach based on fuzzy c-means cluster analysis. Geophysics 72 (3), A35–A39. http://dx.doi.org/10.1190/1.2670341.
Roth, K., Schulin, R., Flühler, H., Attinger, W., 1990. Calibration of time domain reflectometry for water content measurement using a composite dielectric approach. Water Resour. Res. 26 (10), 2267–2273. http://dx.doi.org/10.1029/WR026i010p02267.
Samet, R., Celik, E., Tural, S., Sengönül, E., Özkan, M., Damci, E., 2017. Using interpolation techniques to determine the optimal profile interval in ground-penetrating radar applications. J. Appl. Geophys. 140, 154–167. http://dx.doi.org/10.1016/j.jappgeo.2017.04.003.
Schennen, S., Tronicke, J., Wetterich, S., Allroggen, N., Schwamborn, G., Schirrmeister, L., 2016. 3D ground-penetrating radar imaging of ice complex deposits in northern East Siberia. Geophysics 81 (1), WA195–WA202. http://dx.doi.org/10.1190/geo2015-0129.1.
Schön, J.H., 1998. Physical Properties of Rocks. Pergamon.
Tronicke, J., Holliger, K., 2005. Quantitative integration of hydrogeophysical data: Conditional geostatistical simulation for characterizing heterogeneous alluvial aquifers. Geophysics 70 (3), H1–H10. http://dx.doi.org/10.1190/1.1925744.
Versteeg, R., 1994. The marmousi experience: Velocity model determination on a synthetic complex data set. Leading Edge 13, 927–936. http://dx.doi.org/10.1190/1.1437051.
Walden, A.T., Hosken, J.W.J., 1985. An investigation of the spectral properties of primary reflection coefficients. Geophys. Prospect. 33 (3), 400–435. http://dx.doi.org/10.1111/j.1365-2478.1985.tb00443.x.
Warren, C., Giannopoulos, A., Giannakis, I., 2016. gprMax: Open source software to simulate electromagnetic wave propagation for Ground Penetrating Radar. Comput. Phys. Comm. 209, 163–170. http://dx.doi.org/10.1016/j.cpc.2016.08.020.
Warren, C., Wetter, L., Giannakis, I., Gray, A., Giannopoulos, A., Hamrah, A., Patterson, A., 2018. A CUDA-based GPU engine for gprmax: Open source FDTD electromagnetic simulation software. Comput. Phys. Comm. 237, 208–218. http://dx.doi.org/10.1016/j.cpc.2018.11.007.
Yang, P., Gao, J., Wang, B., 2014. RTM Using effective boundary saving: A staggered grid GPU implementation. Comput. Geosci. 68, 64–72. http://dx.doi.org/10.1016/j.cageo.2014.04.004.
Zakri, T., Laurent, J.P., Vauclin, M., 1998. Theoretical evidence for ‘Lichtenecker’s mixture formulae’ based on the effective medium theory. J. Phys. D: Appl. Phys. 31 (13), 1589–1594. http://dx.doi.org/10.1088/0022-3727/31/13/013.

9