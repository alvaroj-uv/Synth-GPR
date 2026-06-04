Transportation Engineering 23 (2026) 100415

ELSEVIER

Contents lists available at ScienceDirect

Transportation Engineering

journal homepage: www.sciencedirect.com/journal/transportation-engineering

S

Full length article

# The use of Ground Penetrating Radar and artificial intelligence for automated railway trackbed stratigraphy and Ballast Fouling assessment

Ernest Mbubia Tchoua a,d, Jérôme Tissier a,c, Antoine Martin d, Yannick Fargier b, Amine Ihamouten a

$^{a}$ Gustave Eiffel University, Nantes Campus (ex IFSTTAR), Allée des Ponts et Chaussées, Nantes, 44344, France
$^{b}$ Gustave Eiffel University, Bron Campus, 25 Avenue François Mitterrand, Bron, 69675, France
$^{c}$ ESEO Graduate School of Engineering, 10 Boulevard Jean Jeanneteau, Angers, 49107, France
$^{\mathrm{d}}$ ETF - VINCI Construction, 67 Rue Henri Bleriot, Rueil-Malmaison, 92500, France

# ARTICLE INFO

Keywords:
Ballast layer
GPR
Step frequency
Ballast Fouling

# ABSTRACT

Intrusive trenching and coring remain the reference for railway trackbed diagnosis but lack coverage and repeatability. This paper proposes a hybrid GPR-AI framework that automates the detection of dielectric interfaces and the estimation of ballast permittivity and thickness. Synthetic FDTD simulations are used to evaluate Mask Region-based Convolutional Neural Network (Mask R-CNN) for interface segmentation and XGBoost (gradient-boosted trees)/Support Vector Regression(SVR) for layer-wise regression. Results on controlled data confirm high interface detection accuracy  $(\mathrm{IoU}\approx 0.81)$  and robust estimation of shallow dielectric parameters  $(R^2 &gt;0.9)$ , while sequential conditioning markedly improves deeper-layer predictions. Validation on field measurements acquired with a broadband (40-3000 MHz) GPR antenna array demonstrates good transferability of the methodology, with reliable stratigraphy reconstruction and dielectric-based material attribution along an operational track section. The framework unifies stratigraphy and fouling assessment in a single automated workflow, offering a scalable and interpretable alternative to invasive methods and paving the way for predictive maintenance at the network scale.

# 1. Introduction

Railway ballast is a granular material composed of crushed aggregates from natural, artificial, or recycled sources [1]. It plays a critical role in track performance by distributing loads, maintaining geometry, ensuring drainage, and dissipating energy and vibrations [2-5].

In practice, the service life of ballasted tracks is often shorter than expected, primarily due to progressive ballast degradation under repeated train loads [6]. Particle breakage, particularly beneath sleepers where stresses are highest, reduces angularity, surface roughness, and interlocking. This process leads to settlement and a progressive loss of bearing capacity [7-12]. Studies indicate that up to  $70\%$  of short-term vertical deformation originates in the ballast layer itself [2].

Tamping remains the most widespread maintenance practice for restoring track geometry [2]. Although effective in the short term, it accelerates ballast degradation through abrasion and breakage [13-15], particularly in the presence of fines. Dry fines hinder compaction, whereas wet fines act as a lubricant, further reducing shear strength [16,17].

Ballast fouling, caused mainly by aggregate breakdown (up to  $76\%$ ), progressively reduces void space and drainage capacity, thereby compromising the mechanical performance of the track [2,18-20]. Several indices have been proposed to quantify fouling, including the Fouling Index (FI) [2], the Percentage Void Contamination (PVC) [21], and the Relative Ballast Fouling Ratio (Rb-f) [22,23]. Among these, Rb-f provides a volumetric-based classification particularly well suited for integration with GPR dielectric analyses.

Recent advances in computer vision have also explored ballast condition assessment from surface images using deep convolutional or transformer-based architectures [24,25]. Although such vision-based approaches provide valuable insights into surface fouling and particle morphology, they remain limited to the visible layer and cannot access subsurface dielectric contrasts—an aspect that motivates the use of GPR-based signal interpretation in this study.

Compared to vision-based approaches, signal-based methods such as GPR provide complementary information by sensing the internal electromagnetic response of the trackbed rather than its surface texture. While image analysis techniques can efficiently quantify surface

https://doi.org/10.1016/j.treng.2025.100415

Received 6 October 2025; Received in revised form 21 November 2025; Accepted 8 December 2025

Available online 10 December 2025

2666-691X/© 2025 The Authors. Published by Elsevier Ltd. This is an open access article under the CC BY license (http://creativecommons.org/licenses/by/4.0/).

fouling and aggregate morphology, they are inherently restricted to the exposed layer and sensitive to lighting or occlusion conditions. In contrast, GPR offers volumetric information on subsurface stratigraphy and moisture content through the interpretation of wave reflections and dielectric contrasts. These two perspectives are thus complementary: vision-based methods excel in surface inspection and inventory tasks, whereas signal-based approaches enable quantitative, layer-wise characterization of ballast condition. The integration of both modalities could, in future work, support a more comprehensive multi-scale evaluation of railway trackbeds.

Ground Penetrating Radar (GPR) is a valuable non-destructive tool for ballast assessment. Conventional approaches include permittivity estimation through travel-time analysis or CRIM mixing models [26], spectral decomposition [27,28], and scattering envelope analyses [29]. However, most rely on fixed-frequency antennas (400 MHz--2 GHz), which involve trade-offs between resolution and penetration depth. Moreover, dielectric-based methods typically assume prior knowledge of layer thickness, which is often unavailable in the presence of irregular stratigraphy or severe signal attenuation [30,31].

To address these limitations, we propose a hybrid framework that integrates deep learning and supervised regression for GPR interpretation. This paper aims to evaluate a GPR--AI methodology for automated railway trackbed characterization. The study focuses on four key parameters: interface location, layer thickness, effective permittivity, and fouling level, as indicators of stratigraphy and trackbed condition. The specific research questions are: (i) can dielectric interfaces be automatically detected in both synthetic and field B-scans, (ii) can layer-wise permittivities and thicknesses be reliably estimated from A-scans, (iii) can these parameters be combined to infer ballast fouling levels in situ, and (iv) how transferable is the approach from controlled simulations to field measurements?

In a first step, we describe the hybrid methodology that combines interface detection with Mask R-CNN and regression models for permittivity estimation. Compared to previous deep-learning applications to GPR data — mostly limited to highway pavements or laboratory experiments [32,33] — the present study introduces several methodological and operational innovations. First, it extends instance segmentation (Mask R-CNN) to highly scattering railway environments, where coarse aggregates and moisture variability make interface detection particularly challenging. Second, it couples this segmentation stage with a physics-informed sequential regression of dielectric permittivity and thickness (SVR/XGBoost), enabling joint geometric and electromagnetic characterization within a unified pipeline. In addition, ballast fouling is quantified through the Rb-f, a volumetric index derived from the estimated dielectric permittivity in accordance with the material's moisture condition. Unlike empirical classifications directly affected by transient moisture variations, the Rb-f formulation primarily reflects the volumetric fraction of fine particles within the voids, making it more sensitive to fouling accumulation than to short-term hydric effects. This choice enhances the robustness of the dielectric--mechanical interpretation and provides a physically consistent bridge between electromagnetic observables and trackbed condition. Finally, the framework is validated through a dual-scale strategy combining controlled FDTD simulations and in situ broadband (40--3000 MHz) GPR measurements co-located with trench observations, thereby establishing a physically interpretable link between dielectric contrasts, stratigraphy, and ballast fouling under real operational conditions. We then apply this framework to synthetic datasets generated with gprMax to assess parameter identifiability, robustness to acquisition factors, and noise sensitivity. Lastly, the methodology is validated on in situ railway data acquired along a French track section, demonstrating its ability to reconstruct stratigraphy and assess ballast fouling. Together, these successive steps establish a comprehensive and non-destructive framework for predictive railway ballast monitoring.

## Material and methods

The methodology follows a modular workflow integrating interface detection and layer-wise permittivity estimation from GPR data (Fig. 1). The pipeline first evaluates whether dielectric boundaries are visible in the B-scan. When interfaces are detected, they are localized and subsequently used to constrain the permittivity estimation of each layer through supervised regression on A-scans. In the absence of detectable boundaries, the medium is treated as a single effective layer for direct permittivity estimation. The following sections detail each component of this framework.

Ground-truth data from boreholes, trench inspections or complementary measurements can be used at different stages of the pipeline to improve reliability and validate the predictions. The full procedure results in a stratigraphic characterization of the subsurface structure. The main components of this framework are detailed in the following subsections.

### Automatic interface detection

To identify dielectric discontinuities within GPR signals, a semantic image segmentation approach was applied to B-scan images. In GPR terminology, an A-scan represents a single time-domain trace of the reflected electromagnetic signal recorded at a fixed antenna position. A collection of adjacent A-scans acquired along the survey line forms a B-scan, which is a two-dimensional radargram displaying signal amplitude as a function of both time (vertical axis) and distance (horizontal axis). Each bright or dark feature within a B-scan typically corresponds to a subsurface interface or object producing a dielectric contrast (see Fig. 5, Fig. 6 for illustrative examples). These discontinuities correspond to transitions between layers of different permittivity, typically visible as hyperbolic or horizontal high-contrast reflections. The detection task is formulated as an instance segmentation problem: each interface is treated as a thin elongated object to be localized through pixel-wise binary mask prediction.

Among available deep learning techniques, the Mask R-CNN architecture proved to be particularly well-suited for this task due to its ability to segment narrow, low-contrast features with high spatial precision.

### Interface detection with mask R-CNN

The proposed instance segmentation model is based on the architecture introduced by [34], which extends Faster R-CNN [35] by adding a branch for pixel-level mask prediction. The architecture comprises: (i) a convolutional backbone (e.g. ResNet with Feature Pyramid Network) for feature extraction, (ii) a Region of Interest (RoI) alignment module for spatial encoding, and (iii) a prediction head that outputs, for each detected instance, the class, bounding box, and binary mask.

The network is trained by minimizing a multi-task loss function defined as:*L* = *L*_{*c**l**s*} + *L*_{*b**b**o**x*} + *L*_{*m**a**s**k*}where *L*_{*c**l**s*} denotes the classification loss (softmax), *L*_{*b**b**o**x*} the bounding-box regression loss (smooth L1), and *L*_{*m**a**s**k*} the pixel-wise binary cross-entropy loss.

### Inference and interface localization

At inference time, the trained model outputs one or more binary masks corresponding to detected interfaces in the input B-scan. The final interface position is extracted by computing the average vertical coordinate of active pixels for each image column. This results in a continuous curve representing the predicted interface.

In cases where no interface is detected, this may indicate either a truly homogeneous structure or a weak permittivity contrast between adjacent layers, insufficient to generate a detectable reflection.

E. Mbubia Tchoua et al.

Transportation Engineering 23 (2026) 100415

![img-0.jpeg](img-0.jpeg)
Fig. 1. Schematic representation of the hybrid processing workflow combining interface detection and layer-wise permittivity estimation from GPR data.

# 2.2. Permittivity and fouling estimation

This step exploits simulated A-scan signals to predict the permittivity of the modeled layers, assuming that propagation delays, amplitudes, and waveform shapes are governed by the dielectric properties of the materials. The problem is formulated as a supervised regression task, where the model learns to predict effective permittivities from a set of input GPR signals. Two machine-learning algorithms were employed: SVR [26] and XGBoost [37], an optimized implementation of Gradient Boosting [38]. These methods were selected for their robustness to noise, their ability to capture nonlinear relationships, and their demonstrated performance in related GPR-based regression tasks [39-41]. Once the effective permittivity is estimated, the corresponding material type or fouling severity level can be inferred using the predefined classification tables (Tables 1 and 3). Detailed formulations of both algorithms are presented in Sections 2.2.1 and 2.2.2, respectively.

# 2.2.1. Support Vector Regression

Support Vector Regression [36] seeks to approximate a function  $f(\mathbf{x}) = \langle \mathbf{w},\mathbf{x}\rangle +b$  that predicts the target values  $y_{i}$  with a tolerance of  $\varepsilon$ , while maintaining model flatness. The optimization problem is formulated as:

$$
\min  _ {\mathbf {w}, h, \xi_ {i}, \xi_ {i} ^ {*}} \frac {1}{2} \| \mathbf {w} \| ^ {2} + C \sum_ {i = 1} ^ {n} \left(\xi_ {i} + \xi_ {i} ^ {*}\right) \tag {2}
$$

subject to:

$$
y _ {i} - \left\langle \mathbf {w}, \mathbf {x} _ {i} \right\rangle - b \leq \varepsilon + \xi_ {i}
$$

$$
\langle \mathbf {w}, \mathbf {x} _ {i} \rangle + b - y _ {i} \leq \varepsilon + \xi_ {i} ^ {*}
$$

$$
\xi_ {i}, \xi_ {i} ^ {*} \geq 0
$$

Here,  $\varepsilon$  defines the margin of tolerance for error,  $\xi_{i}$  and  $\xi_{i}^{*}$  are slack variables for underestimation and overestimation respectively, and  $C &gt; 0$  is a regularization parameter controlling the trade-off between flatness of the function and tolerance to deviations beyond  $\varepsilon$ .

# 2.2.2. XGBoost regression

Gradient Boosting [38], implemented in this study via XGBoost [37], builds an additive model composed of a sequence of weak learners. The final prediction function is expressed as:

$$
F _ {M} (\mathbf {x}) = \sum_ {m = 1} ^ {M} \gamma_ {m} h _ {m} (\mathbf {x}). \tag {3}
$$

where  $h_m(\mathbf{x})$  denotes the  $m$ th weak learner and  $\gamma_{m}$  its associated weight. Each new learner is fitted to the pseudo-residuals computed as the

negative gradient of the loss function  $\mathcal{L}$  with respect to the current model prediction:

$$
\mathbf {r} _ {i} ^ {(m)} = - \left[ \frac {\partial \mathcal {L} \left(y _ {i} , F _ {m - 1} \left(\mathbf {x} _ {i}\right)\right)}{\partial F _ {m - 1} \left(\mathbf {x} _ {i}\right)} \right] \tag {4}
$$

This iterative process continues until a predefined number of iterations  $M$  is reached, or until the improvements become negligible.

# 2.3. Overview of the processing pipeline

After presenting the main components of the complete characterization framework illustrated in Fig. 1, the processing procedure unfolds as follows:

- Input of GPR data: analysis of both A-scan and B-scan profiles.
- Interface detection (Mask R-CNN): the segmentation algorithm is applied to the B-scan images to identify potential discontinuities between layers. When one or more interfaces are detected, their corresponding arrival times are extracted from the B-scan.
- Bifurcation depending on interface presence:

- Interface detected: the section is marked as a two-layer configuration. The corresponding thicknesses will be calculated after the regression stage using the extracted interface arrival times.
- No interface detected: the structure is considered either homogeneous or composed of layers with insufficient permittivity contrast to generate a detectable electromagnetic signature. A global equivalent permittivity will later be estimated through regression. When available, additional information from field observations or trench data may be used to estimate a potential boundary. In the least favorable case, and where the geometry allows, interpolation between two known interface positions is performed to ensure stratigraphic continuity.

- Permittivity regression (after detection):

- Two-layer case: the permittivity of the upper layer  $(\varepsilon_{1})$  is estimated from A-scan signals. This value, combined with the arrival time of the first subsurface interface, is used to calculate the thickness  $d_{1}$  of the upper layer using an analytical relation. A second regression is then performed to estimate the permittivity of the lower layer  $(\varepsilon_{2})$  using the signal,  $\varepsilon_{1}$ , and  $d_{1}$  as input.
- No-interface case: a regression model is applied to estimate a global equivalent permittivity  $\varepsilon_{\mathrm{eq}}$  from the A-scan signals.

E. Mbubia Tchoua et al.

Transportation Engineering 23 (2026) 100415

Table 1 Ballast classification based on Rb-f index (Relative Ballast Fouling Ratio, %), material characteristics, and relative permittivity ranges (adapted from multiple sources including [13,23,42]).

|  Class | Name | Characteristics | Rb-F (%) | Permittivity range (εr)  |
| --- | --- | --- | --- | --- |
|  Class 1 | Clean ballast | Clean aggregates, high porosity, low moisture, good drainage | < 2 | 3.0–3.5  |
|   |  Clean ballast | Clean aggregates, high porosity, wet (12%), good drainage | < 2 | 3.5–4.5  |
|  Class 2 | Slightly fouled ballast | Presence of fines, drainage still possible | 2–10 | 4.6–5.5  |
|   |  Slightly fouled ballast | Presence of fines, drainage still possible, low to moderate moisture | 2–10 | 5.6–6.5  |
|  Class 3 | Moderately fouled ballast | Significant fines, reduced drainage | 10–20 | 6.6–7.0  |
|   |  Moderately fouled ballast | Significant fines, reduced drainage, moderate moisture | 10–20 | 7.1–8.0  |
|  Class 4 | Fouled ballast | Large amount of fines, partial to total loss of drainage, quite dry | 20–50 | 8.1–9.5  |
|   |  Fouled ballast | Large amount of fines, partial to total loss of drainage, wet (12%) | 20–50 | 9.6–10.5  |
|  Class 5 | Saturated or highly fouled ballast | Saturation with water or fines, no drainage, inoperative ballast | ≥ 50 | > 10.5 (up to 20–38.5)  |

- Optional integration of ground-truth data: in low-contrast or uncertain cases, trench, coring, or field survey data can be integrated to guide or refine the estimation.
- Material identification: the estimated permittivity values are compared with the characteristic ranges defined in Table 1, allowing the material type to be inferred from the combination of estimated permittivity and observed moisture condition.
- Final stratigraphic characterization: a continuous stratigraphic description is produced, including the sequence of layers, their material nature, dielectric properties, Rb-f and thicknesses.

# 2.3.1. Fouling parameter - Rb-f

The Relative Ballast Fouling Ratio (Rb-f) was proposed by Indraratna et al. [22] to overcome the limitations of previous fouling indices. It is defined as the ratio between the solid volume of fine particles (passing the  $9.5\mathrm{mm}$  sieve) and that of ballast particles (retained on the  $9.5\mathrm{mm}$  sieve). This indicator accounts for both mass and specific gravity of the materials, thus providing a more representative measure of the nature and gradation of the fouling content. The formulation is expressed as:

$$
\mathrm {R b - f} = \frac {M _ {f} / G _ {v , f}}{M _ {b}} \times 1 0 0 \tag {5}
$$

where  $M_{f}$  and  $M_{b}$  are the dry masses of fouling particles (passing  $9.5\mathrm{mm}$ ) and clean ballast particles (retained on  $9.5\mathrm{mm}$ ), respectively, and  $G_{v,f}$  is the specific gravity of the fine particles. Therefore, Rb-f expresses the ratio of the solid volume of fines to the mass of ballast, integrating the intrinsic nature of the fouling material. The Rb-f index thus provides a consistent quantitative link between the physical degree of fouling and the corresponding dielectric behavior of ballast materials.

Table 1 summarizes the typical layer types and their association with Rb-f values, dielectric permittivity and moisture condition, as reported in the literature.

# 3. Application of the framework to Simulated Data

We first resort to controlled numerical simulations in order to (i) establish the identifiability of  $(\epsilon_{1},d_{1},\epsilon_{2})$  at  $1.4,\mathrm{GHz}$  and the physical plausibility of the inversions, (ii) quantify the impact of factors that can be controlled upstream (noise/SNR, acquisition frequency and geometry), (iii) optimize the acquisition plan and the sequential estimation order, and (iv) provide labeled and balanced datasets for supervised learning. The synthetic datasets are calibrated from realistic railway track characteristics reported in the literature, ensuring that the simulations reflect representative field conditions.

# 3.1. Synthetic data generation

# 3.1.1. Geometric modeling

The simulated domain represents cross-sectional slices of railway track structures composed of two distinct layers. The different layers

Table 2 Geometric modeling parameters used in the simulated structures.

|  Parameter | Value  |
| --- | --- |
|  Structure dimensions (height × width) | 0.80 × 4.0 m  |
|  First layer thickness | 0.13–0.79 m  |
|  Ballast grain size (diameter) | 36–60 mm  |

Table 3 Relative permittivity ranges and corresponding Rb-f values used for each material type.

|  Material type | Rb-f (%) | Permittivity range εr  |
| --- | --- | --- |
|  Clean ballast | < 2 | 2.5–5.0  |
|  Fouled ballast | 2–18 | 3.8–7.5  |
|  Highly fouled ballast | ≥ 55 | 15.0–18.5  |
|  Wet subgrade soil | ≥ 55 | 20.5–25.0  |

considered include clean ballast, fouled ballast, highly fouled ballast, and subgrade soil.

To ensure a physically realistic representation of the granular nature of the ballast, a 2D model inspired by [42] was implemented based on Random Irregular Polygons (RIP) for the clean and fouled ballast layers. Each polygon represents a ballast grain, defined by a mean radius and angular irregularities to generate diverse shapes and realistic random packing. In contrast, the highly fouled ballast and soil layers were modeled as homogeneous blocks.

By enforcing the condition that the lower layer always exhibits a higher permittivity than the upper layer, a total of many unique cases were generated, covering the following six structure types:

- clean ballast - highly fouled ballast,
- clean ballast - fouled ballast,
- clean ballast - subgrade soil,
- fouled ballast - highly fouled ballast,
- fouled ballast - subgrade soil,
- highly fouled ballast - subgrade soil.

The main geometric modeling parameters used in the simulations are summarized in Table 2.

Figs. 2, 3, and 4 illustrate three examples of modeled structures with different combinations of materials.

To ensure a clear separation between classes and to introduce a permittivity discontinuity at the interface, the relative permittivity values assigned to each layer were chosen according to the ranges presented in Table 3. While Table 1 provides a general classification that explicitly accounts for the hydric state of the layers, Table 3 lists the specific permittivity ranges effectively used in our simulations. These values reflect typical electromagnetic behavior under variable fouling levels, with highly fouled moist ballast and subgrade soil modeled as water-saturated materials [43].

# 3.1.2. Electromagnetic simulation with gprMax 2D

The A-scan and B-scan data used in this study were generated with the 2D electromagnetic simulator gprMax [44], a finite-difference

E. Mbubia Tchoua et al.

Transportation Engineering 23 (2026) 100415

![img-1.jpeg](img-1.jpeg)
Fig. 2. Example of a simulated structure: clean ballast over subgrade soil.

![img-2.jpeg](img-2.jpeg)
Fig. 3. Example of a simulated structure: Fouled ballast over highly fouled ballast.

![img-3.jpeg](img-3.jpeg)
Fig. 4. Example of a simulated structure: highly fouled ballast over subgrade soil.

time-domain tool for modeling electromagnetic wave propagation. The geometries defined in the previous stage were voxelized and converted into spatial maps of permittivity and conductivity. Each voxel was assigned the electromagnetic properties of the corresponding material, enabling the simulation of complex heterogeneous or layered configurations.

The model assumes non-magnetic, weakly conductive media, with electrical properties defined in the time domain as required by FDTD solvers.

# Model verification and validation

The gprMax 2D software has been extensively verified and widely used in the literature for modeling electromagnetic wave propagation in heterogeneous media. In this work, additional verification and validation steps were conducted to confirm the accuracy of the numerical implementation and the consistency of the adopted material parameters.

Benchmark tests were performed on single-layer dielectric structures and on laboratory ballast boxes of known thickness reproducing clean, fouled and subgrade conditions. For each configuration, the relative permittivity was estimated experimentally from travel-time measurements and used as input in gprMax 2D. The simulated two-way travel times were then compared with the measured ones. As reported in Table 4, the relative deviation remained below  $2\%$ , demonstrating the consistency of the simulated wave propagation with the real dielectric responses and confirming the validity of the adopted material parameters.

The main simulation parameters used in gprMax 2D are summarized in Table 5. These include the spatial resolution, the excitation waveform, and the total simulation time.

Table 4 Comparison between simulated and experimental two-way travel times, showing negligible discrepancies and confirming the validity of the numerical model.

|  Material | Simulated Δr (ns) | Measured Δrmean (ns) | Relative deviation (%)  |
| --- | --- | --- | --- |
|  Clean ballast | 2.33 | 2.30 | 1.30  |
|  Fouled ballast | 4.49 | 4.56 | 1.53  |
|  Subgrade soil | 2.86 | 2.81 | 1.77  |

Table 5 Simulation parameters used in gprMax 2D.

|  Parameter | Value  |
| --- | --- |
|  Domain dimensions (L × W × H) | 4.0 × 1.2 × 0.001 m  |
|  Cell size in x and y | 0.002 m  |
|  Cell size in z | 0.001 m  |
|  Central source frequency | 1.4 GHz  |
|  Injected waveform | Ricker wavelet  |
|  Signal recording time | 20 ns  |
|  Antenna height above surface | 0.3 m  |
|  Acquisition mode | Monostatic  |

The mesh size, excitation frequency, and signal recording time were carefully selected to ensure a trade-off between spatial resolution, sensitivity to internal structures, and numerical stability.

A central frequency of  $1.4\mathrm{GHz}$  was chosen to promote multiple scattering phenomena at the scale of individual ballast particles. This corresponds to the Mie scattering regime, in which the wavelength-to-particle size ratio enables enhanced sensitivity to changes in grain-scale

E. Mbubia Tchoua et al.

Transportation Engineering 23 (2026) 100415

![img-4.jpeg](img-4.jpeg)
Fig. 5. Example of a simulated B-scan image corresponding to the structure shown in Fig. 2: clean ballast over subgrade soil.

![img-5.jpeg](img-5.jpeg)
Fig. 6. Example of a simulated A-scan signal for the two-layer structure in Fig. 2. The signal exhibits two main reflections corresponding to dielectric interfaces.

composition and fouling level—particularly relevant for distinguishing between clean, fouled, and highly fouled ballast.

The mesh dimensions were set to  $2\mathrm{mm}$  in the horizontal plane and  $1\mathrm{mm}$  in depth to ensure compatibility with the simulated grain sizes, while satisfying the numerical stability constraints imposed by the Courant-Friedrichs-Lewy condition [45]. This resolution also allows accurate reconstruction of the irregular interfaces defined in the granular geometries.

Two types of simulations were carried out depending on the nature of the required outputs. The first type generated dense B-scan images using a fine lateral scanning step, suitable for automatic interface detection (see Section 2.1). The second type produced individual A-scan signals with a coarser spatial step, which are used for layer-wise characterization of the ballast (see Section 3.2.2).

An example of a simulated B-scan image is shown in Fig. 5. The upper and lower reflections correspond to dielectric contrasts between successive layers, allowing for potential interface localization and classification.

In addition, Fig. 6 shows a typical A-scan signal extracted at a fixed lateral position from a simulated two-layer structure. This type of signal is used as input for permittivity regression tasks, as discussed in Section 3.2.2.

The full synthetic dataset consists of both B-scan images and individual A-scan signals, generated across a wide variety of structural configurations and permittivity combinations. Table 6 summarizes the number of samples used for training and evaluation in each data modality.

Table 6 Number of synthetic samples used for model training and evaluation.

|  Data type | Number of samples  |
| --- | --- |
|  B-scan images | 4588  |
|  A-scan signals | 28,800  |

# 3.2. Result

# 3.2.1. Interface detection

# Data Annotation

In this study, the interfaces present in the simulated B-scan images are considered as elongated linear objects to be precisely segmented. The goal is to accurately detect their position and shape within each image, even in cases where the dielectric transition between layers is gradual or ambiguous.

Annotations were manually performed using binary masks that closely follow the visual trace of the interface in each image. Each interface is treated as an independent instance, allowing the use of instance segmentation models. The annotations were encoded in the COCO format [46], which is widely supported by modern deep learning frameworks such as Detectron2 [47].

# Dataset Splitting

The interface detection process relies on a dataset of 4588 synthetic B-scan images, each corresponding to a simulated two-layer structure.

E. Mbubia Tchoua et al.

Transportation Engineering 23 (2026) 100415

![img-6.jpeg](img-6.jpeg)
(a) Low-contrast case: the second interface is not detected. The predicted contours (green/yellow) follow the ground truth (red) only for the upper interface.

![img-7.jpeg](img-7.jpeg)
(b) Favorable case: both interfaces are detected, and the predicted contours closely match the ground truth despite local irregularities, which partly explain the reduced Precision.
Fig. 7. Examples of interface detection on synthetic B-scan images. Ground truth is shown in red and predicted contours in green/yellow.

Table 7 Average interface detection performance on the test set.

|  Metric | IoU | Precision | Recall | F1-score  |
| --- | --- | --- | --- | --- |
|  Mean value | 0.81 | 0.87 | 0.92 | 0.88  |

Every image depicts at least one visible interface either between two materials or at the surface and in some cases multiple interfaces due to structural irregularities.

From this dataset, 400 images were reserved for the test set. The remaining 4188 images were split into training and validation subsets using an 80/20 ratio. To enhance diversity and model robustness, data augmentation techniques such as vertical translation and contrast adjustment were applied to the training set.

# Detection Results

The trained interface detection model was evaluated on the independent test set of 400 synthetic B-scan images. Performance was assessed using Intersection over Union (IoU), Precision, Recall, and F1-score, averaged over all detected interfaces.

As reported in Table 7, the model achieved a high mean IoU of 0.81, indicating accurate interface localization. The Recall reached 0.92, showing that missed detections are rare, while the slightly lower Precision (0.87) reflects occasional over-segmentation in complex structures. The resulting F1-score of 0.88 confirms a balanced trade-off between detection sensitivity and precision.

To further illustrate the model's behavior, Fig. 7 presents representative cases. In low-contrast conditions, some interfaces are missed, while in more favorable situations the predicted contours align well with the ground truth despite local irregularities, which also contribute to the minor drop in Precision.

# 3.2.2. Permittivity estimation

# Learning Strategy

The aim is to estimate the equivalent permittivities  $\varepsilon_{1}$  (upper layer) and  $\varepsilon_{2}$  (lower layer) from simulated A-scan signals. Each signal corresponds to a two-layer structure composed of clean, fouled, highly fouled ballast, or subgrade soil. The lower layer always has higher permittivity. To capture realistic in situ variability, both linear and curved interfaces were simulated.

Although material classification could have been considered, regression was preferred to enable continuous permittivity retrieval and

subsequent thickness estimation. Three input configurations were evaluated:

1. Signal only: direct estimation of both upper- and lower-layer permittivities  $(\varepsilon_{1}$  and  $\varepsilon_{2})$  from the raw A-scan.
2. Signal  $+\hat{\varepsilon}_{1}$ : estimation of  $\varepsilon_{2}$  using the signal enriched with the known or previously estimated upper-layer permittivity.
3. Signal  $+\hat{\varepsilon}_1 + d_1$ : estimation of  $\varepsilon_{2}$  using the signal together with the upper-layer permittivity and its thickness.

# Regression models and protocol

Support Vector Regression (SVR, RBF kernel) and XGBoost were trained on a dataset of 28,600 signals. A total of 22,880 samples were used for 5-fold cross-validation during hyperparameter optimization, while the remaining 5720 samples constituted an independent test set. All results reported correspond exclusively to this independent test set and therefore reflect the generalization performance on unseen permittivity combinations.

# Evaluation metrics

Model performance was assessed using Mean Absolute Error (MAE), Root Mean Square Error (RMSE), and  $R^2$ , quantifying both accuracy and robustness.

# 3.3. Results

# Global estimation of permittivities

All models were trained using the optimal hyperparameter sets identified through the Bayesian searches. For SVR, the best-performing configurations correspond to  $(C,\epsilon ,\gamma) = (233.5,5.7\times 10^{-3},6.4\times 10^{-4})$  for  $\epsilon_{1}$  and (455.8,  $10^{-3}$ ,  $8.5\times 10^{-4}$ ) for  $\epsilon_{2}$ . For XGBoost, the optimal parameters include moderately deep trees and strong regularization for  $\epsilon_{1}$  (max_depth = 7, colsample_bytree = 0.81, subsample = 0.75, learning_rate = 0.083,  $n_{\mathrm{estim}} = 833$ ,  $\lambda = 0.094$ ), while  $\epsilon_{2}$  requires a deeper ensemble (max_depth = 10, colsample_bytree = 0.57, subsample = 1.0, learning_rate = 0.0089,  $n_{\mathrm{estim}} = 1200$ ,  $\lambda = 10^{-4}$ ).

Table 8 summarizes the estimation accuracy at  $1.4\mathrm{GHz}$ . For the upper layer, both SVR and XGBoost yield highly accurate predictions (MAE  $\approx 2\%$ ,  $R^2 = 0.99$ ), confirming that  $\varepsilon_{1}$  can be reliably estimated from the signal alone. In contrast, direct estimation of  $\varepsilon_{2}$  from the signal is much less precise (MAE  $15\% - 18\%$ ,  $R^2 &lt; 0.65$ ). Adding  $\varepsilon_{1}$  alone does not change this outcome, but the joint inclusion of  $\varepsilon_{1}$  and  $d_{1}$  enables accurate retrieval of the deeper-layer permittivity. The

E. Mbubia Tchoua et al.

Transportation Engineering 23 (2026) 100415

Table 8 Summary of permittivity estimation accuracy across input configurations at  $1.4\mathrm{GHz}$  (SVR vs XGBoost).

|  Input | SVR |   |   | XGBoost  |   |   |
| --- | --- | --- | --- | --- | --- | --- |
|   |  MAE (%) | RMSE | R2 | MAE (%) | RMSE | R2  |
|  ε1(signal) | 2.4 | 0.25 | 0.99 | 2.1 | 0.19 | 0.99  |
|  ε1(signal) | 18.3 | 4.6 | 0.50 | 15.2 | 3.9 | 0.64  |
|  ε2(signal, ε1) | 18.3 | 4.6 | 0.50 | 15.2 | 3.9 | 0.63  |
|  ε2(signal, ε1, d1) | 14.7 | 3.8 | 0.66 | 6.5 | 2.0 | 0.90  |

Table 9 Noise robustness with XGBoost: estimation errors at  $\mathrm{SNR} = 10$  dB.

|  Parameter | Training → Test | MAE (%) | R2  |
| --- | --- | --- | --- |
|  ε1 | Clean → Noisy | 37.4 | 0.38  |
|  ε2 | Clean → Noisy | 37.7 | -0.47  |
|  ε1 | Noisy → Noisy | 6.1 | 0.99  |
|  ε2 | Noisy → Noisy | 20.5 | 0.48  |

Table 10 Comparison of  $\varepsilon_{2}$  estimation accuracy at  $900\mathrm{MHz}$  with XGBoost.

|  Output(Input) | MAE (%) | RMSE | R2  |
| --- | --- | --- | --- |
|  ε1(Signal) | 1.75 | 0.16 | 0.99  |
|  ε2(Signal) | 12.4 | 3.2 | 0.75  |
|  ε2(Signal + ε1) | 12.3 | 3.2 | 0.75  |
|  ε2(signal, ε1, d1) | 6.5 | 1.9 | 0.91  |

gain is particularly clear for XGBoost, where the MAE drops to  $6.5\%$  and  $R^2$  rises to 0.90, while SVR remains limited ( $R^2 = 0.66$ ). This highlights that boosted ensembles are better suited than SVR for capturing the nonlinear dependencies required for deeper-layer permittivity estimation.

# Noise robustness

The noise robustness analysis (Table 9) is reported for XGBoost. When models trained on clean signals are applied to noisy data at SNR  $= 10$  dB, performance degrades sharply, especially for  $\varepsilon_{2}$  where  $R^2$  becomes negative. However, retraining directly on noisy data restores stability:  $\varepsilon_{1}$  remains highly accurate (MAE  $6.1\%$ ,  $R^2 = 0.99$ ), while  $\varepsilon_{2}$  predictions become usable ( $R^2 \approx 0.48$ ). This indicates that realistic levels of measurement noise can be tolerated provided the training conditions match the target acquisition environment.

# Frequency effect (900 MHz)

Table 10 presents the single-band results at  $900\mathrm{MHz}$ , obtained with XGBoost. As expected,  $\varepsilon_{1}$  is recovered with near-perfect accuracy  $(R^{2} = 0.99)$ . For  $\varepsilon_{2}$ , signal-only predictions remain challenging (MAE  $12.4\%$ ,  $R^{2} = 0.75$ ), and adding  $\varepsilon_{1}$  does not improve performance. By contrast, including both  $\varepsilon_{1}$  and  $d_{1}$  halves the error (MAE  $6.5\%$ ,  $R^{2} = 0.91$ ). This demonstrates that the sequential pipeline transfers effectively across acquisition frequencies and maintains high accuracy even under narrower-band excitation.

# 3.3.1. Layer characterization

The final step combines interface detection and permittivity estimation to obtain a full stratigraphic description of the ballast layers, including both dielectric properties and thickness. Under the assumption of a homogeneous and weakly dispersive dielectric medium, the thickness  $d$  of a layer with relative permittivity  $\varepsilon_r$  can be obtained from the two-way travel time  $t$  as:

$$
d = \frac {c _ {0} \cdot t}{2 \sqrt {\varepsilon_ {r}}}, \tag {6}
$$

where  $c_{0}$  is the speed of light in vacuum. This relation allows direct estimation of layer thicknesses once  $\varepsilon_{r}$  and the interface positions have been determined.

Table 11 Characterization results for a clean-most fouled ballast structure.

|  Parameter | Reference | Estimated | AE (%)  |
| --- | --- | --- | --- |
|  ε1 (clean) | 3.40 | 3.403 | 0.1%  |
|  ε2 (most fouled) | 15.35 | 14.84 | 3.3%  |
|  d1 (m) | 0.246 | 0.234 | 4.9%  |
|  d2 (m) | 0.554 | 0.566 | 2.2%  |

Note—AE denotes the absolute error. Percent AE is computed as  $100 \times (\overline{x} - x) / |x|$ , where  $x$  is the reference and  $\overline{x}$  the estimate.

# Structures with detectable interfaces

When a dielectric contrast generates a clear reflection, the interface is segmented from the B-scan and its position extracted. The upper-layer permittivity  $\varepsilon_{1}$  is estimated by regression from the corresponding A-scan, then used with the measured travel time to compute thickness  $d_{1}$ . This information, combined with the signal and the interface position, enables regression of the lower-layer permittivity  $\varepsilon_{2}$  and thickness  $d_{2}$ .

Table 11 summarizes the results obtained when testing the proposed methodology on a clean-most fouled ballast structure. Absolute errors (AE) are  $0.1\%$  for  $\varepsilon_{1}$  and  $3.3\%$  for  $\varepsilon_{2}$ , confirming the robustness of the pipeline even under strong dielectric contrasts.

# Structures without detectable interfaces

When permittivity contrasts are weak (e.g., clean vs. slightly fouled ballast), no reflection is visible and the interface cannot be localized. In this case, only a global equivalent permittivity can be estimated from the A-scan, which limits the accuracy of deeper-layer characterization. Integrating ground-truth information from trenches or boreholes can significantly improve parameter estimation in such cases, underlining the benefit of hybrid electromagnetic-geotechnical approaches.

# 3.4. Discussion

The synthetic analysis highlights clear differences between models and input configurations. XGBoost consistently outperforms SVR, particularly for estimating the lower-layer permittivity  $\bar{\varepsilon}_{2}$ . This behavior arises from the nonlinear dependencies involved: whereas  $\bar{\varepsilon}_{1}$  can be inferred directly from shallow reflections with high accuracy,  $\bar{\varepsilon}_{2}$  depends simultaneously on deeper signal components and on the propagation through the upper layer. Boosted ensembles are better suited to learn such cascaded relationships, while SVR is more affected by error propagation once  $\bar{\varepsilon}_{1}$  is introduced as an additional input feature.

From a physical standpoint, the improvement observed when combining  $\bar{\varepsilon}_{1}$  and  $d_{1}$  confirms the relevance of the sequential hypothesis: the upper-layer properties constrain the time-depth conversion and reduce ambiguity when estimating deeper permittivity. This is consistent with previous studies showing that ballast permittivity increases with fouling and moisture [43,48], while deeper retrieval remains challenging when attenuation and scattering obscure the reflections. The assumption of homogeneous layers facilitates the inversion but neglects intra-layer gradients, which likely explains the residual errors on  $\bar{\varepsilon}_{2}$ .

The noise robustness tests indicate that models trained on clean data do not generalize well to noisy scenarios, leading to unstable predictions. This confirms that realistic training conditions are essential for generalization, in line with recent recommendations [26,28]. Future improvements may include explicit modeling of intra-layer variability, data augmentation with realistic noise, and the integration of additional physical priors such as CRIM-based mixing laws or scattering descriptors.

Overall, the synthetic experiments validate the key assumptions of the proposed pipeline and provide a clear selection of the most relevant configurations: XGBoost emerges as the most robust regression

E. Mbubia Tchoua et al.

Transportation Engineering 23 (2026) 100415

![img-8.jpeg](img-8.jpeg)
Fig. 8. Surveyed railway test section from KP  $40 + 300$  to KP  $47 + 300$  (Saint-Fargeau-Ponthierry, France).

model, and the sequential conditioning strategy significantly enhances the estimation of deeper permittivity. These results are therefore used to restrict the set of candidate models for the subsequent field analysis. Only the numerically validated configurations are retrained on real B-scans, ensuring continuity between the two stages while avoiding redundant experimentation. This motivates the transition to the experimental validation presented in the following section, which evaluates the transferability and robustness of the calibrated methodology under real-world operational conditions.

# 4. Application of the framework to Railway Field Data

Building on the calibration results obtained from the synthetic analyses (Section 3), the proposed methodology was next applied to real GPR measurements acquired along an operational railway section. This stage aims to evaluate the transferability and robustness of the workflow under realistic conditions involving natural heterogeneity, variable moisture, and acquisition artefacts. Such an extension provides a cross-domain validation step linking simulation-based calibration to in situ demonstration.

# 4.1. Field data

Field data were collected on several French railway track sections during scheduled maintenance operations involving ballast renewal. The test and validation section, illustrated in Fig. 8, was surveyed

around the locality of Saint-Fargeau-Ponthierry in the Seine-et-Marne department (France), extending from KP  $40 + 300$  to KP  $47 + 300$ . Here, "KP" denotes the French point kilométrique, i.e., the kilometer post distance measured from Paris as the reference origin. This segment was used to evaluate fouling detection and subsurface characterization within the proposed framework.

# 4.1.1. Acquisition setup

The survey employed a GPR system consisting of a GeoScope control unit, a Kontur Air A1821 multi-channel ultra-wideband antenna, a Stonex S850 GNSS receiver, a distance measurement instrument, and an acquisition laptop. The antenna operates over a broad frequency range (40-3,000 MHz), enabling both high-resolution imaging of shallow interfaces and deeper penetration for fouled layers. The system was mounted in a contactless configuration, with the antenna positioned approximately  $0.3\mathrm{m}$  above the sleepers.

# 4.1.2. Acquisition protocol

The equipment was installed on a lightweight non-motorized rail cart to minimize electromagnetic interference while ensuring mechanical stability, as illustrated in Fig. 9. Data were collected at a steady speed of about  $5\mathrm{km / h}$ . Two successive passes were performed for each section, with the antenna centered first over the left rail and then over the right rail, ensuring full lateral coverage of the trackbed. Each pass produced densely sampled A-scan profiles with centimeter-level georeferencing, which were subsequently assembled into longitudinal and transverse B-scans for analysis.

E. Mbubia Tchoua et al.

Transportation Engineering 23 (2026) 100415

![img-9.jpeg](img-9.jpeg)
Fig. 9. GPR acquisition system mounted on a manually driven rail cart.

# 4.1.3. Ground-truth data

As part of the GPR inspection campaigns, several exploratory trenches (Fig. 10) were manually excavated at different locations along the investigated railway section. In addition to these trenches, penetro-endoscopic probes were performed, providing complementary qualitative insights into the condition of the layers and their thicknesses. Together, these investigations supplied both visual descriptions of materials and geometric data regarding the subsurface structure. This ground-truth dataset served as a reference for the supervised training of permittivity regression model.

The spacing and frequency of the trenches and penetro-endoscopic probes were not uniform and were primarily determined by two criteria:

- noticeable variations in surface properties (e.g., grain size, moisture content, compaction);
- abnormal or high-contrast electromagnetic signatures observed on the GPR profiles during acquisition.

We used the field observations to annotate the A-scan profiles with permittivity values defined in Table 1, and these annotations served as reference labels for model training and validation.

# 4.2. Results

# 4.2.1. Interface detection

Data Annotation

The objective mirrors the synthetic-data case: detect dielectric interfaces in B-scan images acquired along railway track sections. Raw B-scans are converted into images and partitioned into non-overlapping  $4\mathrm{m}$  segments to standardize input dimensions and preserve spatial localization of labels. Given the diversity of in situ conditions (e.g., moisture variability, fouling, geometric irregularities), annotation is a critical step because interface visibility ranges from clear to marginal.

Manual annotations followed the protocol established for the synthetic dataset (see Section 3.2.1). In low-visibility or discontinuous-reflection areas, annotators infer the most plausible path by local interpolation, guided by neighboring columns and stratigraphic context. Ambiguous or cluttered regions are left unlabeled and therefore do not contribute to the training loss. Labels are stored in the same instance-segmentation format as for the synthetic data to ensure full compatibility with the training and evaluation pipeline.

# Dataset Splitting

The in situ corpus comprises 1,150 images for training and 395 images for validation. To increase variability and improve robustness to acquisition artefacts, the training set is augmented with small random rotations and contrast adjustments. After augmentation, the effective training set totals 27,500 images, while the validation set remains unchanged to provide an unbiased estimate of generalization performance. This substantial increase in data volume not only mitigates the risk of overfitting, but also exposes the detector to a wider spectrum of possible field conditions, thereby reinforcing the reliability of the learned features for interface detection.

E. Mbubia Tchoua et al.

Transportation Engineering 23 (2026) 100415

![img-10.jpeg](img-10.jpeg)
Fig. 10. Example of an exploratory trench performed on an inspected track section.

Table 12 Average interface detection performance on the in situ test set.

|  Metric | IoU | Precision | Recall | F1-score  |
| --- | --- | --- | --- | --- |
|  Mean value | 0.73 | 0.79 | 0.80 | 0.78  |

# Detection Results

The interface detector was evaluated on an independent in situ test set of 80 B-scan images. Summary metrics are reported in Table 12. The overall performance remains consistent given the variability of field conditions. It is important to note that the training and validation interfaces were manually annotated, whereas real B-scans often present weakly contrasted or irregular boundaries. Such labeling uncertainty introduces small local discrepancies between ground truth and predictions, and even minor vertical shifts can significantly penalize pixel-based metrics such as IoU and F1-score. This explains the moderate decrease compared to synthetic results, while the detected contours remain sufficiently coherent for the subsequent time-depth conversion and dielectric regression.

A representative qualitative result is provided in Fig. 11, where the ground-truth mask is overlaid in green and the prediction in red.

It is important to note that the detected interfaces correspond to geometric boundaries between successive layers. Their physical nature (e.g., clean ballast, fouled ballast, or subgrade) can only be determined through dielectric characterization in the subsequent analysis.

# 4.2.2. Permittivity estimation

For the in situ dataset, each A-scan associated with the previously detected interfaces (Section 4.2.1) was converted into a feature vector, and the predictions were conditioned sequentially to preserve physical consistency across layers. In this framework, the permittivity  $\varepsilon_{1}$  estimated at  $t_1$  is used as an input for the regression of  $\varepsilon_{2}$ , ensuring that deeper-layer predictions remain constrained by the properties of the upper layer. A total of 52,130 A-scans were extracted from

![img-11.jpeg](img-11.jpeg)
Fig. 11. Example of interface detection on an in situ B-scan image. Ground truth in green; prediction in red.

Table 13 XGBoost regression results for experimental permittivity estimation across input configurations.

|  Input | MAE | RMSE | R2  |
| --- | --- | --- | --- |
|  ε1(signal) | 0.27 | 0.33 | 0.76  |
|  ε2(signal, ε1, d1) | 0.41 | 0.53 | 0.93  |

the field measurements. Among them, 46,917 samples were used to train and validate the regression models using a 5-fold cross-validation procedure, while 5213 samples formed an independent test set. XGBoost models were trained on this dataset, and the predicted permittivities were subsequently mapped to fouling classes (Table 1) for interpretation.

# Regression results

Table 13 presents the regression performance obtained on the independent test set across the considered input configurations. Bayesian optimization was used to determine the optimal XGBoost settings for each layer. For  $\hat{\varepsilon}_1$ , the best-performing model relies on a moderately deep ensemble with strong subsampling and regularization (max_depth = 7, colsample_bytree = 0.81, subsample = 0.75, learning_rate = 0.083,  $n_{\mathrm{estim}} = 833$ , min_child_weight = 5.76, reg_lambda = 0.094). For  $\hat{\varepsilon}_2$ , the optimal configuration corresponds to a deeper boosted model (max_depth = 10, colsample_bytree = 0.57, subsample = 1.0, learning_rate = 0.0089,  $n_{\mathrm{estim}} = 1200$ , min_child_weight = 0.001, reg_lambda = 10-4).

The estimation of the upper-layer permittivity  $\hat{\varepsilon}_{1}$  from the raw signal remains stable, while supplying the sequentially estimated physical parameters  $(\hat{\varepsilon}_{1},\hat{d}_{1})$  enables accurate retrieval of the deeper-layer permittivity  $\hat{\varepsilon}_{2}$ . This confirms that deeper-layer prediction requires upper-layer constraints and supports the relevance of the sequential conditioning strategy.

Overall, these findings demonstrate that XGBoost provides stable and physically coherent predictions across layers. It is also worth noting that the lower  $R^2$  observed for  $\hat{\varepsilon}_1$  is partly due to the limited variability of first-layer permittivity in the in situ dataset: since surface layers almost systematically consist of clean ballast, the target values span a very narrow range, and even small absolute errors mechanically reduce the  $R^2$  despite low MAE and RMSE values. Incorporating the sequentially estimated upper-layer permittivity and thickness significantly constrains the inversion and enhances the reliability of  $\hat{\varepsilon}_2$ . This validates the relevance of the proposed conditioning strategy and confirms its applicability under real measurement conditions.

# 4.2.3. Layer characterization

To obtain a complete stratigraphic description, two complementary outputs were fused: (i) interface detection on B-scans, and (ii) layerwise permittivity regression on A-scans. For field deployment, the antenna channel centered between the rails was used, and the data

E. Mbubia Tchoua et al.

Transportation Engineering 23 (2026) 100415

![img-12.jpeg](img-12.jpeg)
Fig. 12. Reconstructed track stratigraphy for the validation section [KP  $40 + 300 - \mathrm{KP}44 + 000$ ].

Table 14 Comparison between ground-truth and GPR-estimated interfaces along the validation section [KP  $40 + 300 - \mathrm{KP}44 + 000$  ]. Depths in meters; absolute differences in meters. Moisture conditions from trench inspections.

|  Position (m) | GT interface (m) | GPR interface (m) | Absolute difference (m) | Moisture condition  |
| --- | --- | --- | --- | --- |
|  40,500 | 0.82 | 0.74 | 0.08 | dry  |
|  40,900 | 0.76 | 0.73 | 0.03 | -  |
|  41,028 | 0.82 | 0.77 | 0.05 | -  |
|  41,400 | 0.72 | 0.75 | 0.03 | -  |
|  41,800 | 0.67 | 0.71 | 0.04 | -  |
|  42,161 | 0.69 | 0.66 | 0.03 | -  |
|  42,300 | 0.72 | 0.75 | 0.03 | -  |
|  42,700 | 0.66 | 0.72 | 0.06 | -  |
|  43,100 | 0.84 | 0.88 | 0.04 | -  |
|  43,250 | 0.82 | 0.81 | 0.01 | -  |
|  43,350 | 0.79 | 0.82 | 0.03 | -  |
|  43,450 | 0.86 | 0.83 | 0.03 | -  |
|  43,900 | 0.94 | 0.85 | 0.09 | dry  |

were band-pass filtered to [80, 1500] MHz to enhance reflector visibility. The Mask R-CNN detector was applied independently to the outbound and inbound passes; both predictions were then co-registered and merged to improve spatial continuity and reduce missed boundaries.

The models were trained and validated over multiple work sites, and subsequently tested on an independent section from KP  $40 + 300$  to KP  $44 + 000$ . Fig. 12 shows the reconstructed track stratigraphy along this validation segment. The detected interfaces, initially expressed in two-way travel time, were converted into depths using Eq. (6) and the regressed relative permittivity  $\varepsilon_{r}$ . Following the regression step, the Rb-f value for each layer was inferred from the predicted permittivity, using the classification ranges defined in Table 1 and considering the corresponding moisture conditions. In addition to layer thickness, the inferred Rb-f values provide a physically interpretable characterization of the materials, enabling their attribution to clean, fouled, or highly fouled ballast depending on the corresponding range.

A single summary table (Table 14) consolidates, for each reference position, the ground-truth (GT) interface depth, the GPR-estimated depth, their absolute difference, and the observed moisture condition. These values provide a direct comparison between reference and predicted interfaces, offering a compact yet comprehensive evaluation of the framework's performance across the tested segment.

The analysis focuses on the discrepancies between ground-truth (GT) and GPR-derived depths. Overall, the first interface — corresponding to the ballast/sub-ballast boundary — shows consistent agreement within a few centimeters, confirming the robustness of the detection model for upper layers. Slightly larger deviations appear at greater

depths, mainly due to signal attenuation and local heterogeneities affecting reflector contrast. Since all surveyed locations correspond to dry conditions, moisture-induced permittivity variations can be ruled out, indicating that the residual discrepancies are primarily related to spatial variability of material properties and positioning uncertainties.

These results confirm that the proposed framework provides reliable estimates of upper-layer geometry and dielectric behavior under dry field conditions, while deeper interfaces remain more sensitive to signal degradation and material heterogeneity.

# 4.2.4. Discussion

Similarly to the synthetic experiments, the proposed pipeline was applied to the in situ GPR measurements collected along the track, yielding consistent and robust results. In this validation phase, the analysis focused on the characterization of the first two layers of the trackbed. The processing framework combines automated interface detection with layer-wise permittivity regression, offering a comprehensive and fully data-driven approach for subsurface characterization. This integration of deep-learning-based segmentation with physical regression models constitutes one of the main strengths of the study, ensuring both interpretability and operational applicability in railway maintenance contexts.

The framework estimates the relative permittivity values at layer interfaces without accounting for intra-layer variations. Consequently, gradual degradation phenomena occurring within a single layer — such as the progressive increase in permittivity caused by fouling

or fine accumulation — are not explicitly captured. This simplifying assumption of layer homogeneity may induce small inaccuracies in thickness estimation, as it neglects the inherent variability of railway ballast materials [26,28].

The differences observed between ground-truth and GPR-estimated values (Table 14) remain low and spatially consistent. For the first layer, the discrepancies are within the expected range, confirming the robustness of the pipeline under operational conditions. The trenching campaign and GPR survey were conducted only a few months apart, during which the ballast condition remained stable. Although interface identification in trench profiles can vary with operator interpretation and the coarse grain size of ballast [6], the agreement between both datasets confirms the reliability of the proposed approach for near-surface interfaces.

For this section, no comparison was made with the lower boundary of the second layer, as this interface was not systematically detected. Interpolating between sparse or uncertain ground-truth points would have introduced artificial discrepancies, making such a comparison unreliable.

Unlike other studies, all measurements were performed under quasi-dry field conditions; hence, humidity-induced permittivity variations can be ruled out. Residual differences are primarily attributed to signal attenuation at depth, reduced reflector contrast, and minor positioning uncertainties. These results confirm that the pipeline remains stable even under variable acquisition conditions, emphasizing its potential for practical deployment on large-scale maintenance operations.

It is also worth noting that moisture strongly influences the dielectric permittivity of granular materials and can easily lead to misinterpretation when assessing ballast fouling. A layer retaining moisture tends to become more fouled over time as its drainage capacity decreases. The use of the Rb-f index in this study represents another key strength: it allows the interpretation to remain physically meaningful and independent of temporary moisture fluctuations. Because Rb-f is derived from dry-mass measurements, it integrates both permittivity and water-content effects, such that two layers with identical fouling but different moisture levels yield comparable Rb-f values [23].

Finally, the present evaluation relies on a two-dimensional approach (A-scan and B-scan processing), which does not yet capture the full three-dimensional variability of the medium. Recent advances have shown that including this spatial variability of electromagnetic properties can further improve the robustness of both fouling and thickness estimations [26]. Complementary scattering-based indicators have also demonstrated potential to distinguish moisture effects from fouling, reducing interpretation uncertainty [48].

It is important to clarify that this study does not implement a conventional transfer-learning scheme in which a model pre-trained on synthetic data is fine-tuned on field data. Instead, both synthetic and field datasets were used to validate a unified methodological framework under different conditions. The synthetic dataset was employed for model calibration and sensitivity analysis under controlled parameters, while the field dataset provided independent validation to test the approach's robustness under real-world variability (heterogeneity and acquisition artefacts). This dual validation demonstrates not only the methodological consistency but also the transferability of the framework across different domains.

Overall, the proposed approach combines physical interpretability, methodological stability, and operational feasibility. Beyond fouling detection, it enables a continuous characterization of the trackbed stratigraphy, significantly reducing the need for extensive trenching. By linking dielectric parameters with the local moisture state, the framework provides a practical means to infer the degree of fouling without direct physical sampling. These findings demonstrate the robustness and scalability of the proposed GPR--AI framework, confirming its potential as an effective tool for automated trackbed monitoring and predictive maintenance.

## Conclusion

This study presented a hybrid GPR--AI methodology that integrates deep learning and supervised regression to reconstruct trackbed stratigraphy and estimate ballast fouling. The framework was first validated on synthetic datasets, confirming the benefits of embedding sequential physical constraints for robust permittivity estimation, and then successfully applied to in situ measurements, where it achieved consistent interface detection and physically interpretable material characterization.

While results demonstrate accurate interface detection and good layer-wise relative permittivity retrieval — especially when sequentially conditioning *ε̂*_{2} on (*ε̂*_{1},*d*_{1}) — the current two-layer assumption and the water content (moisture) not being quantified precisely may introduce slight uncertainties in fouling attribution. A key lesson from this work is the importance of ground-truth trench data in the final characterization: even if water content is not directly measured, reporting the moisture condition during auscultation provides essential context to disentangle the contribution of humidity from that of fines in the dielectric response. Trench surveys therefore remain necessary, even when performed discontinuously, to provide reference information on hydrogeological state and material transitions.

Overall, the proposed methodology achieves a stratigraphic characterization with a vertical resolution on the order of 0.1 m, bridging the gap between discontinuous trench surveys and continuous GPR sections. Future work will extend the framework to multi-interface scenarios and incorporate moisture-aware features (e.g. scattering indicators) to further stabilize *ε̂*_{2} estimates and to reduce uncertainties in the separation of fouling and hydric effects.

## Data and code availability

Portions of the code used to train and evaluate the learning models (e.g. Mask R-CNN and the regression models) are available from the corresponding author upon reasonable request for research purposes. Some preprocessing and quality-control steps were carried out using Examiner (commercial software); the associated procedures/scripts cannot be shared due to licensing restrictions. The raw and georeferenced field datasets were collected under an industrial agreement and are proprietary to [anonymous], and therefore cannot be made publicly available. Aggregated metrics, figures, and tables required to understand the analyses are provided within the paper.

## CRediT authorship contribution statement

Ernest Mbubia Tchoua: Writing -- review & editing, Writing -- original draft, Methodology, Conceptualization. Jérôme Tissier: Writing -- review & editing, Validation, Supervision, Investigation. Antoine Martin: Writing -- review & editing, Validation, Investigation, Data curation. Yannick Fargier: Writing -- review & editing, Validation, Supervision. Amine Ihamouten: Writing -- review & editing, Validation, Supervision.

## Declaration of Generative AI and AI-assisted technologies in the writing process

During this work's preparation, the authors used GitHub Copilot for code assistance and ChatGPT for language refinement. All content was subsequently reviewed and approved by the authors, who take full responsibility for the published article.

## Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

E. Mbubia Tchoua et al.

Transportation Engineering 23 (2026) 100415

# Data availability

Data will be made available on request.

# References

[1] European Committee for Standardization, Aggregates for railway ballast, eN 13450:2002, 2002.
[2] E. Selig, J. Waters, Track Geotechnology and Substructure Management, Thomas Telford, 1994.
[3] A. Remennikov, S. Kaewunruen, Experimental load rating of aged railway concrete sleepers, Eng. Struct. 76 (2014) 147-162.
[4] S. Kaewunruen, A. Remennikov, Dynamic properties of railway track and its components: recent findings and future research direction, Insight, Non-Destr. Test. Cond. Monit. 52 (1) (2010) 20-22.
[5] C. Ngamkhanong, S. Kaewunruen, C. Baniotopoulos, A review on modelling and monitoring of railway ballast, Struct. Monit. Maint. 4 (3) (2017) 195-220.
[6] N. Oshbi, C. Voivret, G. Perrin, J.-N. Roux, Railway ballast: grain shape characterization to study its influence on the mechanical behaviour, Procedia Eng. 143 (2016) 1120-1127.
[7] S. Chrismer, E. Selig, Computer model for ballast maintenance planning, in: Proceedings of the 5th International Heavy Haul Railway Conference, Beijing, China, 1993, pp. 223-227.
[8] A. Aikawa, Dynamic characterisation of a ballast layer subject to traffic impact loads using three-dimensional sensing stones and a special sensing sleeper, Constr. Build. Mater. 92 (2015) 23-30.
[9] J. Lackenby, Triaxial Behaviour of Ballast and the Role of Confining Pressure under Cyclic Loading (Pb.D. thesis), University of Wollongong, 2006.
[10] C. Shi, Z. Fan, D. Connolly, G. Jing, V. Markine, Y. Guo, Railway ballast performance: recent advances in the understanding of geometry, distribution and degradation, Transp. Geotech. 41 (2023) 101042.
[11] G. Raymond, R. Bathurst, Performance of large-scale model single tie-ballast systems, Transp. Res. Rec. 1131 (1987) 7-14.
[12] C. Charoenwong, D. Connolly, A. Colaço, P. Alves Costa, P. Woodward, A. Romero, Railway slab vs ballasted track: A comparison of track geometry degradation, Constr. Build. Mater. 378 (2023).
[13] Y. Guo, V. Markine, G. Jing, Review of ballast track tamping: Mechanism, challenges and solutions, Constr. Build. Mater. 300 (2021) 123940.
[14] S. Aingaran, L. Le Pen, A. Zervon, W. Powrie, Modelling the effects of trafficking and tamping on scaled railway ballast in triaxial tests, Transp. Geotech. 15 (2018) 84-90.
[15] B. Aurnulkij, A Laboratory Study of Railway Ballast Behaviour under Traffic Loading and Tamping Maintenance (Pb.D. thesis), University of Nottingham, 2007.
[16] C. Paderno, Comportement du ballast sous l'action du bourrage et du traffic ferroviaire, Tech. rep., EPFL, 2010.
[17] R. Perales, Deba : Étude de la dégradation du ballast, Tech. rep., SNCF, 2010.
[18] T. Sussmann, M. Ruel, S. Chrismer, Source of ballast fouling and influence considerations for condition assessment criteria, Transp. Res. Rec. 2289 (1) (2012) 87-94.
[19] V.N. Trinh, A.M. Tang, Y.-J. Cui, J.-C. Dupla, J. Canou, N. Calon, L. Lambert, A. Robinet, O. Schoen, Mechanical characterisation of the fouled ballast in ancient railway track substructure by large-scale triaxial tests, Soils Found. 52 (3) (2012) 511-523.
[20] R. Bruzek, T. Stark, S. Wilk, H. Thompson, T. Sussmann, Fouled ballast definitions and parameters, in: ASME/IEEE Joint Rail Conference, in: American Society of Mechanical Engineers, vol. 49675, 2016, V001T01A007.
[21] F. Feldman, D. Nissen, Alternative testing method for the measurement of ballast fouling: percentage void contamination, in: Conference on Railway Engineering, Railway Technical Society of Australasia, Wollongong, NSW, 2002, pp. 101-111.
[22] B. Indraratna, L. Su, C. Rajikiatkamjorn, A new parameter for classification and evaluation of railway ballast fouling, Can. Geotech. J. 48 (2) (2011) 322-326.
[23] S. Fontul, E. Fortunato, Evaluation of ballast fouling using gpr, in: 15th International Conference on Ground Penetrating Radar, GPR, IEEE, Brussels, Belgium, 2014, http://dx.doi.org/10.1109/ICGPR.2014.6970457.
[24] H. Huang, J. Luo, E. Tutumluer, J.M. Hart, A.J. Stolba, Automated segmentation and morphological analyses of stockpile aggregate images using deep convolutional neural networks, Transp. Res. Rec. 2674 (10) (2020) 285-298, http://dx.doi.org/10.1177/0361198120945853.
[25] J. Luo, H. Huang, K. Ding, LI. Qantiu, E. Tutumluer, J.M. Hart, T.R. Sussmann, Toward automated field ballast condition evaluation: Algorithm development using a vision transformer framework, Transp. Res. Rec. 2677 (10) (2023) 423-437, http://dx.doi.org/10.1177/03611981231189591.

[26] S.S. Artagan, V. Borecky, Advances in the nondestructive condition assessment of railway ballast: A focus on gpr, NDT &amp; E Int. 115 (2020) 102290, http://dx.doi.org/10.1016/j.ndteint.2020.102290.
[27] M. Silvast, F. Künzl, C. Kühnhenn, B. Wiljanen, Frequency domain analysis of gpr data in railway applications, in: 9th International Conference on Ground Penetrating Radar, 2010.
[28] S. Wang, G. Liu, G. Jing, Q. Feng, H. Liu, Y. Guo, State-of-the-art review of ground penetrating radar (gpr) applications for railway ballast inspection, Sensors 22 (7) (2022) 2450, http://dx.doi.org/10.3390/s22072450.
[29] R. De Bold, T. Sussmann, J. Hyslip, Ballast fouling inspection and quantification with ground penetrating radar (gpr), Constr. Build. Mater. 92 (2015) 64-73, http://dx.doi.org/10.1016/j.conbuildmat.2015.05.074.
[30] S.S. Artagan, V. Borecky, Advances in the nondestructive condition assessment of railway ballast: A focus on gpr, NDT &amp; E Int. 115 (2020) 102290, http://dx.doi.org/10.1016/j.ndteint.2020.102290.
[31] P. Anbazhagan, P. Dixit, T. Bharatha, Identification of type and degree of railway ballast fouling using ground coupled gpr antennas, J. Appl. Geophys. 126 (2016) 183-190, http://dx.doi.org/10.1016/j.jappgeo.2016.01.018.
[32] F. Cui, M. Ning, J. Shen, X. Shu, Automatic recognition and tracking of highway layer-interface using faster r-cnn, J. Appl. Geophys. 196 (2022) 104477, http://dx.doi.org/10.1016/j.jappgeo.2021.104477.
[33] A. Elseicy, P. Arias, M. Solla, A. Alonso-Díaz, Pavement layer interface detection from gpr data using deep learning, in: IEEE International Workshop on Advanced Ground Penetrating Radar, IWAGPR, IEEE, 2023, pp. 1-8, http://dx.doi.org/10.1109/IWAGPR57138.2023.10329101.
[34] E. He, G. Gkiosari, P. Dollar, R. Girshick, Mask r-cnn, in: Proceedings of the IEEE International Conference on Computer Vision, 2017, pp. 2961-2969.
[35] S. Ren, K. He, R. Girshick, J. Sun, Faster r-cnn: Towards real-time object detection with region proposal networks, in: Advances in Neural Information Processing Systems (NeurIPS), vol. 28, 2015, pp. 91-99.
[36] H. Drucker, C.J.C. Burges, L. Kaufman, A. Smola, V. Vapnik, Support vector regression machines, in: Advances in Neural Information Processing Systems (NeurIPS), vol. 9, 1996.
[37] T. Chen, C. Guestrin, Xgboost: A scalable tree boosting system, in: Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 2016, pp. 785-794.
[38] J.H. Friedman, Greedy function approximation: A gradient boosting machine, Ann. Stat. (2001) 1189-1232.
[39] G. Andreoli, A. Ihamouten, V. Baliuk, C. Fauchard, R. Jaufer, X. Derobert, Numerical parametric study to classify and estimate pavement characteristics using gpr and machine learning methods, in: 1st International Data Science for Pavements Symposium, 2022.
[40] R.M. Jaufer, 3d mapping of underground utility networks using ultra-wideband multi antenna array step frequency radar (Thèse de doctorat), Nantes Université, 2022.
[41] S.S. Todkar, V. Baltazart, A. Ihamouten, X. Derobert, D. Guilbert, One-class svm based outlier detection strategy to detect thin interlayer debondings within pavement structures using ground penetrating radar data, J. Appl. Geophys. 192 (2021) 104392.
[42] B. Li, Z. Peng, S. Wang, L. Guo, Identification of ballast fouling status and mechanized cleaning efficiency using fdtd method, Remote. Sens. 15 (13) (2023) 3437, http://dx.doi.org/10.3390/rs15133437.
[43] M.R. Clark, R. Gillespie, T. Kemp, D.M. McCann, M.C. Forde, Electromagnetic properties of railway ballast, NDT &amp; E Int. 34 (5) (2001) 305-311, http://dx.doi.org/10.1016/S0963-8695(01)00031-3.
[44] A. Giannopoulos, gprmax: Open source software to simulate electromagnetic wave propagation for ground penetrating radar, Comput. Phys. Comm. 197 (2015) 419-429, http://dx.doi.org/10.1016/j.cpc.2015.08.013.
[45] X. Zhang, F. Bekmambetova, P. Triverio, A stable fdtd method with embedded reduced-order models, IEEE Trans. Antennas and Propagation 66 (2) (2017) 827-837, http://dx.doi.org/10.1109/TAP.2017.2771420.
[46] T.-Y. Lin, M. Maire, S. Belongie, J. Hays, P. Perona, D. Ramanan, P. Dollar, C.L. Zitnick, Microsoft coco: Common objects in context, in: European Conference on Computer Vision, Springer, 2014, pp. 740-755.
[47] Y. Wu, A. Kirillov, F. Massa, W.-Y. Lo, R. Girshick, Detector2, 2019, https://github.com/facebookresearch/detectron2.
[48] R. De Bold, G. O'Connor, J.P. Morrissey, M.C. Forde, Benchmarking large scale gpr experiments on railway ballast, Constr. Build. Mater. 92 (2015) 31-42, http://dx.doi.org/10.1016/j.conbuildmat.2015.04.037.