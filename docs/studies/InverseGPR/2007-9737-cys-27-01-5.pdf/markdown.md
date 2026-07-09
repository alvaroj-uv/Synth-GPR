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

ISSN 2007-9737

6 Kazizat Iskakov, Dinara Tokseit, Samat Boranbaev, et al.

![img-0.jpeg](img-0.jpeg)

Fig. 1. Measurement scheme

This method consists in comparing the obtained radarograms with the standard views available in the database. There is a different direction of radarogram interpretation, namely computer modelling of propagation and reflection of electromagnetic waves in a medium.

The radarogram provides information about the travel time to the heterogeneity, and the task of interpreting radarograms is to determine the physical characteristics of the heterogeneity.

In GPR studies, the measurement data obtained by the GPR antenna is a response of the medium and is a function of travel time. This data is then used as additional information to solve inverse coefficient problems.

To numerically solve this kind of inverse problem, we apply an optimization method, the essence of which is minimization of the quadratic functional of inconsistency of calculated and observed fields (data from the receiving antenna of GPR).

In computer simulations, to solve the inverse coefficient problem, a tabular value of the perturbation source as well as tabular values of the reflected signals at the measurement points are needed.

In order to solve these issues, we have developed a source reconstruction algorithm in this paper. The physical characteristics of the investigated objects include: dielectric and magnetic permeability and conductivity of media.

The issues of numerical method for solving inverse coefficient problems for the geoelectric equation are discussed in the monograph by S. I. Kabanikhin [10].

Application of optimization methods for numerical solution of a class of coefficient inverse problems is presented in the monograph by K.T. Iskakov et al. [8].

The use of engineering methods for interpreting radarograms, the essence of which consists in determining the geoelectric section: dielectric and magnetic permeability; conductivity and depth of heterogeneity are considered in a series of works [24, 20, 23, 12].

The method of layer-by-layer recalculation, for inverse problems in the case of layered media, is widely used.

The idea of layer-by-layer recalculation is that the differential equation describing this process is reduced to Riccati differential equation by special function substitution, for which the solution can be written out in analytical form [15].

The theoretical foundations and practical applications of subsurface georadolocation are outlined in [2, 16, 6, 3, 9, 4].

The theory of uncorrected and inverse problems received a rapid development in the 20th century and goes back to the first works in this direction by academician A.N. Tikhonov [18].

The theoretical aspects and numerical methods for solving inverse coefficient problems for the geoelectric equation are devoted to a monograph by V.G. Romanov and S.I. Kabanikhin [17].

The application of optimization methods for the numerical solution of the coefficient inverse and its theoretical justifications are given in the monograph by S.I. Kabanikhin and K.T. Iskakov. [11].

One of the first algorithms of layer-by-layer recalculation for solving a second-order differential equation for a horizontally layered homogeneous medium is described in the work by A.N. Tikhonov and D.N. Shakhsuvarov. [19].

For solving the practical task of electrical prospecting, this algorithm was used in the work by Dmitriev V.I. [5]. In works of Karchevsky A.L. [13, 14] described an algorithm of solution of seismic task for a horizontally layered medium,

Computación y Sistemas, Vol. 27, No. 1, 2023, pp. 5–12
doi: 10.13053/CyS-27-1-4543

ISSN 2007-9737

Computer Modeling of the Outgoing GPR Signal

7

and in [14] this technique is applied to Maxwell equations in case of horizontally layered medium of any anisotropy. The above-mentioned studies of direct and inverse problems of electrical prospecting refer to a series of problems when observations are carried out on the daytime surface of plane-parallel media.

If the surface has a relief, for example, in archaeological problems of investigation of barrows, then considering the influence of relief of the surface on the electric field and on the results of 2D and 3D inversion of electric tomography (ET) survey data is an important task.

In [25] the effectiveness of elimination of topographical effects in 2D inversion programs that include topography in the grid in the presence of daylight surface topography has been studied. Modeling of the apparent resistivity curves has been performed by the method of integral equations.

Experimental studies were carried out on the laboratory polygon using Loza-V GPR. Real data are used for numerical calculations to determine the shape and tabular value of the emitted signal.

The work also uses the methodology for signal cleaning from noise and interference and signal recovery given in papers [7, 22].

## 2 Mathematical Model for Source Recovery

The propagation of electromagnetic waves in a medium is described by a system of Maxwell's equations [17].

With a special choice of a perturbation source, namely if the source is a long cable located along the coordinate axis and assuming that the functions describing the geoelectric section depend on one variable, namely the depth, then the system of Maxwell equations is simplified and we have a formulation problem for the geoelectric equation [17].

This model is suitable for the study of direct and inverse problems in the case of slime media.

Let us consider the geoelectric equation in cylindrical coordinate system:

$$\varepsilon w_{tt} + \sigma w_t = \frac{1}{\mu} \left( w_{rr} + \frac{1}{r} w_r + w_{zz} \right) + \frac{1}{r} \delta(r) \delta(z - z_*) q(t). \tag{1}$$

The initial conditions are of the form:

$$w(r, z, 0) = 0, \ w_t(r, z, 0) = 0. \tag{2}$$

Assume that $\frac{\partial w}{\partial r}$ is bounded at $r \to 0$. Let the following relation take place:

$$u(\xi, z, \omega) = \int_{-\infty}^{\infty} e^{i\omega t} \int_{0}^{\infty} w(r, z, t) r J_0(\xi r) dr dt. \tag{3}$$

Then, task (1)-(2) will take the form:

$$u_{zz} - b^2(z) u = \delta(z - z_*) \hat{q}(\omega), \tag{4}$$

$$[u_z]_{z=0} = 0, [u]_{z=0} = 0. \tag{5}$$

Let us use the definition of the generalized derivative: $u_z = \{u_z\} + [u]_{z*} \delta(z - z_*)$, in order to transfer the right-hand side of equation (4) to the boundary condition, then finally write problem (4)-(5), differently:

$$u_{zz} - b^2(z) u = 0, \tag{6}$$

$$[u_z]_{z_*=0} = 0, [u]_{z_*=0} = 0, \tag{7}$$

$$u[z]_{z=z_*} = \hat{q}(\omega), [u]_{z=z_*} = 0. \tag{8}$$

Using standard techniques, by analogy as in [13, 14], let us go to the Riccati equation, in order to derive an analytical solution, we have:

$$u_z = yu \Rightarrow y' + y^2 = b^2, \tag{9}$$

$$z \in (-\infty, z_*), z \in [0, \infty), \tag{10}$$

$$y(z) = b_0, \tag{11}$$

$$y(z) = -b_1 = y^0. \tag{12}$$

Computación y Sistemas, Vol. 27, No. 1, 2023, pp. 5–12

doi: 10.13053/CyS-27-1-4543

ISSN 2007-9737

8 Kazizat Iskakov, Dinara Tokseit, Samat Boranbaev, et al.

Let us calculate:

$$y ^ { * } = b _ { 0 } \frac { \left( y ^ { 0 } + b _ { 0 } \right) e ^ { 2 b _ { 0 } z _ { * } } + \left( y ^ { 0 } - b ^ { 0 } \right) } { \left( y ^ { 0 } + b _ { 0 } \right) e ^ { 2 b _ { 0 } z _ { * } } - \left( y ^ { 0 } - b ^ { 0 } \right) } , \tag { 1 3 }$$

$$u | _ { z = z _ { * } + 0 } y ^ { * } - u | _ { z = z _ { * } - 0 } b _ { 0 } = \hat { q } ( \omega ) , \tag { 1 4 }$$

$$u | _ { z = z _ { * } + 0 } - u | _ { z = z _ { * } - 0 } = 0 , \tag { 1 5 }$$

$$u ^ { * } = \frac { \hat { q } ( \omega ) } { y ^ { * } - b _ { 0 } } , \tag { 1 6 }$$

$$u ( 0 ) = \frac { 2 b _ { 0 } e ^ { b _ { 0 } z _ { * } } } { \left( y ^ { 0 } + b _ { 0 } \right) e ^ { 2 b _ { 0 } z _ { * } } - \left( y ^ { 0 } - b _ { 0 } \right) } * \frac { \hat { q } ( \omega ) } { y ^ { * } - b _ { 0 } } . \tag { 1 7 }$$

Let:

$$z _ { * } \rightarrow 0 \Rightarrow y ^ { * } = y ^ { 0 } = - b _ { 1 } , \tag { 1 8 }$$

$$u ( \xi , 0 , \omega ) = \frac { \hat { q } ( \omega ) } { b _ { 1 } + b _ { 0 } } . \tag { 1 9 }$$

And we finally get it:

$$u ( r _ { 0 } , 0 , \omega ) = \hat { q } ( \omega ) \tag { 2 0 }$$

$$\int _ { 0 } ^ { \infty } \frac { \xi J _ { 0 } ( \xi r _ { 0 } ) } { \sqrt { \xi ^ { 2 } - ( \omega ^ { 2 } \mu _ { 0 } \varepsilon _ { 1 } - i \omega \mu _ { 0 } \sigma _ { 1 } ) } + \sqrt { \xi ^ { 2 } - \omega ^ { 2 } \mu _ { 0 } \varepsilon _ { 0 } } } d \xi .$$

Thus, gathering all the calculations, let's describe the solution scheme for source recovery in steps:

1. Let GPR data be known - response of the medium in a homogeneous medium: $w ( r _ { 0 } , 0 , t )$ - real radar data at the measurement point, where $r _ { 0 }$ is the distance of the antenna location from the source. The source power is on the order of 200 kHz.
2. Let us determine the spectrum, function $w ( r _ { 0 } , 0 , t )$ based on the Fourier transform, we obtain $S ( r _ { 0 } , 0 , \omega )$. Solving the Riccati equation analytically, we have:

$$S ( r _ { 0 } , 0 , \omega ) = \tag { 2 1 }$$

$$\hat { q } ( \omega ) \int _ { 0 } ^ { \infty } \frac { \xi J _ { 0 } ( \xi r _ { 0 } ) } { \sqrt { \xi ^ { 2 } - ( \omega ^ { 2 } \mu _ { 0 } \varepsilon _ { 1 } - i \omega \mu _ { 0 } \sigma _ { 1 } ) } + R } d \xi ,$$

where: $R = \sqrt { \xi ^ { 2 } - \omega ^ { 2 } \mu _ { 0 } \varepsilon _ { 0 } }$.

3. By numerically calculating the integral on the right-hand side of formula (2), we obtain that the value of the source in the frequency domain is finally calculated according to the formula:

$$\hat { q } ( \omega ) = - \frac { S ( r _ { 0 } , 0 , \omega ) } { I } , \tag { 2 2 }$$

where I is the approximate value of the integral.

4. The source value in the frequency domain $\hat { q } ( \omega )$ (22) consists of technical and computational errors that result from the averaging of the signal during gating and the conversion of the signal from analog to digital.

To clean the signals from noise and interference, wavelet transform and Harr, Dobesh filters are applied by analogy as in [7]. Translation of signals from binary to another format.

5. We construct a calibration function $\hat { F } ( \omega ; \alpha , \omega _ { 0 } )$, using the theory of uniform function approximation.

6. Let the calibration function $\hat { F } ( \omega ; \alpha , \omega _ { 0 } )$ have the form:

$$\hat { F } ( t ) = e ^ { - \alpha t } \cos ( \omega _ { 0 } t ) . \tag { 2 3 }$$

7. Based on the Fourier transform, we get:

$$\hat { F } ( \omega ; \alpha , \omega _ { 0 } ) = \frac { \alpha - \mathrm { i } ( \omega - \omega _ { 0 } ) } { \alpha ^ { 2 } + ( \omega - \omega _ { 0 } ) ^ { 2 } } . \tag { 2 4 }$$

8. To find the unknown parameters $\alpha , \omega _ { 0 }$ consider the quadratic deviation:

$$\psi = \sum _ { \omega } \left| \hat { q } ( \omega ) - \hat { F } ( \omega ; \alpha , \omega _ { 0 } ) \right| ^ { 2 } , \underline { { { \omega } } } \leq \omega \leq \overline { { { \omega } } } , \tag { 2 5 }$$

where the values of $\underline { { { \omega } } } , \overline { { { \omega } } }$ depend on the radar characteristics.

9. Calculating the derivatives needed to minimise the quadratic deviation (25), we obtain:

$$\psi = \sum _ { \omega } \left[ \hat { q } ^ { r } + i \hat { q } ^ { s } - \hat { F } \right] ^ { 2 } = \tag { 2 6 }$$

$$\sum _ { \omega } \left\{ \left[ \hat { q } ^ { r } - \frac { \alpha } { \alpha ^ { 2 } + ( \omega - \omega _ { 0 } ) ^ { 2 } } \right] ^ { 2 } + \left[ \hat { q } ^ { s } + \frac { \omega - \omega _ { 0 } } { \alpha ^ { 2 } + ( \omega - \omega _ { 0 } ) ^ { 2 } } \right] ^ { 2 } \right\} .$$

Computación y Sistemas, Vol. 27, No. 1, 2023, pp. 5–12
doi: 10.13053/CyS-27-1-4543

ISSN 2007-9737

Computer Modeling of the Outgoing GPR Signal 9

Let us define the following variables in order to make the following expressions easier to understand:

$$A = \hat{q}^r - \frac{\alpha}{\alpha^2 - (\omega - \omega_0)^2}, \quad (27)$$

$$B = \frac{(-1)(\alpha^2 + (\omega - \omega_0)^2) - 2\alpha^2}{(\alpha^2 - (\omega - \omega_0)^2)^2}, \quad (28)$$

$$C = \frac{-(\omega - \omega_0)2\alpha}{[\alpha^2 + (\omega - \omega_0)^2]^2}, \quad (29)$$

$$D = \frac{\alpha[2(\omega - \omega_0)]}{(\alpha^2 + (\omega - \omega_0)^2)^2}, \quad (30)$$

$$K = \hat{q}^i + \frac{\omega - \omega_0}{\alpha^2 + (\omega - \omega_0)^2}, \quad (31)$$

$$N = \frac{(-1)[\alpha^2 + (\omega - \omega_0)^2] + (\omega - \omega_0)^2}{[\alpha^2 + (\omega - \omega_0)^2]^2}. \quad (32)$$

With these definitions in place, we can proceed with the following:

$$\frac{\partial \psi}{\partial \alpha} = \sum_{\omega} \left\{ 2AB + 2 \left[ + \frac{\omega - \omega_0}{\alpha^2 + (\omega - \omega_0)^2} \right] C \right\}, \quad (33)$$

$$\frac{\partial \psi}{\partial \omega_0} = \sum_{\omega} \{ 2[A]D + 2[K]N \}. \quad (34)$$

Apply the method of conjugate gradients [17]:

$$\left[ \begin{array}{c} \alpha \\ \omega_0 \end{array} \right]^{k+1} = \left[ \begin{array}{c} \alpha \\ \omega_0 \end{array} \right]^k - \gamma_k P_k. \quad (35)$$

Here $P_k = \nabla \psi [\alpha^k, \omega_0^k] - \beta_k P_{k-1}$:

$$\nabla \psi = \left[ \begin{array}{c} \frac{\partial \psi}{\partial \alpha} \\ \frac{\partial \psi}{\partial \omega_0} \end{array} \right], \quad (36)$$

$$\beta_k = - \frac{\left| \left| \nabla \psi [\alpha^k, \omega_0^k] \right| \right|^2}{\left| \left| \nabla \psi [\alpha^{k-1}, \omega_0^{k-1}] \right| \right|^2}. \quad (37)$$

10. The next approximations $\alpha^{k+1}, \omega_0^{k+1}$ will be calculated using conjugate gradient formulas (35)-(37).

![img-1.jpeg](img-1.jpeg)

Fig. 2. Radarogram trace plot. (The antenna is positioned from the source at a distance of - 1 metre)

![img-2.jpeg](img-2.jpeg)

Fig. 3. Spectrum of the radarogram trace. (The antenna is located at a distance of 1 metre)

11. As a result of the calibration, the final original source is as follows:

$$F(t) = e^{-\alpha^* t} \cos(\omega_0^* t), \quad (38)$$

where: $\alpha^*, \omega_0^*$ are the found values for which the functional (25), reached a minimum.

The found value of the source, can be used to solve the forward problem, and the inverse problem of determining the dielectric permittivity and conductivity of the media.

Computación y Sistemas, Vol. 27, No. 1, 2023, pp. 5-12
doi: 10.13053/CyS-27-1-4543

ISSN 2007-9737

10 Kazizat Iskakov, Dinara Tokseit, Samat Boranbaev, et al.

![img-3.jpeg](img-3.jpeg)

Fig. 4. Source spectrum graph. (The antenna is located at a distance of - 1 metre)

### 3 Experimental Results

Experimental studies on reception of reflected signals from a homogeneous site (river sand) were carried out. The experiment was carried out with a Loza-V series GPR, with antenna sweep: 100 cm.

Research task: geophysical investigation of homogeneous clean sand underlayer structure: simulation of pulse source from "Loza-V" series device; determination of spectral characteristics of signals emitted by the antenna.

Calculation of the source signal in tabular form, are necessary in the future for solving inverse coefficient problems in determining the geoelectric section. A homogeneous section, river sand, measuring 8 metres in width and in length, was chosen for the experiments.

An experiment was carried out in which the GPR source was placed at point B0 and the antenna was placed at a distance of 1 metre and is shown in Fig. 1. Trace plots, i.e. the response of the medium is shown in Fig. 2.

The actual radarogram data, which has its own format, has been converted into a text format of tabulated signal values. Signals received from Loza-V series GPR are output in "geo" format. For signal analysis and visualization we convert from the binary format of the file "geo" in the format "txt".

File "txt" consists of three columns: x, t, alg. Where: x - number of data received from each observation point, by default x=0 ... 10; T - time, T0=0 ns, T512=255,5 ns, step 0.5 ns; Alg - amplitude values.

To encode the amplitude value of an analogue signal, an 8 or 16 bit representation of the amplitude values is used.

In the case of 8-bit encoding, the amplitude measurements of the analogue signal will be obtained with an accuracy of 1/256 of the dynamic range of the digital device, since 8 bits allow 28 numbers to be represented-256).

The digital signal in this encoding is then a set of numbers from 0 to 255 (or -128 to 127). This accuracy is not sufficient to reconstruct the original signal because there will be errors of non-linear distortion.

If you encode the amplitude of the analogue signal to 16 bits, you will have 265 times the accuracy. Digit capacity of 16 bits allows to encode 216=65536 values of amplitude.

A digital signal is then a collection of numbers from 0 to 65535 (or -32768 to 32767). This coding approach keeps nonlinear distortion to a minimum. A digital signal is a dimensionless set of numbers and has no common units of measurement.

The radarogram data, which has its own format, is converted into a text format of tabulated signal values. Fig. 2 shows a graphical representation of the response.

### 4 Related Work

The spectrum of the radarogram trace (medium response), is shown in Fig. 3. The frequency scale of the graph varies from 0 to 1000MHz.

The modulus of the frequency distribution of the signal $u(r_0, 0, \omega)$ can be seen in Fig. 3. Having the radarogram trace spectra, using equation (2.) we have:

$$\int_{0}^{\infty} \frac{u(r_0, 0, \omega_i) = \hat{q}(\omega_i)}{\sqrt{\xi^2 - (\omega_i \mu_0 \varepsilon_1 - i \omega_i \mu_0 \sigma_1)} + \sqrt{\xi^2 - \omega_i^2 \mu_0 \varepsilon_0}} d\xi. \tag{39}$$

Computación y Sistemas, Vol. 27, No. 1, 2023, pp. 5–12
doi: 10.13053/CyS-27-1-4543

ISSN 2007-9737

Computer Modeling of the Outgoing GPR Signal 11

For $i = 1, 2, 3, \dots, n/2$. Let us represent the integral of the complex function in equation (39) as:

$$\int_0^\infty \frac{\xi J_0(\xi r_0)}{\sqrt{\xi^2 - (\omega^2 \mu_0 \varepsilon_1 - i \omega \mu_0 \sigma_1)} + \sqrt{\xi^2 - \omega^2 \mu_0 \varepsilon_0}} d\xi$$
$$= \int_0^\infty (p(\xi) + iq(\xi)) d\xi = \int_0^\infty f(\xi) d\xi. \quad (40)$$

The numerical calculation of the integral (40) is realised by the iterative rectangular (or trapezoidal) method:

$$\int_0^\infty f(\xi) b\xi \approx h \sum_{j=0}^\infty f(\xi_j). \quad (41)$$

The summation is carried out to a given accuracy $\varepsilon$:

$$|f(\xi_j)| < \varepsilon.$$

The following parameters were used in the calculation: $\varepsilon_0 = 1$, $\varepsilon_1 = 5$, $\mu_0 = 1$, $r_0 = 1$, $\sigma_1 = 1/500$. The graph of the source spectrum is shown in Fig 4.

By inverse Fourier transform of the spectrum $q(\omega)$ we find the absolute (complex) source signal. The plot of the real part of the source signal, in the case of our experiment is shown in Fig. 5.

Fig. 5 below shows a graph of the reconstructed source, when the antenna is located at a distance of 1 metre from the source.

A certificate of authorship No 31827 dated "17" January 2023 [21] was received for GPR signal source detection program.

## 5 Conclusion

We considered a computer model to reconstruct the shape and tabular value of the source on the basis of real data of signals from the Loza-V series GPR receiver.

As a result of strictly justified mathematical calculations, we obtained an explicit expression linking the spectrum function describing the response of the medium (real radar data) and the spectrum function describing the source behavior.

Based on the found source spectrum on the basis of inverse Fourier transform, the emitted

![img-4.jpeg](img-4.jpeg)

Fig. 5. Graph of the recovered signal source, from experiment

GPR source itself is reconstructed in tabular form and its graphical representation.

The results of researches of this article can be applied to numerical solution of inverse coefficient problems, as it is necessary to have a tabular value of the source of disturbance, as well as tabular values of reflected signals (GPR data), in the points of measurements.

A series of numerical calculations were carried out to show the effectiveness of the considered computer model on source recovery.

## References

1. Aleksandrov, P. N. (2017). Theoretical foundations of the GPR method. Editorial de Literatura de Física y Matemáticas de Moscú.
2. Andriyanov, A. V. (2005). Issues of subsurface radiolocation. Collective monograph, Moscow: Radiotekhnika, pp. 416.
3. Conyers, L. B., Goodman, D. (1997). Ground-penetrating radar: An introduction for archaeologists. AltaMira press.
4. Daniels, D. J. (2004). Ground penetrating radar. The Institution of Electrical Engineers, London, UK. DOI: 10.1049/PBRA015E.

Computación y Sistemas, Vol. 27, No. 1, 2023, pp. 5–12
doi: 10.13053/CyS-27-1-4543

ISSN 2007-9737

12 Kazizat Iskakov, Dinara Tokseit, Samat Boranbaev, et al.

5. Dmitriev, V. (1968). General method of electromagnetic field calculation in layered medium. Computational Methods and Programming, Vol. 10, pp. 55–65.
6. Finkelstein, M. I., Karpukhin, V. I., Kutev, V. A., Metelkin, V. N. (2017). Subsurface radiolocation. Moscow, Radio and Communications, pp. 216.
7. Iskakov, K. T., Boranbaev, S. A., Uzakkyzy, N. (2017). Wavelet processing and filtering of the radargram trace. Eurasian Journal of Mathematical and Computer Applications, Vol. 5, No. 4, pp. 43–54. DOI: 10.32523/2306-3172-2017-5-4-43-54.
8. Iskakov, K. T., Romanov, V. G., Karchevsky, A. L., Oralbekova, J. O. (2014). Research of inverse problems for differential equations and numerical methods of their solution. L.N. Gumilev Eurasian National University Press.
9. Jol, H. M. (2009). Ground penetrating radar. Theory and applications, Elsevier sciences, pp. 524.
10. Kabanikhin, S. I. (2018). Inverse and uncorrected problems. Siberian Scientific Publishing House, pp. 511.
11. Kabanikhin, S. I., Iskakov, K. T. (2001). Optimization method of the solution of coefficient inverse problems. Novosibirsk State University.
12. Kabanikhin, S. I., Iskakov, K. T., Sholpanbaev, B., Shishlenin, M. A., Tokseit, D. K. (2018). Development of a mathematical model for signal processing using laboratory data. Bulletin of the Karaganda university-mathematics, Vol. 92, No. 4, pp. 148–157.
13. Karchevsky, A. L. (2005). The direct dynamic seismic problem for horizontally layered media. Siberian Electronic Mathematical Proceedings, Vol. 2, pp. 23–61.
14. Karchevsky, A. L. (2007). Analytical solution of maxwell equations in the frequency domain for horizontally layered anisotropic media. Geology and Geophysics, Vol. 48, No. 8, pp. 689–695. DOI: 10.1016/j.rgg.2006.08.005.
15. Karchevsky, L., Andrey (2020). Analytical solutions to the differential equation of transverse vibrations of a piecewise homogeneous beam in the frequency domain for the boundary conditions of various types. Journal of Applied and Industrial Mathematics, Vol. 14, pp. 648–665. DOI: 10.1134/S1990478920040043.
16. Kopeikin, V. V. (2007). Wave refraction in linear media with frequency dispersion. M:Nauka.
17. Romanov, V. G., Kabanikhin, S. I. (1991). Inverse Problems of Geoelectrics. Nauka.
18. Tikhonov, A. N., Arsenin, V. I. (1977). Solutions of Ill-posed Problems. Wiley.
19. Tikhonov, A. N., Shakhsuvarov, D. N. (1956). Method for calculation of electromagnetic fields excited by alternating current in layered media. Izv. AN SSSR, Geofizika, Vol. 3, pp. 251–254.
20. Tokseit, D. K., Boranbaev, S. A., Oralbekova, J., Nurzhanova, A. B. (2020). Determination of the geoelectric section by georadar data. Bulletin of D.Serikbayev East Kazakhstan State Technical University, Vol. 89, No. 3, pp. 154–160.
21. Tokseit, D. K., Iskakov, K., Boranbayev, S. A. (2023). GPR signal source identification software. Certificate of Record in the State Register of Rights to objects protected by copyright, No 9319, pp. 1.
22. Tokseit, D. K., Iskakov, K. T., Boranbaev, S. A. (2022). Techniques for processing source signals emitted by GPR. Universitet Enbekteri – University Proceedings, Vol. 86, No. 1, pp. 323–333.
23. Tokseit, D. K., Iskakov, K. T., Boranbayev, S. A., Shishlenin, M. A. (2020). Interpretation of radargrams of geological section based on experimental calculation formulas. Certificate of Record in the State Register of Rights to objects protected by copyright, No 9319, pp. 1.
24. Tokseit, D. K., Iskakov, K. T., Kabanikhin, S. I., Shishlenin, M. A. (2020). Program for calculating a mathematical model for determining the response of the medium and detecting heterogeneity. Certificate of Record in the State Register of Rights to objects protected by copyright, No 12894, pp. 1.
25. Turarova, M. K., Mirgalikyzy, T., Mukanova, B., Modin, I. N. (2022). Elimination of the ground surface topographic effect in the 2D inversion results of electrical resistivity tomography data. Eurasian Journal of Mathematical and Computer Applications, Vol. 10, No. 3, pp. 84–104.

Article received on 08/11/2022; accepted on 12/01/2023.
Corresponding author is Irina Gelbukh.

Computación y Sistemas, Vol. 27, No. 1, 2023, pp. 5–12
doi: 10.13053/CyS-27-1-4543