Construction and Building Materials 140 (2017) 508–520

ELSEVIER

Contents lists available at ScienceDirect

Construction and Building Materials

journal homepage: www.elsevier.com/locate/conbuildmat

Construction and Building MATERIALS

# Railway ballast condition assessment using ground-penetrating radar – An experimental, numerical simulation and modelling development

Andrea Benedetto $^{a}$, Fabio Tosti $^{b,*}$, Luca Bianchini Ciampoli $^{a}$, Alessandro Calvi $^{a}$, Maria Giulia Brancadoro $^{a}$, Amir M. Alani $^{b}$

$^{a}$ Department of Engineering, Roma Tre University, Via Vito Volterra 62, 00146 Rome, Italy
$^{b}$ School of Computing and Engineering, University of West London (UWL), St Mary's Road, Ealing, London W5 5RF, UK

# HIGHLIGHTS

- A GPR-based assessment of clean and fouled railway ballast.
- Four ballast/pollutant mixes analysed (100% clean ballast to highly-fouled (24%).
- Use of different GPR air-coupled antenna systems (1000 MHz and 2000 MHz).
- Use of several processing methods for assessing the ballast electric permittivity.
- Application of the RSA and the FDTD paradigms to the laboratory physical models.

# ARTICLE INFO

Article history:
Received 28 May 2016
Received in revised form 17 February 2017
Accepted 21 February 2017

Keywords:
Ground-penetrating radar
GPR
Non-destructive testing
Railway ballast
Ballast fouling
Volumetric mixing formula
Random-sequential adsorption (RSA)
paradigm
Finite-difference time-domain (FDTD)
simulation
gprMax

# ABSTRACT

This paper reports on the ground-penetrating radar (GPR)-based assessment of railway ballast which was progressively "polluted" with a fine-grained silty soil material. It is known how the proper operation of a ballast track bed may be undermined by the presence of fine-grained material which can fill progressively the voids between the ballast aggregates and affect the original strength mechanisms. This occurrence is typically defined as "fouling". To this effect, a square-based methacrylate tank was filled with ballast aggregates in the laboratory environment and then silty soil (pollutant) was added in different quantities. In order to simulate a real-life scenario within the context of railway structures, a total of four different ballast/pollutant mixes were introduced from 100% ballast (clean) to highly-fouled (24%). GPR systems equipped with different air-coupled antennas and central frequencies of 1000 MHz and 2000 MHz were used for testing purposes. Several processing methods were applied in order to obtain the dielectric permittivity of the ballast system under investigation. The results were validated using the "volumetric mixing approach" (available within the literature) as well as by performing a numerical simulation on the physical models used in the laboratory. It is important to emphasize the significance of the random-sequential absorption (RSA) paradigm coupled with the finite-difference time-domain (FDTD) technique used during the data processing. This was proved to be crucial and effective for the simulation of the GPR signal as well as in generating synthetic GPR responses close to the experimental data.

© 2017 Elsevier Ltd. All rights reserved.

# 1. Introduction

The structure of a traditional railway is typically constituted of steel rails fastened to the sleepers and laid on a coarse rocky material, i.e., the ballast. Railway ballast can be defined as a homogeneously graded material coming from the crushing of hard rocks or, seldom, of coarse gravel with small-sized particles sieved out. A railway track bed structure made of ballast aggregate particles is typically laid on the subgrade directly. In some configurations, a filter layer between the ballast and the subgrade, i.e., the sub-ballast, is also included. This is manufactured by smaller-sized soil materials, such as sand or gravel. Typically, the thickness of a track bed structure ranges between 0.45 m and 0.75 m. From a structural and operational point of view, the ballast/sub-ballast system accomplishes the tasks of dissipating the vertical, lateral and longitudinal stresses induced by the loads (i.e., trains passing on

http://dx.doi.org/10.1016/j.conbuildmat.2017.02.110

0950-0618/© 2017 Elsevier Ltd. All rights reserved.

the rails), and draining the meteoric water by means of the high percentage of air-filled voids [1].

The proper operation of a ballast track bed is ruled by the friction between the aggregates, which in turn is granted by their own angularity. This strength mechanism may be undermined by the presence of fine-grained material which can fill progressively the voids between the ballast aggregates. This occurrence is typically defined as “fouling” and may be related to three main factors, i.e. i) the segregation of the ballast aggregates under load, ii) the production of metal dust from the wheel/rail contact and iii) the rise of fine-grained materials from the subgrade by means of capillary actions. This last factor affects greatly the strength properties of the entire railway track bed, mostly in the case of clayey soil material which flows from the foundation level [2].

Although the modern railroads are provided of geotextiles between the ballast layer and the subgrade to avoid fouling in the rail track bed, most of the dated railway asset was not purposely designed and it is nowadays affected by this occurrence. Above certain levels, the ballast fouling can involve several issues such as the loss of regularity of the rails (reduction of the train speed) and the instability of the rail track (potential derailments). Thereby, the early-stage assessment of fouling is of paramount importance for railway managers in order to minimise the costs of maintenance and the risk of accidents. This concern implies the routine assessment of the geometric, physical and mechanical properties of the ballast/sub-ballast system and, accordingly, the effective detection of fouling. This operation is carried out traditionally in the laboratory environment according to international standard test methods [3], [4], [5], [6], [7], [8], [9], [10], [11], [12]. The application of these standards is extremely time-consuming, although the information retrieved are highly reliable. Similarly, the collection of ground-truth data by digging test pits has drawbacks in terms of time-efficiency and data representativeness. In view of the above, the use of time-efficient and cost-effective technologies may be an added value within the context of the effective management of railway infrastructures.

Within this framework, ground-penetrating radar (GPR) represents a powerful tool, which is being increasingly used for the rapid and non-intrusive assessment and the health monitoring of railways. This method relies on the electromagnetic (EM) theory and it has found major application in differing areas, such as civil and environmental engineering [13], archaeology [14], planetary explorations [15] and forensics [16]. According to Roberts et al. [17], the first GPR application in railway engineering dates back to 1985 [18] and involved the use of a low-frequency antenna system mounted over the interaxis of the rails. The low resolution of the system caused uncertainty in the interpretation of the results; thereby, later applications have focused more on the use of higher frequency antenna systems [19], [20], [21]. Several GPR-based models for the assessment of the railway ballast condition and the prediction of fouling can be found in the literature [22], [23], [24]. These models are mostly based on the processing of the actual GPR data collected in the real life/laboratory environment.

In this paper, several configurations of ballast/fine-grained pollutant mixes were first analysed electromagnetically in the laboratory environment using different signal processing techniques. Subsequently, a novel numerical-simulation-based methodology was developed for the validation of the results.

It is important to emphasize the relevance of the proposed methodology in terms of the achievable efficiency in the investigation of the railway ballast condition. Indeed, the complex own nature and the highly variable physical-mechanical conditions of the railway ballast aggregates within a rail track bed may require the use of specialist antenna frequencies in combination with dedicated signal processing techniques. Within this context, the use of the simulation technique may provide invaluable support in the interpretation of the fouling process. The thorough assessment of the main geometric, mechanical and physical properties of the ballast and the pollutant material carried out in the laboratory, represented a comprehensive source of ground-truth data for the calibration and the validation of the proposed methodology. Information such as the grain size of the particles, the mineralogy and the compaction rate between the aggregates allowed to reproduce effectively the numerical simulation domain of the rail track bed as well as to obtain a reliable validation of the results. In addition, the use of differing antenna systems and frequencies of investigation allowed to demonstrate the actual applicability of the discussed methodology as well as to select the antenna frequencies suited for the purpose.

## Objectives and methodologies

This paper reports on the EM assessment of railway ballast in both clean and fouled conditions using different signal processing methods. A new numerical simulation methodology was also introduced. Four configurations of ballast aggregate particles and pollutant fine-grained silty soil material were manufactured within a square-based methacrylate tank representing a railway ballast layer of a track bed structure. At each step of the fouling process, the data were collected using several GPR systems equipped with different air-coupled antennas and central frequencies of 1000 MHz and 2000 MHz. Various processing methods were performed for the computation of the dielectric permittivity of the ballast system. The results were obtained by using several models available within the literature. In addition, a new numerical simulation methodology based on the combination of the random-sequential adsorption (RSA) and the finite-difference time-domain (FDTD) paradigms was presented. The remainder of this paper is organized as follows. In Section 3, the EM basics and the main working principles behind the GPR technique are discussed. Section 4 focuses on the experimental design, the laying out of the laboratory setup and the main standard test methods followed for the assessment of the main geometric, physical and mechanical properties of the investigated materials. The results of the GPR surveys are presented in Section 5, where the values of the relative dielectric permittivity computed by the time-domain signal picking (TDSP) technique, the surface reflection method (SRM) and the volumetric mixing formula (VMF) approaches (across the various ballast/pollutant scenarios) are compared each to one another. The outcomes of the aforementioned simulation-based methodology obtained by the use of the 1000 MHz antenna frequency data are therefore analysed. Conclusion and future perspectives are discussed in Section 6.

## The GPR method

GPR is a geophysical non-destructive technique based on the transmission of an EM impulse towards a generic surface and the reception of the back-reflected signal. When the EM wave tackles an electric discontinuity (e.g. the interface between two geological formations or road pavement layers), part of the energy gets reflected, whereas the remaining part gets transmitted and travels throughout the material before being absorbed. Therefore, it is possible to retrieve information about the subsurface non-destructively by the interpretation of the back-reflected signal.

From a theoretical standpoint, the EM behaviour of the surveyed material is ruled by its dielectric and magnetic properties, i.e. the relative dielectric permittivity ε, the electric conductivity σ and the magnetic permeability μ [25]. The values of ε and σ greatly influence the velocity and the attenuation of the wave propagation, respectively, whereas μ does not affect the EM

With regard to the case of a multi-phase material (such as the ballast aggregate/air mix in a railway track bed), the overall EM behaviour is influenced by the electric properties of each phase. In particular, as the air and the free water components represent opposite edge values in terms of conductivity and permittivity, their rates within the mixed material affect highly the overall electric behaviour of the multi-phase medium. In view of this, the grain size distribution and the voids index of the mix are important in determining the values of the electric parameters, as they are directly related to the presence of air and free water.

With regard to the hardware structure of a pulsed GPR system, it is broadly constituted by a control unit generating a fixed EM impulse and one or more antennas containing the transmitter (Tx) and the receiver (Rx) units. A radar system is configured as mono-static when a unique antenna operates as both Tx and Rx. In the case of separated Tx and Rx, the GPR system is defined as bi-static. In addition, the GPR systems can be sorted in ground-coupled and air-coupled based on the type of the antenna. In ground-coupled GPR systems, the antenna is directly in contact with the ground and allows a deeper penetration in the medium. Central frequencies available for this configuration usually range from 80 MHz to 2000 MHz. In the case of air-coupled systems, the antenna is typically kept at a constant height above the surface, which can range from 0.15 m to 0.50 m. The most common air-coupled GPR systems are pulsed systems operating in the range 500÷2500 MHz, with a central frequency of typically 1000 MHz. The resolution of the collected signal and the signal penetration mainly depend on the frequency of investigation.

Applications of GPR in railway engineering are typically performed using air-coupled radar systems and central frequencies between 500 MHz and 2500 MHz [26].

## Experimental framework

### Experimental design

The experimental design was aimed at assessing the main geometric, mechanical, physical and the EM properties of the investigated railway ballast and the pollutant soil material using traditional standard test methods and differing GPR antenna systems. To this purpose, a laboratory setup was developed at the Department of Engineering of Roma Tre University, Rome, Italy. A methacrylate tank with dimensions reproducing a typical railway ballast layer (full scale) was filled up with limestone-derived ballast aggregates, with a growing percentage by weight of pollutant material. At each pollution level, GPR tests were carried out by using the available set of air-coupled antenna systems in order to investigate the influence of fouling on the EM behaviour of the reproduced ballast layer.

### Materials: assessment of the main geometric, mechanical and physical properties

The assessment of the main geometric, mechanical and physical properties of the investigated materials was performed in compliance with three principal objectives: i) classifying and verifying the consistency of these materials with the main international standards and regulations for the construction of railway track beds, ii) assessing and controlling the geometric, mechanical and physical properties of the ballast aggregates which can be relevant in EM inspections and iii) ensuring the repeatability of the tests for future comparisons of the results.

### Railway ballast

Limestone aggregates typically employed for the construction of ballasted railroads were used for testing purposes. Within the international scenario of standards and practices in the field, the EN 13450:2002/AC:2004 standard [3] is the principal benchmark at the European level. The standard requires a comprehensive amount of information about the geometric, mechanical and physical properties that the railway ballast layer must comply with in a rail track bed. The most relevant parameters considered in this standard were selected herein and the corresponding (specific) standards were followed to assess the investigated material in terms of particle size distribution [4], content of fine particles [4], particle length [3] and shape index [5], resistance to fragmentation [6] and particle density [7]. Further mechanical and physical properties relevant to the interpretation of the results, such as the content of voids [8] and water [9], were also evaluated. Both of these latter parameters may affect the value of the relative dielectric permittivity of a multi-phase medium. This is much more evident in the case of coarse-grained material, such as the railway ballast layer, where the index of voids is a relevant component. The values found for all the above parameters are listed in Table 1.

With regard to the geometric properties, the grain size of the ballast was classified as the finest-grained class out of the six identified by the EN 13450:2002/AC:2004 standard [3], i.e. class A within the main category of the aggregate dimensions 31.5 mm÷50 mm. The content of fine particles passing the 0.063 mm sieve size was calculated according to the sieving procedures described in the EN 933-1:2012 standard [4]. This parameter turned out to be equal to 0.5%; hence, it can be classified as a very low value. The tests run for the classification of the particles length [5] provided a rate of 5.5% by weight of aggregates with length ≥ 100 mm. To this purpose, 40 kg of ballast material were sampled. The shape index SI was evaluated according to the EN 933-4:2008 standard [5] as follows:*S**I* = (*M*_{2}/*M*_{1}) × 100

where M_{1} is the weight of the whole ballast sample [g], made of minimum 100 aggregates, and M_{2} is the weight of the non-cubic ballast samples [g] (i.e. where the ratio between the particle length L and the particle thickness E is greater than 3). This index was found to be 20%, thereby proving an average amount of too long particles as well as an average level of heterogeneity in the aggregate particle shapes of the ballast.

With regard to the assessment of the main mechanical and physical properties, two further parameters are provided in the EN 13450:2002/AC:2004 standard [3]: the resistance to fragmentation LA_{BB} and the particle density ρ_{s}. The specific technical procedures for the above standards are described within the EN 933-4:2008 [5] and the EN 1097-6:2013 [7] documents, respectively. The resistance to fragmentation was assessed by the Los Angeles test method using the relevant equipment indicated in the EN 1097-2 standard [6] and following the changes to the test method included in the EN 13450:2002/AC:2004 standard [3]. This was due to the larger grain size of the ballast aggregates with respect to the fine-grained soil material which is usually tested by this method. The Los Angeles abrasion index LA_{BB} was evaluated as follows:$$LA_{BB} = \frac{10000 - m}{100}$$where m [g] measures the mass of material segregated, as indicated by Eq. (3):*m* = (*m*_{50 - 31.5})_{10*k**g* - *B*} - (*T*_{1.6})_{*A*}being (*m*_{50 - 31.5})_{10*k**g* - *B*} the 10 kg mass of the material sieved before running the Los Angeles test with grain size comprised between 31.5 mm and 50 mm, and T_{1.6} the material retained on the 1.6 mm sieve, after running the Los Angeles test. The LA_{BB} index

A. Benedetto et al./ Construction and Building Materials 140 (2017) 508-520

Table 1 Geometric, mechanical and physical properties of the ballast aggregates assessed in the laboratory environment.

|  Ballast property |   | Regulation |   | Reference unit | Value | Class  |
| --- | --- | --- | --- | --- | --- | --- |
|  Geometric | Grain size | EN 13450:2013 [3] | EN 933-1:2012 [4] | % passing vs. sieve size (mm): 80-63-50-40-31.5-22.4 | 100-100-79.9-30.6-1.2-0.3 | A  |
|   |  Fine particles content |  | EN 933-1:2012 [4] | % passing vs. sieve size (mm): 0.063 | 0.5 | A  |
|   |  Particle length |  | EN 933-4:2008 [5] | % | 5.5 | B  |
|   |  Shape index - SI - |  | EN 933-4:2008 [5] | % | 20.0 | SI20  |
|  Mechanical & physical | Resistance to fragmentation - LAM - |  | EN 1097-2:2010 [6] | % | 20.0 | LAM 20  |
|   |  Particle density - ρs - |  | EN 1097-6:2013 [7] | g/cm3 | 2.8 | /  |
|   |  Percentage of voids - φ - | EN 1097-3:1998 [8] |  | % | 39.0 | /  |
|   |  Water content - w - | CEN ISO/TS 17892-1:2005 [9] |  | % | 0.2 | /  |

The particle density  $\rho_{s}$  was evaluated according to both the wire basket (Fig. 1) and the pycnometer methods for, respectively, the aggregate particles passing the  $63\mathrm{mm}$  test sieve and retained on the  $31,5\mathrm{mm}$  test sieve, and the aggregate particles passing the  $31.5\mathrm{mm}$  test sieve and retained on the  $4\mathrm{mm}$  test sieve. An average value of  $2.8\mathrm{g/cm^3}$  was found, in line with the literature reference on limestone ballast stones.

In addition to the above mechanical and physical properties included in the EN 13450:2002/AC:2004 standard test method [3], the evaluation of the percentage of intergranular voids was carried out according to the EN 1097-3:1998 standard [8]. The index found was cross-checked by weighing the distilled water

content which filled the inter-particle voids of a number of sampled ballast aggregates. These were arranged within a laboratory formwork of known volume (Fig. 2). By correlation of the weight collected for the distilled water to the water density (modified as a function of the room temperature), it was found a value of  $39\%$  for the voids parameter. This value agrees with the benchmark value indicated by Sussmann et al. [27] in the case of loose ballast aggregates.

Furthermore, the value of the water content parameter  $w$  was assessed according to the CEN ISO/TS 17892-1:2005 standard [9]. This standard was used for the evaluation of the moisture of the ballast aggregates taken from the quarry and the assessment of

![img-0.jpeg](img-0.jpeg)

![img-1.jpeg](img-1.jpeg)

![img-2.jpeg](img-2.jpeg)

![img-3.jpeg](img-3.jpeg)
Fig. 1. Test procedure for the wire basket method [7]: (a) sampling and measurement of the aggregates by calibre; (b) cleaning and removal of fine particles within the number of aggregates retained on the  $63\mathrm{mm}$  and the  $31,5\mathrm{mm}$  test sieves; (c) water-soaking of the sampled ballast aggregates; (d) measurement of the apparent weight of the material soaked in water by a hydrostatic weighing table; (e) drying of the sampled material by means of an absorbent tissue; (f) drying of the sampled material by oven at  $110\mathrm{C}^{\circ}$  until the achievement of a constant weight of the aggregates.

![img-4.jpeg](img-4.jpeg)

![img-5.jpeg](img-5.jpeg)

A. Benedetto et al./ Construction and Building Materials 140 (2017) 508-520

![img-6.jpeg](img-6.jpeg)
Fig. 2. Distilled water filling the inter-particle voids of the ballast aggregates within a test formwork. This operation was part of the laboratory procedures carried out for the evaluation of the percentage of intergranular voids.

the time required for drying the materials and performing the experimental tests at controlled room conditions. The water content $w[\%]$ was calculated as follows:

$$
w = \frac {m _ {1} - m _ {2}}{m _ {2} - m _ {c}} \times 100 = \frac {m _ {v}}{m _ {d}} \times 100 \tag {4}
$$

where $m_{1}$ [g] is the mass of the container and the moist test specimen, $m_{2}$ [g] is the mass of the container and the dried test specimen, $m_{c}$ [g] is the mass of the container, $m_{v}$ [g] and $m_{d}$ [g] are, respectively, the water and the dried test specimen masses. Three samples were collected at three random locations within the storage of the aggregates available from the quarry. A reference value of $w$ equal to $0.2\%$ was found for the ballast aggregates used in this study.

## 4.2.2. Pollutant soil material

A fine-grained loose soil material was used for pollution of the clean ballast aggregates in order to reproduce various fouling conditions. The most important geometric (i.e., the grain size), mechanical and physical properties (i.e., plasticity, particle density, water content at room temperature) were determined in the laboratory environment (Fig. 3). The relevant values are listed in Table 2.

Grain size analyses [4] (Fig 3(a-b)) and plasticity tests [10] (Fig. 3(c)) were performed to identify the class of the material within the framework of the American Association of State Highway and Transportation Officials (AASHTO) soil classification [11]. The percentage of soil particles passing the $0.075\mathrm{mm}$ sieve size was found to be greater than $35\%$. The liquid limit $L_{L}$ and the plastic index $I_{P}$ were equal to $24.6\%$ and $7.6\%$, respectively. The above values allowed to classify the pollutant as a silty soil material within the A4 AASHTO group.

The particle density $\rho_{s}$ of the pollutant material is an important parameter for the investigation of the EM response of the soil

![img-7.jpeg](img-7.jpeg)

![img-8.jpeg](img-8.jpeg)
Fig. 3. Tests performed in the laboratory environment for the assessment of the pollutant soil material properties: (a) samples preparation; (b) soil particles sieving under water flow (grain size analysis) [4]; (c) cutting of a standard groove into the molded material with a test-specific knife (soil plasticity test) [10]; (d) boiling of the immersed specimen for deaeration (particle density evaluation test) [12].

A. Benedetto et al./ Construction and Building Materials 140 (2017) 508-520

Table 2 Geometric, mechanical and physical properties assessed in the laboratory environment for the pollutant soil material.

|  Soil loose material property |   | Regulation | Reference unit | Value | Class  |
| --- | --- | --- | --- | --- | --- |
|  Geometric | Grain size | EN 933-1:2012 [4] | % passing vs. sieve size (mm): 4.75–2–0.425–0.075 | 100–99.6–99.4–84.7 | A4 - AASHTO - [11]  |
|  Mechanical & physical | Liquid limit - L1- | ASTM D4318-10e1 [10] | % | 24.6 |   |
|   |  Plastic index - lp- | EN ISO 17892-3:2015 [12] | g/cm3 | 7.6 |   |
|   |  Particle density - ρs- | EN ISO/TS 17892-1:2005 [9] | % (cm3/cm3) | 2.5 | /  |
|   |  Water content - w (θ)- |  |  | 2.5 (4.0) | /  |

[28,29]. Furthermore, it was widely used in the literature for the assessment of several indexes of fouling [30,31]. In this study, the particle density was determined according to the EN ISO 17892-3:2015 standard [12] (Fig. 3(d)) and evaluated as follows:

$$
\rho_ {s} = \frac {p}{p + p _ {2} - p _ {1}} \cdot \rho_ {w} \tag {5}
$$

being  $p$  the dry mass of the specimen,  $p_1$  the mass of the pycnometer, completely filled with the saturated specimen and the control liquid;  $p_2$  the mass of the pycnometer, completely filled with the control liquid;  $\rho_w$  the density of the control liquid (differing values are given in the norm as a function of the temperature  $T$ ). The average of the results obtained from three tests has provided a value of  $2.5\mathrm{g/cm^3}$  for  $\rho_s$ .

The environmental water content of the silty soil  $w$  was determined after oven drying all the material and leaving this at room temperature and ambient humidity for seven days. The soil moisture was then evaluated according to the CEN ISO/TS 17892-1:2005 standard [9] and turned out to be  $2.5\%$  (i.e.,  $\theta = 4\mathrm{cm}^3 /\mathrm{cm}^3$ ).

## 4.3. GPR equipment

The experimental tests were performed using three air-coupled pulsed radar systems [32] all manufactured by IDS Georadar (Fig. 4), with central frequencies of  $1000\mathrm{MHz}$  (RIS Hi-Pave HR1 1000), and  $2000\mathrm{MHz}$  (RIS Hi-Pave HR1 2000 and 2000 NA). Time windows of 25 ns and 15 ns were set for the  $1000\mathrm{MHz}$  and the  $2000\mathrm{MHz}$  systems, respectively. With regard to the  $2000\mathrm{MHz}$  radar systems, one ordinary (i.e.,  $2000\mathrm{MHz}$  EU) and one low-powered (i.e.,  $2000\mathrm{MHz}$  NA) version of the horn antennas for the European (EU) and the North-American (NA) markets, respectively, were used for testing purposes. Nominal resolutions (the quarter-wavelength criterion) of  $7.5\times 10^{-2}\mathrm{m}$  and  $3.75\times 10^{-2}\mathrm{m}$  can be reached by the  $1000\mathrm{MHz}$  and  $2000\mathrm{MHz}$  antenna systems, respectively. These comply satisfactorily with the aggregates particle size, roughness, voids content as well as with the fouling scenarios that were reproduced.

## 4.4. Laboratory setup and testing

### 4.4.1. Testing equipment

The railway ballast aggregates were investigated within a square-based methacrylate tank, with an outer base side and height of, respectively,  $1.55\mathrm{m}$  and  $0.55\mathrm{m}$  (Fig. 5), and inner dimensions of  $1.47\mathrm{m}$  for the base side and  $0.48\mathrm{m}$  for the height. A number of preliminary investigations were performed to determine the most suitable manufacturing material (i.e., methacrylate) and the dimensions of the tank, in order to i) provide data consistent with real-life scenarios and the arrangement of railway ballast aggregates; ii) reproducing effectively the action of relevant physical agents which may affect the mechanical behaviour of the railway ballast layer; iii) avoiding any edge effects which may cause noise disturbance to the EM signal; iv) allowing direct observation of both the aggregates/pollutant-soil arrangement and the progress of the physical-mechanical occurrences in the tank.

The height of the tank was selected according to typical design thicknesses for granular ballast layers. These usually range between  $0.45\mathrm{m}$  and  $0.75\mathrm{m}$  [33]. In addition, the average dimension and roughness of the used aggregates along with the reference size of the inter-particle voids were taken into account for design purposes. The width and depth of the tank were established after the evaluation of the antennas' footprints as per the information provided by the manufacturer. Further experimental tests were carried out to confirm the given data. To this purpose, analyses of the boundaries of the noise effects to the signal were performed and a reference GPR standard on air-coupled radar systems [34] was followed. The tank dimensions (width and depth) also comply with the planimetric dimensions of common track beds, when considering the distance between the rails as well as the length of the sleepers [35].

The tank was laid above a  $2\mathrm{m} \times 2\mathrm{m}$  copper-made perfect electric conductor (PEC) sheet, which allowed to reflect completely the waves propagating through the investigated material [36]. Indeed, the use of a PEC avoids the propagation of the EM waves through the floor and prevents to illuminate possible sources of noise such as the structural concrete or the reinforcement bars embedded in the ground of the laboratory.

Calibration measurements complying with the ASTM D6087-08 standard [34] were performed and a reference distance of  $0.40\mathrm{m}$  between the bottom of each GPR apparatus and the PEC was set.

### 4.4.2. Procedures for materials layout

The considerable size of the investigation domain and the relevant quantity of ballast aggregates ( $\sim 1500\mathrm{kg}$ ) and pollutant soil material (from  $\sim 250\mathrm{kg}$  to  $\sim 800\mathrm{kg}$ , depending on the fouling level) to manage, have led developing preliminary "small-scale" laboratory procedures. These have favoured standardizing the mechanical and physical conditions that were reproduced subsequently for the material within the entire volume of the tank.

To ensure the effective distribution and uniformity of the pollutant material within the ballast inter-particle voids, a wooden square grid mesh of 16 quadrants with  $0.35\mathrm{m}$  sides (Fig. 6(a)) was equipped with a  $4\mathrm{mm}$ -size sieving grid (Fig. 6(b)).

Once the silty soil was distributed within the wooden support quadrants, compaction and filling of the intergranular voids were obtained by using a hammer drill equipped with a square-shaped drill bit (Fig. 7(a)). To this purpose, a dedicated laboratory procedure was preliminarily implemented in a small-scale formwork with dimensions comparable to those of the above quadrants (Fig. 7(b-f)). In addition, the time required for reaching the maximum compaction of the silty material with the above hammer drill was evaluated. In this regard, the maximum value of dry density  $\rho_{d}$  was reached after  $10\mathrm{s}$  of vibration induced by the hammer.

To make the results from the proposed compaction procedure comparable to the outcomes of the relevant standard test methods, the energy of compaction spent with the hammer drill was compared to the same parameter achieved with i) the Proctor test for mixes compacted with a  $2.5\mathrm{kg}$  rammer in the Proctor mould and ii) the Modified Proctor test for mixes compacted with a  $4.5\mathrm{kg}$  rammer in the large Proctor mould [37]. The overall compaction

A. Benedetto et al./ Construction and Building Materials 140 (2017) 508-520

![img-9.jpeg](img-9.jpeg)
Fig. 4. Air-coupled GPR antenna systems used for the experimental surveys.

![img-10.jpeg](img-10.jpeg)
Fig. 5. Laboratory setup used for the GPR tests.

![img-11.jpeg](img-11.jpeg)
Fig. 6. Equipment for ensuring the effective distribution of the pollutant material within the railway ballast inter-particle voids: (a) wooden square grid mesh of 16 quadrants with  $0.35\mathrm{m}$  sides; (b)  $4\mathrm{mm}$ -size sieving grid.

A. Benedetto et al./ Construction and Building Materials 140 (2017) 508-520

![img-12.jpeg](img-12.jpeg)

![img-13.jpeg](img-13.jpeg)

![img-14.jpeg](img-14.jpeg)

![img-15.jpeg](img-15.jpeg)

![img-16.jpeg](img-16.jpeg)

Fig. 7. Compaction procedures carried out on a small-scale formwork: (a) hammer drill equipped with a square-shaped drill bit; (b) placement and levelling of the dry silty soil material within the test formwork; (c) addition of the extension collar and connection to the formwork by means of a metal connector to prevent material waste during compaction; (d) induction of 10 s steps of vibration by resting the square-shaped drill bit to the formwork cover cap; (e) removal of the cover cap and (f) measurement of the induced subsidence.

![img-17.jpeg](img-17.jpeg)

energy per unit volume spent with the hammer amounted to $1.04 \times 10^{6} \mathrm{~J} / \mathrm{m}^{3}$, whereas values of $0.59 \times 10^{6} \mathrm{~J} / \mathrm{m}^{3}$ and $2.68 \times 10^{6} \mathrm{~J} / \mathrm{m}^{3}$ were found for the Proctor and the Modified Proctor tests, respectively. In view of the obtained values of energy, it can be argued that the compaction procedure here proposed ranked between the Standard and the Modified Proctor test.

## 4.4.3. Test scenarios

Four main configurations (Table 3) were manufactured in the laboratory environment. In all of these scenarios, the material investigated filled the entire inner tank height $h$ of $0.48\mathrm{m}$.

Starting from the clean ballast condition (i.e., Test scenario 0), the fouling was reproduced by layers of a mix between the

pollutant A4 silty soil and the ballast aggregates. The height of this mix was progressively increased by steps of $0.10\mathrm{m}$. Mixing and compaction of the materials were performed according to the procedures discussed in Section 4.4.2. The above fouled configurations

Table 3 Configurations of the ballast-pollutant mixes investigated in the laboratory.

|  Test scenario | Height of the ballast-pollutant mix [m] | Configuration [m]  |
| --- | --- | --- |
|  0 | 0.48 | 0.48 m Clean Ballast (CB) [no Fouled Ballast (FB)]  |
|  I | 0.48 | 0.10 m FB + 0.38 m CB  |
|  II | 0.48 | 0.20 m FB + 0.28 m CB  |
|  III | 0.48 | 0.30 m FB + 0.18 m CB  |

A. Benedetto et al./ Construction and Building Materials 140 (2017) 508-520

![img-18.jpeg](img-18.jpeg)

![img-19.jpeg](img-19.jpeg)
Fig. 8. (a) Methacrylate tank filled with clean ballast aggregates; (b) all-in-one image of the four scenarios merged together (the dashed lines separate the clean (top) from the uniformly-fouled (bottom) ballast layer).

were set to be representative of low (i.e.,  $0.10\mathrm{m}$  of fouled ballast (FB) - Test scenario I), medium (i.e.,  $0.20\mathrm{m}$  of FB - Test scenario II) and high (i.e.,  $0.30\mathrm{m}$  of FB - Test scenario III) levels of fouling within the ballast layer of a railway track bed.

A loop laboratory procedure was followed for the manufacturing of the four scenarios. Starting from no-fouled ballast conditions (i.e., Test scenario 0), the clean ballast aggregates were removed from the top of the tank at progressively lower amounts each more step, up to reaching the wanted height of the fouled layer. Therefore, mixing and compaction procedures were carried out. Afterwards, the clean ballast aggregates were placed again above the compacted fouled layer of ballast up to filling the entire height of the tank. The above "emptying and filling" loop was repeated until the conditions of scenario III were reached. The GPR surveys

with the three aforementioned air-coupled antenna systems were performed at each of the above reproduced scenarios.

Fig. 8 shows the tank filled with clean ballast aggregates (Fig. 8(a)) and an all-in-one image of the above four configurations merged together (Fig. 8b)).

# 5. Results

# 5.1. Relative dielectric permittivity estimate by signal processing methods

In order to minimise the stochastic variability of the signals, a number of 100 traces were collected at each reproduced scenario

![img-20.jpeg](img-20.jpeg)
Fig. 9. Average traces obtained for the four tested scenarios. Line styles indicate the different scenarios, whereas the markers point out the position of the reflection peaks at the interfaces between the air-ballast and the ballast-metal plate.

A. Benedetto et al./ Construction and Building Materials 140 (2017) 508-520

and the average trace was computed. In view of this, one unique (average) A-scan was related to each tested configuration. The average traces representative of the four investigated scenarios are depicted in Fig. 9. Thereby, the value of the relative dielectric permittivity $\varepsilon_{\mathrm{r}}$ of the ballast/air/pollutant mix was inferred from each of these traces using differing processing techniques.

The time-domain signal picking (TDSP) technique [38] accounts for the time interval between the reflection peaks of the first (air/ballast) and the last interface (ballast/PEC), i.e., the two-way travel time $t$ taken by the EM wave for propagating through the material. Since the thickness $h$ of the tank was known, it was possible to infer the propagation speed $v = 2h / t$, hence, the relative dielectric permittivity as follows:

$$
\varepsilon_ {\mathrm {r}} = \left(\frac {c _ {0}}{v}\right) ^ {2} \tag {6}
$$

with $c_{0}$ being the speed of light.

The surface reflection method (SRM) [39] is based on the comparison between the amplitude $A_0$ of the reflection peak from the air/surface interface, and the reference amplitude $A_{\mathrm{PEC}}$ reflected by a metal plate (perfect electric conductor (PEC)) larger than the GPR footprint. The relevant relationship is expressed as follows:

$$
\varepsilon_ {\mathrm {r}} = \left[ \frac {\left(1 + \frac {A _ {0}}{A _ {\mathrm {P E C}}}\right)}{\left(1 - \frac {A _ {0}}{A _ {\mathrm {P E C}}}\right)} \right] ^ {2} \tag {7}
$$

In order to reach the maximum accuracy in the estimation of the permittivity, both the amplitudes must be recorded at the same height from the reflector. In this regard, it is worth to emphasize the difficulty to reach a stable value for the height during the operations. This is due to the size and the rough shape of the ballast aggregates which cannot provide a smooth reflection interface.

## 5.2. Relative dielectric permittivity estimate by theoretical models

The volumetric mixing formula (VMF) approach [40] was performed to compute the dielectrics using a theoretical multiphase modelling of the investigated scenarios. This method requires the knowledge of both the relative dielectric permittivity $\varepsilon_{\mathrm{r,i}}$ and the corresponding volumetric fraction $f_{i}$ of each ith component of the $n$-phase mix. These parameters are arranged in the linear combination given by Eq (8):

$$
\varepsilon_ {\mathrm {r}} ^ {\alpha} = \sum_ {i = 1} ^ {n} f _ {i} \varepsilon_ {\mathrm {r}, i} ^ {\alpha} \tag {8}
$$

with $\alpha$ being a geometric fitting parameter, whose values were investigated in the literature [41-44]. In this study, a value of 0.5 was used for the $\alpha$ factor. Table 4 lists the parameters set in Eq. (8).

The values of the dielectric permittivity of the ballast (i.e., the dielectrics of the source limestone-derived rock) and the methacrylate were derived from the literature [45]. The dielectric permittivity of the A4 silty soil was computed by the application of the TDSP technique on the GPR data collected within a $0.10\mathrm{m}$ height layer of this material (laid out within the (same) empty methacrylate tank).

Table 4 Values of the parameters set in Eq. (8).

|  ith Component | εr,i | f_i(EL H)* | f_i(EL I) | f_i(FL H) | f_i(FL IR)  |
| --- | --- | --- | --- | --- | --- |
|  Ballast | 6.50 | 0.53 | 0.53 | 0.53 | 0.53  |
|  A4 Soil | 5.03 | 0.00 | 0.08 | 0.16 | 0.24  |
|  Methacrylate | 4.00 | 0.08 | 0.08 | 0.08 | 0.08  |
|  Air | 1.00 | 0.39 | 0.31 | 0.23 | 0.15  |

* FL - Fouling Level.

## 5.3. Methods comparison

Comparisons between the outcomes of each of the above two signal processing-based methods and the VMF are given in Fig. 10. The results obtained from the full set of used antenna frequencies are depicted.

With regard to the permittivity estimates by the TDSP technique (Fig. 10(a)), it is worth noting the overall good agreement between the dielectrics achieved in all the case-scenarios across the full set of used frequencies. Values of permittivity comprised between 3.51 and 5.35, which raise consistently with the increasing levels of fouling, were observed. This behaviour agreed with the theoretical assumption, since increasing rates of air voids $(\varepsilon_{\mathrm{r,a}} = 1)$ were progressively filled with the pollutant material, which was characterised by a higher permittivity value (i.e., $\varepsilon_{\mathrm{r}} = 5.03$). Thereby, the relative dielectric permittivity of the whole multi-phase system tended to increase. These results and the overall trend of permittivity values versus the level of fouling were

![img-21.jpeg](img-21.jpeg)

![img-22.jpeg](img-22.jpeg)
Fig. 10. Relative dielectric permittivity estimates from (a) the TDSP technique (acquisitions made with the $1000\mathrm{MHz}$, $2000\mathrm{MHz}$ EU and $2000\mathrm{MHz}$ NA antenna systems) and the VMF, and (b) the SRM ($1000\mathrm{MHz}$, $2000\mathrm{MHz}$ EU and $2000\mathrm{MHz}$ NA antenna systems) and the VMF.

well confirmed by the volumetric approach. The modulus of the incidences of the residuals (i.e. the percentage ratio of the difference between the VMF and the TDSP permittivity values (numerator), and the corresponding dielectrics by the VMF (denominator)) was comprised between 0.10% and 6.90%. In addition and with respect to the trend of the estimates obtained across the four investigated scenarios, the permittivity values retrieved with the TDSP were overall lower than the corresponding VMF values. Exceptions were the estimates reached with both the 2000 MHz systems in the clean condition (i.e. scenario 0) and the permittivity retrieved with the 1000 MHz GPR in the highly-fouled condition (i.e. scenario III).

On the contrary, the outcomes from the application of the SRM were not consistent with the VMF estimates such as in the case of the TDSP technique. From Fig. 10(b), it is clear how the SRM approach provided lower values of permittivity with respect to both the VMF and the TDSP techniques, and proved to be not suitable to assess both the clean and the fouled ballast condition across all the investigated scenarios. A possible motivation for this mismatching lies within the amplitude-based nature of the own method and the coarse grain-size and rough shape of the ballast aggregates. Indeed, the SRM relies on the value of the first-peak amplitude of the collected signal, which in turn depends on several factors including the configuration of the air-surface interface. In this regard, it is worth mentioning that the surface configuration of the four scenarios (i.e. the arrangement of the clean ballast aggregates at the top of the tank) has changed in all the investigated cases, due to the requirements of the testing protocol for laying out the material (i.e. Section 4.4.3). In addition, it is well-known how the wavelength of the signal is a critical survey parameter mostly in the case of railway ballast, due to the variability of the dimension and shape of the aggregates, as well as of the volume of the air-filled voids (which can vary according to the fouling level). The consistency between the wavelength of a GPR signal and the dimension of the targets in a railway track bed (e.g. the ballast aggregates or the air voids) can generate considerable scattering patterns and it can affect, amongst the other, the first-peak amplitude of the signal. As a rule of thumb, the lower is the frequency of the investigation, the longer is the signal wavelength, the smaller will be the scattering generated by the ballast aggregates and the air voids. In such a case, the energy extracted to the signal will be lower [24], [46]. According to the wavelengths of the two central frequencies used in this study, it can be seen how the highest permittivity values closer to the above VMF (and TDSP) permittivity estimates (which are both expected to well approximate the searched dielectrics), were reached by the 1000 MHz antenna system (Fig. 10(b)). Indeed, this was due to the longer wavelength and the lower sensitivity of this antenna frequency towards the rough shape of the surface aggregates and the dimensions of the air voids. This fact generated less scattering and lower impact on the first-peak amplitude of the signal. Thereby, permittivity estimates much closer to the expected ones were reached.

### Validation through the numerical simulation

A new simulation-based methodology was introduced for generation of the synthetic GPR response from the investigated experimental scenarios and the validation of the results discussed in Section 5.3.

A combined approach that uses the random-sequential adsorption (RSA) paradigm [47] and the finite-difference time-domain (FDTD) technique [48], [49], [50] was implemented for the simulation of the GPR signal. The RSA paradigm was first used for generating random bi-dimensional (2-D) distributions of the compacted ballast aggregates, which were schematically represented by a comprehensive set of circumferences with different diameters. The RSA algorithm followed two main steps. As a first mandatory selection condition, the grain size distribution of the circumferences needed to comply with the experimental (actual) one (i.e. Table 1). As a result, the algorithm provided a number of 200 circumferences, on the average, with diameters ranging from 2.5·10^{-2} m and 8·10^{-2} m. The second step of the RSA algorithm allowed compacting the circumferences along the vertical axis to ensure the contacts between the aggregates and reach a content of voids equal to 39%. This value was constrained to the actual value obtained from the relevant standard test method performed in the laboratory [8].

Afterwards, the generated 2-D scenario was simulated using the FDTD technique implemented in the gprMax 2D simulator package [51]. The physical structure of the GPR antenna was not included in the model. The real test environment was reproduced by positioning a source of line of current in the free space at a height by the target equal to the actual height of the antenna source. The exact test domain was accurately designed with respect to the size of the tank, the layers composing the investigated multi-phase system (ballast/methacrylate/PEC) and the electric properties of the materials involved (Fig. 11). Detailed information about the simulation can be found in Benedetto et al. [52].

At the current stage of the research, the GPR signals obtained across the full set of scenarios using the 1000 MHz central frequency were simulated. In Fig 12 the comparison between the measured and the simulated signals is shown for each combination of ballast and pollutant material. The overall relatively good matching between the radar sweeps indicates a substantial reliability of the used simulation-based approach. In addition, the good agreement between the measured and simulated signals (in terms of time distance between the first (i.e. air-ballast interface) and the last (i.e. ballast-PEC interface) peak) allowed to validate the values of the relative dielectric permittivity computed for the whole set of scenarios using the TDSP technique (i.e. Fig. 10(a)).

A. Benedetto et al./ Construction and Building Materials 140 (2017) 508-520

![img-23.jpeg](img-23.jpeg)

![img-24.jpeg](img-24.jpeg)

![img-25.jpeg](img-25.jpeg)
Fig. 12. Comparison between measured (dashed line) and simulated data (solid line) for the investigated scenarios: (a)  $0.48\mathrm{m}$  of clean ballast - Scenario 0; (b)  $0.10\mathrm{m}$  of fouled ballast beneath  $0.38\mathrm{m}$  of clean ballast - Scenario I; (c)  $0.20\mathrm{m}$  of fouled ballast beneath  $0.28\mathrm{m}$  of clean ballast - Scenario II; (d)  $0.30\mathrm{m}$  of fouled ballast beneath  $0.18\mathrm{m}$  of clean ballast - Scenario III.

![img-26.jpeg](img-26.jpeg)

# 6. Conclusion and future perspectives

This work reports on the ground-penetrating radar (GPR)-based assessment of railway ballast which was progressively "polluted" with a fine-grained silty soil material. The experimental setup was designed to represent the real-life scenario of a ballast layer within a railway track bed. To this purpose, a methacrylate square-based tank sized  $1.47\mathrm{m} \times 1.47\mathrm{m} \times 0.48\mathrm{m}$  height (inside dimensions) was manufactured and filled with clean ballast aggregates. The air-filled inter-particle voids were progressively "polluted" with a fine-grained silty soil, classified as A4 according to the AASHTO soil classification. Four levels of fouling within the ballast aggregate particles were reproduced. The GPR tests were performed at each fouling step using pulsed GPR systems equipped with differing air-coupled antennas of  $1000\mathrm{MHz}$  and  $2000\mathrm{MHz}$  central frequencies. The relative dielectric permittivity values of the ballast-silty soil mixes were retrieved using two signal-processing-based methods, i.e., the time-domain signal picking (TDSP) technique and the surface reflection method (SRM), and one theoretical-based model, i.e., the volumetric mixing formula (VMF). The results showed that the values of the dielectric permittivity increased with the level of fouling and were comprised between 3.51 and 5.35. The comparison between the above three models proved that the SRM

was not suitable for assessing the permittivity of the materials under investigation across the range of the used antenna frequencies. Good matching was found between the permittivity values assessed by the TDSP technique and the VMF approach. In particular, the best agreement was observed in the case of data collected with the  $1000\mathrm{MHz}$  antenna system. Moreover, the results emerged from the peak-to-peak estimates of the relative dielectric permittivity (TDSP technique) were further confirmed by the numerical-based simulation methodology implemented by the combination of the random-sequential (RSA) paradigm and the finite-difference time-domain (FDTD) technique. Indeed, the time position of the two main peaks of reflection (i.e., the peaks relative to the reflections from the air/ballast and the ballast/PEC interfaces) matched relatively well in both the simulated and the measured data.

It is important to emphasize the significance of the RSA paradigm coupled with the FDTD technique used for the data processing. This was proved to be of paramount importance for the simulation of the GPR signal as well as for the generation of synthetic GPR responses close to the experimental data. The relatively good agreement between the measured and the simulated GPR data paves the way for future research about the investigation of more complex multi-phase configurations of ballast/air/fouling components.

A. Benedetto et al./Construction and Building Materials 140 (2017) 508-520

## Acknowledgements

The authors express their thanks to Mr. Spartaco Cera, from Roma Tre University, for the technical assistance and the invaluable help provided during the laboratory surveys. Special thanks to IDS Georadar for supplying part of the GPR antenna systems and Clax Italia s.r.l. for manufacturing and on methacrylate tank. This work has also benefited from the network activities carried out within the EU funded COST Action TU1208 “Civil Engineering Applications of Ground Penetrating Radar.”

## References

[1] M.R. Clark, R. Gillespie, T. Kemp, D.M. McCann, M.C. Forde, Electromagnetic properties of railway ballast, NDT &amp; E Int. 34 (2001) 305-311.
[2] E.T. Selig, B.I. Collingwood, S.W. Field, Causes of fouling in track, AREA Bull. 71 (1998).
[3] EN 13450:2002/AC:2004, Aggregates for Railway Ballast, European Committee for Standardization, 2004.
[4] EN 933-1:2012, Tests for Geometrical Properties of Aggregates - Part 1: Determination of Particle Size Distribution - Sieving Method, European Committee for Standardization, 2012.
[5] EN 933-4:2008, Tests for Geometrical Properties of Aggregates - Part 4: Determination of Particle Shape - Shape Index, European Committee for Standardization, 2008.
[6] EN 1097-2:2010, Ests for Mechanical and Physical Properties of Aggregates - Part 2: Methods for the Determination of Resistance to Fragmentation, European Committee for Standardization, 2010.
[7] EN 1097-6:2013, Tests for Mechanical and Physical Properties of Aggregates - Part 6: Determination of Particle Density and Water Absorption, European Committee for Standardization, 2013.
[8] EN 1097-3:1998, Tests for Mechanical and Physical Properties of Aggregates - Part 3: Determination of Loose Bulk Density and Voxels, European Committee for Standardization, 1998.
[9] CEN ISO/TS 17892-1:2014, Geotechnical Investigation and Testing - Laboratory Testing of Soil - Part 1: Determination of Water Content (ISO 17892-1:2014), European Committee for Standardization, 2014.
[10] ASTM D4318-10e1, Standard Test Methods for Liquid Limit, Plastic Limit, and Plasticity Index of Soils, ASTM International, West Conshohocken, PA, 2010.
[11] American Association of State Highway and Transportation Officials (AASHTO), Roadside Design Guide, fourth ed., AASHTO, Washington, DC, 2011.
[12] EN ISO 17892-3:2015, Geotechnical Investigation and Testing - Laboratory Testing of Soil - Part 3: Determination of Particle Density (ISO 17892-3:2015, Corrected Version 2015-12-15), European Committee for Standardization, 2015.
[13] A. Benedetto, L. Pajewski, Civil Engineering Applications of Ground Penetrating Radar, Springer Transactions in Civil and Environmental Engineering Book Series, 2015.
[14] D. Goodman, Ground-penetrating radar simulation in engineering and archaeology, Geophysics 59 (2) (1994) 224-232.
[15] F. Tosti, L. Pajewski, Applications of radar systems in Planetary Sciences: an overview, in: Chapt. 15 - Civil Engineering Applications of Ground Penetrating Radar, Springer Transactions in Civil and Environmental Engineering Book Series, 2015, pp. 361-371. 4-232, 1994.
[16] J.J. Schultz, M.E. Collins, A.B. Falsetti, Sequential monitoring of burials containing large pig cadavers using ground-penetrating radar, J. Forensic. Sci. 51 (3) (2006) 607-616.
[17] R. Roberts, A. Schutz, LL. Al-Qadi, E. Tutumluer, Characterizing railroad ballast using GPR: recent experiences in the United States, in Proc. of the 2007 4th International Workshop on Advanced Ground Penetrating Radar (IWAGPR 2007), Naples, Italy, Jun. 2007.
[18] Railway Track and Structures Magazine, June 1985.
[19] J. Hagenichmidt, Railway track inspection using GPR, J. Appl. Geophys. 43 (2-4) (2000) 147-155.
[20] G.R. Olhoeft, E.T. Selig, Ground penetrating radar evaluation of railroad track substructure conditions, in Proc. 9th International Conference on Ground Penetrating Radar (GPR 2002), Santa Barbara, USA, Apr.-May 2002.
[21] Z. Leng, I.L. Al-Qadi, Railroad ballast evaluation using ground-penetrating radar, Transp. Res. Rec. 2159 (2010) 110-117.
[22] F. De Chiara, Improvement of railway track diagnosis using Ground Penetrating Radar, (PhD Thesis), 2014.
[23] I.L. Al-Qadi, S. Zhao, P. Shangguan, Railway ballast fouling detection using GPR data: introducing a combined time-frequency and discrete wavelet techniques, Near Surf. Geophys. 14 (2) (2016) 145-153.
[24] I.L. Al-Qadi, W. Xie, R. Roberts, Scattering analysis of ground-penetrating radar data to quantify railroad ballast contamination, NDT &amp; E Int. 41 (6) (2008) 441-447.

[25] H. Jol (Ed.), Ground Penetrating Radar, Elsevier, 2009.
[26] D. Li, J. Hyslip, T.R. Sussmann, S. Chrismer, Railway geotechnics, Taylor and Francis, 2015.
[27] T.R. Sussmann, M. Ruel, S. Christmer, Sources, influence, and criteria for ballast fouling condition assessment, in: Proceeding of the 91st Annual Meeting of the Transportation Research Board, 11 p. 2012.
[28] F. Tosti, C. Patriarca, E.C. Slob, A. Benedetto, S. Lambot, Clay content evaluation in soils through GPR signal processing, J. Appl. Geophys. 97 (2013) 69-80.
[29] F. Tosti, A. Benedetto, L. Bianchini Ciampoli, S. Lambot, C. Patriarca, E.C. Slob, GPR analysis of clayey soil behaviour in unsaturated conditions for pavement engineering and geoscience applications, Near Surf. Geophys. 14 (2) (2016) 127-144.
[30] B. Indraratna, L.J. Su, C.A. Rujikiatkamjorn, A new parameter for classification and evaluation of railway ballast fouling, Can. Geotech. J. 48 (2) (2011) 322-326.
[31] N. Tennakoon, B. Indraratna, C. Rujikiatkamjorn, S. Nimbalkar, T. Neville, The role of ballast-fouling characteristics on the drainage capacity of rail substructure, Geotech. Test. J. 35 (4) (2012) 1-12.
[32] L. Pajewski, F. Tosti, W. Kusayanagi, Antennas for GPR Systems, in: Chapter 2 - Civil Engineering Applications of Ground Penetrating Radar, Springer Transactions in Civil and Environmental Engineering Book Series, 2015, pp. 41-67.
[33] R. Roberts, I. Al-Qadi, E. Tutumluer, J. Boyle, and T.R. Sussmann, Advances in Railroad Ballast Evaluation Using 2 GHz Horn Antennas, in Proc. 11th International Conference on Ground Penetrating Radar, Columbus, OH, USA, 2006.
[34] ASTM D6087-08, Standard Test Method for Evaluating Asphalt-Covered Concrete Bridge Decks Using Ground Penetrating Radar, ASTM International, West Conshohocken, PA, 2008.
[35] J.S. Mundrey, Railway Track Engineering, Tata McGraw-Hill Education, 2009.
[36] F. Benedetto, F. Tosti, A signal processing methodology for assessing the performance of ASTM standard test methods for GPR systems, Signal Process. 132 (2017) 327-337.
[37] EN 13286-2:2005, Unbound and Hydraulically Bound Mixtures - Part 2: Test Methods for the Determination of the Laboratory Reference Density and Water Content - Proctor Compaction, European Committee for Standardization, 2015.
[38] R. Wu, J. Li, Z.S. Liu, Super resolution time delay estimation via MODEWRELAX, IEEE Aero. Elec. Syst. 35 (1) (1999) 294-307.
[39] J. Redman, J. Davis, L. Galagedara, G. Parkin, Field studies of GPR air launched surface reflectivity measurements of soil water content, in Proc. of the 9th International Conference on Ground Penetrating Radar (GPR 2002), Santa Barbara, California, USA, 2002, art. no. 4758, pp. 156-161.
[40] J.R. Birchak, C.G. Gardner, J.E. Hipp, J.M. Victor, High dielectric constant microwave probes for sensing soil moisture, Proc. IEEE 62 (1974) 93-102.
[41] K. Lichtenecker, K. Rother, Die herleitung des logarithmischen mischungsgesetzes aus allgemeinen prinzipien der stationaren strömung, Phys. Z 32 (1931) 255-260.
[42] K. Roth, R. Schulin, H. Fluhler, W. Attinger, Calibration of time domain reflectometry for water content measurement using composite dielectric approach, Water Resour. Res. 26 (1990) 2267-2273.
[43] A. Brovelli, G. Cassiani, Effective permittivity of porous media: a critical analysis of the complex refractive index model, Geophys. Prospect. 56 (2008) 715-727.
[44] C. Patriarca, F. Tosti, C. Velds, A. Benedetto, S. Lambot, E.C. Slob, Frequency dependent electric properties of homogeneous multi-phase lossy media in the ground-penetrating radar frequency range, J. Appl. Geophys. 1 (97) (2013) 81-88.
[45] W.E. Fensler, E.F. Knott, A. Olte, K.M. Siegel, The electromagnetic parameters of selected terrestrial and extraterrestrial rocks and glasses, in: Z. Kopal, Z.K. Mikhailov (Eds.), The moon, IAU Symposium 14, pp. 545-565.
[46] M.C. Forde, R. De Bold, G. O'Connor, J.P. Morrissey, New analysis of Ground Penetrating Radar testing of a mixed railway trackbed, Transportation Research Board Annual Meeting, 2010.
[47] A. Benedetto, A. Umiliaco, Evaluation of hydraulic permeability of open-graded asphalt mixes using a full numerical simulation, J. Mater. Civil Eng. 26 (4) (2014) 599-606.
[48] K.S. Kunz, R.J. Luebbers, The Finite Difference Time Domain Method for Electromagnetics, CRC Press, 1993.
[49] A. Taflore, Computational Electrodynamics: The Finite-Difference Time-Domain Method, Artech House, 1995.
[50] K.S. Yee, Numerical solution of initial boundary value problems involving Maxwell equations in isotropic media, IEEE T. Antenn. 14 (1966) 302-307.
[51] A. Giannopoulos, Modelling ground penetrating radar by GprMax, Constr. Build. Mater. 19 (10) (2005) 755-762.
[52] A. Benedetto, F. Tosti, L. Bianchini Ciampoli, L. Pajewski, D. Pirrone, A. Umiliaco, M.G. Brancadoro, A simulation-based approach for railway applications using GPR, in Proceedings of the 2016 International Conference of Ground Penetrating Radar, Hong Kong, pp. 1-6, 13-16 June, 2016. doi: 10.1109/ICGPR.2016.7572609.