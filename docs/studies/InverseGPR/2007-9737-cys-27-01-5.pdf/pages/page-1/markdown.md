ISSN 2007-9737

# Computer Modeling of the Outgoing GPR Signal

Kazizat Iskakov¹, Dinara Tokseit¹, Samat Boranbaev¹,
Iskander Akhmetov², Irina Gelbukh³

¹ Lev Nikolayevich Gumilev Eurasian National University,
Astana,
Kazakhstan

² Institute of Information and Computational Technologies,
Almaty,
Kazakhstan

³ Instituto Politécnico Nacional,
Centro de Investigación en Computación,
Mexico

{tokseit1990, iskander.akhmetov, ir.gelbukh}@gmail.com,
{kazizat, boranbaevsa}@mail.ru

Abstract. This paper considers a mathematical model to reconstruct the shape and tabular value of the source based on real signal data from a Loza-V series GPR receiver. A geoelectric equation in a cylindrical coordinate system is chosen as the mathematical model. Experiments, using GPR, were conducted on a homogeneous area of clean river sand, with known geoelectric properties. In this case, the equation in question is reduced to the Riccati differential equation using a special function substitution. This allowed us to obtain an explicit expression linking the spectrum function describing the response of the medium (the real radar data) and the spectrum function describing the source behavior. From the found source spectra, using inverse Fourier transforms, the emitted source itself is reconstructed in tabular form. The methodology of source reconstruction was carried out at different locations of the receiver antenna from the source antenna. In practice, geophysicists are interested in the physical characteristics of heterogeneity depending on spatial coordinates. For numerical solution of inverse coefficient problem it is necessary to have tabular value of disturbance source and tabular values of reflected signals (GPR data) at measurement points. To solve these problems we have developed an algorithm of source reconstruction and, as a consequence, determination of media response corresponding to real GPR data at the points of observation.

A series of numerical calculations demonstrating the effectiveness of the considered computer model for source recovery have been carried out.

Keywords. GPR, mathematical model, Riccati equations, inverse Fourier transform, experimental studies, radar trace spectrum, source spectrum.

## 1 Introduction

Electromagnetic investigation methods are used: for non-destructive examination of minerals in geology; diagnostics of objects in construction; condition of highways; in archaeological and other natural science tasks. Geophysical equipment is used for experimental research: ground penetrating radar (GPR).

Theoretical provisions and practical description for solution of such a class of tasks – georadar are proposed in [1]. GPRs come with software, the output of this software product is a radarogram.

To interpret radarograms, the essence of which is to determine the geophysical section, physics-based formulas or a fitting method are used.

Computación y Sistemas, Vol. 27, No. 1, 2023, pp. 5–12

doi: 10.13053/CyS-27-1-4543