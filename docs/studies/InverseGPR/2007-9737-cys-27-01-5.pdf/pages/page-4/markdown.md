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