Journal of the Korean Geotechnical Society, Volume 37,
Issue 9, September 2021, pp. 13 □ 24
Vol.37, No.9, September 2021 pp. 13 □ 24

ISSN 1229-2427 (Print)
ISSN 2288-646X (Online)
https://doi.org/10.7843/kgs.2021.37.9.13

# Numerical Modeling for the Identification of Fouling Layer

## Numerical Modeling for the Identification of Fouling Layer
in Track Ballast Ground

Go, Gyu-Hyun 1 Go, Gyu-Hyun

Lee, Sung-Jin 2 Lee, Sung-Jin

### Abstract

Recently, attempts have been made to detect fouling patterns in the ground using Ground Penetrating Radar (GPR) during the maintenance of gravel ballast railway tracks. However, dealing with GPR signal data obtained with a large amount of noise in a site where complex ground conditions are mixed, often depends on the experience of experts, and there are many difficulties in precise analysis. Therefore, in this study, a numerical modeling technique that can quantitatively simulate the GPR signal characteristics according to the degree of fouling of the gravel ballast material was proposed using python-based open-source code gprMax and RSA (Random sequential Absorption) algorithm. To confirm the accuracy of the simulation model, model tests were manufactured and the results were compared to each other. In addition, the identification of the fouling layer in the model test and analysis by various test conditions was evaluated and the results were analyzed.

### Keywords

Recently, attempts have been made to detect fouling patterns inside the ground using Ground Penetrating Radar (GPR) equipment during maintenance of gravel trackbeds. However, reading GPR signal data obtained with a large amount of noise in sites with complex ground conditions often depends on expert experience, and there are many difficulties in precise analysis. Therefore, in this study, a numerical analysis technique is proposed that can quantitatively analyze and evaluate GPR signal characteristics according to the degree of fouling of gravel ballast material using the Python-based open-source codes gprMax and RSA (Random Sequential Absorption). To evaluate the accuracy of the interpretation model, model test specimens were fabricated and the results were compared with the interpretation results to confirm the predictive accuracy of the interpretation model. In addition, the identification of the fouling layer under various test conditions in model tests and interpretations was evaluated, and the results were analyzed.

Keywords: Fouling, gprMax, Ground penetrating radar, Model test, RSA

1 Member, Assistant Professor, Department of Civil Engineering, Kumoh National Institute of Technology

2 Member, Principal Researcher, Track & Roadbed Research Team, Korea Railroad Research Institute, Tel: +82-31-460-5072, geolsj@krri.re.kr,
Corresponding author

* Members who wish to discuss this paper are requested to send their comments to the society by March 31, 2022. The authors' review content will be published in the proceedings.

Copyright © 2021 by the Korean Geotechnical Society

This is an Open-Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License (http://creativecommons.org/licenses/by-nc/3.0)
which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is properly cited.

Numerical Modeling for the Identification of Fouling Layer 13

1. Introduction

Railway track typically distinguishes between ballast tracks and concrete ballast tracks, but ballast track structures, which are cheaper to install initially and easier to maintain elasticity and repair, have been used worldwide for a long time (Shin et al., 2017; Lee et al., 2020). In Korea, about 80% of railway tracks are ballasted, and as railway use increases, the importance and interest in efficient maintenance technology for ballast material have grown. Ballast materials experience fragmentation and wear due to repetitive vibrations from trains and maintenance activities, intrusion of external materials, and rise of subgrade materials, forming an fouling layer inside the ground as shown in Fig. 1 (Selig and Waters, 1994). This fouling layer reduces inter-particle friction effects (interlocking effect) and leads to deterioration of track safety performance (Leng and Al-Qadi, 2010). In the field, exploration of fouling layers inside railway subgrade has mainly involved excavation, but recently attempts have been made to detect the fouling pattern inside the ballast using Ground Penetrating Radar (GPR), and related lab and field tests have been conducted (Shin et al., 2017; Lee et al., 2020; Benedetto et al., 2017; Robert et al., 2009; Sadeghi et al., 2018). GPR equipment transmits an electromagnetic pulse into the ground and can image high-resolution responses to ground variations, making it effective for identifying ground variation patterns in the field, enabling preliminary anomaly detection in a short time, and is used in various geological survey fields (Choi et al., 2001; Hong et al.

In 2015). However, because signal propagation behavior varies greatly depending on the type of GPR antenna, soil structure, material properties, moisture content, and salinity, a thorough reliability review and validation of observed signal data is required, and for this, a GPR modeling analysis technique that can evaluate and verify internal states relatively accurately even under mixed complex ground conditions is currently needed.

Numerous numerical modeling studies of GPR for identifying fouling layers have been attempted abroad. For example, Huang and Tutumluer (2011) proposed a polluted aggregate model using an image-aided based DEM technique by referring to experimentally observed images, then compared lab tests and DEM simulations to calibrate and validate model parameters. Also, Ngo et al. (2016) used DEM to model micro-scale behavior of polluted fouling layers and found that as fouling increases, the maximum contact force between ballast grains decreases. In Korea, GPR numerical modeling technology development and application studies are gradually becoming active, but so far most cases are in the field of underground cavity detection. Cheon (2016) conducted GPR interpretation studies for subterranean cavity detection on roadbeds and compared signal responses with field results, and Jang et al. (2016) developed a 3D model simulating EM pulsing of GPR to examine responses of a simplified cavity model, confirming that the developed model can effectively obtain information on cavities beneath urban roads. As mentioned above, there are cases of applying GPR numerical modeling to underground cavity detection in Korea, but there are virtually no cases where a GPR numerical model is used to detect fouling layers inside ballast substructure of rail tracks. Therefore, this study proposes a numerical analysis technique that quantitatively analyzes and evaluates GPR signal characteristics according to the fouling degree of ballast materials using the open-source Python-based software gprMax and the Random Sequential Absorption (RSA) algorithm. In addition, to verify the predictive reliability of the analysis results, the GPR signal characteristics of the model specimen were compared and reviewed with model experiment data, and the identification of fouling layers under various subgrade conditions was confirmed.

![img-0.jpeg](img-0.jpeg)

Fig. 1. Typical active railroad ballast cross-section (Roberts et al., 2009)

14

Journal of the Korean Society for Geotechnical Engineering, Vol. 37, No. 9

2. Numerical Modeling

### 2.1 Governing Equations

The gprMax used in this study is an analytical software that can simulate the propagation behavior of signals transmitted and received by GPR equipment, using Maxwell's equations as governing equations (http://www.gprmax.com). It employs the Finite-Difference Time-Domain (FDTD) method, which discretizes the spatial and temporal continuities to approximate solutions (Yee, 1996).

\[
\begin{array}{l} E \quad \frac {B}{t} \\ H \quad \frac {D}{t} \quad \text {   j   } \text {   cs   } \\ \begin{array}{c c} B & 0 \\ D q v \end{array} \tag {1} \\ \end{array}
\]

Here, E is the electric field strength (V/m), H is the magnetic field strength (A/m), D is the electric displacement density (C/m^2), B is the magnetic flux density (T), JC is the current density at the antenna source (A/m^2), JS is the current density in the resistive element (A/m^2), t is time (s), and qv is the volumetric charge density (C/m^3).

gprMax fundamentally solves the electric and magnetic fields in 3D space using the Finite Difference Time Domain method in the time domain and refers to this as the TEM mode. However, in this study, to improve efficiency for interpreting complex and various particle shapes and grain size distributions, a 2D TM (transverse magnetic) z-direction mode was used for the cells. In this case, Maxwell's equations can be expressed as three coupled partial differential equations, discretized in time and space, and applied to each FDTD cell shown in Fig. 2.

\[
\begin{array}{l} \frac {1}{\eta \eta} \frac {\partial H y}{\partial t x y} \frac {H}{\partial t x y} \\ \frac {\partial H _ {x}}{t y} \frac {1 (\cdot) \partial E z}{\cdot} M H y \\ \frac {}{t x} \frac {1 (\cdot) \partial E z}{\cdot} M H y s y \tag {2} \\ \end{array}
\]

![img-1.jpeg](img-1.jpeg)

Fig. 2. Single FDTD Yee cell showing electric (red), magnetic (green), and zeroed out (grey) field components for 2D transverse magnetic (TM) z-direction mode (Yee, 1966)

Here,  \( \varepsilon \)  is the permittivity (farads/meter),  \( \mu \)  is the permeability (henries/meter),  \( \sigma \)  is electrical conductivity (Siemens/meter), and  \( \sigma\star \)  is magnetic loss (Ohms/meter).

Meanwhile, it is very important to define appropriate sizes for the discretized elements  \( \Delta x \) ,  \( \Delta y \) ,  \( \Delta z \)  and the small time step  \( \Delta t \)  in the model. As element size and time step become smaller, the propagated signals resemble real signals more closely, but given the limited memory space and finite processing speed of the computing hardware, an appropriate level of size and spacing is required. The required element (cell) size should be less than one-tenth of the wavelength  \( \lambda \) , which is calculated by Equation (3).

\[
\begin{array}{c} \text {c} \\ \text {Er} \end{array} \tag {3}
\]

Here, c is the speed of light  \( 2.99 \times 10^{8} \)  m/s, f is the maximum frequency of the signal (Hz), and  \( \varepsilon r \)  denotes the relative permittivity of the ground material. Once the element size is defined, the minimum time step  \( \Delta t \)  must satisfy the Courant stability condition below (Taflove, 1995; Sullivan, 2000). In this study, the TMz mode is considered with  \( \Delta z \rightarrow \infty \) .

\[
\frac {1}{c \sqrt {\left( \begin{array}{l l} 1 1 & 1 \\ 1 & 2 2 \\ 1 & 2 \end{array} \right) ^ {2} + \left(\Delta \Delta \Delta\right) ^ {- 2}}} \tag {4}
\]

Numerical Study for Identifying Fouling Layers in Gravelly Soil

15

![img-2.jpeg](img-2.jpeg)

Fig. 3. Two dimensional domain used in the numerical study

![img-3.jpeg](img-3.jpeg)

(a) Clean ballast (CB)

![img-4.jpeg](img-4.jpeg)

(b) Fully Fouled ballast (FFB)

![img-5.jpeg](img-5.jpeg)

(c) Floated ballast (FB)

Fig. 4. Critical ballast fouling phases

2.2 Particle Modeling and Material Properties

In this study, as shown in Fig. 3, the contamination level of the fouling layer was classified into three stages to model the gravel-surface ground, and the boundary between the gravel layer and subgrade was simulated with a 'Ballast Pocket' to build an interpretation domain similar to actual ground (Ballast Pocket refers to a bend formed when ballast particles penetrate the subgrade, with moisture infiltrating at the surface tending to accumulate). Fig. 4 shows the fouling levels of the fouling layer, distinguishing the fouling stages of the gravel-surface material as Clean Ballast (hereafter CB), Fully Fouled Ballast (hereafter FFB), and Floated Ballast (hereafter FB). CB means a clean state where there are no fine particles and the voids of ballast grains are filled with air; FFB means the voids are filled with fine particles; FB means the fine particles are included in volumes exceeding the voids between ballast grains, so that ballast grains float among the fine particles, indicating a very severe level of contamination.

In addition, to determine the particle size distribution for each soil material, sieve analysis was conducted beforehand, and the particle size distributions (Particle size distribution) for each soil material are shown in Fig. 5. In this study, ballast particles were generated to reasonably model the size distributions for each material and applied as model input parameters. This includes the RSA improved by itself.

![img-6.jpeg](img-6.jpeg)

Fig. 5. Particle size distribution of ballast and subgrade used in this study

(Random sequential Absorption) algorithm was applied; considering the average number of particles to be returned and the range of particle diameters, particles were generated randomly, and if particles overlapped, they were regenerated in the vicinity of the overlapped region rather than the entire domain to significantly shorten the total particle generation time (Fig. 6). Meanwhile, the electromagnetic properties of the soil materials used in this study are listed in Table 1. Among these, the relative permittivity of each material is the equivalent electromagnetic properties measured in full-scale model tests VMF

16 Korean Geotechnical Society Journal, Vol. 37, No. 9

Table 1. Material properties used in the study

|  Type | Parameter | Value | Unit  |
| --- | --- | --- | --- |
|  Air | Default parameter, 'free_space'  |   |   |
|  Ballast | Relative permittivityεr | 6.5 | -  |
|   |  Electric conductivityσ | 5.05E-7 | Siemens/meter  |
|   |  Relative permeabilityμr | 1 | -  |
|   |  Magnetic loss, σ* | 0 | Ohms/meter  |
|  Fouled clay | Relative permittivityεr | 3 | -  |
|   |  Electric conductivityσ | 0.05 | Siemens/meter  |
|   |  Relative permeabilityμr | 1 | -  |
|   |  Magnetic loss, σ* | 0 | Ohms/meter  |
|  Subgrade | Relative permittivityεr | 6 | -  |
|   |  Electric conductivityσ | 0.005 | Siemens/meter  |
|   |  Relative permeabilityμr | 1 | -  |
|   |  Magnetic loss, σ* | 0 | Ohms/meter  |

![img-7.jpeg](img-7.jpeg)

Fig. 6. Particle making technology based on the advanced RSA algorithm

(Volumetric Mixing Formulas) applied and the individual element properties were back-calculated to estimate them (see Fig. 6).

2.3 GPR Antenna Specifications

In this analytical study, there are a total of two types of GPR equipment (1,600

MHz, 400MHz) were considered, and the waveform type used was the Gaussian waveform commonly used by the GPR antennas. The specifications of each antenna are given in Table 2. One of the important input information related to the source is the centre frequency (centre frequency, Hz), and it is calculated based on the relationship between the high-pass filter frequency (f1) and the low-pass filter frequency (f2) of the equipment as in Equation (5), or using the Taguchi method.

Table 2. Specification of GPR Antenna

|  Type | GSSI 1.6 GHz | GSSI 400 MHz | Unit  |
| --- | --- | --- | --- |
|  Range | 12 | 50 | ns  |
|  High pass filter, f1 | 250 | 100 | MHz  |
|  Low pass filter, f2 | 3000 | 800 | MHz  |
|  Samples per scan | 512 | 512 | -  |
|  Scans per second | 100 | 120 | -  |

Numerical analysis study for identifying fouling layers in gravelly subgrade

17

(Taguchi et al., 2005; Warren and Giannopoulos, 2011) can also be determined through optimization algorithms such as those. In this study, the central frequency was determined using the Taguchi method.

$$f_{centre} = \sqrt{V} /$$

This source information is used as the model input parameter. In the TMz mode, the physical structure of the GPR antenna is not fully modeled, and the transmitting unit and receiving unit are each defined as a single point. Since the full-scale experimental testing equipment used in this study is of the Ground-coupled type, the antenna position in the analysis model was assumed to be completely in contact with the ground surface, and the separation distance between the transmitting unit and the receiving unit was set to 0.15m.

# 3. Ballast track and fouling layer model specimens

In this study, to verify the predictive reliability of the proposed analysis model, model specimens were fabricated by classifying the contamination level of the fouling layer that may occur in the ballast track into three stages. Fig. 7 shows the sequence of model specimen preparation. In the model specimens, the CB layer was prepared by purchasing ballast track material to be used in an actual railway site from a supplier and without adding any fine particles. The FFB layer was prepared by mixing the ballast track material and the fine particles in a volume ratio of 1:1, and the FB layer was prepared by mixing them in a volume ratio of 1:2 to form the model specimens. In addition, to simulate the 'Ballast Pocket' in Fig. 3, grooves with a depth of 300mm and a width of 900mm were made on the subgrade surface, compacted with CB, FFB, and FB materials, and compacting was performed up to a height of about 200mm in each section with CB, FFB, and FB samples. Sleeper thickness

![img-8.jpeg](img-8.jpeg)

(a) Subgrade in progress

![img-9.jpeg](img-9.jpeg)

(b) Ballast in progress

![img-10.jpeg](img-10.jpeg)

(c) 3 sections of Ballast (CB, FFB, FB)

![img-11.jpeg](img-11.jpeg)

(d) Completed construction of the test model

![img-12.jpeg](img-12.jpeg)

(e) GPR test on ballast model

Fig. 7. Process of test model construction

18

Journal of the Korean Geotechnical Society, Vol. 37, No. 9

The 200mm subsurface layer corresponding to this was prepared with CB to simulate the ballast track ballast and the ballast bed layer at the site. The survey line of the GPR equipment was selected in the transverse direction of the model, and the same location was observed for each antenna frequency so that signal changes according to frequency variations could be compared and analyzed. The main controller used in the model specimen test was the 4-channel SIR-30 System manufactured by the US company GSSI (Geophysical Survey Systems, Inc.), and the GPR antennas used equipment of 1,600MHz and 400MHz (Lee et al., 2020).

# 4. Results and Analysis

Using the numerical analysis model proposed in this study, an electromagnetic analysis was performed considering a total interpretation time of 22 ns per run. In signal analysis, the electromagnetic wave amplitude in the depth direction along the survey line presented in one dimension is referred to as an A-scan, and the electromagnetic wave signal in the depth direction represented in two dimensions along the survey line is expressed as a B-scan of the GPR signal. When determining the B-scan, the antenna movement interval was defined as 0.005 m, and the number of repeated calculations was defined as 1,200 times. Fig. 8 is a snapshot image showing the propagation pattern of the GPR signal over time. The output data obtained from gprMax is Paraview (https://www.

It can be visualized through post-processing software such as paraview.org). Although these snapshot images are helpful for visually identifying the response signal characteristics when GPR propagation signals encounter different media (subsurface layers), there is a limitation in quantitatively analyzing and evaluating this. Therefore, in practice, an A-scan that can observe changes in the response signal over time at a specific location may be more useful as an analysis data set.

Fig. 9 shows the A-scan results calculated at the center of the domain according to the model specimen conditions considered in this study (Fig. 3), and presents the comparison results with the model test results. It can be seen that there is a slight error between the analytical and experimental A-scan results under each test condition, which is considered to have occurred because the 2D numerical analysis model considered in this study treated the transmitting and receiving parts of an antenna having a 3D shape as a single point (point) each. To obtain more reliable A-scan data, it is deemed that an extension to a 3D analysis model that fully accounts for the antenna shape will be necessary in the future.

Figs. 10–12 show the B-scan images derived for each test condition when using 400MHz low-frequency equipment. In the B-scan generation, given the assumption that the signal intensity attenuates in the depth direction,

![img-13.jpeg](img-13.jpeg)

(a) After 5.3 ns

![img-14.jpeg](img-14.jpeg)

(b) After 9 ns

Fig. 8. Snapshot image post-processed with Paraview

Numerical Analysis Study for Identifying a Fouling Layer in a Ballast Track Bed

19

![img-15.jpeg](img-15.jpeg)

![img-16.jpeg](img-16.jpeg)

![img-17.jpeg](img-17.jpeg)

Fig. 9. Comparison results for the A-scan at the center point of the domain (a) CB-Subgrade, (b) CB-FB-Subgrade, (c) CB-FFB-Subgrade

![img-18.jpeg](img-18.jpeg)

![img-19.jpeg](img-19.jpeg)

![img-20.jpeg](img-20.jpeg)

Fig. 10. B-scan image of 400 MHz (a) Ground condition: CB-Subgrade layer, (b) Simulated image, (c) Measured image

20

Soil Engineering Society of Korea Journal, Vol. 37, No. 9

(a)

![img-21.jpeg](img-21.jpeg)

Simulated B-scan

(b)

![img-22.jpeg](img-22.jpeg)

![img-23.jpeg](img-23.jpeg)

(c)

![img-24.jpeg](img-24.jpeg)

![img-25.jpeg](img-25.jpeg)

Fig. 11. B-scan image of 400 MHz (a) Ground condition: CB-FFB-Subgrade layer, (b) Simulated image, (c) Measured image

(a)

![img-26.jpeg](img-26.jpeg)

Simulated B-scan

(b)

![img-27.jpeg](img-27.jpeg)

![img-28.jpeg](img-28.jpeg)

(c)

![img-29.jpeg](img-29.jpeg)

![img-30.jpeg](img-30.jpeg)

Fig. 12. B-scan image of 400 MHz (a) Ground condition: CB-FB-Subgrade layer, (b) Simulated image, (c) Measured image

Numerical analysis study for identification of fouling layer in gravelly ground

21

Also, both the measured data and the interpreted data were subjected to the same proportion of attenuation characteristic correction (Gain compensation). In Fig. 10-12, the B-scan obtained from numerical analysis relatively clearly identified the boundary interface between the gravel layer and the subgrade for all considered fouling conditions; however, it can be seen that the interface between the CB layer and the FFB layer was not identified as a clear reflected-wave signal in the interpretation results (Fig. 11). This is analyzed as being because the FFB layer has a small content of fine particles within the voids, making it difficult to clearly distinguish the material characteristics from those of the upper CB layer. Nevertheless, the numerical analysis model also had the CB"

![img-31.jpeg](img-31.jpeg)

(a) A-scan with time domain including direct wave

![img-32.jpeg](img-32.jpeg)

(b) A-scan with depth domain excluding direct wave

Fig. 13. Comparison of A-scan between CB-FB-Subgrade and CB-FFB subgrade

"interface between the CB layer and the FB layer was identified relatively clearly (Fig. 12), which is considered to be because the electromagnetic waves emitted by the 400 MHz equipment have a sufficiently high amplitude (Amplitude) to identify the particle size distribution on the gravel bed and the electromagnetic characteristics of the fine particles present within the voids. Fig. 13(a) shows a comparison of the time-domain A-scan (x=4 m) under the CB-FB-Subgrade condition and the CB-FFB-Subgrade condition. The interval t1 represents the reflected-wave signal caused by the direct wave within the antenna, and the portion after t2 is the reflected-wave signal caused by the ground medium. Fig. 13(b) presents the results of converting the reflected-wave signal in the region after t2 of Fig. 13(a) into a depth axis rather than a time axis to derive the graph, and it was confirmed that at the boundary where the medium changes from the gravel layer to the fouling layer, the FB layer shows a relatively higher amplitude energy value than the FFB layer. In other words, it is judged that the reflected-wave intensity and variability are pronounced at the boundary between the gravel layer and the FB layer, causing the boundary of the fouling layer to appear more prominently on the B-scan. In particular, in that the boundary of the fouling layer, which appeared somewhat unclear due to a large amount of noise in the B-scan data from the model-body test, is identified more clearly and sharply in the interpretation data, it is considered that if the proposed numerical analysis results in the future are used as reference material to analyze and review the measurement data, the difficulty of reading the boundary layers when analyzing GPR signal data with complex ground conditions and mixed noise could be substantially alleviated."

Meanwhile, Fig. 14 shows the B-scan image derived from the experiment and interpretation when using a 1,600 MHz high-frequency device

![img-33.jpeg](img-33.jpeg)

Fig. 14. B-scan image for CB-FB-Subgrade layer condition of 1600 MHz (simulated image, measured image)

22 Journal of the Korean Geotechnical Society Vol. 37 No. 9

is producing it. In the case of high-frequency signals, in both experiments and interpretations, the resolution of the scan B-scan images increased, whereas identifying the material boundary interfaces was difficult. This is because the relative difference in the reflected waves of the signals reflected at the boundary interfaces was not large. To compensate for this, it will be necessary to develop optimal signal processing techniques in the future, such as filtering and amplification. However, in the case of high-frequency signals, with their high resolution, the analysis technique can be made useful as data for developing analytical methods by utilizing scattering characteristics that reflect changes in the characteristics of the ballast material, such as particle boundaries and voids.

## 5. Conclusion

In this study, we proposed an interpretation technique that enables quantitative analysis and evaluation of the GPR signal characteristics according to the degree of fouling of railway ballast track materials using the gprMax and RSA algorithms. To verify the predictive reliability of the interpretation results, we compared and reviewed the GPR signal characteristics for a full-scale model test specimen with experimental data, and confirmed whether the fouling layer could be identified under each test condition. The conclusions derived through this are as follows.

(1) In each test condition, the A-scan had some error between the interpretation and the model test, which is considered to be due to a fundamental limitation of the two-dimensional numerical analysis model (assuming an antenna with a three-dimensional shape as two points). To enhance the reliability of the interpretation results, an expansion to a three-dimensional model that can reflect the actual geometry of the antenna is required.

(2) For analysis using reflected wave images (B-scan) for the interface between the ballast track layer and the subgrade boundary layer, or between the fouling layer and the interface, signals at the relatively low frequency of 400 MHz showed favorable characteristics. This made it possible to confirm that the cleaner the condition of the ballast track, the greater the reflected-wave strength occurs in the FB layer where fouling has progressed severely.

(3) When using 1,600MHz high-frequency equipment, the resolution of the scan data increased, whereas identification of the fouling layer and the boundary of the bedrock layer was not possible. This is because the relative difference in the reflected waves of the signals reflected at the boundary interface was not large; therefore, to compensate for this, it will be necessary in the future to develop optimal signal processing techniques such as filtering and amplification.

(4) In the case of 1,600MHz high-frequency signals, both in experiments and interpretations

The resolution of the scan B-scan image increased, while identification of the material interface boundaries was difficult. This is because the relative difference in the reflected waves of the signals reflected at the boundary interfaces was not large; therefore, it is judged that additional research on signal processing techniques is necessary. On the other hand, in the case of high-frequency signals, it is expected that they can be usefully utilized as data for developing analysis techniques by using scattering characteristics that reflect changes in characteristics of the ballast track material, such as particle boundaries and voids, with their high resolution.

## Acknowledgements

This paper is a study conducted with support from the National Research Foundation of Korea, funded by the Government in 2019 (Ministry of Science and ICT) (Development of technology for evaluating ballast track and subgrade conditions using GPR, 2019R1A 2C200744212).

## References

1. Benedetto, A., Tosti, F., Ciampoli, L.B., Calvi, A., Brancadoro, M.G., and Alani, A.M. (2017), Railway Ballast Condition Assessment Using Ground-penetrating Radar-An Experimental, Numerical Simulation and Modelling Development, Construction and Building Materials, 140, pp.508-520.
2. Cheon, S.W. (2016), GPR response analysis using numerical modeling for cavity detection, Master's thesis, Sejong University.
3. Choi, Y.G., Seol, S.J., and Suh, J.H. (2001), Dipole Antennas and Radiation Patterns in the Three-Dimensional GPR Modeling, Geophysical exploration, Vol.4, No.2, pp.45-54.
4. Hong, W.T., Kang, S.H., and Lee, J.S. (2015), Application of Ground Penetrating Radar for Estimation of Loose Layer, Journal of the Korean Geotechnical Society, Vol.31, No.11, pp.41-48.
5. Huang, H. and Tutumluer, E. (2011), Discrete Element Modeling for fouled railroad, Construction and Building Materials, 25, pp.3306-3312.
6. Jang, H., Kim, H.J., and Nam, M.J. (2016), Three-dimensional Finite-difference Time-domain Modeling of Ground-penetrating Radar Survey for Detection of Underground Cavity, Geophysics and Geophysical Exploration, Vol.19, No.1, pp.20-28.
7. Lee, S.J., Choi, Y.T., and Park, B.S. (2020), Analysis of GPR Signals by Different Frequencies According to Ballast Fouling Degree, Journal of the Korean Society for Railway, Vol.23, No.6, pp.513-523.
8. Leng, J. and Al-Qadi, I. (2010), Railroad Ballast Evaluation Using Ground-Penetrating Radar: Laboratory Investigation and Field Validation. Transportation Research Record: Journal of the Transportation Research Board, Vol.2159, No.1, pp.110-117.
9. Ngo, N.T., Indraratna, B., and Rujikatkamjorn, C. (2016), Micro-mechanics based Investigation of Fouled Ballast Using Large-scale Triaxial Tests and Discrete Element Modeling, J Geotech Geoenviron

Numerical analysis study for identification of the fouling layer in ballast track subgrade

23

Eng., Vol.143, No.2, pp.04016089.

10. Roberts, R. Al-Qadi, I., Tutumluer, E., and Boyle, J. (2009), Subsurface Evaluation of Railway Track Using Ground Penetrating Radar, Technical report, U.S. Department of Transportation.

11. Sadeghi, J., Motieyan-Najar, M.E., Zakeri, J.A., Yousefi, B., and Mollazadeh, M. (2018), Improvement of Railway Ballast Maintenance Approach, Incorporating ballast Geometry and Fouling Conditions,

Journal of Applied Geophysics, 151, pp.263-273.

12. Selig, E.T. and Waters, J.M. (1994), Track geotechnology and substructure management, Thomas Telford, London.

13. Shin, J.H., Choi, Y.T., and Jang, S.Y. (2017), New Gain Function Based on Attenuation Characteristics of Ballast Track for GPR Analysis, Journal of the Korean Geo-Environmental Society, Vol. 18, No.4, pp.13-21.

14. Sullivan, D.M. (2000), Electromagnetic Simulation Using the FDTD

Method, IEEE Press.

15. Taflove, A. (1995), Computational electrodynamics: the finite- difference time-domain method, Artech House.

16. Taguchi, G. Chowdbury, S., and Wu, Y. (2005), Taguchi's quality engineering handbook: John Wiley and Sons, Inc.

17. Warren, C. and Giannopoulos, A. (2011), Creating FDTD models of commercial GPR antennas using Taguchi's optimisation method,

Geophysics, 76:G37.

18. Yee, K.S. (1966), Numerical solution of initial boundary value problems involving Maxwell's equations in isotropic media, IEEE

Trans. Antennas Propag, Vol.14, No.3, pp.302-307.

Received : August 30th, 2021

Revised : September 15th, 2021

Accepted : September 16th, 2021

24 Korean Geotechnical Society Journal, Vol. 37, No. 9