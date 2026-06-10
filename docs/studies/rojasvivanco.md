Transportation Geotechnics 55 (2025) 101701

ELSEVIER

Contents lists available at ScienceDirect

Transportation Geotechnics

journal homepage: www.elsevier.com/locate/trgeo

GEOTECHNICS

Original article

# Assessment of railway ballast fouling using GPR and AI-Based learning from LDCP and geoendoscopy data

Jorge Rojas-Vivanco $^{a,\ast}$, Miguel Benz-Navarrete $^{b\bullet}$, José García $^{a}$, Pierre Breul $^{c\bullet}$, Aurélie Talon $^{c\bullet}$, Gabriel Villavicencio $^{a}$

$^{a}$ Escuela de Ingeniería de Construcción y Transporte, Pontificia Universidad Católica de Valparaíso, Avenida Brasil 2147, Valparaíso, Región de Valparaíso, 2340000, Chile
$^{b}$ Research and Development, Sol Solution, Riom Cedex, 63204, Riom, France
$^{c}$ Institut Pascal, Clermont Auvergne University, Aubière, 63174, France

# ARTICLE INFO

Keywords:
Fouling index
GPR
Penetrometer
Geoendoscopy
Ballasted track
Machine learning

# ABSTRACT

Ballast is a key components of ballasted railway tracks. Its main function is to guarantee the vertical, lateral and longitudinal stability of the track for the passage of trains. These functions are compromised when ballast begins to deteriorate or becomes fouled, so it is imperative to monitor the rate of fouling index to determine the necessary maintenance or renovation actions. The objective of this study is to characterize the fouling index of the ballast using Ground Penetrating Radar (GPR) measurements with 400 MHz antennas and employing machine learning techniques. The proposed methodology focuses on the parametric development of GPR signals, incorporating both time and frequency domain analyses, along with specific analytical parameters. This comprehensive approach enables a more precise characterization of GPR signals, enhancing their interpretation and analysis in various geotechnical contexts. This analysis will be carried out using a historical database of French railways, consisting of 4700 km of GPR measurements and 12,000 soundings with the light dynamic cone penetration (LDCP)/geoendoscopy test principle. The determination of the target variable, which is the fouling state of the ballast layer, will be performed through the soundings. The results obtained show that the most appropriate model for estimating the fouling index is Random Forest, demonstrating an accuracy of 96% in the training phase. On the other hand, in the model evaluation phase with cases external to the database, the XGBoost model obtained the best result, with a maximum accuracy of 86%.

# Introduction

The structure of railway tracks in terms of their components can vary significantly depending on multiple factors associated with traffic demands (axle load, frequency, and speed of trains), as well as the on-site conditions of the track (geology, hydrology, climate, etc.). In the present study, we will focus on the analysis of ballasted railways, characterized by sleepers supported by a layer of ballast, an angular granular material obtained from the crushing of rocks to produce coarse gravel [1].

This layer must comply with a series of factors established by different national standards such as grain size, grain shape (coefficient of flattening and coefficient of shape), resistance to fragmentation, wear and durability (resistance to freezing/thawing, true density and coefficient of water absorption) [2]. When some of these factors are not met, the performance of the layer is affected and the fulfillment of the functions for which it was designed is reduced. Among all

the factors involved in the composition of the ballast layer, we will focus specifically on the grain size distribution, as this is associated with the state of fragmentation and contamination of the layer due to the passage of trains and the conditions in situ. Fragmentation is mainly associated with the initial break of the ballast grains [3], which produces small particles that agglomerate in the voids of the layer, while contamination is produced by fine material from sources external to the layer (foreign sources from the surface, wear of the sleepers, subballast, and the subgrade) [4].

Ballast layer degradation alters particle size distribution, deviating from regulatory parameters and changing its behavior. The degree of displacement of the curve will depend on the amount of fouling material (material from fragmentation and contamination). This degradation will directly affect the mechanical behavior of the railway track, causing greater deformation of its geometry [5]. As the level of contamination increases, the track will deform in shorter periods of

https://doi.org/10.1016/j.trgeo.2025.101701

Received 18 June 2025; Received in revised form 28 August 2025; Accepted 30 August 2025

Available online 8 September 2025

2214-3912/© 2025 Elsevier Ltd. All rights are reserved, including those for text and data mining, AI training, and similar technologies.

time. On the other hand, when there is less contamination, the track is maintained at longer intervals, thus reducing the impact on the need for maintenance. For this reason, the characterization and diagnosis of the ballast layer are important for the safety and comfort of rail transport [6].

This article presents a novel methodology for characterizing the ballast layer using Ground Penetrating Radar (GPR) measurements, combined with machine learning techniques, to determine the fouling level of the ballast layer. The proposed approach utilizes a historical database of 4700 km of GPR measurements and 12,000 lightweight dynamic cone penetrometer (hereafter LDCP) and geoendoscopy test, providing a robust dataset for model training and validation. The results demonstrate that the Random Forest model achieved the highest accuracy when evaluated on the training set, effectively capturing the complex relationships between GPR signal characteristics and ballast contamination. However, in practical applications with data outside the original training set, the XGBoost model demonstrated superior performance, indicating better generalization to unseen conditions. This methodology significantly improves the reliability of ballast condition assessments, facilitating more precise maintenance planning and cost-effective infrastructure management.

## Literature review on fouling index estimation

### Types of fouling indexes

In railway geotechnical engineering, various indicators have been proposed that are used by railway managers to determine the level of fouling and to make decisions about the actions to be taken in asset management. The first fouling index (FI), proposed by Selig and Water [4], consisted of combining the 4.75 mm (*P*_{*h*}) and 75 *μ*m (*P*_{200}) sieves (see Eq. (1)). As a result of this work, some modifications have been made to the indicator, as well as new proposals, some of which are as follows:Fouling Index (FI) proposed by Australian regulations [7], is calculated by combining the material passing through the 13.2 mm and 75 *μ*m sieves, as expressed in Eq. (2).Fouling Index (BF_{*p*}) proposed by Ionescu [8], it consists of dividing the nominal diameter of the 90% grading curve by that of the 10% (see Eq. (3)).Ballast Fouling Factor (BF_{*f*}) performs a combination by multiplying the different factors corresponding to the mass percentages of the material passing through the 0.15, 1.18, 6.7, and 19 mm sieves [9,10](see Eq. (4)).Void Contaminant Index (VCI) combines different parameters, such as the void index (e), the specific gravity (Gs) and the masses (M) associated with the clean ballast and the fouling material [11], [12], [13] (see Eq. (5)).Percentage Void Contamination (PVC) evaluates the percentage of the total volume of ballast voids that has been occupied by contaminating material [14,15].Relative Ballast Fouling Ratio (R_{*b*-*f*}) takes into account the amount of contaminant material and clean ballast by mass [15].$$FI = P_{h} + P_{200}$$ $$FI_{p} = P_{13.2} + P_{200}$$ $$FI_{D} = \frac{D_{90}}{D_{10}}$$ $$BF_{F} = \frac{10 \cdot P_{0.15}}{27} + \frac{20 \cdot P_{1.18}}{11.5} + \frac{5 \cdot P_{0.7}}{3} + \frac{40 \cdot P_{19}}{27}$$ $$VCI = \frac{(1 + e_{\text{fouling}})}{e_{\text{ballast}}} \cdot \frac{G_{s\text{-ballast}}}{G_{s\text{-fouling}}} \cdot \frac{M_{\text{fouling}}}{M_{\text{ballast}}} \cdot 100$$ $$PVC = \frac{V_{\text{fouling}}}{V_{\text{void}}} \cdot 100$$ $$R_{b - f} = \frac{M_{f}}{M_{b}} \cdot \frac{G_{b - f}}{G_{s - f}} \cdot 100%$$where:P_{*c*}: Percentage by weight of particles passing through a sieve with an aperture size x mm.D_{90}: Particle diameter corresponding to the 90% passing in the particle size distribution.D_{10}: Particle diameter corresponding to the 10% passing in the particle size distribution.e_{fouling}: Void index of the fouling material.e_{ballast}: Void index of the clean ballast.G_{s-ballast}: Specific gravity of the ballast.G_{s-fouling}: Specific gravity of the fouling material.M_{fouling}: Mass of the fouling material.M_{ballast}: Mass of the ballast.V_{fouling}: Volume of the fouling material.V_{void}: Volume of the voids in the ballast.G_{b-f}: Combined specific gravity of the ballast and fouling material.G_{s-f}: Specific gravity of the fouling material.

This literature review shows that there are different perspectives for quantifying ballast layer fouling. This study adopts only the original fouling index of Selig and Waters (FI) because: (i) this indicator has been adapted in several studies [1], and (ii) the data set used in this research is mainly related to this indicator (see Section “Target variable database”).

### Fouling state classification

In addition to the continuous value of the Fouling Index (FI), different qualitative states have been defined in order to give greater engineering significance to the condition of the ballast layer. This classification allows the numerical values of the index to be translated into severity levels, facilitating the interpretation of their implications for the mechanical and hydraulic behavior of the railway track.

In this context, one of the most widely recognized classifications is that proposed by Selig and Waters [4], who, based on the FI value defined in Eq. (1), established five fouling states. This typology allows the degree of ballast contamination to be quantified and directly associated with its structural and functional performance. The proposed states are as follows:C (Clean, 0% ≤ FI ≤ 1%): The ballast is considered clean, with minimal contamination, maintaining high permeability and stability.MC (Moderately Clean, 1% < FI ≤ 10%): The ballast contains some fine material, but without significantly affecting its mechanical performance or drainage capacity.MF (Moderately Fouled, 10% < FI ≤ 20%): The ballast shows moderate contamination, with a noticeable reduction in void space and permeability, increasing the risk of track settlement.F (Fouled, 20% < FI ≤ 40%): The ballast is significantly contaminated, with reduced drainage capacity and compromised load-bearing ability, leading to more frequent track deformation.HF (Highly Fouled, FI > 40%): The ballast is heavily contaminated, exhibiting poor drainage, significant loss of mechanical stability, and severe mechanical degradation, requiring immediate maintenance intervention.

J. Rojas-Vivanco et al.

Transportation Geotechnics 55 (2025) 101701

![img-0.jpeg](img-0.jpeg)
Fig. 1. Procedure to determine the grain size distribution of the ballast layer (a) Sampling, (b) Sieving and (c) Results of the grain-size distribution.

![img-1.jpeg](img-1.jpeg)

![img-2.jpeg](img-2.jpeg)

![img-3.jpeg](img-3.jpeg)
Fig. 2. LDCP/geoendoscopy tests.

![img-4.jpeg](img-4.jpeg)

# Methods for determining the fouling index

# Sampling and laboratory testing

In contrast to the other methods mentioned in this section, taking samples in conjunction with laboratory evaluations has the capacity to reproduce the various indicators developed with the purpose of quantifying the level of fouling of the ballast layer described above. Determining the Fouling Index on a sample basis involves the following procedure: (i) Take a sample from the railway track (see Fig. 1a), which should be representative of the granular medium. Depending on the national standards or regulations and the maximum grain size, a minimum of  $50\mathrm{kg}$  for  $63\mathrm{mm}$  maximum nominal diameter and  $35\mathrm{kg}$  for  $50\mathrm{mm}$  maximum nominal diameter is required [15,16], (ii) sieve the sample from  $80\mathrm{mm}$  to  $75\mu \mathrm{m}$  (see Fig. 1b) and (iii) calculate the grain size distribution curve (see Fig. 1c).

From the grain size distribution curve calculated in Fig. 1c, we only need the percentage of  $4.75\mathrm{mm}$ , equivalent to  $18.48\%$ , and that of  $75\mu \mathrm{m}$ , equivalent to  $7\%$ , which added together give us the fouling index equivalent to  $25.48\%$ .

# LDCP/geoendoscopy coupling method

The LDCP/geoendoscopy methodology consists of combining the variable-energy lightweight dynamic cone penetrometer [17] (see Fig. 2a) with the geoendoscopic test developed by Breul et al. [18] (see

Fig. 2b), in order to characterize the granular medium mechanically and physically [6]. The LDCP/geoendoscopy test consists of two stages: (i) a mechanical characterization of the layers is carried out by means of a dynamic penetration test with the LDCP [17] and (ii) the rods are then removed to insert the geoendoscope and allows for a physical characterization of the track material to be obtained [19].

The LDCP/geoendoscopy test methodology has enabled the development of two approaches to determine the level of fouling [6]: (i) The first approach consists of the thorough analysis of image coupling and LDCP to estimate the index properties of the granular medium that can be used to assess the mass and volume of the ballast and pollution material. This allows the joining of the grain size distribution of the ballast through a semi-automatic analysis and those of the pollution material using automatic algorithms and (ii) The second approach involves the relationship between the thickness of the fouled ballast (i.e., the voids in the ballast filled with pollution material) and the total thickness of the ballast layer (i.e., clean ballast plus fouling ballast), with a correction factor that accounts for the nature of the fouling material (sand or clay) [6]. The thickness of the layers was determined by expert interpretation using the penetrogram and geoendoscopic images to identify the different materials present in the profile.

# Image analysis

Determining the level of fouling using images varies depending on the input data and the way the images are analyzed. The input images

J. Rojas-Vivanco et al.

Transportation Geotechnics 55 (2025) 101701

![img-5.jpeg](img-5.jpeg)
Fig. 3. Image capture to determine the fouling of the ballast layer [20,21]. (For interpretation of the references to color in this figure legend, the reader is referred to the web version of this article.)

![img-6.jpeg](img-6.jpeg)

Table 1 Image analysis applications to estimate ballast layer fouling index or condition.

|  N° | Input data | Methodology (approach and method studied) | Validation and perspectives | Ref.  |
| --- | --- | --- | --- | --- |
|  1 | High-resolution digital images taken in the laboratory and in the field. They were labeled manually to train the models. The images analyzed are similar to those described in Fig. 3a. | Neural network techniques were used for the automatic classification of ballast degradation. The AlexNet and VGG architectures were used for this purpose. | Cross-validation and confusion matrices were used to model the accuracy of the calculated model. Moderate errors were obtained, establishing that the model can handle moderate image noise, but depends on the high initial quality of the training data. | [22]  |
|  2 | Digital images of horizontal and vertical sections of the ballast, with grain size analysis. The images analyzed are both cases described in Fig. 3 in the field and laboratory. | Watershed segmentation image processing called 'Percent Degraded Segments' (PDS). | VA statistical validation was carried out with a total of 28 labeled images, where the coefficient of determination R2=0.84 in the correlation between PDS and FI. This method has as a limitation the manual adjustment of some segmentation parameters, in addition to developing a greater number of case studies to make the model more robust. | [21]  |
|  3 | 2D and 3D digital images obtained using the Ballast Scanning Vehicle (BSV). The images analyzed are similar to those described in Fig. 3b. | Deep Learning-based ballast segmentation techniques were implemented, consisting of a Swin Transformer and Cascade Mask R-CNN model to carry out the challenging task of ballast image segmentation. The indicators used in this study were the Degradation Index (PDS), Ballast Fouling Index (FI), and aggregate gradation. | Validation was carried out by comparing the predictions with the measurements made in the laboratory. High performance was demonstrated under various environmental conditions and for different ballast conditions. | [23]  |
|  4 | Real and synthetic images generated in Blender. Plan and section views are included. | Creation of a set of real and synthetic data. Indicators: Mean Accuracy (mAP), FI-Score, degradation index. | Comparison between real and synthetic images. Adequate results. | [24]  |
|  5 | High-resolution RGB (color model based on the basic colors of light: red, green and blue) images with 48-megapixel sensors. | The fouling index was determined using a statistical model that correlates the RGB variances of the subsampled images. | A cross-validation was performed using linear regression with 95% prediction intervals. | [25]  |

may initially vary depending on the configuration and type of device used. However, a more critical factor is the section of the railway track where the photographs are taken. In the work carried out using image analysis, two ways of taking photographs have been detected: (i) removing the material between the sleepers and then taking a photograph of the ballast under the sleeper (for example, the red area in Fig. 3a), which applies to field and laboratory measurements, and (ii) removing the material next to the sleepers and taking the photograph from the side of the sleeper (for example, the red area in Fig. 3b).

As for image analysis, there are various perspectives: (i) segmentation, (ii) the use of machine learning techniques, and (iii) RGB color analysis. Table 1 present a synthesis of the work applied to the assessment of the fouling index by means of image analysis with laboratory and/or field data.

# Ground Penetration Radar (GPR)

GPR is a geophysical technique based on the characterization of the granular medium through the propagation of electromagnetic waves [1]. An antenna has an emitter or transmitter which generates the electromagnetic impulse that begins to travel through the air (a void) to the receiver which is responsible for recording all the reflections. This first reflection is called a direct wave (S1 in Fig. 4). The wave then propagates to the ballast surface where another reflection is generated (S2 in Fig. 4) and so on with the rest of the reflections from the granular medium. The result of this procedure is a graph showing the amplitude of the reflected waves as a function of time, this graph is known as a 'radargram' [26].

The electromagnetic wave analysis provides essential information for evaluating the state of the substructure. Focusing exclusively on the

J. Rojas-Vivanco et al.

Transportation Geotechnics 55 (2025) 101701

![img-7.jpeg](img-7.jpeg)
Fig. 4. Principle of the GPR detection technology for the ballast layer [26].

ballast fouling index, different perspectives have emerged which are summarized in Table 1, emphasizing the antennas used, the parameters necessary to determine the degree of fouling, the method used to correlate the parameters with the degree of fouling as well as the main results obtained.

# Limitations of methods for determining the Fouling Index

In general, all the methods described present operational and practical limitations. In the case of traditional sampling, it is necessary to physically intervene in the track by removing granular material, potentially altering the structural and functional integrity of the railway system. Added to this is the process of transporting the extracted material and its subsequent analysis in the laboratory, which entails significant time and logistical resources. Furthermore, as it is a one-off, localized procedure, its application over long stretches of track is inefficient and economically unviable for systematic monitoring purposes.

LDCP/geoendoscopy tests share the limitation of being spot techniques. Although the level of intervention is lower than in physical sampling, and data processing can be carried out in a more reasonable time frame, their coverage remains limited for continuously characterizing the condition of ballast over long sections.

As for image analysis, its applicability depends largely on the methodology used. As shown in Fig. 3, some approaches require partial removal of the ballast to expose the target section, which involves a high degree of physical intervention. This restricts its use in extensive auscultation campaigns, particularly in contexts where uninterrupted track operation is required.

While GPR has emerged as a promising tool for non-destructive assessment of railway ballast conditions, existing studies present significant limitations that hinder the robustness and generalizability of their proposed models. Most investigations rely on relatively small datasets, often restricted to laboratory-prepared boxes or short rail segments. For instance, Birhane et al. [39] and Matsimbe et al. [37] trained classification models using fewer than 10 representative A-scans per fouling class. De Bold et al. [30] conducted their analysis on a single  $10\mathrm{-m}$  test section, and Roberts et al. [27] used only 15 ground truth trenches over  $25\mathrm{km}$ . Eriksen et al. [31] validated their method on 14 sections of less than  $100\mathrm{m}$  each, while Sadeghi et al. [29] applied their algorithm to a  $17\mathrm{km}$  stretch divided into 80 segments.

This limited data volume prevents proper evaluation of model performance across the full range of real-world conditions, including variations in sleeper type (e.g., timber or concrete), ballast thickness, moisture content, drainage capacity, and fouling material composition. In addition, many approaches lack standardized performance metrics (e.g., accuracy, F1-score, RMSE) and are seldom tested on independent datasets or across different railway lines. The electromagnetic response captured by GPR is often similarly affected by both fouling and moisture, making their distinction particularly difficult using conventional features [35].

Tables 2 and 3 show that the various studies have used antennas between 400 and  $2000\mathrm{MHz}$ . The frequency and type of antenna are critical in characterizing the granular medium. Some studies have shown that higher frequency antennas can detect the dirt in the ballast layer more accurately [40,41]. Lower frequency antennas offer greater penetration into the granular medium, but less sensitivity to changes in surface levels [40,41].

These limitations highlight the need for a new diagnostic framework that integrates a broader and more diverse dataset, encompasses the complexity of operational and geotechnical variability, and leverages data fusion techniques along with explainable artificial intelligence [42]. Such an approach would allow for a more accurate and robust evaluation of ballast condition, thereby improving decision-making in railway infrastructure maintenance [42].

# A methodology integrating GPR measurements and LDCP/ Geoendoscopy-based learning

GPR is a technique that has been widely used to determine the ballast layer fouling index (FI), especially at high frequencies, and results with high levels of accuracy have been obtained using different parameters. In this proposal, the aim is to develop a machine learning model to estimate (FI). To do this, there is a historical database of French tracks consisting of a total of  $4700\mathrm{km}$  of GPR measurements with three  $400\mathrm{MHz}$  antennas and around of 12000 LDCP/Geoendoscopy test soundings. Additionally, it is necessary to carry out a parametric study of the GPR signals to quantify all the possible information that will be used to estimate this index based on the bibliographic analysis and statistical parameters. The LDCP/Geoendoscopy test surveys are important, as they allow the degree of railway track fouling to be

J. Rojas-Vivanco et al.

Transportation Geotechnics 55 (2025) 101701

Table 2 GPR applications to estimate the fouling index. Part 1.

|  N° | Antennas | Parameters | Correlations between GPR parameters and fouling index | Main results | Ref.  |
| --- | --- | --- | --- | --- | --- |
|  1 | 1 and 2 GHz. | Dispersion amplitude versus depth. | The amplitude values were compared with data from visual inspection, samples and dynamic penetration analysis (DCP). | Direct relationships were identified between attenuation and the presence of fouling material. For clean ballast, attenuation values of less than 5 dB were obtained; for partially fouled ballast, values of between 5 and 15 dB, and for very fouled ballast, attenuations greater than 15 dB. | [27]  |
|  2 | 1 and 2 GHz. | Dielectric constants, spectral integration index (integration area under the curve), axis crossings, inflection points and the high frequency dispersion index. | With the different parameters, linear regressions and quadratic models were applied to correlate them with the different fouling indexes, such as those of Selig and Ionescu. | High correlation in the determination of the fouling index for high frequencies (2 GHz), independent of the pollution index used as the target variable. | [26]  |
|  3 | 500 MHz and 2 GHz | Amplitude of the reflected signal and the spectral integration index (area under the amplitude curve in the frequency domain) mainly associated with 2 GHz antennas. | Implementation of linear regression models to establish trends between GPR measurements and those of the fouling index. | A high correlation was found between GPR predictions and physical ballast analyses. | [28]  |
|  4 | 2 GHz. | Amplitude of reflection, wave speed and spectrum. | The BFI index was defined by a mathematical model that includes the percentage of color-coded areas. | The results obtained in the laboratory showed a significant correlation, while in the field tests there was a good correlation with an error of less than 10% of the cases identified. | [29]  |
|  5 | 500 and 900 MHz, and 1, 1.6 and 2 GHz. | Dispersion area, axis crossing points and inflection points. | Correlation between parameters obtained with the fouling index. Fouling index calculated from P14 and P200. | Out of all the comparisons made, the 500 MHz antenna, using the dispersion area, showed a strong correlation with the fouling index. In contrast, the high frequency antennas were less consistent in defining whether the ballast was clean or fouled. | [30]  |
|  6 | 400 MHz and 2 GHz. | 2 GHz signal dispersion data is analyzed to model the reduction of empty spaces between ballast particles due to fouling. It is established that 400 MHz antennas are not suitable for determining the fouling state of the ballast. | This model establishes a correspondence between the GPR data and the fouling index obtained from tests, and determines the fouling states determined by Selig and Waters. | The BFI showed a reliable correlation with the results of the physical analysis of the ballast samples. Areas with high BFI values were associated with a greater accumulation of fine particles (particles that pass through the P4 and P200). | [31]  |

quantified. These reference values will serve as labels to train the machine learning model using the parameters derived from GPR signal processing.

# Description of the used data

After characterizing the granular medium and collecting the corresponding GPR data, it is important to apply a signal processing stage. This step aims to enhance key features of the acquired signals, improving their clarity and diagnostic value. The primary goal of this processing is to generate outputs that can be readily interpreted by operators or to classify detected objects based on established models or predefined criteria [38]. The treatments established by experimented engineers (hereafter experts) and consistently applied across all evaluated study sites include [42]:

- Normalization of the signals with respect to the direct wave.
- Elimination of the DC-Shift component, that is, the signals are centered so that they have a mean equal to zero.
- Elimination of the direct wave: to do this, the time associated with the direct wave must be found. Once located, a new zero time is placed at this point. From this zero time, a shift of 30 samples is made. The shift of 30 samples corresponds to the estimated time it takes for the wave to travel from the antenna to the surface of the runway. It is at this point that the new zero is established for the next step.
- A band-pass filter is applied between the frequencies of  $150\mathrm{MHz}$  and  $800\mathrm{MHz}$ .

- Signals are cut to obtain the windows length identified as the area of interest.
- To reduce the background noise, the BGR filter is applied with a window of 1000 signals.
- Once the signals have been processed, the analytical envelope of the signal is obtained. In order to perform, the signals are normalized to their maximum value.

# GPR parameterization

GPR signals can be analyzed using various quantitative parameters that provide insight into subsurface conditions. These parameters are commonly categorized into two primary groups based on the nature of the analysis: time domain parameters and frequency domain parameters. Below, we describe the main characteristics and typical features of each domain:

Time domain. The description of signals in the time domain is focused on the distribution of amplitudes [43]. The parameters describing its distribution are specific in order to describe a distribution curve, such as: quartiles, deciles, root mean square, median, skew, kurtosis. The maximum and minimum values of the signals in the time domain are also taken into account. The raw GPR signals are represented in the time domain. In Fig. 5a, the unprocessed electromagnetic waves are plotted as a function of track length and depth. In Fig. 5b, the complete set of signals along the entire track is shown in gray, while the red curve represents the average signal. In this plot, the  $y$ -axis corresponds to depth in nanoseconds, and the  $x$ -axis to wave amplitude. Another type of time-domain signal corresponds to the processed signals (see Fig. 5c),

J. Rojas-Vivanco et al.

Transportation Geotechnics 55 (2025) 101701

Table 3 GPR applications to estimate the fouling index. Part 2.

|  N° | Antennas | Parameters | Correlations between GPR parameters and fouling index | Main results | Ref.  |
| --- | --- | --- | --- | --- | --- |
|  7 | 2 GHz | Reflection amplitude and dispersion index. | The reflection amplitude and dispersion index were compared with the data measured in the laboratory using statistical regression. | The GPR-based fouling index (BFI) showed an 87% correlation with the Selig index. | [32,33]  |
|  8 | 400, 500, 900, 1600 MHz | Dielectric constant, Signal strength, Area of the frequency spectrum of the Signal and Ballast Condition Scoring Index (BCSI). | The parameters were directly related to the level of fouling measured in the laboratory and in the field. | The BCSI showed a greater correlation than the individual signal parameters. Accuracy in real conditions decreases due to variations in thickness, humidity and the type of fouling material. | [34]  |
|  9 | 400 MHz and 2 GHz | Effective dielectric constant, dispersion index and dispersion width. | The first approximation was made by modeling the electromagnetic properties using the complex refractive index model (CRIM) to calculate the dielectric constant of the ballast. These values were correlated with laboratory measurements. In the second, GPR parameters were extracted and compared with measurements taken by vibro-sampler, establishing empirical correlations. | High precision of clean ballast thickness, limitations when detecting the ballast-subballast interface, reliability of the CRIM model to define dielectric constants and contaminant properties, differentiation between fouling and moisture. | [35]  |
|  10 | 400 and 900 MHz, and 2 GHz | Relative dielectric permittivity (RDP) and electromagnetic wave velocity (EMWV). | An empirical correlation was made between the GPR values and the levels of fouling. | The use of GPR showed high accuracy in identifying critical ballast conditions, optimizing maintenance interventions and reducing associated costs. | [36]  |
|  11 | 900 MHz, 1 and 2 GHz | Amplitude of flexion, electromagnetic propagation velocity, A-Scan (one-dimensional graph of amplitudes versus time) and B-Scan (two-dimensional image that combines consecutive A-Scans showing distance and depth). | KNN (K-Nearest Neighbors) was used to classify the ballast as clean, moderate and contaminated using the A-Scan data. The second method used was XAI (explanatory machine learning model) with the aim of explaining the influence of moisture and contaminants on the GPR response. | The model obtained from KNN is able to perform high-precision classifications in the field and laboratory. While XAI identified the moisture and contaminant content. | [37]  |
|  12 | 400 MHz, 1 and 2 GHz | Amplitude of reflection, dispersion, Short-Time Fourier Transform (STFT) and the Wavelet Transform (WT). | The mathematical calculation of the standard deviation between the STFT and the WT was carried out. | High levels of correlation between the standard deviation and ballast layer contamination. | [38]  |

which enhance the representation of the granular medium's characteristics. In Fig. 5d, as in the previous case, the set of all individual signals is shown in gray, and their average in red.

Analytical signal. This is defined as a complex signal whose imaginary part is obtained through the Hilbert transform of its real part. In this work, the envelope of the analytic signal has been identified as a key tool for achieving the proposed objectives. This approach is supported by the conclusions of Braun [44], who states that "the envelope of this signal generally contains important information about it the signal". The Hilbert transform makes it possible to eliminate the rapid oscillations of the signal and obtain a direct representation of the envelope alone". Similarly, Feldman [45] highlights that the envelope of the analytic signal often captures the most relevant features for its interpretation. In this context, the envelope serves as a powerful means to extract the essential characteristics of GPR signals, thereby enhancing the analysis and facilitating the interpretation of subsurface conditions. The analytic signal is classified as a time-domain signal. An example is shown in Fig. 5e, where it is plotted along a section of the track as a function of time, representing depth. In Fig. 5f, the complete set of analytic signals is displayed in gray, while their average is highlighted in red.

Frequency domain. In the frequency domain, the Fourier transform was used to represent the spectrum and calculate the area under the curve, as proposed by Silvast [46]. They suggest that this area provides information on the degree of clogging of the ballasted layer, namely: it is lower for contaminated ballast than for clean ballast [26]. In Fig. 5g,

the Fourier spectrum corresponding to a specific section of the track is shown, plotted as a function of frequency (in MHz) and depth. In Fig. 5h, the complete set of Fourier spectra is displayed in gray, while the red curve represents the average value of these spectra.

The following section describes a set of parameters used to characterize the signals obtained from GPR recordings. The purpose of this parameterization is to support the development of machine learning models for assessing the fouling condition of the ballast layer and to establish correlations with geotechnical measurements, such as those obtained from LDCP/Geondoscopy tests. A summary of the calculated parameters is provided in Table 4.

# Target variable database

The target variable is the fouling of the ballast layer, which can be determined by different indicators. These indicators will be determined from the LDCP/geo-endoscopy by means of the estimation determined by Rojas [6] and a theoretical approximation based on the index properties of the ballast.

Empirical approach. The empirical approach of LDCP/geoendoscopy to determine the fouling index is based on the relationship between the thicknesses of the fouled ballast layer (indices of voids filled with fouling material) and the total thickness of that layer. Fig. 6 shows a description of the relationship between fouling height (FH) and fouling index (FI). Fig. 6a shows a clean state of the ballast layer. Fig. 6b shows the presence of fouling material (red section), which corresponds to a state of moderately clean. Fig. 6c illustrates a highly fouled ballast

J. Rojas-Vivanco et al.

Transportation Geotechnics 55 (2025) 101701

![img-8.jpeg](img-8.jpeg)

![img-9.jpeg](img-9.jpeg)

![img-10.jpeg](img-10.jpeg)

![img-11.jpeg](img-11.jpeg)

![img-12.jpeg](img-12.jpeg)

![img-13.jpeg](img-13.jpeg)

![img-14.jpeg](img-14.jpeg)
Fig. 5. Representation of the signals used in the parametric analysis: (a) individual raw signal, (b) set of raw signals, (c) processed signal, (d) set of processed signals, (e) analytic signal obtained via the Hilbert transform, (f) set of analytic signals, (g) Fourier spectrum of a single signal, (h) set of Fourier spectra. (For interpretation of the references to color in this figure legend, the reader is referred to the web version of this article.)

![img-15.jpeg](img-15.jpeg)

Table 4 Summary of parameters calculated from GPR measurements.

|  Parameters | Domain | Signal analyzed | Analysis group | Number of parameters  |
| --- | --- | --- | --- | --- |
|  Area under the Hilbert transform curve | Time | Analytics signal | 1 | 1  |
|  Area under the Fourier spectrum curve and dominant frequency | Frequency | Fourier spectrum | 1 | 2  |
|  Signal area, zero steps, inflection points, amplitude peaks | Time | Processed signal | 1 | 4  |
|  Signal (Sampling every 0.1 ns up to 7 ns) and signal statistics [mean, root mean square, standard deviation, median, skewness, kurtosis, quartiles, deciles] | Time | Processed signal | 2 | 127  |
|  Signal (Sampling every 0.1 ns up to 7 ns) and signal statistics [mean, root mean square, standard deviation, median, skewness, kurtosis, quartiles, deciles] | Time (Analytics) | Analytics signal | 3 | 127  |

layer, where the voids are almost completely filled with fine material, resulting in a fouling index close to its maximum value. Finally, Fig. 6d shows the correlation between fouling height and fouling index, indicating that as the height of the fouled layer increases, the proportion of voids filled with fine material also rises, leading to higher fouling index values.

The proposal of Rojas [6], allows to establish a correlation between the fouling height (FH) and the fouling index (FI), but associating a correction factor depending on the nature of the fouling material (sand or clay). The equations that describe how to obtain the fouling index from the thickness response are as follows:

$$
\% F H = \frac {H _ {F B}}{H _ {B T}} \times 100 \tag{8}
$$

J. Rojas-Vivanco et al.

Transportation Geotechnics 55 (2025) 101701

![img-16.jpeg](img-16.jpeg)
Fig. 6. Effect of height and state of ballast layer fouling. (For interpretation of the references to color in this figure legend, the reader is referred to the web version of this article.)

$$
\% F I = \frac {F H}{F} \tag{9}
$$

where:

- $H_{FB}$ = Fouled ballast thickness (in meters);
- $H_{BT}$ = Ballast layer thickness (in meters);
- $F$ = Empirical coefficient obtained in laboratory (For sands $\approx 2$ and for clays $\approx 1.5$ [6]).

Theoretical approach. This seeks to optimize the assessment of thicknesses by formulating an equation that relates thicknesses to the ballast layer's fouling index. This equation will be based on the index properties, allowing for a more precise evaluation of the degree of fouling.

For the purposes of defining an equation based on the index properties of soils, the following hypotheses must be defined:

- The equation will be calculated for a cube of $1\mathrm{m}^3$;
- The void ratio of the ballast is the same over the entire area studied;
- The void ratio of the fouling material is the same throughout the space studied;
- The specific weight of the ballast and fouling material is $26\mathrm{kN} / \mathrm{m}^3$. In the case of fouling material, this value is assumed because the fine contaminant particles observed on the railroad tracks studied are mainly from the mechanical breakage of ballast grains.
- The grain size composition of the fouling material is between $4.75\mathrm{mm}$ and $75\mu \mathrm{m}$.

The first phase is to define the mass and volume of the ballast in the cubic meter studied, to obtain these two variables it is necessary to initially obtain the density of the granular medium. Eq. (10) shows how to obtain the ballast density $(\rho_{B})$ from the specific weight $(y_{b})$ and void ratio $(e_b)$ of the ballast.

$$
\rho_ {B} = \frac {y _ {b}}{g} \times \frac {1}{1 + e _ {b}} \tag {10}
$$

The definition of the volume of ballast $(V_{B})$ is obtained by means of Eq. (11), which relates the total volume $(V_{T} = 1\mathrm{m}^{3})$ with its void ratio $(e_b)$ of the ballast.

$$
V _ {B} = \frac {V _ {T}}{1 + e _ {b}} \tag {11}
$$

Given the volume of ballast $(V_{B})$ and the volume studied $(V_{T} = 1\mathrm{m}^{3})$, it is possible to define the volume of voids $(V_{V})$ using Eq. (12). Disassociating the volume between the ballast and the void is important, as the volume of voids will indicate how much fouling material can fill the ballast layer.

$$
V _ {V} = V _ {T} - V _ {B} \tag {12}
$$

The input parameters assigned to the fouling material are the mass $(m_{FM})$ and the void ratio $(e_{MF})$. Using Eq. (13) it is possible to determine the density of the fouling material $(\rho_{FM})$ and to determine its volume $(V_{FM})$, Eq. (14) is used.

$$
\rho_ {F M} = \frac {y _ {F M}}{g} \times \frac {1}{1 + e _ {F M}} \tag {13}
$$

$$
V _ {F M} = \frac {m _ {F M}}{\rho_ {F M}} \tag {14}
$$

To determine the percentage of height occupied by the fouling material, the volume of fouling material is divided by the total volume of voids. This ratio allows the calculation of the fouling height $(FH)$ as a percentage, as expressed in the corresponding equation:

$$
\% F H = \frac {V _ {M F}}{V _ {V}} \times 100 \tag{15}
$$

The calculation of the fouling index $(FI)$ will be carried out using the expression proposed by Selig [4]. According to the hypothesis, only one particle size distribution is considered, with a maximum particle size of $4.75\mathrm{mm}$, that is, this will be the total mass of fouling material and the smallest size will be $75~{\mu\mathrm{m}}$. The percentage of mass passing through $P_{4}$ is calculated by dividing the mass of $P_{4}(M_{P4})$ by the total mass of the granular medium, i.e. the mass of the ballast $(M_B)$ plus the mass of the fouling material $(M_{P4})$, as described in Eq. (16). The percentage of mass that passes through $P_{200}$ is calculated with Eq. (17).

$$
P _ {4} = \frac {M _ {P 4}}{M _ {B} + M _ {P 4}} \tag {16}
$$

$$
P _ {2 0 0} = \frac {M _ {P 2 0 0}}{M _ {B} + M _ {P 4}} \tag {17}
$$

To create curves that relate the height of fouling to the fouling index using the approach described above, it is necessary to have synthetic data that allows the application of the corresponding equations. This data will be generated using a numerical simulation based on python scripts. Fig. 7 shows the Python code for generating all the parameters required to calculate the correlation between the fouling height $(FH)$ and the fouling index $(FI)$.

As for the ballast void ratio $(e_b)$, three representative values were considered, associated with different states of compaction: loose $(\approx 0.7)$, medium (0.6) and compact (0.53) [5]. The mass ranges for $M_{P4}$ and $M_{P200}$ were defined up to $7\mathrm{kN}$ because, by iterative calculation, with that amount there were cases where $100\%$ of the height was passed with fouling material. The void ratios of the fouling material are associated with the limits established for sands and clays for a compact or dense state.

Based on the synthetic data generated with the code in Fig. 7, the height and the fouling index were calculated. Subsequently, an average

value was obtained for each ballast consistency state. The following equations describe how to calculate the fouling index as a function of the fouling height for the different ballast layer consistencies.*%*F**I*_{(*L**o**o**s**e* *b**a**l**l**a**s**t* *c**o**n**d**i**t**i**o**n*)} = - 0.0013 *F**H*^{2} + 0.5570 *F**H* + 0.4170*%*F**I*_{(*M**e**d**i**u**m* *b**a**l**l**a**s**t* *c**o**n**d**i**t**i**o**n*)} = - 0.0017 *F**H*^{2} + 0.6311 *F**H* + 0.4933*%*F**I*_{(*C**o**m**p**a**c**t**e**d* *b**a**l**l**a**s**t* *c**o**n**d**i**t**i**o**n*)} = - 0.0022 *F**H*^{2} + 0.7248 *F**H* + 0.6753

Fig. 8 shows the theoretically calculated curves for the different levels of compaction. It can be observed that all the curves follow the same trend, with a directly proportional non-linear behavior. The compaction state indicates the amount of material that the ballast layer can hold. Therefore, for the same height, a loose state will hold more fouling material than the medium and compact states. This causes the fouling index to be higher. For example, for a height of 60%, the compact state obtains a fouling index of 29%, the medium state of 32.2% and the loose state of 36.2%. This difference is small when the fouling height is low and increases as the height increases.

#### Comparison between empirical and theoretical estimation

Fig. 8 shows the empirical and theoretical estimation, together with the data obtained in the laboratory and in the field. In addition, the different states proposed by Selig and Waters [4] are identified by different color ranges.

The empirical estimation associated with the clay contamination method tends to quantify a greater amount of fouling material compared to the other curves. In the case of the empirical estimation for sands, it initially optimally matches a compact state. However, as the height increases, the estimation begins to adjust to an intermediate state and, finally, to a loose state.

In general, a certain degree of similarity can be observed between the estimation obtained through empirical methods, which suggests a correlation between both approaches.

### Machine learning techniques

This section describes the machine learning algorithms employed in this study, focusing on ensemble-based methods known for their high predictive accuracy and robustness. Specifically, we implemented XGBoost and Random Forest, two well-established tree-based classifiers. Their respective learning principles, strengths, and suitability for structured data are outlined below, followed by an explanation of the Bayesian hyperparameter tuning approach used to optimize their performance.

The choice of XGBoost and Random Forest was driven by their robust handling of outliers, missing values, and heterogeneous data types, as well as their capacity to model complex, non-linear relationships in structured datasets. These ensemble methods provide a wide range of tunable hyperparameters, supporting flexible and robust model adaptation. Furthermore, they scale efficiently to large datasets; in this study, we leveraged GPU acceleration for XGBoost to make hyperparameter tuning computationally feasible. Compared to traditional algorithms such as logistic regression, both XGBoost and Random Forest consistently achieved higher classification performance in our experiments. Detailed comparative results are presented in the Results section.

### Logistic regression

Logistic regression is a linear classification algorithm widely used as a baseline in supervised learning tasks. It models the probability that a given input belongs to a particular class using a logistic (sigmoid) function, making it suitable for binary and multiclass problems via extensions such as one-vs-rest. The model estimates coefficients for each feature, representing their contribution to the decision boundary that separates classes.Linear Decision Boundary: Assumes a linear relationship between input features and the log-odds of the target class Regularization: Supports *L*_{1} (lasso) and *L*_{2} (ridge) regularization to prevent overfitting and control model complexity. Interpretability: Coefficients provide direct insights into the influence of each feature, facilitating interpretation and transparency.

In this study, logistic regression was implemented as a baseline model and further optimized using the Optuna framework for hyperparameter tuning. While it is generally less expressive than ensemble-based approaches, it provides a robust and interpretable reference point for evaluating the added value of more complex classifiers.

### XGBoost

XGBoost (Extreme Gradient Boosting) is a scalable, tree-based ensemble method that builds gradient-boosted decision trees in an efficient manner. It leverages second-order gradient information for tree construction and uses several system-level optimizations (such as approximate histograms and out-of-core computation) to process large datasets efficiently. At the algorithmic level, XGBoost adds regularization (e.g. *L*_{1} or *L*_{2}) to prevent overfitting, and it allows parallel computation of tree nodes as well as efficient handling of sparse data.Gradient Boosting Principle: Trees are built sequentially, with each new tree attempting to correct errors from the previous ensemble of trees. Regularization: Penalty terms for model complexity avoid overfitting.Second-Order Approximation: The loss function is expanded using second-order derivatives, providing more precise updates compared to first-order boosting approaches.

### Random Forest

Random Forest is another ensemble learning method that builds a large number of decision trees, each trained on different subsamples of the data (and often using feature randomness). The final prediction is commonly obtained by majority voting in classification tasks or averaging in regression tasks.

J. Rojas-Vivanco et al.

Transportation Geotechnics 55 (2025) 101701

![img-17.jpeg](img-17.jpeg)
Fig. 8. Effect of height and state of ballast layer fouling. (For interpretation of the references to color in this figure legend, the reader is referred to the web version of this article.)

- Bootstrap Aggregation (Bagging): Each tree is trained on a randomly sampled subset of the training data.
- Feature Randomness: A random subset of features is used at each node, increasing diversity among the trees.
- Overfitting Mitigation: By combining multiple de-correlated trees, the ensemble reduces variance, thus achieving robust predictions.

# Bayesian hyperparameter tuning

Bayesian hyperparameter tuning is an optimization strategy that builds a probabilistic model of the objective function and uses it to select the most promising hyperparameter configurations to evaluate. One of the most effective implementations of this approach is the Tree-structured Parzen Estimator (TPE), which models the likelihood of achieving high performance based on past trials.

In this study, the Optuna framework was employed, which applies TPE to efficiently guide the hyperparameter search process. The method prioritizes exploration of hyperparameter regions with higher expected improvement, rather than evaluating configurations at random or on a fixed grid. This technique was used to tune critical model parameters such as learning rate, number of estimators, and maximum tree depth. The objective function was based on validation accuracy, and underperforming trials were pruned early to reduce computational cost.

# Training and validation methodology

This section presents the process of hyperparameter tuning applied to the machine learning algorithms previously described, using Bayesian optimization. Specifically, we used the Optuna framework to explore the hyperparameter space and identify the most effective parameter combinations for each model.

# Bayesian hyperparameter tuning strategy

Bayesian optimization is a sequential model-based approach to finding the optimal set of hyperparameters. It builds a probabilistic model of the objective function and uses it to choose the most promising hyperparameter values to evaluate next. In this work, we employed the Tree-structured Parzen Estimator (TPE), a non-parametric Bayesian algorithm implemented in Optuna, which models the conditional probability distribution of the objective score given hyperparameter configurations.

Optuna creates a study that orchestrates the tuning process, sampling values from user-defined ranges, training the model, and evaluating its performance. Based on this feedback, the algorithm updates its internal model and continues exploring the parameter space more efficiently than traditional grid or random search.

# Tuning hyperparameters for XGBoost

The following hyperparameters were tuned for the XGBoost model:

- n_estimators: Number of boosting rounds. Controls model complexity and risk of overfitting.
- max_depth: Maximum depth of each tree. Larger values increase capacity but may overfit.
- learning_rate: Shrinks the contribution of each tree; smaller values lead to slower but more stable convergence.
- subsample: Fraction of the training set used per tree. Reduces variance and overfitting.
- colsample_bytree: Fraction of features sampled per tree. Helps reduce correlation among trees.
- gamma: Minimum loss reduction required to make a further partition on a leaf node.
- reg_alpha, reg_lambda: L1 and L2 regularization terms, respectively.

# Tuning hyperparameters for Random Forest

For the Random Forest classifier, the following key hyperparameters were tuned:

- n_estimators: Total number of trees in the forest.
- max_depth: Maximum depth of each tree.
- min_samples_split: Minimum number of samples required to split a node.
- max_features: Number of features to consider at each split.

# Dataset structure and validation strategy

The training dataset was created from a historical database of measurements performed on the French railway network. In this context, a total of approximately 60,000 LDCP/geoendoscopy test measurements and  $4700\mathrm{km}$  of GPR were performed, but only in 12,000 soundings are both measurements at the same point [42]. Fig. 9 shows the spatial

J. Rojas-Vivanco et al.

Transportation Geotechnics 55 (2025) 101701

![img-18.jpeg](img-18.jpeg)
Fig. 9. Distribution of the application of the LDCP/geoendocopy test methodology and GPR measurements in France [42].

![img-19.jpeg](img-19.jpeg)

distribution of both measurements throughout France. Each instance is described by 262 independent predictor variables, whose types and signal domains are summarized in Table 4. The categorical target vector is stored separately. This constitutes a multi-class classification problem with five distinct classes, whose distribution is summarized in the Results section. During Optuna's Bayesian search, model performance was estimated using 2-fold stratified cross-validation on the training portion. The mean validation score of these two folds served as the optimization objective. This approach avoids the need for a separate hold-out validation set while still providing an unbiased estimate of generalization performance. Random seeds were fixed (numpy.random.seed = 42) for reproducibility. Standardization parameters were computed on the training folds only and applied consistently to the validation folds and the final test set.

# Implementation using Optuna

The tuning process was implemented using the Optuna framework, where an objective function is defined for each model. This function receives a trial object, which is used to sample hyperparameter values from predefined search spaces. The model is then instantiated with these values, trained using the training set, and evaluated through cross-validation. The average validation score is returned as the optimization objective.

In practice, four experiments were conducted to evaluate both the XGBoost and Random Forest classifiers using two performance metrics: accuracy and precision. Each combination was tuned independently to assess model robustness under different evaluation criteria. Algorithm 1 illustrates the implementation of the tuning strategy for the case of XGBoost, using accuracy as the optimization metric and GPU acceleration to reduce training time.

In this pseudocode:

- The objective(trial) function encapsulates the evaluation logic for a single trial.
- The trial.suggest methods define the search space for each hyperparameter.
- The study.optimize call executes the tuning process for a fixed number of trials (45 in this case), aiming to maximize classification accuracy.

Once completed, the optimal hyperparameter configuration is extracted using study.best.params, which is then used for final model training and testing.

Algorithm 1 Optuna-based Hyperparameter Tuning for XGBoost (GPU)
1: function OBJECTIVE(trial)
2:  $n_{est} \gets \text{trial.SUGGEST_INT("n_estimators", 100, 500)}$
3: max_d  $\gets$  trial.SUGGEST_INT("max_depth", 3, 15)
4: lr  $\gets$  trial.SUGGEST_FLOAT("learning_rate", 0.01, 0.3)
$\triangleright$  Additional options: subsample, colsample_bytree, gamma
$\triangleright$  GPU acceleration enabled with tree_method = "hist", device = "cuda"
5: model  $\gets$  XGBCLASSIFIER(n_estimators=n_est, max_depth=max_d, learning_rate=lr, tree_method="hist", device="cuda", eval_metric="logloss")
6: score  $\gets$  CROSS_VAL SCORE(model, X_train, y_train, cv=2, scoring="accuracy")
7: return mean of score
8: end function
9: study  $\gets$  OPTUNA.CREATE_STUDY(direction="maximize")
10: STUDY OPTIMIZE(Objective, n_trials=45)
11: PRINT(study.best.params)
12: PRINT(study.best_value)

# Validation and evaluation metrics

After identifying the best hyperparameter configurations using Bayesian optimization, the models were retrained on the training set and evaluated on a separate test set. To assess classification performance, several standard metrics were computed: accuracy, precision, recall, and F1-score. These metrics offer a comprehensive evaluation of the model, balancing both global correctness and class-specific behavior.

A confusion matrix was also generated for each trained model, enabling a more detailed analysis of misclassification patterns across classes.

Importantly, cross-validation was used throughout the entire process—not only during final evaluation but also as part of the objective function in Optuna's tuning loop. During each trial, the model's performance was estimated using cross-validation based on the target metric (either accuracy or precision). This strategy ensured that hyperparameter search was guided by reliable estimates of generalization performance and aligned with the final evaluation criteria.

J. Rojas-Viranco et al.

Transportation Geotechnics 55 (2025) 101701

![img-20.jpeg](img-20.jpeg)
Fig. 10. Normalized confusion matrix  $(\%)$  for the baseline logistic regression model optimized with Optuna.

# Results

The following section presents a systematic evaluation of the proposed classification framework. We begin by establishing a baseline using logistic regression optimized with Optuna, which provides a reference point for subsequent comparisons. The performance of this baseline model is then contrasted with that of more advanced ensemble methods, namely Random Forest and XGBoost. Both training and field application results are reported and discussed in detail, with particular attention to each model's ability to classify the different geotechnical categories and to generalize across diverse study sites.

# Baseline model

Before evaluating more advanced classifiers, a baseline model was defined using logistic regression. This approach was chosen due to its simplicity, interpretability, and solid theoretical grounding, making it a standard reference for classification tasks. The logistic regression model was optimized using the Optuna framework, which systematically explored the regularization parameter and penalty configuration. The final model employed an L2 penalty with a regularization strength of approximately 4.95, providing a well-balanced trade-off between model complexity and generalization.

This baseline serves as a consistent benchmark for assessing the relative improvements brought by more complex algorithms such as Random Forest and XGBoost. Although ensemble methods are expected to outperform it in terms of predictive power, the logistic regression model offers a useful lower bound for model performance. The confusion matrix in Fig. 10 summarizes the classification results for the five geotechnical categories, normalized by row to highlight class-wise recall behavior.

The confusion matrix in Fig. 10 shows that the Optuna-tuned logistic-regression baseline separates the two most frequent categories - MC and MF - only moderately well; at the same time it redirects a substantial portion of C and F instances into those classes and achieves very low recall for the HF category. This behavior indicates that the linear decision surface is unable to capture the subtle transitions between ballast-cleanliness levels, particularly at the clean and highly fouled extremes. These shortcomings motivate the use of more expressive, non-linear algorithms. Consequently, the next section evaluates Random Forest and XGBoost to determine whether their ensemble architectures can more accurately discriminate among the five geotechnical classes.

# Evaluation of ensemble methods

Fig. 11 presents a comparative evaluation of the performance of two classification models, Random Forest (RF) and XGBoost (XGB), in identifying five geotechnical classification categories: C (Clean), MC (Moderately Clean), MF (Moderately Fouled), F (Fouled), and HF (Highly Fouled). Subplots (a) and (d) correspond to the confusion matrices for the accuracy metric of both models, while (b) and (e) show the matrices for the precision metric. It can be observed that both approaches achieve accurate classification, with values exceeding  $90\%$  for most categories. However, slight differences in misclassification rates can be identified among adjacent classes, particularly in the MF, F, and HF categories, where the similarity in sample characteristics may lead to higher confusion rates. Notably, for both metrics, the models exhibit their best performance in the 'C' and 'MC' classes, while the 'HF' class tends to have higher misclassification rates, suggesting greater complexity in distinguishing this category due to its geotechnical variability.

Subplots (c) and (f) illustrate the evolution of accuracy and precision metrics over 45 trials for both models. In the case of RF, a high degree of stability is observed in both metrics, with consistently high values, indicating robust performance even in the presence of variations in data partitioning. In contrast, XGB, although also demonstrating high precision, exhibits greater variability in its results, particularly in precision, which may be associated with a higher sensitivity to training data or a more complex decision structure.

In general, the results presented in this figure highlight the strengths and limitations of both algorithms for geotechnical classification. The more consistent performance of RF suggests that, for applications where prediction stability is critical, this approach may be preferable. However, the ability of XGB to capture more complex relationships between features could make it more suitable for scenarios with more imbalanced datasets or with more pronounced non-linear characteristics. These results provide valuable insights for selecting the most appropriate algorithm in future geotechnical diagnostic applications.

# Analysis of the importance of the variables using SHAP

Fig. 12 shows an analysis performed with a SHAP model to interpret the parameters that make up the model. As indicated in Section "Dataset structure and validation strategy", a total of 262 parameters were obtained to estimate the classification of the fouling state of the ballast layer. Due to the large number of variables, the parameters were grouped into three different groups, which are specified in Table 4: group 1 (parameters used in other studies), group 2 (associated with the processed signal) and group 3 (associated with the analytical signal).

Fig. 12a shows the distribution of SHAP values by group, where it can be seen that: (i) group 1 shows mostly positive values, indicating that it contributes to the model, although to a lesser extent; (ii) group 2 shows a high dispersion of SHAP values associated with negative and positive values, indicating that the parameters used have a different influence depending on the sample, and (iii) group 3 shows more uniformly distributed values, which could indicate that this group contributes more consistently and stably to the model.

Fig. 12b shows a complementary analysis of the relative importance of the groups for the five established fouling state classes, calculated as the percentage of the total importance of the SHAP. It is observed that group 3 is the dominant group, with importance percentages between 60 and  $65\%$ , while group 2 contributes values between 30 and  $40\%$ , with a constant participation in the classes. Finally, group 1 generates a very small importance, less than  $5\%$ , in all cases.

From this analysis, it is clear that the model relies mainly on group 3 for decision making and that the contribution of group 1 to the predictions is limited.

J. Rojas-Vivanco et al.

Transportation Geotechnics 55 (2025) 101701

![img-21.jpeg](img-21.jpeg)

![img-22.jpeg](img-22.jpeg)

![img-23.jpeg](img-23.jpeg)

![img-24.jpeg](img-24.jpeg)

![img-25.jpeg](img-25.jpeg)
Fig. 11. Confusion matrices for Random Forest and XGBoost models.

![img-26.jpeg](img-26.jpeg)

![img-27.jpeg](img-27.jpeg)
Fig. 12. Confusion matrices for Random Forest and XGBoost models.

![img-28.jpeg](img-28.jpeg)

# Field application

# Description of the study sites

To evaluate the generalization capability of the classification models (Random Forest and XGBoost) in identifying different fouling states in railway ballast, five independent sites were used, distinct from those employed for initial model training. Each of these sites includes measurements obtained through GPR, which serve as input data for the application of the pre-trained models. In order to validate the

performance of the predicted outcomes, the results will be compared against reference measurements obtained using LDCP tests and geoendoscopy. This evaluation is essential to assess the robustness of the models unseen real-world conditions, where acquisition characteristics may differ significantly from the training dataset.

Table 5 presents the five study sites, along with their general characteristics, with particular emphasis on whether their acquisition conditions differ from or resemble those of the data set used during model training.

J. Rojas-Vivanco et al.

Transportation Geotechnics 55 (2025) 101701

Table 5 Summary of acquisition conditions and characteristics of each surveyed site.

|  Site/location | Acquisition system | Speed (km/h) | Antenna height (cm) | Armament configuration | Substructure | Alignment with training  |
| --- | --- | --- | --- | --- | --- | --- |
|  Site 1/France | Lorry (see Fig. 13) | 4 | 10 | 50E6 (U50) or 60E1 (UIC 60) and 1435 mm gauge | Ballast, Interlayer and Subgrade | Non  |
|  Site 2/France | Train | 30 to 60 | 50 | 50E6 (U50) or 60E1 (UIC 60) and 1435 mm gauge | Ballast, Interlayer and Subgrade | Yes  |
|  Site 3/France | Train | 30 to 60 | 50 | 50E6 (U50) or 60E1 (UIC 60) and 1435 mm gauge | Ballast, Interlayer and Subgrade | Yes  |
|  Site 4/No France | Train | 30 to 60 | 50 | Rails UIC 60/60E1 and 1676 mm gauge | Ballast, Subballast and Subgrade | Non  |
|  Site 5/No France | Train | 30 to 60 | 50 | Rails UIC 60/60E1 and 1676 mm gauge | Ballast, Subballast and Subgrade | Non  |

![img-29.jpeg](img-29.jpeg)
Fig. 13. Data acquisition performed by manually moving the antenna.

# Performance of the models at the study sites

The results for each site, presented in the confusion matrices of Fig. 14, are described below. Each row of graphs in the figure corresponds to a different study site: the first row represents the results for Site 1, the second row for Site 2, the third row for Site 3, the fourth row for Site 4, and the fifth row for Site 5.

- Site 1: Compared to the training dataset, this site shows significantly lower performance, with average precision scores of  $50.7\%$  for Random Forest (RF) and  $53.7\%$  for XGBoost, and accuracy scores of  $47.8\%$  for RF and  $50.7\%$  for XGBoost (see first row of Fig. 14). Among all the evaluated models, XGBoost demonstrated slightly better precision, which could be related to its ability to model nonlinear relationships in noisier data. This performance difference is largely due to the atypical acquisition conditions at this site, including lower travel speed and a reduced antenna-to-ground distance ( $10\mathrm{cm}$  instead of  $50\mathrm{cm}$ ), which significantly affect the GPR signal characteristics, including spatial resolution and amplitude. Additionally, the highest classification errors were observed between the MF and F categories, where the similarity in sample characteristics introduces higher confusion rates.
- Site 2: The performance at this site is considerably better, with precision scores of  $79.7\%$  for XGBoost and  $67.6\%$  for RF, and accuracy scores exceeding  $68.9\%$  for both models (see second

row of Fig. 14). This improved performance is consistent with the more similar acquisition conditions to those of the training dataset, including comparable travel speed and antenna-to-ground distance. This consistency reduces discrepancies between training and testing data, leading to more accurate classifications. However, classification errors between the MF and F categories remain present, reflecting the ongoing challenge of distinguishing samples with similar characteristics.

- Site 3: Similar to Site 2, this site exhibits robust performance, with precision scores reaching  $86.7\%$  for XGBoost and  $75.6\%$  for RF, and accuracy scores above  $75.6\%$  for both models (see third row of Fig. 14). These results align with expectations for sites with acquisition conditions similar to the training set, suggesting that the models are highly effective when the data characteristics closely match those used during training. However, as with other sites, the most frequent classification errors occur between the MF and F categories, potentially due to the proximity of their geotechnical characteristics.
- Site 4: Although the results for this site are superior to those of Site 1, they still show greater variability in performance, with precision scores ranging from  $50.0\%$  to  $73.1\%$  for XGBoost and from  $39.6\%$  to  $54.6\%$  for RF (see fourth row of Fig. 14). This variability may be due to structural differences in the terrain and acquisition conditions at this site, including different rail profiles

J. Rojas-Viranco et al.

Transportation Geotechnics 55 (2025) 101701

![img-30.jpeg](img-30.jpeg)
Fig. 14. Confusion matrix - Results obtained from applying the case studies to different trained models.

and antenna-to-ground distances that do not match the  $50~\mathrm{cm}$  standard used in the training set, introducing higher classification error rates, particularly between the MF and F categories.

- Site 5: This site exhibits the most variable results, with precision scores ranging from  $50.0\%$  to  $62.3\%$  for XGBoost and from  $39.6\%$  to  $54.6\%$  for RF (see fifth row of Fig. 14). Although these values are higher than those observed for Site 1, they still reflect the challenges associated with geographical and structural differences between this site and the training data, including variations in rail height and differences in the density of the granular medium, which can significantly affect GPR signal characteristics and, consequently, model accuracy. The highest classification errors are again observed between the MF and F categories, indicating that variations in site conditions further complicate the differentiation of these classes.

Although higher frequency antennas can provide better resolution, the performance variation observed in this study is mainly due to factors related to data acquisition. This is because, when the acquisition was performed under the same conditions as the training set, the results obtained were relevant, especially for XGBoost (points 2 and 3). However, when the data are different, there is a significant loss of performance in the models, although XGBoost was always the best.

Fig. 15 shows an example of the application of the XGBoost (Accuracy) model. The figure is divided into three sections:

- Fig. 15a - Processed Signals: This section presents the preprocessed GPR signals, where the raw data has been filtered and adjusted to enhance the visibility of key structural features. The grayscale representation emphasizes the amplitude variations and reflection patterns, providing a detailed view of the subsurface characteristics.

J. Rojas-Vivanco et al.

Transportation Geotechnics 55 (2025) 101701

![img-31.jpeg](img-31.jpeg)

![img-32.jpeg](img-32.jpeg)

![img-33.jpeg](img-33.jpeg)
Fig. 15. Application of the XGBoost (Accuracy) model: (a) processed signals from the study site, (b) results derived from the analytic signal, and (c) predictions generated by the Machine Learning model. (For interpretation of the references to color in this figure legend, the reader is referred to the web version of this article.)

- Fig. 15b - Hilbert Transform: This subplot shows the analytical signal obtained through the Hilbert Transform, which highlights the instantaneous amplitude of the treated signals. The color map clearly distinguishes high-energy zones (in red) from lower energy areas (in blue), reflecting the varying densities and material properties within the granular medium.
- Fig. 15c - Fouling State Prediction: This section illustrates the results of the machine learning model. The gray dots represent the fouling state estimations for each meter, as predicted by the ML model. The black curve shows the regularization applied every  $5\mathrm{m}$ , smoothing the classification results to reduce noise and increase interpretability. Finally, the blue points correspond to punctual field measurements, providing a reference for the model's accuracy against ground truth data.

# Conclusions

In this study, a methodology was developed to assess railway ballast fouling through the integration of GPR data and machine learning models. The data was acquired using a  $400\mathrm{MHz}$  antenna, which, although not conventionally used for fouling index estimation (as higher frequency antennas are typically preferred), proved effective in capturing critical granular medium characteristics. This intermediate frequency allowed for the detection of both near-surface reflections and deeper internal structures within the ballast, providing detailed information for subsequent analysis.

During the training phase, the machine learning models were optimized using preprocessed GPR data, including time and frequency domain analyses, as well as specific analytical parameters to enhance signal characterization. In this phase, the Random Forest algorithm demonstrated superior performance, achieving the highest accuracies

in fouling index estimations. Specifically, a global precision of  $96.08\%$  was achieved across all classes, with the highest performance observed for the medium fouling (MF) class at  $97.89\%$ , and the lowest for the high fouling (HF) class at  $94.09\%$ .

However, when the models were applied to new data not included in the original training set, the XGBoost model showed greater robustness, yielding more consistent and accurate results. This indicates that, while Random Forest is effective under controlled conditions, XGBoost is better suited for scenarios where the data is more variable or contains nonlinear features, as often encountered in different sections of railway tracks. Specifically, the XGBoost model achieved  $79.7\%$  and  $86.7\%$  accuracy when the test data closely resembled the training conditions (site 2 and 3), outperforming the other models evaluated. In moderately similar conditions (site 4 and 5), accuracy dropped to  $62.3\%$  and  $73.1\%$ , and in completely different scenarios (site 1), performance dropped even further, to  $50.7\%$ . Despite this decline, XGBoost consistently outperformed the other models in all but the most different scenario.

Despite promising results, traditional methods for assessing ballast fouling have significant limitations. Physical sampling, although accurate, is highly invasive and impractical for extensive applications. The combined technique of LDCP/geoendoscopy tests, while less intrusive, remains sporadic and limited in spatial coverage. Image analysis, meanwhile, requires interventions that make it difficult to implement in systematic monitoring. In addition, many studies that integrate GPR with machine learning use small data sets and controlled conditions, which limits their applicability in real-world settings. Added to this is the difficulty of distinguishing between signals associated with contamination and moisture, which can compromise diagnostic accuracy if not addressed through more robust and adaptive approaches.

In conclusion, the results confirm that integrating GPR data with machine learning models is a promising approach for non-destructive

ballast fouling assessment. However, future studies should consider the use of higher frequency antennas to improve the resolution of measurements and explore advanced data fusion techniques — such as Bayesian inference, possibility theory combined with fuzzy sets and Dempster--Shafer evidence theory with the objective of evaluating multiple sources of information to provide greater robustness to models under more diverse and realistic conditions. Regarding data fusion, some generalized applications have already been carried out with promising results [42,47].

## CRediT authorship contribution statement

Jorge Rojas-Vivanco: Writing -- review & editing, Writing -- original draft, Visualization, Validation, Supervision, Methodology, Investigation, Formal analysis, Data curation, Conceptualization. Miguel Benz-Navarrete: Writing -- review & editing, Conceptualization. José García: Writing -- original draft, Methodology, Formal analysis, Data curation. Pierre Breul: Writing -- review & editing, Supervision. Aurélie Talon: Writing -- review & editing, Supervision. Gabriel Villavicencio: Writing -- review & editing, Supervision.

## Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## Acknowledgments

The authors gratefully acknowledge the support of Sol Solution, which partially funded the doctoral research of the first author [42]. The first author also wishes to express sincere thanks to the research engineers at Sol Solution -- particularly Antonio Herrera Bautista, Sebastien Barbier, Fabien Ranvier, and Younes Haddani -- for their valuable technical assistance, continuous support throughout the doctoral work [42], and meaningful contributions to the development of this research.

## Data availability

The data that has been used is confidential.

## References

[1] Rojas J, Breul P, Talon A, Benz-navarrete MA, Barbier S, Haddani Y. Importance of geotechnical diagnosis in railway management: A review. Transp Eng 2024;18(100293). http://dx.doi.org/10.1016/j.treng.2024.100293.

[2] AFNR. NF EN 13450 - Granulats pour ballasts de voies ferrées. CEN - Afnor, France; 2003, p. 40.

[3] Indraratna B. 1St ralph proctor lecture of ISSMGE. Railroad performance with special reference to ballast and substructure characteristics. Transp Geotech 2016;7:74--114. http://dx.doi.org/10.1016/j.trgeo.2016.05.002.

[4] Selig E, Waters J. Track geotechnology and substructure management. Thomas Telford; 1994.

[5] Li D, Hyslip J, Sussmann T, Chrismer S. Railway geotechnics, vol. 1, CRC Press - Taylor & Francis Group; 2016.

[6] Rojas-Vivanco J, Breul P, Talon A, Benz-Navarrete M, Barbier S, Ranvier F. On site fouling index assessment of ballasted layers using cone dynamic penetrometer and miniature borescope image analysis. Transp Geotech 2024;45:1--14. http://dx.doi.org/10.1016/j.trgeo.2024.101213.

[7] Austroads. AS 2758.7—1996 aggregates and rock for engineering purposes part 7: Railway ballast. 1996, Australian.

[8] Ionescu D. Ballast degradation and measurement of ballast fouling. In: 7th railway engineering proceedings. 2004, p. 169--80, no. February, Online available: https://www.researchgate.net/publication/275341734%0ABallast.

[9] Paiva C, Ferreira M, Ferreira A. Ballast drainage in Brazilian railway infrastructures. Constr Build Mater 2015;92:58--63. http://dx.doi.org/10.1016/j.conbuildmat.2014.06.006.

[10] Bassey D, Ngene B, Akinwumi I, Akpan V, Bamigboye G. Ballast contamination mechanisms: A criterial review of characterisation and performance indicators. Infrastructures 2020;5(11):1--24. http://dx.doi.org/10.3390/infrastructures5110094.

[11] Indraratna B, Nimbalkar S, Tennakoon N. The behaviour of ballasted track foundations: Track drainage and geosynthetic reinforcement. In: GeoFlorida 2010: Advances in analysis, modeling & design. 2010, p. 2378--87, no. Gsp 199.

[12] Tennakoon N, Indraratna B, Rujikiatkamjorn C, Nimbalkar S, Neville T. The role of ballast-fouling characteristics on the drainage capacity of rail substructure. Geotech Test J 2012;35(4):25. http://dx.doi.org/10.1520/GTJ104107.

[13] Scanlan KM. Evaluating degraded ballast and track geometry variability along a Canadian freigbt railroad through ballast maintenance records and ground penetrating radar (Ph.D. thesis), University of Alberta; 2018.

[14] Feldman F, Nissen D. Alternative testing method for the measurement of ballast fouling: percentage void contamination. In: Conference on railway engineering. 2002, p. 101--11, Online available: https://search.informit.com.au/documentSummary;dss=303805891788837;res=IELENG.

[15] Indraratna B, Su LJ, Rujikiatkamjorn C. A new parameter for classification and evaluation of railway ballast fouling. Can Geotech J 2011;48(2):322--6. http://dx.doi.org/10.1139/T10-066.

[16] AFNOR. NF EN 933-3 Essais pour déterminer les caractéristiques. 1996.

[17] Gourvès R, Barjot R. Le pénétromètre dynamique léger PANDA, the PANDA ultralight dynamic penetrometer. 1992, no. 313.

[18] Breul P. Caractérisation endoscopique des milieux granulaires couplée à l'essai de pénétration (Ph.D. thesis), Clermont-Ferrand, France: Université Blaise Pascal -- Clermont II, École Doctorale Sciences pour l'Ingénieur de Clermont-Ferrand; 1999.

[19] Rojas-Vivanco J, Barbier S, Navarrete MAB, Breul P. Statistical analysis of the influence of ballast fouling on penetrometer and geoendoscope data. Adv Transp Geotech IV 2021;165:915--30. http://dx.doi.org/10.1007/978-3-030-77234-5_75.

[20] SafeRack. Railroad facts...construction, safety and more. 2019, URL https://www.saferack.com/railroad-track-facts-construction-safety/. [Accessed 31 July 2025].

[21] Tutumluer MME, Abuja N. Field Evaluation of Ballast Fouling Conditions Using Machine Vision. Tech. rep. University of Illinois at Urbana-Champaign; 2017.

[22] Delay BL. Machine learning techniques for identifying railroad ballast degradation (Ph.D. thesis), University of Illinois at Urbana-Champaign; 2016.

[23] Luo J, et al. Towards automated field ballast condition evaluation: Field validation of the ballast scanning vehicle capabilities. Transp Geotech 2024;48(March):101311. http://dx.doi.org/10.1016/j.trgeo.2024.101311.

[24] Ding K, Luo J, Huang H, Hart JM, Qambia I, Tutumluer E. Augmented dataset for vision-based analysis of railroad ballast via multi-dimensional data synthesis. MDPI Algorithms 2024.

[25] Gong Y, Qian Y. Lite RGB-based measurement method for ballast fouling index prediction through subsampling. Measurement 2024;234(4):114813. http://dx.doi.org/10.1016/j.measurement.2024.114813.

[26] Wang S, Liu G, Jing G, Feng Q, Liu H, Guo Y. State-of-the-art review of ground penetrating radar (GPR) applications for railway ballast inspection. Sensors 2022;22(7):2450. http://dx.doi.org/10.3390/s22072450.

[27] Roberts B, Rudy J, Al-Qadi I, Tutumluer E, Boyle J. Railroad ballast fouling detection using ground penetrating radar -- a new approach based on scattering from voids. In: Ecndt. 2006, p. 8.

[28] Roberts R, Al-Qadi IL, Tutumluer E, Boyle J. Subsurface evaluation of railway track using ground penetrating radar. 2009, [Online]. Available: http://trid.trb.org/view.aspx?id=902895.

[29] Sadeghi J, Motieyan-Najar ME, Zakeri JA, Yousefi B, Mollazadeh M. Improvement of railway ballast maintenance approach, incorporating ballast geometry and fouling conditions. J Appl Geophys 2018;151:263--73. http://dx.doi.org/10.1016/j.jappgeo.2018.02.020.

[30] Bold D, O'Connor, Morrissey, Forde. New analysis of ground penetrating radar testing of a mixed railway trackbed. 2009, p. 1--17, 13.

[31] Basye C, Wilk S, Gao Y. Ground Penetrating Radar (GPR) technology evaluation and implementation. 2020, [Online]. Available: https://railroads.dot.gov/sites/fra.dot.gov/files/2020-05/GPR%20Tech%20and%20Eval%20Implementation_rev.pdf.

[32] Eriksen A, Gascoyne J, Fraser R. Ground penetrating radar as part of a holistic strategy for inspecting trackbed. In: Australian geomechanics society adelaide, 19th September 2011. 2011, no. September.

[33] Zhang Q, Eriksen A, Gascoyne J. Rail radar - a fast maturing tool for monitoring trackbed. In: Proceedings of the 13th international conference on ground penetrating radar. GPR 2010, 2010, http://dx.doi.org/10.1109/ICGPR.2010.5550142, no. 1.

[34] Birhane FN, Choi YT, Lee SJ. Development of condition assessment index of ballast track using ground-penetrating radar (GPR). 2021.

[35] Barrett BE, Day H, Gascoyne J, Eriksen A. Understanding the capabilities of GPR for the measurement of ballast fouling conditions. J Appl Geophys 2019;169:183--98. http://dx.doi.org/10.1016/j.jappgeo.2019.07.005.

[36] Borkovcová A, Borecký V, Artagan SS, Ševčík F. Quantification of the mechanized ballast cleaning process efficiency using GPR technology. Remote Sens 2021;13(8). http://dx.doi.org/10.3390/rs13081510.

J. Rojas-Vivanco et al.

Transportation Geotechnics 55 (2025) 101701

[37] Matsimbe FNB, Michael A, Choi YT. Explainable machine learning model for ballast condition assessment using ground penetrating radar scans. In: International conference on civil, structural and transportation engineering. vol. 21, 2024, http://dx.doi.org/10.11159/iccste24.146, no. 146.
[38] Alzarrad A, Wise C, Chattopadhyay A, Chowdhury S, Cisko A, Beasley J. Railroad infrastructure management: A novel tool for automatic interpretation of GPR imaging to minimize human intervention in railroad inspection. CivilEng 2024;5(2):378-94. http://dx.doi.org/10.3390/civileng5020019.
[39] Birhane FNea. Explainable machine learning model for ballast assessment using GPR. CivilEng 2024;5:388-404.
[40] Liu G, Peng Z, Jing G, Wang S, Li Y, Guo Y. Railway ballast layer inspection with different GPR antennas and frequencies. Transp Geotech 2022;36:100823. http://dx.doi.org/10.1016/j.trgeo.2022.100823.
[41] Li B, Guo L, Peng Z, Wang S, Liu G, Li Y. FDTD analysis of ballast fouling status using PFC with discrete random medium model. J Appl Geophys 2025;233:105605. http://dx.doi.org/10.1016/j.jappgeo.2024.105605.

[42] Rojas-Vivanco J. Developpement d'indicateurs de performance pour le diagnostic geotechnique des voies ferrees par l'integration de sources de donnees multiples (Ph.D. thesis), Clermont-Ferrand, France: Clermont Auvergne University; 2025.
[43] Daniels D. Ground penetrating radar. 2005, http://dx.doi.org/10.1002/0471654507.eme152.
[44] Braun B, Ewins L, Rao P. Signal processing for ground penetrating radar. In: Proceedings of the 2001 IEEE international conference on acoustics, speech, and signal processing. ICASSP, vol. 5, 2001, p. 3013-6.
[45] Feldman M. Hilbert transform in vibration analysis. Mech Syst Signal Process 2011;25(3):735-802. http://dx.doi.org/10.1016/j.ymssp.2010.07.018.
[46] Silvast M, Levomäki M, Nurmikolu A, Noukka J. NDT techniques in railway structure analysis. In: Proceedings of the 7th world congress on railway research, montreal, Canada. 2006, p. 12, [Online]. Available: https://researchportal.tuni.fi/en/publications/ndt-techniques-in-railway-structure-analysis,
[47] Rojas Vivanco J, Breul P, Talon A, Benz Navarre M, Barbier S, Ranvier F. Application of data fusion to determine the geotechnical model of the substructure. 5th Int Conf Transp Geotech 2024. http://dx.doi.org/10.1007/978-981-97-8213-0_22, URL https://link.springer.com/chapter/10.1007/978-981-97-8213-0_22.