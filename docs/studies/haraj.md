# Comparative study of realistic and homogenized ballast layer

Sepideh Harajchi [ Department of Geoscience & Engineering
Delft University of Technology
Delft, The Netherlands
s.harajchi@tudelft.nl ] Evert Slob [ Department of Geoscience & Engineering
Delft University of Technology
Delft, The Netherlands
e.c.slob@tudelft.nl ]

###### Abstract

Accurate monitoring of railway ballast and embankments is critical for ensuring stability and safety in railway operations. Ground Penetrating Radar has emerged as a powerful non-destructive tool for characterizing ballast and underlying layers, particularly in estimating layer thickness. The ballast layer is modeled as a heterogeneous layer with pieces of rock and as a homogenized layer represented by a single relative permittivity value using the complex refractive index model. Numerical simulations were performed to evaluate the effects of ballast heterogeneity, layer composition, and thickness on expected reflection data. The results indicate that while homogeneous models are computationally efficient, they fail to capture the intrinsic scattering and attenuation effects of realistic ballast geometries, particularly under variable substructure configurations. The results suggest that laboratory measurements can be performed to understand the quality of the current state of the numerical models.

###### Index Terms:

Ground Penetrating Radar, Ballast Modeling, Layer Thickness Estimation, Railway Embankment, GPR

## I Introduction

Railway embankments are critical for ensuring the stability and safety of railway operations. The ballast layer, a fundamental component of the railway structure, provides essential support for the tracks by distributing loads, facilitating drainage, and maintaining alignment *[1]*.

Over time, ballast deteriorates due to fouling, moisture retention, and mechanical wear, which diminishes track performance *[2]*. Accurate monitoring of the ballast and embankment conditions, particularly the thickness of the ballast and underlying layers, is essential because each layer in the railway substructure serves a distinct purpose *[3]*. This monitoring is deemed to maintain long-term structural stability *[4]* and to ensure the safety and efficiency of railway systems *[3]*.

Ground Penetrating Radar (GPR) applications in railway surveys have experienced rapid growth in recent years *[5]*. It has become a leading non-destructive technology, providing continuous, rapid measurements of electromagnetic signal reflections from the ballast and embankment. The corresponding data can be analyzed to detect fouling, moisture content, and, most importantly, variations in layer thickness, which are essential for assessing track stability and drainage *[2]*.

Understanding the thickness of both the ballast and the underlying layers is particularly important, as these parameters directly influence the structural stability and drainage capacity of railway tracks *[1]*. GPR has also proven useful in detecting problems related to embankment instability and the risk of track settlement *[6]*.

Reference *[7]* demonstrated the effectiveness of GPR applications by collecting data from the centerline and sides of the track. They showed how consistent results indicate stability, while discrepancies highlight potential instability.

Despite its advantages, challenges remain in GPR applications. Electromagnetic interference from rails and sleepers, as well as complexities in optimizing antenna configurations *[7, 8, 9]* and data collection speeds *[10]*, can hinder data quality *[5]*. Moreover, the interpretation of GPR signals often relies on homogenized ballast models that assume uniform relative permittivity. While computationally efficient, homogenized models may lead to failure to capture the effect of real ballast heterogeneity. This in turn may lead to errors in interpreting data and layer thickness estimations.

Precise modeling of ballast and sub-ballast layers is essential to improve the accuracy of GPR data, particularly for thickness estimation. This study addresses the potential limitations of models by introducing a comparative framework that evaluates homogeneous and heterogeneous ballast modeling in GPR simulations. The research objectives are:

- To compare the effects of treating ballast as a homogeneous medium versus a heterogeneous medium with distinct stones and air properties on GPR signal behavior.
- To evaluate the accuracy of layer thickness estimation in varying substructure configurations.

By simulating electromagnetic wave propagation in more realistic ballast geometries, this study bridges the gap between computational simplicity and physical accuracy. The findings enable the evaluation of realistic modeling of the ballast bed for accurate layer thickness estimation from GPR reflection data.

## II METHODOLOGY AND MODEL SETUP

This study focuses on comparing the effects of homogeneous and heterogeneous ballast modeling on GPR signal behavior, with particular emphasis on the accurate estimation of ballast and sand layer thickness. It consists of development of heterogeneous ballast layer, creating homogeneous layers using the Complex Refractive Index Model (CRIM) model

[11] and simulation of GPR signal propagation using gprMax [12].

# A. Development of heterogeneous ballast layer

The development of the heterogeneous ballast layer begins with the creation of ten distinct stone models using Blender, a powerful 3D modeling software [13]. Each stone is designed with intricate polygonal meshes to replicate the irregular geometries of real ballast particles. These stones are exported as .obj files, preserving detailed vertex coordinates and triangular face definitions for further processing.

In Python, the .obj files are imported and voxelized by discretizing their bounding volumes into uniform grids using Delaunay Triangulation, which ensures high precision representation of the stone's geometry. Each stone model is then used to create a standardized block measuring  $0.1\mathrm{m}\times 0.1\mathrm{m}$  x  $0.1\mathrm{m}$ , which serves as a modular unit for constructing the ballast layer. A total of 147 such blocks are generated and systematically arranged to form a layered structure with dimensions of  $0.7\mathrm{m}\times 0.7\mathrm{m}\times 0.3\mathrm{m}$ , accurately simulating a realistic ballast layer.

To introduce physical realism, random rotations and translations are applied to the stones within the blocks using Euler Angle Transformations, creating natural variability in orientation and spatial positioning. Figure 1 presents a sample stone model, showcasing its geometry and irregular surface, which contribute significantly to the electromagnetic heterogeneity of the ballast layer.

![img-0.jpeg](img-0.jpeg)
Fig. 1. Voxelized sample stone.

# B. Layers and configurations

Three distinct layered configurations are designed to represent realistic railway substructure scenarios:

- Scenario 1:  $0.3\mathrm{m}$  ballast layer overlying  $0.5\mathrm{m}$  of clay.
- Scenario 2:  $0.3\mathrm{m}$  ballast layer, followed by a  $0.1\mathrm{m}$  sand layer, and  $0.4\mathrm{m}$  of clay.
- Scenario 3:  $0.3\mathrm{m}$  ballast layer, a  $0.3\mathrm{m}$  sand layer, and  $0.2\mathrm{m}$  of clay.

The ballast layer is modeled in two ways:

- Heterogeneous Model: Individual ballast stones are assigned specific relative permittivity values, with void spaces filled with air to accurately replicate the heterogeneous nature of the ballast.

- Homogeneous Model: The CRIM model is used to calculate the bulk relative permittivity of the ballast. This model combines the relative permittivity of stone and air based on their volume fractions.

# C. Material properties

The dielectric properties, including relative permittivity and conductivity, are assigned to each material based on their composition:

- Clay: Dry kaolinite clay with a porosity of  $45\%$ , a residual volumetric water content of  $5\%$ , and a conductivity of  $1 \times 10^{-8} \mathrm{~S/m}$ .
- Sand: Dry sand with a porosity of  $37.5\%$ , a residual volumetric water content of  $4.5\%$ , and a conductivity of  $1 \times 10^{-6} \mathrm{~S/m}$ .
- Ballast: Dry ballast with a porosity of  $49\%$ , a volumetric water content of  $0\%$ , and a conductivity of  $0 \, \text{S/m}$ .

# D. Simulation setup

The simulations are performed using gprMax, an open-source software that solves Maxwell's equations in 3D using the Finite-Difference Time-Domain (FDTD) method. This approach ensures an accurate representation of electromagnetic wave propagation within the subsurface layers.

The key simulation parameters are summarized in Table I.

TABLEI SIMULATION PARAMETERS

|  Parameters | Homogenizeda | Realistica  |
| --- | --- | --- |
|  Domain size | 0.74m x 0.74m x 1.098m  |   |
|  Diameter of stones | 0.023m-0.027m  |   |
|  Ballast thickness | 0.3m  |   |
|  Sand thickness | 0m-0.1m-0.3m  |   |
|  Clay thickness | 0.5m-0.4m-0.2m  |   |
|  εr of ballast | εr,efct = 3.73 | εr,stone = 8  |
|  εr of sand | εr,grains = 5, εr,efct = 4.54  |   |
|  εr of clay | εr,grains = 10, εr,efct = 6.69  |   |
|  Voxel size | 0.002m  |   |
|  Spatial sampling | 0.002m  |   |
|  S & R antennas' heightb | 0.078m  |   |
|  Horizontal distancec | 0.2m  |   |
|  Simulation time | 30ns  |   |

aBallast layer.
bSource and receiver antennas' height above the surface.
Horizontal distance between source &amp; receiver antennas.

A dipole antenna with a center frequency of  $1\mathrm{GHz}$  is employed for the simulations. The source time signature is modeled using a Ricker Wavelet, which effectively replicates the electromagnetic signals used in GPR surveys.

Each of the three scenarios is simulated twice:

- Using the bulk relative permittivity for the ballast layer.
- Treating the ballast layer as a heterogeneous medium.

# E. Boundary conditions

In gprMax, the default absorbing boundary conditions (ABCs) are first-order Complex Frequency Shifted (CFS) Perfectly Matched Layers (PML) with a thickness of 10 cells applied to each side of the model domain [12]. To ensure

Authorized licensed use limited to: Zhejiang University. Downloaded on October 31,2025 at 21:35:27 UTC from IEEE Xplore. Restrictions apply.

consistent boundary conditions across both homogeneous and heterogeneous cases, a PML boundary of 10 cells containing layers with a relative permittivity of 8 and a conductivity of  $0.01\mathrm{S / m}$  was utilized. These values were determined through preliminary simulations to optimize the configuration for realistic ballast scenarios.

This setup accommodates the inherently more scattered nature of heterogeneous scenarios while maintaining a lower level of scattering in homogenized cases, thus enabling logical comparisons between scenarios. Although this configuration increases contrast in homogeneous scenarios, the resulting effects occur outside the time range of interest for this study. Furthermore, the chosen boundary conditions reduce reflections from stones near the boundary in heterogeneous cases, allowing for the comparison of results under identical boundary conditions across all scenarios.

# III. RESULTS AND DISCUSSION

# A. Simulation results for homogeneous ballast layer

The simulation results for the homogeneous ballast layer are presented in Figure 2, which illustrates reflections from various interfaces across three scenarios. These results emphasize how the layer composition and thickness influence the detectability and separation of reflections.

![img-1.jpeg](img-1.jpeg)

![img-2.jpeg](img-2.jpeg)

![img-3.jpeg](img-3.jpeg)
Fig. 2. The reflections observed from various interfaces in three homogeneous ballast scenarios. (Top, H0) Scenario 1 consists of  $0.3\mathrm{m}$  homogeneous ballast layer overlying  $0.5\mathrm{m}$  of clay. (Middle, H1) Scenario 2 consists of  $0.3\mathrm{m}$  homogeneous ballast layer, followed by a  $0.1\mathrm{m}$  sand layer, and  $0.4\mathrm{m}$  of clay. (Bottom, H2) Scenario 3 consists of  $0.3\mathrm{m}$  homogeneous ballast layer, a  $0.3\mathrm{m}$  sand layer, and  $0.2\mathrm{m}$  of clay.

- Scenario H0: This scenario consists of a homogenized ballast layer overlying clay. A prominent reflection from the bottom of the ballast is observed at approximately 5.4 ns (blue circle). This reflection is clearly distinguishable due to the sharp interface between the ballast and the clay.

- Scenario H1: In this case, the configuration includes ballast, a  $0.1\mathrm{m}$  sand layer, and  $0.4\mathrm{m}$  clay. The reflection from the bottom of the ballast begins at approximately 5.6 ns (blue circle) and overlaps with the reflection from the thin sand layer, continuing up to 8.9 ns. While these reflections indicate the presence of two distinct layers, differentiating between them is challenging due to their overlap.
- Scenario H2: This scenario introduces ballast, a  $0.3\mathrm{m}$  sand layer, and  $0.2\mathrm{m}$  clay. The reflection from the bottom of the ballast at 5.6 ns (blue circle) is clearly distinguishable, unlike in H1. Due to the thicker sand layer, an additional reflection from the bottom of the sand layer is observed at around 10 ns (purple circle).

Across all scenarios, green oval shows the diminishing of small amplitude of reflection from surface and a late-time reflection from the boundary near 14 ns (orange circle) is consistently observed. However, this reflection occurs outside the time of interest for the study.

# B. Simulation results for heterogeneous ballast layer

The results for the heterogeneous ballast layer, shown in Figure 3, highlight the changes in reflection characteristics caused by the ballast's variability. Each scenario demonstrates how heterogeneity influences the behavior of the reflected signals.

![img-4.jpeg](img-4.jpeg)

![img-5.jpeg](img-5.jpeg)

![img-6.jpeg](img-6.jpeg)
Fig. 3. The reflections observed from various interfaces in three heterogeneous ballast scenarios. (Top, SH0) Scenario 1 consists of  $0.3\mathrm{m}$  heterogeneous ballast layer overlying  $0.5\mathrm{m}$  of clay. (Middle, SH1) Scenario 2 consists of  $0.3\mathrm{m}$  heterogeneous ballast layer, followed by a  $0.1\mathrm{m}$  sand layer, and  $0.4\mathrm{m}$  of clay. (Bottom, SH2) Scenario 3 consists of  $0.3\mathrm{m}$  heterogeneous ballast layer, a  $0.3\mathrm{m}$  sand layer, and  $0.2\mathrm{m}$  of clay.

- Scenario SH0: This scenario features a heterogeneous ballast layer overlying clay. The reflection from the top of the ballast layer decreases in amplitude, (green circle) followed by an increase around 5.6 ns, indicating the

Authorized licensed use limited to: Zhejiang University. Downloaded on October 31,2025 at 21:35:27 UTC from IEEE Xplore. Restrictions apply.

bottom of the ballast layer and its contrast with the clay (blue circle).
- Scenario SH1: In this configuration, ballast, a 0.1 m sand layer, and 0.4 m clay are included. The reflection from the ballast layer shows a continued decrease in amplitude (green circle), with a higher amplitude reflection starting around 6.9 ns and continuing until approximately 9.3 ns (blue circle).
- Scenario SH2: This scenario consists of a heterogeneous ballast layer, a 0.3 m sand layer, and 0.2 m clay. The reflection from the top of the ballast layer continues to decrease in amplitude (green circle), with a small increase observed around 6.5 ns. A prominent reflection from the bottom of the sand layer occurs at approximately 10 ns.

Similar to the homogeneous scenarios, a late-time reflection from the boundary near 14 ns (orange circle) is observed in all cases. However, this reflection remains outside the time of interest for the investigation.

### III-C Discussion

The results across all scenarios demonstrate the varying ability to estimate layer thickness and distinguish reflections in homogeneous and heterogeneous cases.

In Scenario 1, the thickness of the ballast layer is correctly estimated for both homogeneous and heterogeneous cases, with clear and distinguishable reflections.

For Scenario 2, the homogeneous case reveals multiple reflections extending over time, indicating the presence of two layers; however, estimating the thickness of the thin sand layer remains challenging. In the heterogeneous case, the reflections in the blue circle start later and have a shorter duration than in the homogeneous case. This is possibly caused by scattering within the ballast stones layer that is absent in the homogeneous case. Such scattering may partially cancel the reflection from the top of the sand layer. This could imply that scattering inside the ballast stones layer leads to a field with lower amplitude that is transmitted down below the ballast layer.

In Scenario 3, the homogeneous case allows for accurate estimation of the thickness of each layer, with well-separated and distinguishable reflections. Conversely, in the heterogeneous case, the bottom of the ballast layer cannot be estimated accurately due to less distinguishable reflections. The reflection from the top of the ballast layer decreases in amplitude, with only a small increase at the contact area with the sand layer. Despite this, the thickness of the sand layer in the heterogeneous case can still be accurately estimated.

These findings underscore the complexities introduced by heterogeneity and the challenges in interpreting reflections for accurate layer characterization.

## IV CONCLUSION

This study provides a comparative analysis of homogeneous and heterogeneous ballast models to understand their impact on GPR signal behavior and thickness estimation.

The results reveal that homogeneous models, while simplifying computations, overlook the complexities associated with heterogeneous ballast geometries, including scattering and reflection attenuation.

Accurate thickness estimation is notably more challenging in heterogeneous scenarios due to lower reflection distinguishability and increased variability in signal amplitude. These challenges emphasize the importance of simulating realistic ballast conditions to improve the reliability of GPR-based railway monitoring.

The results suggest that laboratory measurements can be performed to understand the quality of the current state of the numerical models. This, in turn, can enhance the predictive accuracy of GPR for real-world applications. This approach could enable the development of more robust, non-invasive railway maintenance systems.

## ACKNOWLEDGMENT

This research is conducted as part of the RESET project, supported by ProRail, the Dutch government organization responsible for maintaining and expanding the national railway network infrastructure.

## References

- [1] C. Esveld, *Modern Railway Track*, 2nd ed. MRT Productions, 2001, pp. 1–653.
- [2] S. Wang, G. Liu, G. Jing, Q. Feng, H. Liu, and Y. Guo, “State-of-the-Art Review of Ground Penetrating Radar (GPR) Applications for Railway Ballast Inspection,” *Sensors*, vol. 22, no. 7, p. 2450, 2022. [Online]. Available: https://doi.org/10.3390/s22072450
- [3] C. Rujikiatkamjorn, J. Xue, and B. Indraratna, Eds., *Proceedings of the 5th International Conference on Transportation Geotechnics (ICTG) 2024, Volume 2*. Springer Singapore, 2024. [Online]. Available: https://doi.org/10.1007/978-981-97-8217-8
- [4] C. Ferrante, L. B. Ciampoli, A. Benedetto, A. M. Alani, and F. Tosti, “Non-destructive technologies for sustainable assessment and monitoring of railway infrastructure: A focus on GPR and InSAR methods,” *Environmental Earth Sciences*, vol. 80, p. 806, Nov. 2021. [Online]. Available: https://doi.org/10.1007/s12665-021-10068-z
- [5] H. M. Jol, *Ground Penetrating Radar Theory and Applications*. Elsevier, 2009. [Online]. Available: https://doi.org/10.1016/b978-0-444-53348-7.x0001-4
- [6] T. R. Sussman, E. T. Selig, and J. P. Hyslip, “Railway track condition indicators from ground penetrating radar,” *NDT and E International*, vol. 36, no. 3, pp. 157–167, 2003.
- [7] G. R. Olhoeft and E. T. Selig, “Ground penetrating radar evaluation of railway track substructure conditions,” in *Proc. Ninth Int. Conf. Ground Penetrating Radar*, Santa Barbara, CA, Apr. 29–May 2, 2002, S. Koppenjan and H. Lee, Eds., Proc. SPIE, vol. 4758, pp. 48–53.
- [8] M. R. Clark, D. M. McCann, and M. C. Forde, “GPR as a tool for the characterization of ballast,” in *Proc. 6th Int. Conf. Railway Engineering*, London, UK, Apr. 30–May 1, 2003, pp. 9p.
- [9] T. Saarenketo, M. Silvast, and J. Noukka, “Using GPR on railways to identify frost susceptible areas,” in *Proc. 6th Int. Conf. Railway Engineering*, London, UK, Apr. 30–May 1, 2003, pp. 11p.
- [10] M. Clark, M. Gordon, and M. C. Forde, “Issues over high-speed non-invasive monitoring of railway trackbed,” *NDT and E International*, vol. 37, pp. 131–139, 2004.
- [11] J. R. Birchak, C. G. Gardner, J. E. Hipp, and J. M. Victor, “High dielectric constant microwave probes for sensing soil moisture,” *Proc. IEEE*, vol. 62, no. 1, pp. 93–98, Jan. 1974.
- [12] C. Warren, A. Giannopoulos, and I. Giannakis, “gprMax: Open source software to simulate electromagnetic wave propagation for Ground Penetrating Radar,” *Computer Physics Communications*, vol. 209, pp. 163–170, 2016.
- [13] B. O. Community, “Blender - a 3D modelling and rendering package,” Stichting Blender Foundation, 2018.