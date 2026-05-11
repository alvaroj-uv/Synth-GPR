IEEE GEOSCIENCE AND REMOTE SENSING LETTERS, VOL. 22, 2025

3500604

# FDTD Medium Dimension Selection Guidelines for GPR Synthetic Data Generation

Noushin Khosravi Largani $^{\text{©}}$ , Graduate Student Member, IEEE, Seyed Zekavat $^{\text{©}}$ , Senior Member, IEEE, and Himan Namdari $^{\text{©}}$

Abstract—Ground-penetrating radar (GPR) has been traditionally used for subsurface assessment. In many applications, such as precision agriculture via drone-borne radar, it is critical to use machine learning (ML) techniques to map GPR received signals into soil subsurface moisture and texture. Supervised ML methods need a large number of labeled data for their training process which is expensive and time-consuming to attain through actual field measurements. The gprMax software, which is created based on the finite difference time domain (FDTD) method, has been introduced as a reliable tool to emulate soil media and create synthetic labeled data. Proper selection of gprMax soil medium dimensions is critical to the generation of reliable synthetic data. The selection of large soil medium dimensions for gprMax emulations leads to synthetic data consistent with realistic scenarios. However, larger medium dimensions lead to higher computation complexity. This letter investigates and validates a proper selection of medium dimensions that maintains a tradeoff across the accuracy and computational complexity of creating synthetic data. The results of this study are critical to researchers who adopt gprMax or any FDTD-oriented emulations for soil subsurface assessment. To maintain a tradeoff between accuracy and complexity, the letter confirms that the minimum medium surface dimension should be in the order of 1.5 times the maximum wavelength.

Index Terms—Emulation, finite difference time domain (FDTD), ground-penetrating radar (GPR), impulse response, medium dimension, soil.

# I. INTRODUCTION

SoIL subsurface investigation is key to hydrological studies, environmental monitoring, and precision agriculture [1], [2], [3]. Ground-penetrating radar (GPR) is a conventional tool for soil subsurface assessment. GPR transmits electromagnetic waves toward the ground to characterize soil subsurface based on the received signal [2], [4]. Traditional GPR signal processing methods are complex, and thus it is hard to leverage them for subsurface assessment of a large area such as a megafarm [5], [6]. Machine learning (ML) can be considered as an effective approach for (real-time) subsurface assessment of large areas. However, supervised

Received 23 September 2024; revised 6 November 2024; accepted 20 November 2024. Date of publication 4 December 2024; date of current version 17 December 2024. This work was supported by United States Department of Agriculture under Grant USDA NR223A750013G032. (Corresponding author: Noushin Khosravi Largani.)

The authors are with the Data Science Department of Worcester Polytechnic Institute, Worcester, MA 01609 USA (e-mail: nlargani@wpi.edu; rezaz@wpi.edu).

Digital Object Identifier 10.1109/LGRS.2024.3510683

![img-0.jpeg](img-0.jpeg)
Fig. 1. Soil medium and its dimensions  $x$ ,  $y$ , and  $z$ .

ML methods need a large number of labeled data that are very difficult to create using real field measurements for GPR applications. gprMax is open-source software that uses the finite difference time domain (FDTD) technique [7] capable of creating a large number of labeled GPR synthetic data.

The soil medium acts as a channel with an impulse response. The soil channel impulse response (CIR) is a key feature that can be used to extract soil subsurface information [4], [8]. Soil CIR contains information about the illuminated soil medium such as permittivity and the number of layers at the frequency of interest. Soil CIR corresponds to

$$
h (t) = \sum_ {l = 1} ^ {L} a _ {l} \delta \left(t - \tau_ {l}\right) \tag {1}
$$

in which  $a_{l}, \tau_{l}$ , and  $L$  indicate channel gains, delays, and the number of multiple reflections. Parameters such as permittivity, conductivity, and depth of the medium determine  $a_{l}$  and  $\tau_{l}$  [4].

The dimensions of a soil medium (i.e.,  $x$ ,  $y$ , and  $z$ ) are shown in Fig. 1, where  $x$  and  $y$  represent the medium surface dimension, and  $z$  refers to the medium depth. If the dimensions of the illuminated medium vary, the soil CIR will change. Thus, dimension alterations impact the accuracy of subsurface feature analysis. As the medium dimensions increase, emulations become more accurate but expensive in terms of time and the required memory.

Setting the medium dimension in FDTD modeling remains an underexplored area in the literature, suggesting a potential area for further research. To train an ML framework estimating rebar's cover depth and diameter, Giannakis et al. [9] and

1558-0571 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.

See https://www.ieee.org/publications/rights/index. for more information.

Authorized licensed use limited to: Pontificia Universidad Catolica de Valparaiso. Downloaded on May 08,2026 at 21:40:54 UTC from IEEE Xplore. Restrictions apply.

IEEE GEOSCIENCE AND REMOTE SENSING LETTERS, VOL. 22, 2025

Patsia et al. [10] generate a large training dataset of emulated GPR signals using gprMax software. However, the authors do not discuss the reason and impact of selecting the medium's dimension. In [11], the CIR of a horizontal layered soil is calculated while a large-size ground medium surface (i.e., $300 \times 300\,\mathrm{m}^2$) for simulation validation is used. Implementing this dimension in complex and detailed models requires significant computational resources.

In this letter, we investigate the adoption of proper medium dimensions $(x, y, \text{and } z)$ for gprMax emulations that support high-precision and low-complexity CIR extraction. To assess the impact of dimensions on gprMax synthetically generated data, we increase the medium dimensions gradually and obtain the corresponding CIR. The Euclidean distance between the extracted CIR channel gains for different consecutive medium dimensions is used as the precision measure. FDTD computation time is considered as the emulation complexity. We select the dimension that facilitates a balance between precision and complexity. The results of this letter can be used as a guideline for researchers who aim to use gprMax (or any FDTD-based synthetic data generation) to emulate soil medium illuminated by GPR signals. The results confirm that a surface dimension consistent with 1.5 times the maximum wavelength leads to acceptable precision and complexity.

The methods for impulse response extraction, the emulation parameter selection, and the verification of minimum surface dimension are explained in Sections II-IV, respectively. The letter concludes in Section V.

## II. IMPULSE RESPONSE EXTRACTION

We use the transmitted and received signals that are created in the time domain by gprMax to extract the CIR of the soil medium that was presented in (1). Some initial components of the received signal correspond to the leakage between the antennas of the transmitter and receiver. To create a CIR that only includes the impact of the soil channel, we need to eliminate the antenna leakage. To eliminate the antenna leakage, we simulate the same setup, excluding the soil medium. The recorded signal in this step shows only the impact of antenna leakage as there is no soil medium to create reflections. Then, we subtract the signal caused by antenna leakage from the received signal. After removing the leakage effect, we obtain the fast Fourier transform (FFT) of the received signal that is expressed as

$$
Y = H X + N \tag{2}
$$

where $Y$, $H$, $X$, and $N$ denote the Fourier transform of the received signal, CIR, transmitted signal, and noise, respectively. The CIR in the frequency domain is represented by $H = (Y / X)$ [4]. The CIR in the time domain $(h(t))$ is obtained using inverse FFT (IFFT). The whole process has been detailed in Fig. 2. To elucidate the whole process, the example of normalized transmitted and received signals, FFT of the received signal, and CIR are depicted in Fig. 3.

## III. EMULATION PARAMETER SELECTION

We considered a single-layer medium as shown in Fig. 1, for our emulations. Based on studies conducted in [12], [13],

![img-1.jpeg](img-1.jpeg)
Fig. 2. Flowchart of extracting soil CIR.

![img-2.jpeg](img-2.jpeg)

![img-3.jpeg](img-3.jpeg)

![img-4.jpeg](img-4.jpeg)
Fig. 3. (a) Example of normalized transmitted and received signals, (b) FFT of the received signal, and (c) CIR.

and [14], we have selected the following pairs for soil medium permittivity $(\epsilon)$ and conductivity $[\sigma\,(\mathrm{mS/m})]$:

$$
\begin{array}{l}
(\epsilon, \sigma) = (4, 1), (8, 80), (38, 80), \\
(38, 20), (20, 1), (15, 120), (25, 200). \tag{3}
\end{array}
$$

We select Ricker for medium illumination as this waveform is widely used for GPR inspections and emulates pulses of real GPR systems. The center frequency $(f_c)$ of Ricker is set to $825\,\mathrm{MHz}$. The minimum $(f_{\mathrm{min}})$ and maximum $(f_{\mathrm{max}})$

Authorized licensed use limited to: Pontificia Universidad Catolica de Valparaiso. Downloaded on May 08,2026 at 21:40:54 UTC from IEEE Xplore. Restrictions apply.

KHOSRAVI LARGANI et al.: FDTD MEDIUM DIMENSION SELECTION GUIDELINES FOR GPR SYNTHETIC DATA GENERATION

3500604

TABLE I
PARAMETERS SELECTED FOR EMULATIONS

|  Parameter | Value  |
| --- | --- |
|  Transmitted waveform | Ricker, $f_c = 825$ MHz  |
|  Depth of medium | 20 cm  |
|  Antenna polarization | Y  |
|  Pixel size | 0.001  |
|  Time window | 10⁻⁸ s  |

frequencies of Ricker are derived based on the equations presented in [16], which have the values of 375.168 and 1274.831 MHz, respectively. This frequency range is selected to maintain consistency with the soil Peplinski model, which is valid for frequencies from 300 to 1300 MHz [17]. Adopting any other center frequency for the Ricker waveform moves the frequency range outside of the validity range of the Peplinski model. Therefore, the bandwidth of the transmitted waveform ($f_{\mathrm{max}} - f_{\mathrm{min}}$) is 899.663 MHz, and accordingly, the range resolution is approximately 17 cm. Thus, we set the depth of the illuminated medium to 20 cm (more than the range resolution). We adopt a Hertzian dipole antenna located at the center of the $x-y$ plane with a height of 41 cm from the soil medium surface. The Hertzian dipole antenna is well-suited for qualitative observations, making it suitable for studying the impact of medium size. The selected height is more than $(\lambda_{\mathrm{max}}/2)$, lying within the intermediate-field region of the antenna and providing appropriate output [18]. The dipole antenna's omnidirectional radiation pattern enables it to capture reflections from all the directions. Among various types of dipole antennas, the Hertzian dipole exhibits the broadest pattern size [18], facilitating a more comprehensive medium-scale verification.

The minimum wavelength (23.5 cm) determines the FDTD pixel size in gprMax. The pixel size is set to 0.001 m, based on the rule of thumb condition $\Delta x \leq (\lambda_{\min} / 10)$ [19]. Then, the vertical distance between the antenna and the medium's upper boundary can be calculated by considering a minimum of 20 pixels that is required for gprMax implementation. The surface ($x - y$ plane) dimension of the medium is kept variable to study the proper dimension that maintains a tradeoff between accuracy and time-memory efficiency. Table I summarizes parameter selection.

# IV. GPRMAX MINIMUM SURFACE DIMENSION VERIFICATION

One of the main disadvantages of the FDTD method is its brute-force calculation nature, which causes the memory requirements to scale with the third order of the emulation domain size $O((N)^3)$ and the computation time to scale with the fourth order $O((N)^4)$ [20]. $N$ refers to the number of grid points in a single dimension. Hence, we consider the maximum order (i.e., $N^4$) as the bottleneck of the emulation complexity. We set $x = y$ (because of the pattern of the dipole antenna) starting from 80 to 300 cm with a step size of 20 cm. The channel gains' vector is obtained for each pair of $x$, $y$ based on the process shown in the flowchart of Fig. 2 and (1). This vector is compared with the next $x$, $y$ pair in terms of

![img-5.jpeg](img-5.jpeg)
Fig. 4. Measure and complexity for different $x, y$ dimensions, $d_i = 100$ cm.

![img-6.jpeg](img-6.jpeg)
Fig. 5. Measure for different $x, y$ dimensions, $d_i = 120$ cm.

Euclidean distance to create an error percentage measure that corresponds to

$$
\text{Error Percentage} = \frac{\left\| d_i - d_{i-1} \right\|_2}{\left\| d_{i-1} \right\|_2} \times 100\% \tag{4}
$$

where $d_i$ is the vector of $a_l$ for $i = 100:300$ cm with the step of 20 cm, and $d_{i-1}$ is the vector of $a_l$ for $i = 80:280$ with the step of 20. $\| d_i - d_{i-1} \|_2$ represents the Euclidean distance between $d_i$ and $d_{i-1}$. $\| d_i \|_2$ denotes the $\ell_2$-norm of vector $d_i$.

Fig. 4 shows both the error percentage and the computational complexity ($N^4$). As the error percentage is relatively calculated (between $d_i$ and $d_{i-1}$), the horizontal axis shows the surface dimensions related to $d_i$. Thus, $x = 80$ cm is not represented in Fig. 4. It is observed that the channel gains tend to get closer as $x$ and $y$ dimensions increase. The dimensions $x$, $y = 120$ cm and more can be observed in the values where the Euclidean distance between channel gain vectors ($d_i$ and $d_{i-1}$) is acceptably small, getting better from 120 to 300 cm. In addition, it is shown that the complexity increases with the medium dimension. Based on these curves, we suggest that medium dimensions between 120 and 140 cm lead to low error percentage and complexity.

Fig. 5 is a zoom-in version of Fig. 4 for $d_i$ starting from $i = 120:300$ cm. We have also removed the complexity curve from this figure to allow a focus on values around 120 cm in dimension. It is observed that for different ranges of permittivity and conductivity, the difference between channel gains tends to zero when the dimension size for $x$ and $y$ reaches 300 cm. The observed fluctuations are caused by numerical dispersion in FDTD computations [21].

Authorized licensed use limited to: Pontificia Universidad Catolica de Valparaiso. Downloaded on May 08,2026 at 21:40:54 UTC from IEEE Xplore. Restrictions apply.

IEEE GEOSCIENCE AND REMOTE SENSING LETTERS, VOL. 22, 2025

The maximum and minimum practical values for soil permittivity (38 and 4) and conductivity (200 and 1) adopted in (3) create a broader perspective for selecting an appropriate dimension. Permittivity directly affects the wavelength and conductivity affects the wave propagation and subsequently the channel gains. To adequately represent the wave's characteristics and to minimize boundary effects, the medium dimensions should be selected much higher (e.g., $5\lambda_{\mathrm{max}}$) than the maximum wavelength *[20]*. However, the implementation of gprMax using $5\lambda_{\mathrm{max}}$ dimension is computationally expensive in terms of time and memory. Thus, based on Figs. 4 and 5, we adopt a dimension of $1.5\lambda_{\mathrm{max}}$, that is a compromise across precision and computation cost.

## V Conclusion

This letter studies the minimum acceptable medium dimensions to maintain proper precision and complexity using gprMax. Emulations are conducted for a wide range of soil electric features, i.e., permittivity and conductivity values. To maintain a tradeoff between accuracy and complexity for different soil features, the letter confirms that the minimum medium surface dimension should be in the order of $1.5\lambda_{\mathrm{max}}$.

## References

- [1] V. Filardi et al., “Data-driven soil water content estimation at multiple depths using SFCW GPR,” in *Proc. IEEE Int. Opportunity Res. Scholars Symp. (ORSS)*, Apr. 2023, pp. 86–90.
- [2] H. Namdari, M. Moradikia, R. Askari, O. Mangoubi, D. Petkie, and S. Zekavat, “Advancing precision agriculture: Machine learning-enhanced GPR analysis for root-zone soil moisture assessment in mega farms,” *IEEE Trans. Agrifood Electron.*, early access, Oct. 4, 2024, doi: 10.1109/TAFE.2024.3455238.
- [3] H. Namdari, M. Moradikia, D. T. Petkie, R. Askari, and S. Zekavat, “Comprehensive GPR signal analysis via descriptive statistics and machine learning,” in *Proc. IEEE Int. Conf. Wireless Space Extreme Environments (WiSEE)*, Sep. 2023, pp. 127–132.
- [4] S. Zheng, X. Pan, A. Zhang, Y. Jiang, and W. Wang, “Estimation of echo amplitude and time delay for OFDM-based ground-penetrating radar,” *IEEE Geosci. Remote Sens. Lett.*, vol. 12, no. 12, pp. 2384–2388, Dec. 2015.
- [5] H. M. Jol, *Ground Penetrating Radar Theory and Applications*. Amsterdam, The Netherlands: Elsevier, 2008.
- [6] L. B. Conyers, *Ground-Penetrating Radar for Archaeology*. Lanham, MD, USA: Rowman, 2023.
- [7] C. Warren, A. Giannopoulos, and I. Giannakis, “GprMax: Open source software to simulate electromagnetic wave propagation for ground penetrating radar,” *Comput. Phys. Commun.*, vol. 209, pp. 163–170, Dec. 2016.
- [8] H. Huh, H. Goh, J. W. Kang, S. François, and L. F. Kallivokas, “Using the impulse–response pile data for soil characterization,” *J. Eng. Mech.*, vol. 149, no. 10, Oct. 2023, Art. no. 04023078.
- [9] I. Giannakis, A. Giannopoulos, and C. Warren, “A machine learning-based fast-forward solver for ground penetrating radar with application to full-waveform inversion,” *IEEE Trans. Geosci. Remote Sens.*, vol. 57, no. 7, pp. 4417–4426, Jul. 2019.
- [10] O. Patsia, A. Giannopoulos, and I. Giannakis, “Full waveform inversion of common offset GPR data using a fast deep learning based forward solver,” in *Proc. 11th Int. Workshop Adv. Ground Penetrating Radar (IWAGPR)*, Dec. 2021, pp. 1–4.
- [11] J. Zou, X. Du, and C. Zhou, “Fast calculation of the green function of a point current source in a horizontal layered soil with a new complex path and its application in grounding system,” *IEEE Trans. Magn.*, vol. 51, no. 3, pp. 1–4, Mar. 2015.
- [12] S. Friedman, “Electrical properties of soils,” in *Encyclopedia of Agrophysics*. Dordrecht, The Netherlands: Springer, 2011, pp. 242–255.
- [13] J. Cihlar and F. T. Ulaby, “Dielectric properties of soils as a function of moisture content,” Univ. Kansas, Lawrence, KS, USA, Tech. Rep. NASA-CR-141868, 1974.
- [14] B. Allred, J. J. Daniels, and M. R. Ehsani, *Handbook of Agricultural Geophysics*. Boca Raton, FL, USA: CRC Press, 2008.
- [15] H. J. Farahani and G. W. Buchleiter, “Practical utility of bulk soil electrical conductivity mapping,” Presented at the 2002 Irrigation Association Conf., USDA Agricult. Res. Service (USDA-ARS), Water Management Research Unit, Fort Collins, CO, USA, 2002.
- [16] Y. Wang, “Frequencies of the Ricker wavelet,” *Geophysics*, vol. 80, no. 2, pp. A31–A37, Mar. 2015.
- [17] N. R. Peplinski, F. T. Ulaby, and M. C. Dobson, “Dielectric properties of soils in the 0.3–1.3-GHz range,” *IEEE Trans. Geosci. Remote Sens.*, vol. 33, no. 3, pp. 803–807, May 1995.
- [18] C. A. Balanis, *Antenna Theory: Analysis and Design*. Hoboken, NJ, USA: Wiley, 2016.
- [19] K. Yee, “Numerical solution of initial boundary value problems involving Maxwell’s equations in isotropic media,” *IEEE Trans. Antennas Propag.*, vol. AP-14, no. 3, pp. 302–307, May 1966.
- [20] A. Taflove and S. C. Hagness, *Computational Electrodynamics: The Finite-Difference Time-Domain Method*, 3rd ed., Norwood, MA, USA: Artech House, 2005.
- [21] B. Finkelstein and R. Kastner, “A comprehensive new methodology for formulating FDTD schemes with controlled order of accuracy and dispersion,” *IEEE Trans. Antennas Propag.*, vol. 56, no. 11, pp. 3516–3525, Nov. 2008.

Authorized licensed use limited to: Pontificia Universidad Catolica de Valparaiso. Downloaded on May 08,2026 at 21:40:54 UTC from IEEE Xplore. Restrictions apply.