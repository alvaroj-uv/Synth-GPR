Journal of Physics: Conference Series

PURPOSE-LED PUBLISHING

PAPER • OPEN ACCESS

# Numerical parametric study for ballast assessment using SVM applied to GPR data

To cite this article: Ernest Mbubia T et al 2024 J. Phys.: Conf. Ser. 2887 012047

View the article online for updates and enhancements.

# You may also like

- Mortar layer void detection of ballastless track using the impact echo method based on support vector machine
Shengteng Li, Yadong Xue, Kai Shen et al.
- GPR identification of voids inside concrete based on the support vector machine algorithm
Xiongyao Xie, Pan Li, Hui Qin et al.
- Classification Size of Underground Object from Ground Penetrating Radar Image using Machine Learning Technique
Mohd Shuhanaz Zanar Azalan, Tang Esian, Hasimah Ali et al.

This content was downloaded from IP address 181.43.210.215 on 10/06/2026 at 04:14

20th International Conference on Ground Penetrating Radar
Journal of Physics: Conference Series 2887(2024) 012047
IOP Publishing
doi:10.1088/1742-6596/2887/1/012047

# Numerical parametric study for ballast assessment using SVM applied to GPR data

Ernest Mbubia T$^{1,5}$, David Guilbert$^{2}$, Jérome Tissier$^{1,4}$, Antoine Martin$^{5}$, Théo Dezert$^{6}$, Yannick Fargier$^{3}$, Amine Ihamouten$^{1}$

$^{1}$ Lames, Mast department, Gustave Eiffel University, Bouguenais, France (ernest.mbubia@univ-eiffel.fr)
$^{2}$ GeoEnd, Gers department, Gustave Eiffel University, Bouguenais, France
$^{3}$ Rro, Gers department, Gustave Eiffel University, Bron, France
$^{4}$ Eseo, engineering school, Angers, France
$^{5}$ Technical Department, ETF, Vinci Construction, Rueil-Malmaison, France
$^{6}$ FI-NDT, Start-up of Gustave Eiffel University, Bouguenais, France

Abstract. This study explores novel radar-based methodologies for ballast fouling evaluation and structural anomalies in railway structures. Ground Penetrating Radar (GPR), coupled with numerical modeling, is utilized to provide insights into ballast condition and structure. Various data processing methods, including the Matrix Pencil Method (MPM) and Full Waveform Inversion (FWI), are investigated for their effectiveness in detecting fouling. Support Vector Machine (SVM)-based machine learning approaches are employed to enhance classification accuracy. The results demonstrate that integrating raw GPR signals with MPM yields the most accurate classification results, facilitating efficient assessment of ballast condition and contributing to improved railway maintenance strategies.

# 1. Introduction

Ground Penetrating Radar (GPR) technology significantly enhances railway infrastructure maintenance, especially in addressing ballast fouling. This fouling, marked by the accumulation of particles and water infiltration, leads to operational disruptions and escalated maintenance expenses [1, 2]. Current methodologies, such as visual inspection, are recognized for their limitations in precision and time-consuming nature. While Selig and Waters' approach [3] effectively addresses granular aspects, its lack of continuity and high cost renders it inadequate and insufficient for quantifying fouling.

In response to this gap, novel radar-based methodologies for detecting fouling and structural anomalies are being investigated, with GPR coupled with numerical modeling providing valuable insights into ballast condition and structure [4, 5, 6]. This study introduces a numerical approach utilizing gprMax simulations [7], evaluating methods like the Matrix Pencil Method (MPM) and Full Waveform Inversion (FWI), alongside a Support Vector Machine (SVM)-based machine learning approach. A hybrid approach combining MPM, SVM, and FWI is aimed at enhancing classification accuracy between fouled and clean zones. These methods are tested on numerical data with the objective of comprehensively comparing their accuracy and efficiency in detecting ballast fouling.

CC BY
Content from this work may be used under the terms of the Creative Commons Attribution 4.0 licence. Any further distribution of this work must maintain attribution to the author(s) and the title of the work, journal citation and DOI.
Published under licence by IOP Publishing Ltd

## 2 Data processing methods

The investigation of the SVM method and its application to raw and processed GPR data is proposed. The delayed response of the GPR signal enables feature identification based on its geometry and physical properties. This signal can be dimensionally reduced using processing methods such MPM or inversion method (FWI) while preserving its essence. The SVM is effectively applied to both raw and processed data, as well as to the combination of raw and processed signals, to study the influence of the two previously mentioned methods on classification.

### 2.1 Support Vector Machine (SVM)

Conventional radar techniques can estimate subsurface characteristics but struggle with detecting subtle dielectric variations. Machine Learning, particularly SVM, offers a solution by classifying data based on labels established during GPR data training.

SVM maximizes the decision boundary to separate variables and classify them, using support vectors and selecting an optimal hyperplane *[8]*.

Key parameters in SVM include the kernel function and hyperparameters $C$ and $\gamma$, which control regularization and error penalty during classification.

The model outputs automatic classification results for the evaluated zone, providing information on the ballast’s condition.

### 2.2 Matrix Pencil Method (MPM)

The MPM is a linear algebra technique used for analyzing signals composed of exponentially damped sinusoids. It separates observations into signal and noise components and is commonly applied in adaptive filtering and parameter estimation. MPM involves computing a Hankel matrix to determine the number and values of poles, utilizing eigenvalue and singular value decompositions. For a detailed understanding, refer to *[9]*. MPM enables the reconstruction of the original signal from obtained poles and residues, enhancing precision and robustness of inverse calculations while significantly reducing input data dimensionality.

### 2.3 Full Waveform Inversion (FWI)

The electromagnetic model presented here describes radar wave propagation in a multi-layered medium, considering the frequency-dependent nature of EM properties. The objective is to compute causal parameters from the GPR signal, involving solving an inverse problem *[10]*. FWI allows reconstruction of the original signal from Green’s functions with limited parameters, enhancing precision and robustness of the inverse calculation while reducing input data dimensionality. Therefore, we will explore this method’s potential for replacing raw GPR signals with a reduced dimensionality of Green’s function parameters while incorporating all relevant signal components.

## 3 Parametric numerical study

Following extensive experimental validation to determine the ranges of dielectric properties of the media under study, a framework is developed for the numerical investigation presented in this paper. GprMax is employed to produce multiple signals that are representative of real-world scenarios. The modeling characteristics and the study database are elaborated upon in the subsequent section. Additionally, the aim is to model the propagation of electromagnetic waves through multi-layered structures with well-defined physical and geometric properties, with the objective of distinguishing between clean and fouled ballast in railway structures.

20th International Conference on Ground Penetrating Radar

IOP Publishing

Journal of Physics: Conference Series 2887 (2024) 012047

doi:10.1088/1742-6596/2887/1/012047

# 3.1. Modeling

To effectively address the problem, we model EM wave propagation through different configurations considering the number of layers and the ballast's state. Simulation domain parameters are set as follows:

- Domain size:  $0.051\mathrm{m}$ ,  $0.425\mathrm{m}$ ,  $0.001\mathrm{m}$  with a spatial discretization of  $0.001\mathrm{m}$ .
- Theoretical Hertzian dipole source with a Ricker waveform (1.5 GHz center frequency).
- Antenna position at  $(0.026\mathrm{m}, 0.405\mathrm{m})$  (5 mm above the surface).
- Time window: 12 ns.
- Total thickness of the ballast layer:  $0.4\mathrm{m}$

We create a database containing different configurations, defining four ballast conditions (Table 1): Clean, Moderate 1, Moderate 2, and Fouled. Each condition exhibits distinct dielectric permittivity and conductivity characteristics, with variable thickness ranging between  $0.04\mathrm{m}$  and  $0.4\mathrm{m}$  depending on the specific configurations. In the results, Moderate 2 and Fouled states are considered as Fouled, while Clean and Moderate 1 states are assimilated to Clean. For each state, we consider single-layer, bi-layer, tri-layer, and four-layer configurations, resulting in over 3700 A-scans (3200 corresponding to various levels of ballast fouling and 500 to a clean ballast).

Table 1. Ballast Layer State.

|  Ballast Layer State | Permittivity ε | Conductivity σ (Sm-1)  |
| --- | --- | --- |
|  Clean | [2.5 - 3.5] | 10-5  |
|  Moderate 1 | [5.5 - 6.5] | 10-4  |
|  Moderate 2 | [8.5 - 9.5] | 10-3  |
|  Fouled | [11 - 12] | 10-2  |

# 3.2. Processing step

A comparative study of SVM performance between global and local approaches, utilizing raw signals and features extracted from preprocessing methods (MPM and FWI), is conducted. We employ a two-class SVM method to identify ballast fouling anomalies, separating data into "Clean" and "Fouled" classes. The inputs injected into the SVM model include: case 1: Global approach (raw signal only); case 2: Local approach (MPM only); case 3: Mixed approach (Raw signal + MPM); case 4: Raw signal + FWI.

A 70/30 split is employed for training and test sets, with  $70\%$  used for training (2590 A-scans) and  $30\%$  for testing (1110 A-scans).

# 3.3. Results

Through a parametric numerical study, we explored various configurations and data processing methods to improve accuracy and efficiency in detecting fouling. The SVM-based machine learning approach, coupled with features extracted from MPM and FWI, provided valuable insights into the ballast's condition, further enhancing the model's performance in distinguishing between clean and fouled samples. The confusion matrix (Table 2) highlights the effectiveness of each approach, with the "Predict Raw signal + MPM" scenario achieving the highest classification accuracy across both clean and fouled samples. This approach significantly improves prediction and classification while efficiently reducing computational costs. It may be necessary to incorporate some limitations into our study. These could include factors such as noise in the measurement not being accounted for, as well as the binary nature of our approach

20th International Conference on Ground Penetrating Radar

IOP Publishing

Journal of Physics: Conference Series 2887 (2024) 012047

doi:10.1088/1742-6596/2887/1/012047

(fouled/clean). This underscores the importance of integrating advanced data processing techniques with machine learning algorithms to achieve reliable and accurate classification results. This choice is reinforced by the continuously improving capabilities of learning-based methods compared to FWI. Nonetheless, the unoptimized SVM kernels and 'limited' database suggest that higher-quality results could be achieved with optimization in the future.

Table 2. Confusion matrix for the various approaches using SVM.

|  Real | Clean | 106(73 %) | 40(27 %)  |
| --- | --- | --- | --- |
|   |  Fouled | 6(1 %) | 958(99 %)  |
|   |  | Clean | Fouled  |
|   |  | PredictCase 1: Raw signal  |   |

|  75(51 %) | 71(49 %)  |
| --- | --- |
|  1(0 %) | 963(100 %)  |
|  Clean | Fouled  |
|  PredictCase 2: MPM  |   |

|  135(92 %) | 11(8 %)  |
| --- | --- |
|  1(0 %) | 963(100 %)  |
|  Clean | Fouled  |
|  PredictCase 3: Raw signal + MPM  |   |

|  129(88 %) | 17(12 %)  |
| --- | --- |
|  0(0 %) | 964(100 %)  |
|  Clean | Fouled  |
|  PredictCase 4: Raw signal + FWI  |   |

# 4. Conclusion

In conclusion, our study contributes to the development of an innovative radar-based methodology for detecting ballast fouling and structural anomalies in railway infrastructure. The proposed approach offers a viable solution for efficient and accurate assessment of ballast condition, ultimately leading to improved maintenance strategies and enhanced railway operations. Future research should focus on further optimizing SVM kernels, expanding the database, and refining hyperparameters to achieve even higher-quality results in real-world applications.

# References

[1] Sussmann T R, Ruel M and Chrismer S M 2012 Transportation Research Record 2289 87-94
[2] Bruzek R, Stark T D, Wilk S T, Thompson H B and Sussmann Jr T R 2016 Fouled ballast definitions and parameters ASME/IEEE Joint Rail Conference
[3] Selig E T and Waters J M 1994 TRACK GEOTECHNOLOGY and SUBSTRUCTURE MANAGEMENT (Thomas Telford Publishing)
[4] Fontul S, Fortunato E, De Chiara F, Burrinha R and Baldeiras M 2016 Procedia Engineering 143 1193-1200 ISSN 1877-7058 advances in Transportation Geotechnics III
[5] Wang S, Liu G, Jing G, Feng Q, Liu H and Guo Y 2022 Sensors 22 ISSN 1424-8220
[6] Kingsuwannaphong T, Brau C and Heberling D 2022 Fouled railway ballast modeling using rigid body simulation (Society of Exploration Geophysicists) pp 63-66
[7] Warren C, Giannopoulos A and Giannakis I 2016 Computer Physics Communications 209 163-170 ISSN 0010-4655
[8] Xie X, Li P, Qin H, Liu L and Nobes D C 2013 Journal of Geophysics and Engineering 10 034002
[9] Drissi K E K and Poljak D 2015 WIT Transactions on Modelling and Simulation 59 13-24
[10] Guan B, Ihamouten A, Derobert X, Guilbert D, Lambot S and Villain G 2017 IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing 10 4328-4336