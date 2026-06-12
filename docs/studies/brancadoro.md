# An Investigation into the Railway Ballast Grading using GPR and Image Analysis

M.G. Brancadoro, L. Bianchini Ciampoli, C. Ferrante, A. Benedetto

Department of Engineering, Roma Tre University Via Vito Volterra 62, 00146, Rome, Italy
mariagiulia.brancadoro@uniroma3.it,
luca.bianchiniciampoli@uniroma3.it,
chiara.ferrante@uniroma3.it,
andrea.benedetto@uniroma3.it

F. Tosti, A.M. Alani

School of Computing and Engineering

University of West London (UWL)

St Mary's Road, Ealing, W5 5RF, London, UK

Fabio.Tosti@uwl.ac.uk

Amir.Alani@uwl.ac.uk

Abstract—This study reports on an investigation into the grain size distribution of the railway ballast using ground-penetrating radar (GPR) and image analysis. The proposed approach relies on the hypothesis that the dimension (grading) of the ballast aggregates can influence the back-reflected spectrum received by the use of GPR. This assumption was confirmed by the finite difference time-domain (FDTD) simulations of the GPR signal, which were run by using the numerical simulator package gprMax 2D. A regression model was developed which related the "equivalent" diameter of the ballast aggregates and the frequency of the peak within the received spectrum. The model was validated in the laboratory environment by means of a $155\mathrm{cm}\times 155\mathrm{cm}\times 50$ cm methacrylate tank, filled up with railway ballast. An air-coupled GPR system equipped with a $2000\mathrm{MHz}$ central frequency antenna was used for testing purposes. A total of three spatial distributions of the ballast aggregates within the tank were investigated, by emptying out and filling up thrice the tank with the same material. The geometric information on the ballast grading obtained from the simulation-based regression model was compared to the actual grading curve of the ballast. To this effect, an algorithm based on the automatic image analysis was developed. The comparison showed that the modelled aggregate diameter corresponded to the $70\%$ of the grading of the material sieved out in the laboratory. This contribution paves the way to new methodologies for the non-destructive assessment and the monitoring of segregation phenomena within the ballast layers in railway track-beds.

Keywords—GPR; ground-penetrating radar; FDTD simulations; railway ballast; image analysis

# I. INTRODUCTION

The progressive aging of railway infrastructures and the growing transportation demand require proper scheduling of maintenance and rehabilitation activities, in order to maintain the highest standards in the operation of the infrastructure. Within this context, the case of ballasted track-beds is critical within a rail network, as the ballast layer is progressively polluted by the effects of the train passages during the infrastructure life-cycle. Among these factors, the segregation of the aggregates is one of the most critical, as it implies changes in the original grading of the ballast [1, 2].

In view of the above, administrations and managing companies are seeking high-performance and non-destructive inspection technologies, for the assessment of the health conditions of the track-bed and the early-stage detection of structural weaknesses. To this purpose, several studies report on the application of ground-penetrating radar (GPR) [3, 4], as it allows to perform very detailed surveys over long distances, at relatively high speeds.

This work proposes an experimental based approach for the assessment of the railway ballast conditions, which relies on the analysis of the GPR data in the spectral (frequency) domain and requires no calibration steps (i.e., no need for digging holes/trenches).

The proposed algorithms may be embedded within an automatic process for assessing changes in the railway ballast grading. The detection of the spatial and temporal variation of the grain size properties of the ballast may be reached by performing periodic surveys of the railway network.

# II. THEORETICAL BACKGROUND

The proposed approach relies on the evidence that a generic object (e.g., a railway ballast aggregate) subjected to the action of an electromagnetic (EM) field holds a characteristic frequency $f^*$, which is inversely related to its size. When the frequency of the EM waves hitting on the object equals the object characteristic frequency, resonant effects are generated.

In view of the pulsed GPR system used in this study, the EM waves are emitted within a frequency band $B$ rather than a single frequency. The bandwidth can be broadly quantified as twice the pulsed central frequency $f_{c}$ [5]. Thereby, it can occur that $f^{*}$ falls within $B$. In this case, the EM waves are found to resonate at that particular frequency of the spectrum. To this effect, it is expected a shift of the amplitude peak from $f_{c}$ towards $f^{*}$ within the bandwidth of the back-received spectrum.

![img-0.jpeg](img-0.jpeg)
Fig. 1. The simulation domains: single-particle(a) and multi-particle(b) configurations.

![img-1.jpeg](img-1.jpeg)

# III. FDTD SIMULATION

To underpin the theoretical assumption discussed in Section II, finite-difference time-domain (FDTD) simulations of the GPR signal were run on ballast particles with a simplified circle shape and differing size. An ad hoc simulation scenario was purposely set up (Fig. 1) using the numerical simulator package gprMax 2D [6].

A single ballast aggregate and an ensemble of equally-sized particles, simplified as circles with diameter  $d$  in a two-dimensional plane, were immersed into an air-filled domain. This domain was surrounded by perfectly matched layers (PML) to avoid any possible border effect on the signal. One transmitter  $tx$  and one receiver  $rx$  have been suspended in the air to a height of  $80~\mathrm{cm}$  from the particles, thereby reproducing a horn antenna working with the aperture suspended at  $40~\mathrm{cm}$  from the surface. Simulations have been run for both the configurations, with an increasing value of  $d$ , within the range  $4 - 12~\mathrm{cm}$ , i.e. the typical dimensions of ballast grains used for track-bed construction purposes. The central frequency of the synthetic pulse was set to  $2000~\mathrm{MHz}$ .

In both the analysed scenarios, the received spectra turned out to be influenced by the dimension of the object. Decreasing values of the frequency of the major amplitude peak have been recorded for increasing values of  $d$ . On the contrary, it was observed that for the greatest sizes of the aggregates (i.e. for  $d &gt; 8$  cm), the frequency shift did not occur, which was due to the low rate of energy received at the boundaries of the spectrum. This is particularly true in the case of the multi-grain configuration,

![img-2.jpeg](img-2.jpeg)
Fig.2. Regression curves from the two simulated configurations.

where the scattering between the particles tends to absorb a further part of the emitted energy [7].

# A. Regression Model

From the analysis of the trend of the spectral frequency peaks against the grain size of the analysed particles, it is possible to propose an exponential regression model, as in (1):

$$
f _ {p} = \alpha \cdot e ^ {- \beta d} \tag {1}
$$

with  $f_{p}$  being the resonance frequency,  $d$  being the diameter of the ballast particle,  $\alpha$  and  $\beta$  being the regression parameters depending on the simulated configuration. The regression curves are shown in Fig. 2. The values of the fitting parameters are listed in Table 1.

TABLE I. FITTING PARAMETERS IN EQ. 1

|   | Fitting Parameters  |   |   |
| --- | --- | --- | --- |
|   |  Configuration | α (×104) | β  |
|  1 | Single-particle | 6.6 | 18.0  |
|  2 | Multi-particle | 4.8 | 15.7  |

# IV. EXPERIMENTAL FRAMEWORK

In order to confirm the theoretical assumption discussed in Section I as well as the outcomes from the simulations showed in Section II, an experimental activity was purposely performed.

A  $155\mathrm{cm}\times 155\mathrm{cm}\times 55\mathrm{cm}$  square-based methacrylate tank (Fig. 3), was filled up with limestone ballast aggregates. A thorough assessment of the main physical and electromagnetic properties of the material was carried out according to standard test methods performed in the laboratory environment [8].

A total of three spatial distributions of the ballast aggregates within the tank were investigated by means of image analysis. This was achieved after emptying out and filling up thrice the tank with the same material.

# A. Image Analysis Algorithm

An ad hoc image analysis algorithm was developed in order to infer the geometric properties (grading) of the ballast by a photographic survey. This is an important tool for calibrating and validating the model.

![img-3.jpeg](img-3.jpeg)
Fig. 3. Plan view of the ballast-filled methacrylate tank, from Test 1. (a): the raw picture taken with a photocamera suspended in the air above the center of the formwork. (b): the binary image obtained from the processing of the raw picture.

The proposed algorithm is composed of two main steps. Firstly, a threshold to the RGB image is set, such that the original image is transformed into a binary matrix. The pixels of this matrix are filled with "ones" if they exceed the above set threshold; else (pixels below the threshold), the pixels are filled with "zeroes". Hence, morphological operators are required for cleaning up the image from the smaller objects, which can be attributed to clutter rather than to the actual size of the ballast particles. In Fig. 3 the planar picture of the ballast configuration from Test 1 (Fig. 3a) along with the corresponding binary matrix (Fig. 3b), are reported.

In the second step, the algorithm is aimed at recognising the different particles. This is a relatively complex procedure, which is highly dependent on the quality of the photography. Particularly, the condition of lighting has great influence on the reliability of the process. Indeed, since the system searches for zero-filled areas (i.e., void cells) within the analysed matrix in order to define the size of the ballast particles, the light contrast of the raw image is a crucial variable that may affect the reliability of the proposed algorithm. In view of a poor contrast of the raw image, the algorithm may fail in detecting the contour of the particle; hence this may be not recognized as a single particle. To prevent this failure, a threshold to the maximum admitted size of the recognized particles was arbitrary set. Thereby, the algorithm detects only the fraction of particles that complies with the above set filters. The reliability of this approach used for the partition of the dataset was proven. The comparison of the grain size distribution retrieved by means of the discussed algorithm with that defined through the sieve method [9], performed in the laboratory environment, is shown in Fig. 4. The normalised root mean square deviation (NMRSD) is equal to  $8\%$ ,  $14\%$  and  $15\%$  for Test 1, 2 and 3, respectively.

The final outcome of this second step is a sequence of recognized particles with corresponding areas expressed in number of pixels. To outline the grading curves from the analyses of the images, the areas of the ballast particle has been converted from pixels to  $\mathrm{cm}^2$ , by taking the known dimension of the methacrylate tank as scale reference. Subsequently, a specific diameter was assigned to each particle by referring to the equivalent virtual circle-shaped particles (with the same area of those captured from the image analysis). Finally, the volume of the aggregates was calculated after assuming the aggregate particles as 3-D spheres. To pass from volume to weight units, it

![img-4.jpeg](img-4.jpeg)
Fig. 5. Grading curves obtained by running the algorithm on Test 1 (dot-dashed) and from the Sieve Method (dashed).

![img-5.jpeg](img-5.jpeg)
Fig. 4. Raw (dashed) and processed (solid) GPR data collected on Test 1.

was used the information on the density of the ballast aggregates, as per the aforementioned laboratory tests [8].

# B. Data Collection and Signal Processing

An air-coupled GPR system manufactured by IDS Georadar and equipped with a 2000 MHz central frequency antenna, was used for testing purposes. The antenna was suspended in the air at  $40~\mathrm{cm}$  from the center of the ballast surface. To raise the stability of the signal and to cut off the random noise, 100 traces were collected and the corresponding average sweep was taken as a reference.

Subsequently, the GPR data were processed according to the standard scheme discussed in [8], and including zero-offset removal and band-pass filtering. As good practice, the cut-off bandwidth was set 1.5 times the central frequency. Fig. 5 depicts the GPR signal collected in Test 1, before and after the data processing.

# V. RESULTS

To test the effectiveness of the proposed approach, the data gathered from the GPR laboratory tests have been worked out into Eq. (1). This allowed for the computation of the geometric parameter  $d$  of the tested ballast. This information was finally compared with the same parameter derived from the image analysis.

![img-6.jpeg](img-6.jpeg)
Fig. 6. Frequency spectra of the three configurations of ballast aggregates reproduced.

![img-7.jpeg](img-7.jpeg)
Fig. 7. Grading curves obtained from the image analysis run on Test 1 (square-marked), Test 2 (triangle-marked), Test 3 (cross-marked), and the curve interpolating the average values (solid line).

In Fig. 6, the frequency spectra from the GPR tests performed within the three ballast configurations are reported. The frequency peak for Test 1, 2 and 3 is detected at  $1430\mathrm{MHz}$ ,  $1120\mathrm{MHz}$  and  $1430\mathrm{MHz}$ , respectively. These frequencies are consistently lower than the nominal frequency of the emitted GPR signal, which confirms that the EM waves are subjected to resonance when hitting the ballast aggregates. By inversely applying Eq. (1), it was possible to obtain the relevant diameter of the aggregates for each of the three cases. This resulting diameter  $D^{*}$  is a characteristic feature which depends on the whole grain size distribution. The application of Eq. (1) provided a value of  $D^{*}$  of  $0.077\mathrm{m}$ ,  $0.092\mathrm{m}$  and  $0.077\mathrm{m}$  for Test 1, 2 and 3, respectively.

To investigate how  $D^{*}$  relates to the actual ballast grading, the grain size distribution curves of the three configurations were considered (Fig. 7). To this effect, as both the diameters of the aggregates and the distribution curves are related to the same ballast sample (same aggregates reshuffled within the same volume in each analysed scenario), and rather depend on the spatial distribution of the aggregates, their average values were taken as reference. In view of this, the average diameter  $D_{avg}^{*}$  turned out to be  $0.087\mathrm{m}$ . The average grading curve is shown in Fig. 7. Looking at the graph, it is worth noting how  $D_{avg}^{*}$  corresponds to the sieve with the  $70\%$  of retained material.

# VI. CONCLUSIONS AND FUTURE PERSPECTIVES

This paper reports on a new ground-penetrating radar (GPR)-based approach for the assessment of the railway ballast grading. Data were collected using an air-coupled GPR system equipped with a  $2000\mathrm{MHz}$  central frequency antenna. The here presented algorithm was based on the spectral analysis of the GPR data in the frequency domain. As the finite-difference time-domain (FDTD) simulations confirmed, the frequency peak of the back-received spectrum was influenced by the size of the aggregates, if the resonance frequency was included in the spectrum frequency band. Thereby, after obtaining the frequency spectrum, it is possible to infer important geometric

information on the tested ballast, by means of the exponential equation given in Eq. 1.

To investigate how the ballast grading influences the electromagnetic response of the railway track-bed, an experimental activity was purposely performed. A methacrylate tank was filled up with limestone ballast aggregates and emptied out thrice. The GPR data were collected at the center of the formwork. The same test scenarios were investigated through an ad hoc automatic image analysis algorithm, aimed at reconstructing the grading curve of the material. The comparison between the characteristic diameter  $D^{*}$  and the grading curves (obtained by GPR and image analysis, respectively) showed how the geometrical feature is representative of the sieve with the  $70\%$  of retained material (actual sieving test).

It is important to emphasize on the innovation of the proposed approach in terms of integration between the GPR and the image analysis techniques and minimisation of destructive sampling for the assessment of the geometric features of the railway ballast.

# ACKNOWLEDGMENTS

The authors express their gratitude to Mr. Spartaco Cera for the invaluable help during the laboratory activities. Special thanks to IDS Georadar for supplying part of the GPR systems, and Clax Italia s.r.l. for manufacturing the methacrylate tank. This work has also benefited from the network activities carried out within the COST Action TU1208 "Civil Engineering Applications of Ground Penetrating Radar".

# REFERENCES

[1] B. Indraratna, "1st Ralph Lecture of ISSMGE. Railroad performance with special reference to ballast and substructure characteristics," Transportation Geotechnics, vol. 7, pp. 74-114, 2016.
[2] E.T. Selig, J.M. Waters, "Track geotechnology and substructures management," Thomas Telford, London, United Kingdom, 1994.
[3] J. Hugenschmidt, "Railway track inspection using GPR," Journal of Applied Geophysics, vol. 43, pp. 147-155, 2000.
[4] R. Roberts, A. Schultz, I.L. Al-Qadi, E. Tutumluer, "Characterizing railroad ballast using GPR: recent experiences in the Unites States", Proc. of the  $4^{\text{th}}$  international Workshop on Advanced Ground Penetrating Radar (IWAGPR 2007), Naples, Italy, 2007.
[5] D.J. Daniels, “Ground Penetrating Radar,  $2^{\mathrm{nd}}$  Edition,” IEE Radar, Sonar and Navigation Series, London, United Kingdom, 2016.
[6] A. Giannopoulos, "Modelling ground penetrating radar by GPRMax," Construction and Building Materials, vol. 19, no. 10, pp. 755-762, 2005.
[7] I.L. Al-Qadi, W. Xie, and R. Roberts, "Scattering analysis of groundpenetrating radar data to quantify railroad ballast contamination,"NDT&amp;E Int., vol. 41, pp. 441-447, 2008.
[8] A. Benedetto, F. Tosti, L. Bianchini Ciampoli, A. Calvi, M.G. Brancadoro, A.M. Alani, "Railway ballast condition assessment using ground-penetrating radar - An experimental, numerical simulation and modelling development," Construction &amp; Building Materials, vol. 140, pp. 508-520, 2017.
[9] EN 933-1:2012. Tests for geometrical properties of aggregates - Part 1: Determination of particle size distribution - Sieving method. European Committee for Standardization, 2012.