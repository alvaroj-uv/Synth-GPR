Journal of Applied Geophysics 233 (2025) 105605

ELSEVIER

Contents lists available at ScienceDirect

Journal of Applied Geophysics

journal homepage: www.elsevier.com/locate/jappgeo

Journal of Applied Geophysics

# FDTD analysis of ballast fouling status using PFC with discrete random medium model

Bo Li a, Linyan Guo b, Zhan Peng c,\*, Shilei Wang c, Guixian Liu c, Yaonan Li c

$^{a}$ Department of Electronic Engineering, Tsinghua University, Beijing 100084, China
$^{b}$ School of Geophysics and Information Technology, China University of Geosciences, Beijing 100083, China
$^{c}$ Infrastructure Inspection Research Institute, China academy of railway sciences corporation limited, Beijing 100081, China

# ARTICLEINFO

Keywords:

Ground penetrating radar (GPR)

Particle Flow Code (PFC)

Discrete random medium (DRM)

FDTD

Ballast fouling

# ABSTRACT

Numerical simulation techniques for ground penetrating radar (GPR) railway ballast inspection offer significant advantages, including the avoidance of extensive field surveys and excavation work. This helps minimize construction challenges and costs while providing crucial technical support and insights for railway maintenance. Nevertheless, the intricate nature of ballast particles and bed structures, combined with the challenges in discerning their patterns, present formidable obstacles to achieving high-precision modeling. This paper employs the Particle Flow Code (PFC2D) to extract and project 2D natural ballast particles from laser scanning, generating a clean ballast physical model considering mechanical interactions. As fouling arises from fine particles smaller than  $25\mathrm{mm}$ , the discrete random medium theory is applied to validate the heavy ballast fouling. This involves filling the voids in the clean ballast to simulate and analyze the electromagnetic properties of the ballast fouling. The generated ballast physical model is converted into HDF5 files and simulated using a 2.0 GHz Rayleigh wave excitation through the Finite Difference Time Domain (FDTD) method. Through S-transform and Hilbert energy results, it becomes feasible to accurately differentiate the ballast fouling. The study reveals that highly fouling ballast predominantly exhibits frequency energy concentrated within the  $1.0 - 3.0\mathrm{GHz}$  range. As depth increases, the energy experiences faster attenuation, and the distribution of Hilbert energy becomes denser and stronger. Field tests conducted on a specific railway line in southern China validate the method's effectiveness, making it a valuable tool for guiding GPR-based ballast fouling detection projects and providing a scientific basis for railway infrastructure maintenance.

# 1. Introduction

Ballast beds provide support and drainage, however, long-term operation leads to wear and deterioration of ballast particles, jeopardizing the safety and stability of the track. Accurate and effective assessment and monitoring of the condition of railroad ballast is essential to reduce maintenance costs and accident risks. Ground penetrating radar (GPR) technology is a fast, continuous, and highly accurate tool, which meets the requirements for continuous inspection of ballast beds, and is increasingly used for condition assessment of the fouling and health detection of ballast beds Shapovalov et al. (2022); Artagan and Borecky (2020). The use of GPR in various fields Wai-Lok Lai et al. (2018); Catapano et al. (2019); Li et al. (2022) faces limitations due to engineering complexity Ciampoli et al. (2020), high costs Artagan

et al. (2020), specialized antenna requirements Ciampoli et al. (2018), and challenges in interpreting and validating data, particularly in extensive infrastructure like mainline ballast beds Barrett et al. (2019). Numerical simulations are effective in replicating the behavior of physical systems. They assist in understanding complex phenomena and engineering problems, providing support for the identification of railway ballast conditions.

The significance of reasonable forward physical models in electromagnetic simulation of ballast lies in their compliance with both mechanical and electromagnetic properties. Various approaches exist for mechanical and electromagnetic forward modeling of ballast and similar geomaterials. Kneib and Kerner (1993) proposed criteria for accuracy and effectiveness in the finite difference modeling of random medium, while Frenje and Juhlin (1998) presented a random medium model

https://doi.org/10.1016/j.jappgeo.2024.105605

Received 1 July 2024; Received in revised form 29 November 2024; Accepted 8 December 2024

Available online 20 December 2024

0926-9851/© 2024 Published by Elsevier B.V.

based on sonic logging curves. However, such random medium models have been less applied in modeling and simulation of large-grained ballast and may struggle to reflect the influence of particle shape and internal pore space structure, potentially deviating from mechanical principles. In the detailed modeling of ballast and similar geomaterials, Lanaro and Tolppanen (2002) utilized three-dimensional imaging of block stones through laser scanning and employed geometric analysis to statistically determine the microscale parameters of these stones. Tutumluer et al. (n.d.) scanned three-dimensional ballast models and selected 11 typical polyhedral models to represent the real shapes of ballast particles, achieving satisfactory results. Ngo et al. (2017) conducted discrete element method (DEM) studies on the microstructure and interaction mechanisms of ballast particles. In recent years, researchers have employed DEM to construct detailed ballast models and analyze the effects of ballast fouling through mechanical means (Wang et al. (2021); Jing et al. (2021)). Fan et al. (2023) conducted research on the detection of internal cracks within asphalt pavements using ground penetrating radar (GPR). They implemented a novel multiphase heterogeneous model and developed sample identification and virtual generation methods to create a finite-difference time-domain (FDTD) model, aiming to increase the precision of GPR in capturing the intricate, multiphase composition of asphalt surfaces. Furthermore, in previous work (Li et al. (2023)), we proposed an algorithm for modeling and stacking ballast particles, but its structure deviates significantly from the real ballast structure in terms of model fidelity, and the considerations of pores and mechanical principles in stacking are insufficient. High-precision models of ballast and similar geomaterials can better reflect the real particle shapes and surface features, while DEM can establish detailed two-dimensional and three-dimensional ballast structures of different particle sizes, generating models closer to the real form of ballast and in better agreement with mechanical principles. Also, in recent years, with the rapid development of digital twins and AI-based intelligent detection, high-precision ballast bed modeling has significantly enhanced the reliability of numerical simulations. The reliable datasets it provides can compensate for the high costs and labor-intensive nature of traditional data collection. The research approach presented in this paper is expected to offer valuable insights for advancing the field by increasing the dataset size while simultaneously reducing the cost and complexity associated with implementing detection models (Koohmishi et al. (2024); Luo et al. (2024); Qin et al. (2025); Saputra and Kuo (2023)).

Inspired by these research results, to address issues such as roughness and irrationality in modeling railway ballast particles, this study utilizes laser scanning technology, the Particle Flow Code (PFC2D) for discrete element simulations, and Finite Difference Time Domain (FDTD) techniques to construct highly accurate models of ballast particles and beds from both mechanical and electromagnetic perspectives. Detailed modeling procedures and methods like reference Fan et al. (2023), can be found in the Appendix A, but ballast particles are more suitable for this virtual generation method because they are much larger than asphalt particles. The constructed physical models of ballast and beds exhibit higher accuracy and greater persuasiveness compared to real-world environments. Additionally, considering that the internal porosity fouling of ballast beds consists predominantly of fine fragmented particles rather than soil-like medium, this study employs discrete random medium theory to construct models of fouled ballast beds. Furthermore, to validate whether fragmented particles are the primary cause of fouling, the voids in the ballast bed models generated by PFC are filled with discrete random medium for verification purposes. Simulation results are analyzed using Hilbert energy transformation (Guo et al. (2023)) and S-transforms (Bi et al. (2020)), which demonstrate that the proposed approach can better illustrate the clean and fouled states of real track beds through forward simulations, as evidenced by a comparative analysis of electromagnetic detection results on clean and fouled track beds in a Southern passenger railway. Subsequent sections of this paper will elaborate on the methodology, results, and conclusions.

## The ballast modeling and simulation analysis

### Clean and heavily ballast fouling models

The technology workflow in Fig. 1 illustrates that the work of this paper begins by generating a 2D model of the ballast bed through laser scanning, CAD, and Particle Flow Code (PFC2D 0.5), with detailed modeling mechanisms provided in the Appendix A. Considering the constraints of Chinese railway ballast particle size and the limitations of PFC2D software in particle modeling scale, the particle size range is selected between 15 and 63 mm, with detailed reasons available in the Appendix A. Subsequently, the model output from PFC2D in jpg or png format is processed through image binarization using PyCharm to generate an HDF5 file representing the random geometric shape model for constructing a clean ballast bed model in gprMax (Giannopoulos (2005)). To further construct a fouled ballast bed model formed by fragmented particles, a discrete random medium principle algorithm is employed to generate 2D discrete random medium with particle diameters smaller than 15 mm to characterize the fouling material of the ballast bed. These smaller particles can then be filled into the pores of the clean ballast bed to analyze the electromagnetic properties of the ballast bed transitioning from clean to fouled conditions. Similarly, HDF5 files are first generated and imported into gprMax to construct high-precision ballast beds under both clean and fouled conditions. FDTD simulations of GPR are conducted after configuring the gprMax in-file. Models generated by gprMax can be visualized using the vti files to examine their corresponding geometric model structures. Finally, simulation results undergo data post-processing and visualization using time-domain grayscale images, S-transform results, and Hilbert transform energy maps from the outputted out files for further analysis of ballast bed electromagnetic properties.

As shown in Fig. 2(a) and (b), these are visualizations of the clean and fouled ballast bed models generated from vti files outputted by FDTD simulations, viewed using Paraview software. The length of each model is 1.3 m, and the height is 1.6 m. These models are divided from top to bottom into the air, ballast bed, sand bedding, and subgrade, with their corresponding electromagnetic parameters in gprMax software detailed in Table 1.

The gprMax grid parameters were set to dx_dy_dx = |0.001. 0.001. 0.01| for the FDTD simulations. In the FDTD simulation of GPR, a pair of simple dipole antenna models are selected as the transmitting and receiving antennas, the frequency center is 2.0 GHz as depicted in Fig. 2. They are positioned at a height of 0.2 m above the ballast bed to simulate air-coupled GPR detecting the ballast bed. The distance between the transmitting and receiving antennas was maintained at 0.02 m, with an elevation of 0.2 m above the ballast bed. The scanning of the antennas was carried out in the lateral x-direction with increments of 0.02 m. To expedite the simulations and reduce gprMax's computational time, a high-performance 6GB RTX 3060 GPU was employed. To minimize the impact of gprMax's absorption boundaries on the electromagnetic waves transmitted and received by the antennas, a total of 60 traces were collected along a measurement line spanning from 0.0 to -1.2 m in the positive x-axis direction, using 0.02-m increments. The outermost layer of the model in Fig. 2 is a PML layer. The initial position of the antenna along the x-axis is 0.02 m, which is set as the reference starting point at the origin. After completing the measurements along the profile line, the antenna remains at a distance of 1.22 m from the PML boundary, ensuring that it is sufficiently far from the boundary to avoid interference.

Fig. 3 shows B-Scan and Hilbert transform energy results for clean and fouled ballast beds model from simulations. Fig. 3 (a) and (b) depict normalized B-Scan results for ballast beds with varying fouling status. Without direct wave removal, a distinct interface appears at around 8.8 ns for heavily fouled status. After background noise removal, as shown

B. Li et al.

Journal of Applied Geophysics 233 (2025) 105605

![img-0.jpeg](img-0.jpeg)
Fig. 1. Technology roadmaps in this paper.

![img-1.jpeg](img-1.jpeg)
Fig. 2. Paraview visualization model, (a) clean ballast, (b) heavily ballast fouling status.

Table 1 Electromagnetic parameters of gprMax models at different levels [18].

|  Model Level | Dielectric constant | Permeability (H/m) | Conductivity (S/m)  |
| --- | --- | --- | --- |
|  Air | 1 | 1 | 1  |
|  Ballast | 4 | 1 | 0.01  |
|  Sandbedding | 8 | 1 | 0.001  |
|  Subgrade | 13 | 1 | 0.01  |

in Fig. 3 (c) and (d), the interface between air and both clean and fouled ballast beds becomes more distinct, appearing at 1.52 ns. Moreover, the ballast beds with severe fouling, due to the increased presence of fragmented ballast particles and the more irregular distribution of pores, result in highly chaotic and scattered hyperbolic distributions in the reflected detection images. And Hilbert energy transform results

indicate significantly higher Hilbert energy for heavily fouled beds, with pronounced energy concentration. Post-processing on ballast beds with varying fouling status at the same location is conducted for further analysis, as shown in Fig. 4. Fig. 4 (a) represents a clean ballast bed modeled using PFC, where the ballast bed exhibits more fouling as longitudinal depth extends. Fig. 4 (b) shows a faster electromagnetic attenuation rate, with energy primarily concentrated in the  $1.0 - 3.0\mathrm{GHz}$  range. Furthermore, the normalization and background noise removal methods employed in this study are detailed in the Appendix B, with subsequent data processed using standard methods.

# 2.2. The ballast bed model filled with discrete random medium

Fouling of the ballast bed is exacerbated as larger ballast particles break down into smaller ones over time, particularly as the ballast

B. Li et al.

Journal of Applied Geophysics 233 (2025) 105605

![img-2.jpeg](img-2.jpeg)

![img-3.jpeg](img-3.jpeg)

![img-4.jpeg](img-4.jpeg)
Fig. 3. FDTD simulation results of clean and heavily fouling of ballast beds. (a) and (b) are the original B-Scan grayscale figures after normalization, (c) and (d) are the results after background denoising, and (e) and (f) are the Hilbert energy results.

![img-5.jpeg](img-5.jpeg)
Fig. 4. Results of S-transform at the same location for (a) clean and (b) heavily fouling of ballast beds.

undergoes prolonged service. These smaller particles fill the voids between the larger particles, contributing to the degradation of the ballast bed. While these finer particles are not entirely fouled, they are crushed ballast with a diameter of less than  $25\mathrm{mm}$ , which typically results from mechanical wear and environmental factors. This size classification aligns with industry standards, such as the Chinese Railway Ballast Standard (Baba (2024)), which specifies the particle size distribution for fouled ballast. Consequently, a discrete random medium model can be employed to simulate the gradual filling of the interstitial gaps in the clean ballast bed, leading to a deterioration of its condition and an increase in fouling. The derivation of the algorithm theory and pseudocode implementation are shown in Appendix C. This model effectively represents the complex interplay between particle size and fouling in real-world ballast beds, where the accumulation of finer particles compromises the bed's structural integrity and drainage capacity. The physical model of the ballast bed generated using this method is shown in Fig. 5. To investigate whether the accumulation of finer particles

exacerbates the fouling status of the ballast bed, this study employs a hybrid approach. It involved combining the models generated by PFC with randomly ballast particles, resulting in the creation of new HDF5 files. Subsequent gprMax simulations and the visualization of results in Paraview are presented in Fig. 5. To maintain consistent variables, all dimensions and simulation parameters were held constant. It is apparent that the surfaces and interstices of larger particles are filled with smaller gravel. Likewise, the corresponding simulation results, encompassing normalized B-Scans, background noise reduction, Hilbert energy transformation, and S-transform results, are displayed in Fig. 6.

As shown in Fig. 6(b), a comparison with Fig. 3(c) and (d) for clean and fouled ballast beds reveals that the accumulation of finer, fragmented particles exacerbates ballast fouling, leading to increased clutter in the resulting images. This observation aligns with the characteristics displayed by the fouled ballast beds. Additionally, the Hilbert energy variations in Fig. 6(c), compared with Fig. 3(e) and (f), show that the finer ballast particles contribute to an increase in energy, particularly in

B. Li et al.

Journal of Applied Geophysics 233 (2025) 105605

![img-6.jpeg](img-6.jpeg)
Fig. 5. PFC generates visualization results for the combination of a clean ballast bed model and a random particle model.

the 4-8 ns range. This suggests that prolonged service results in the growth of finer particles, which increases the Hilbert energy observed in the electromagnetic detection results.

Normalization in this study was conducted by direct standardization, using the maximum values as a reference. The S-transform in the fouled

ballast bed indicates a significantly faster electromagnetic wave attenuation, with the signal decay concluding around 8 ns, whereas the clean ballast bed exhibits a more gradual decay, extending to approximately 12 ns.

# 3. Experimentation and analysis

To compare and validate the consistency between simulation results and experimental data, this study selected a  $50\mathrm{km}$  section of the passenger railway mainline in southern China, between two provinces and cities. Within this section, there is an  $18\mathrm{km}$  segment that underwent ballast cleaning in March 2023, representing a clean ballast bed, while the remaining part, which was not cleaned, represents a heavily fouled ballast bed that has been in service for an extended period. As shown in Fig. 7 (a) and (b), the ballast bed center was chosen as the measurement line, with a track spacing of  $8.3\mathrm{cm}$  and a time window of  $15\mathrm{ns}$ . The radar equipment utilized in this study consisted of a GSSI-SIR30 four-channel main unit paired with a 4200S  $2.0\mathrm{GHz}$  air-coupled antenna. Prior to testing, three sampling points in the sleeper box areas were selected from both the ballast cleaning and uncleaned segments to obtain the ballast gradation data for the railway section. As illustrated in Fig. 7 (c), photographs were taken during the excavation process, and Fig. 7 (d) displays the segregated ballast particles after mechanized cleaning.

In order to further scrutinize these experimental results, this paper selectively extracts and analyzes data from lines 61 to 80 and 300,061 to 300,080, which correspond to heavily fouled and clean ballast beds, respectively. For this subset of data, the first step involves the removal of direct-wave components in the experimental data. Fig. 8(a), (b), (d), and (e) illustrate this process, with the region between 3 and 3.5 ns corresponding to sleeper-related information retained due to its negligible impact on the results presented in this study. In Fig. 8(a) and (d), it is

![img-7.jpeg](img-7.jpeg)

![img-8.jpeg](img-8.jpeg)

![img-9.jpeg](img-9.jpeg)
Fig. 6. The combined model's normalized (a) B-Scan, (b) background noise reduction, (c) Hilbert energy, and (d) S-transform results.

![img-10.jpeg](img-10.jpeg)

B. Li et al.

Journal of Applied Geophysics 233 (2025) 105605

![img-11.jpeg](img-11.jpeg)
Fig. 7. The experimental testing environment, (a) the testing instruments and conditions, (b) a Google satellite map provides an overview of the railway section between two southern Chinese provinces, (c) photographs capturing the excavation process of the ballast bed, (d) the differently graded railway ballast particles following the mechanized cleaning process.

![img-12.jpeg](img-12.jpeg)
Fig. 8. Experimental data for heavily fouled and clean ballast beds, including (a) and (d) B-Scan grayscale images, (b) and (e) Hilbert energy transformation images, and (c) and (f) time-frequency plots of the 30th cross-line data.

evident that weak interfaces appear around 8 ns and 12 ns. Due to the presence of finer particles in the lower layers, Fig. 8(b) and (e) show a denser distribution of energy in the Hilbert energy transform for the heavily fouled ballast bed, whereas the energy distribution for the clean ballast bed is comparatively sparse and concentrated mainly near the

surface. Furthermore, during the processing of experimental data, we chose the 10th data point between the two datasets for time-frequency energy analysis using the S-transform. The energy is concentrated around  $1.0 - 4.0\mathrm{GHz}$ . With increasing depth, we observe that the energy attenuation in the heavily fouled ballast bed is faster than that in the

clean ballast bed. At approximately 6 ns, the high-frequency energy has almost completely attenuated in the heavily fouled ballast bed, whereas in the clean ballast bed, the 1.0--4.0 GHz energy is still evident and has not substantially attenuated until around 14 ns. Therefore, through the processing and analysis of experimental data, it can be comprehensively demonstrated that the clean and heavily fouled ballast bed models proposed in this study effectively explain the actual status of fouling in ballast beds. This can provide guidance for real-world GPR applications in assessing and analyzing ballast fouling status.

To recapitulate, we have primarily focused on fouling due to ballast breakdown. However, it is important to acknowledge that other factors, such as contamination from mud and silt, can also significantly contribute to fouling processes. While these factors were not the central focus of our investigation, they are known to affect the efficiency and longevity of various systems and structures. Future research should consider the combined effects of ballast breakdown and environmental contaminants to provide a more comprehensive understanding of fouling dynamics.

## Conclusion

This work presents a 2D physical modeling approach for clean and heavily fouled ballast beds using CAD, PFC software and the discrete random medium algorithm. The method fully considers the voids and fine structures of the ballast, combining ballast mechanics principles and electromagnetic characteristics to construct a highly accurate and practical ballast model. The generated model is simulated using the FDTD algorithm and compared with experimental results. The simulation results exhibit excellent consistency with experimental test data, signifying significant research value. The simulation results, analyzed through Hilbert energy transformation and S-transform in the time-frequency domain, effectively distinguish between clean and heavily fouled railway ballast beds. Both simulation and experimental evidence confirm that as the fouling status increases, there is a higher presence of fine-grained particles. This is manifested in elevated Hilbert energy and more concentrated energy distribution. Additionally, the time-frequency results from S-transform indicate that as the depth increases, the ballast fouling status experiences faster attenuation. Conversely, cleaner ballast beds display contrasting effects. This simulation analysis's results have been validated through a comparison with experimental data from a high-speed railway line in southern China, demonstrating a strong consistency. This further affirms the reliability and accuracy of the model proposed in this paper. Moreover, the research method presented in this study accurately constructs models of clean and heavily fouled ballast beds, holding significant potential for practical applications in railway ballast beds inspection and defect elimination. However, it's worth noting that this model has not yet taken into account real-world 3D modeling and the influence of complex environmental factors. These aspects will be addressed and refined in subsequent research.

## CRediT authorship contribution statement

Bo Li: Writing -- review & editing, Writing -- original draft, Visualization, Validation, Software, Methodology, Data curation. Linyan Guo: Writing -- review & editing, Software, Methodology, Funding acquisition. Zhan Peng: Validation, Methodology, Funding acquisition, Data curation. Shilei Wang: Methodology, Funding acquisition, Data curation. Guixian Liu: Validation, Software, Methodology, Funding acquisition, Data curation. Yaonan Li: Methodology, Funding acquisition, Data curation.

## Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## Acknowledgements

This work was supported by the Research on Evaluation System for Rail Transit Infrastructure Detection Equipment and Key Calibration Technology under Grant 2020YJ219, the Research on Rapid Detection of Sub-Structure Conditions of Ballasted Track and Decision-Making Technology for Trackbed Overhaul under Grant K2022G015 and the National Natural Science Foundation of China under Grant 42274189, 42074155 and 42274193.

## Ballast and beds modeling methods

Due to limitations in the gprMax software, which currently only supports the creation of regular geometric shapes such as spheres, rectangles, and cylinders, irregular 3D or 2D shapes like ballast and block stones, with curved surfaces or curves, are challenging to create using gprMax, and the process as showed in Fig.A.1. Substituting regular shapes for complex ones in electromagnetic simulations or mechanical calculations often results in significant errors. Although the “geometry_objects_read” command in gprMax allows for the generation of arbitrary geometric shapes from HDF5 files, converting conventional 3D or 2D models into HDF5 files is difficult, and preprocessing functions and feature extraction for converting 3D to 2D models require the use of other software platforms. Therefore, this study establishes a physical model of ballast particles based on CAD, PFC, and gprMax platforms, providing a simple and user-friendly way to accurately model complex rock particles using mature technologies and software. Leveraging the mechanical calculation capabilities of PFC, the algorithm generates geometric models that better reflect engineering reality, enabling joint computational analysis of mechanical and electromagnetic modeling for arbitrary-shaped objects. This approach helps to address deficiencies in custom and traditional algorithms, facilitating the extraction of real form characteristics of complex objects and analyzing the relationship between target bodies and radar signal changes. Additionally, this algorithm holds significant importance for correlational analysis between electromagnetic and mechanical indicators, paving the way for direct detection of ballast bed mechanical properties using GPR based on in-depth research utilizing this algorithm.

The algorithmic process for constructing ballast particles and beds in this study is illustrated in Fig. A.2. This algorithm utilizes relatively mature 3D scanning technology and industrial reverse engineering digitizers to obtain DXF or STL format 3D files of ballast particles, which can be edited and calculated using various software. Considering the complexity of directly importing 3D ballast, random angle projection is applied to extract the 2D ballast structure in advance to reduce computational and operational complexity. Furthermore, to meet the grading standards of track bed ballast, calculations are conducted for particle size distribution and porosity using PFC2D software. The particles are segmented into spherical boundaries, and relevant particle information is extracted to generate the corresponding track bed. PFC provides a range of particle calculation functions and supports the Fish language, through which the “clump” command is invoked to fit the imported DXF format 2D ballast model and generate accurate particle models.

PFC2D is a discrete element software used to simulate the motion and interactions of 2D spherical geometries of any shape and size. The ballast bed generation process is illustrated in Fig. A2, where external 2D particle templates are imported, and the “clump generate” command is used to generate realistic-shaped ballast particles. The “Generate” command can produce non-overlapping particles or clusters within the computational area, but the generated particles are relatively loose. These loose particles, simulated using a linear elastic contact model and gravity parameters, simulate the free fall and stacking of ballast under gravity, resulting in a track bed model with a random distribution and random shapes of ballast, as shown in the lower-left corner of Fig. A2. The particle size range of this model conforms to the Chinese railway ballast particle size standard, with a minimum size set at 15 mm and a maximum at 63 mm. The constructed ballast has a length of 1.3 m and a height of 0.65 m. According to the ballast bed fouling ballast grading standard and a porosity rate of 80 %, the ballast particle sizes are divided into five different gradations, represented by different colors, and randomly placed into the ballast bed of a given size to generate a clean track bed model. It is worth noting that the particle size standards for modeling ballast particles and the criteria for determining track bed fouling and grading are referenced from “Railroad crushed ballast TB/T2140-2008” (Baba (2024)), ensuring that the constructed models and gradations adhere to engineering practicality.

## Data processing

In the study, we processed the simulation data of the ballast bed with clean and fouled ballast beds. The steps of data processing consist of several steps. Background elimination. The average value of each segment of the traces was subtracted to complete this stage, which simply included removing the background mean. This method can be represented by eq. (B. 1), where A represents the curve data of the B-Scan, n indicates the trace number, and k denotes the window size for background removal.$$A_{i}(n) = A_{i}(n) - \frac{1}{K}\sum\limits_{k = 0}^{K - 1}A_{K}(n)$$Data normalization process. Divide all of the variables to be compared by the highest value of these values to normalize the comparison.

B. Li et al.

Journal of Applied Geophysics 233 (2025) 105605

# Appendix C. Discrete random medium algorithm

The process for generating a discrete random medium (DRM) model begins with the generation of the coordinate grids in both the  $x$ - and  $z$ -directions.

The coordinate grids are defined as:

Algorithm 1. DRM Model Generation Algorithm.

1. Input:  $x_{\mathrm{len}}$ ,  $z_{\mathrm{len}}$ ,  $a$ ,  $b$ ,  $\dot{\mathbf{a}}$
2. Initialize  $r = 0.4$ ,  $\nu_0 = 2000$
3. Generate one-dimensional vectors  $\mathbf{A}$  and  $\mathbf{B}$
4. Generate two-dimensional coordinate grids  $\mathbf{x}$  and  $\mathbf{y}$
5. Compute elliptical function  $f(x,y)$
6. Perform Fourier transform to obtain  $F(u, v)$
7. Add random phase  $\phi (u,v)$
8. Perform inverse Fourier transform to obtain  $zz(x,y)$
9. Calculate mean  $\mu$  and variance  $d$
10. Compute standard deviation-adjusted random variable

11. Output:random.  $(x,y)$

$$
\begin{array}{l} A = \left[ 0, \Delta x, 2 \Delta x, \dots , \left(x _ {\text {l e n}} - 1\right) \Delta x \right], \\ B = \left[ 0, \Delta z, 2 \Delta z, \dots , \left(z _ {\text {l e n}} - 1\right) \Delta z \right] \end{array} \tag {C.1}
$$

where the step sizes are given by:

$$
\Delta x = \frac {1 0 0 0}{x _ {\text {l e n}} - 1}, \quad \Delta z = \frac {1 0 0 0}{z _ {\text {l e n}} - 1}. \tag {C.2}
$$

Next, two-dimensional coordinate grids  $\mathbf{x}$  and  $\mathbf{y}$  are generated using Kronecker products:

$$
\mathbf {x} = \mathbf {1} _ {x _ {\text {l e n}}} \odot \mathbf {A}. \quad \mathbf {y} = \mathbf {B} \odot \mathbf {1} _ {x _ {\text {l e n}}}
$$

The elliptical function  $f(x,y)$  is defined as:

$$
f (x, y) = \exp \left(- \left(\left(\frac {x}{a}\right) ^ {2} + \left(\frac {y}{b}\right) ^ {2}\right) ^ {\frac {1}{1 + y}}\right) \tag {C.4}
$$

The Fourier transform of  $f(x,y)$  is given by:

$$
F (u, v) = \mathbf {F} \{f (x, y) \} = \int \int_ {- \infty} ^ {\infty} f (x, y) e ^ {- 2 \pi i (u x + v y)} d x d y \tag {C.5}
$$

A random phase  $\phi (u,v)$  is added to the Fourier transform:

$$
\phi (u, v) = \operatorname {u n i f o r m} (0, 2 x, F. \text {s h a p e}), \quad F _ {1} (u, v) = | F (u, v) | \cdot e ^ {i \phi (u, v)} \tag {C.6}
$$

The inverse Fourier transform is applied to obtain  $zz(x,y)$ :

$$
z (x, y) = \mathbf {F} ^ {- 1} \left\{F _ {1} (u, v) \right\} = \int \int_ {- \infty} ^ {\infty} F _ {1} (u, v) e ^ {2 \pi i (u x + v y)} d u d v \tag {C.7}
$$

and the imaginary part is extracted as:

$$
z z (x, y) = I m (z (x, y)) \tag {C.8}
$$

The mean  $\mu$  and variance  $d$  of the generated medium are computed as follows:

$$
\mu = \frac {1}{x _ {\text {l e n}} \cdot z _ {\text {l e n}}} \sum_ {i = 1} ^ {x _ {\text {l e n}}} \sum_ {j = 1} ^ {x _ {\text {l e n}}} z z (i, j) \tag {C.9}
$$

$$
d = \frac {1}{x _ {\text {l e n}} \cdot z _ {\text {l e n}} - 1} \sum_ {i = 1} ^ {x _ {\text {l e n}}} \sum_ {j = 1} ^ {x _ {\text {l e n}}} \left(z z (i, j) - \mu\right) ^ {2} \tag {C.10}
$$

The standard deviation-adjusted random variable is then computed as:

$$
\sigma (i, j) = \frac {\dot {\mathbf {a}}}{d} (z z (i, j) - \mu), \quad v _ {1} = v _ {0} \left(1 + \frac {\sigma (i , j)}{1 0 0 0}\right) \tag {C.11}
$$

Finally, the random variable is given by:

$$
\operatorname {r a n d o m}. (x, y) = \frac {v _ {1}}{1 0 0 0} + 1 \tag {C.12}
$$

The pseudocode implementation for generating the discrete random medium model is Algorithm 1.

Due to the difficulty in obtaining 3D laser scans of fine ballast particles, and considering that the small size of these particles allows for the neglect

B. Li et al.

Journal of Applied Geophysics 233 (2025) 105605

of their true shape's impact, this study employs a discrete random medium (DRM) generation algorithm to simulate these particles for the modeling of both clean and fouled ballast beds. This approach not only reduces the time required for model generation but also significantly lowers engineering costs and implementation complexity. It holds substantial potential for application in the field, streamlining the process of simulating ballast fouling and the transition from clean to fouled conditions in ballast beds.

# Data availability

The authors do not have permission to share data.

# References

Artagan, S.S., Borecky, V., 2020. Advances in the nondestructive condition assessment of railway ballast: a focus on GPR. NDT &amp; E Int. 115, 102290.
Artagan, S.S., Bianchini Ciampoli, L., D'Amico, F., Calvi, A., Tosti, F., 2020. Nondestructive assessment and health monitoring of railway infrastructures. Surv. Geophys. 41, 447-483.
Baba, Daske, 2024. (Railway Standard) TR/T 2140-2008 Railway Crushed Ballast accessed Mar. 01, 2024. [Online]. Available: https://www.doc88.com/p-5631604029681..
Barrett, B.E., Day, H., Gascoyne, J., Eriksen, A., 2019. Understanding the capabilities of GPR for the measurement of ballast fouling conditions. J. Appl. Geophys. 169, 183-198.
Bi, W., Zhao, Y., Shen, R., Li, B., Hu, S., Ge, S., 2020. Multi-frequency GPR data fusion and its application in NDT. NDT &amp; E Int. 115, 102289.
Catapano, I., Gennarelli, G., Ludeno, G., Soldovieri, F., 2019. Applying ground-penetrating radar and microwave tomography data processing in cultural heritage: state of the art and future trends. IEEE Signal Process. Mag. 36, 53-61.
Ciampoli, L.B., Artagan, S.S., Tosti, F., Gagliardi, V., Alani, A.M., Benedetto, A., 2018. A comparative investigation of the effects of concrete sleepers on the GPR signal for the assessment of railway ballast. In: 2018 17th International Conference on Ground Penetrating Radar (GPR), pp. 1-4.
Ciampoli, L.B., Calvi, A., D'Amico, F., Tosti, F., 2020. GPR data collection and processing strategies for railway ballast evaluation. In: 2020 43rd International Conference on Telecommunications and Signal Processing (TSP), pp. 426-429.
Fan, J., Ma, T., Zhu, Y., Zhang, Y., 2023. Ground penetrating radar detection of buried depth of pavement internal crack in asphalt surface: a study based on multiphase heterogeneous model. Measurement 221, 113531.
Frenje, L., Juhlin, C., 1998. Scattering of seismic waves simulated by finite difference modelling in random media: Application to the Gravberg-1 well, Sweden. Tectonophysics 293, 61-68.
Giannopoulos, A., 2005. Modelling ground penetrating radar by GprMax. Constr. Build. Mater. 19, 755-762.
Guo, Y., Liu, G., Jing, G., Qu, J., Wang, S., Qiang, W., 2023. Ballast fouling inspection and quantification with ground penetrating radar (GPR). Int. J. Rail Transp. 11, 151-168.

Jing, G., Zong, L., Ji, Y., Aela, P., 2021. Optimization of FFU synthetic sleeper shape in terms of ballast lateral resistance. Sci. Iran. 0 (0), 0.
Kneib, G., Kerner, C., 1993. Accurate and efficient seismic modeling in random media. Geophysics 58, 576-588.
Koohmishi, M., Kaewunruen, S., Chang, L., Guo, Y., 2024. Advancing railway track health monitoring: Integrating GPR, InSAR and machine learning for enhanced asset management. Autom. Constr. 162, 105378.
Lanaro, F., Tolppanen, P., 2002. 3D characterization of coarse aggregates. Eng. Geol. 65, 17-30.
Li, C., Zheng, Y., Wang, X., Zhang, J., Wang, Y., Chen, L., Zhang, L., Zhao, P., Liu, Y., Lv, W., Liu, Y., Zhao, X., Hao, J., Sun, W., Liu, X., Jia, B., Li, J., Lan, H., Fu, W., Pan, Y., Wu, F., 2022. Layered subsurface in Utopia Basin of Mars revealed by Zhurong rover radar. Nature 610, 308-312.
Li, B., Peng, Z., Wang, S., Guo, L., 2023. Identification of ballast fouling status and mechanized cleaning efficiency using FDTD method. Remote Sens. 15, 3437.
Luo, J., Ding, K., Huang, H., Qamhia, I.I.A., Tutumluer, E., Hart, J.M., Thompson, H., Sussmann, T.R., 2024. Towards automated field ballast condition evaluation: field validation of the ballast scanning vehicle capabilities. Transp. Geotech. 48, 101311.
Ngo, N.T., Indraratna, B., Rajikiatkamjorn, C., 2017. A study of the geogrid-subballast interface via experimental evaluation and discrete element modelling. Granul. Matter 19, 54.
Qin, X., Peng, Z., Jing, G., 2025. Al-based ballasted track GPR application and development. In: Indraratna, B., Rajikiatkamjorn, C. (Eds.), Recent Advances and Innovative Developments in Transportation Geotechnics: Keynote Volume ICTG 2024. Springer Nature, Singapore, pp. 45-55.
Saputra, R.V.J., Kao, C., 2023. Ground penetrating radar signals, an efficient way to estimate fouled ballast. Indonesian Geotech. J. 2, 1-8.
Shapovalov, V., Vasilchenko, A., Yavna, V., Kochur, A., 2022. GPR method for continuous monitoring of compaction during the construction of railways subgrade. J. Appl. Geophys. 199, 104608.
E. Tutumluer, H. Huang, Y. Hashash, J. Ghaboussi, Aggregate Shape Effects on Ballast Tamping and Railroad Track Lateral Stability, n.d.
Wai-Lok Lai, W., Derobert, X., Annan, P., 2018. A review of ground penetrating radar application in civil engineering: a 30-year journey from locating and testing to imaging and diagnosis. NDT &amp; E Int. 96, 58-78.
Wang, L., Meguid, M., Mitri, H.S., 2021. Impact of ballast fouling on the mechanical properties of railway ballast: insights from discrete element analysis. Processes 9, 1331.