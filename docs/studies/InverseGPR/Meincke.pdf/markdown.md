Downloaded from orbit.dtu.dk on: jun 30, 2026

DTU Library

# Linear GPR inversion for lossy soil and a planar air-soil interface

Meincke, Peter

Published in:
I E E E Transactions on Geoscience and Remote Sensing

Link to article, DOI:
10.1109/36.975005

Publication date:
2001

Document Version
Publisher's PDF, also known as Version of record

Link back to DTU Orbit

Citation (APA):
Meincke, P. (2001). Linear GPR inversion for lossy soil and a planar air-soil interface. I E E E Transactions on Geoscience and Remote Sensing, 39(12), 2713 - 2721. https://doi.org/10.1109/36.975005

General rights

Copyright and moral rights for the publications made accessible in the public portal are retained by the authors and/or other copyright owners and it is a condition of accessing publications that users recognise and abide by the legal requirements associated with these rights.

- Users may download and print one copy of any publication from the public portal for the purpose of private study or research.
- You may not further distribute the material or use it for any profit-making activity or commercial gain
- You may freely distribute the URL identifying the publication in the public portal

If you believe that this document breaches copyright please contact us providing details, and we will remove access to the work immediately and investigate your claim.

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 39, NO. 12, DECEMBER 2001

2713

# Linear GPR Inversion for Lossy Soil and a Planar Air–Soil Interface

Peter Meincke

**Abstract**—A three-dimensional (3-D) inversion scheme for fixed-offset ground penetrating radar (GPR) is derived that takes into account the loss in the soil and the planar air–soil interface. The forward model of this inversion scheme is based upon the first Born approximation and the dyadic Green function for a two-layer medium. The forward model is inverted using the Tikhonov-regularized pseudo-inverse operator. This involves two steps: filtering and backpropagation. The filtering is carried out by numerically solving Fredholm integral equations of the first kind and the backpropagation is performed using fast Fourier transforms (FFTs). Numerical results are provided to illustrate the performance of the inversion scheme.

**Index Terms**—Diffraction tomography, ground penetrating radar (GPR), inverse scattering, pseudo-inverse operator.

## I. INTRODUCTION

WITHIN the framework of geophysical diffraction tomography [1], several inversion schemes have been developed for monostatic or fixed-offset ground penetrating radars (GPRs) [2]–[6]. Molyneux and Witten [2] derived two different two-dimensional (2-D) inversion schemes referred to as the far-field method and the Fourier transform (FT) method, respectively. These two inversion schemes were tested on measured data in [3] and it was concluded that the FT method is superior. In deriving the FT method it was assumed that the first Born approximation applies, the background medium is homogeneous and the buried object, of which a quantitative image is desired, is located deep in the soil. Thereby, a relation between the one-dimensional (1-D) spatial FT of the data measured over a line and the 2-D spatial FT of the permittivity variation in the soil was obtained. An inversion scheme involving a closed-form expression for the desired image was then derived using the inverse spatial FT. This inversion scheme constitutes a more general form of the filtered backpropagation algorithm of [1] because it applies to illumination by 2-D point sources and to multiple frequencies. Recently, Hansen and Meincke-Johansen [4] presented a 3-D version of the FT method in which the planar air–soil interface is taken into account. In [4] a configuration in which the GPR antennas are 4 cm above the ground was considered and for this configuration an improved image quality was achieved when including the interface in the inversion. However, as also was the case in [2] and [3], the background medium was assumed lossless—an assumption that usually does not hold for soil. A heuristic approach was suggested in [4] to compensate for the loss. Since this approach is not exact it produces unwanted artifacts in the image, as shown in [4, Fig. 5]. Therefore, it is highly

desirable to develop a version of the inversion scheme of [4] that rigorously takes into account the loss in the soil.

Deming and Devaney [5], [6] employed the Tikhonov-regularized pseudo-inverse operator to obtain an inversion scheme for GPR in which the background medium is lossy and homogeneous. The pseudo-inverse operator implies two solution steps: 1) filtering of the radar data and 2) backpropagation of the filtered data. In [5], a 2-D configuration was considered and the incident field was assumed to consist of several plane waves with the same frequency but with different directions of incidence. Also, it was shown that in the case of a lossless background medium and an infinite number of plane waves (infinite view), the pseudo-inverse solution reduces to the filtered backpropagation algorithm of [1]. The approach of [5] was extended in [6] to a 3-D configuration in which the incident field originates from an arbitrary transmitting antenna. The receiving antenna can also be arbitrary and several probing frequencies can be included. However, the calculation of the filters to be applied in the filtering step is extremely time consuming since it involves evaluation of several 4-D integrals with highly oscillating integrands. This fact hampers the practical applicability of the approach in [6]. Also, in [6] the air–soil interface is not taken into account.

In the present paper, a pseudo-inverse based inversion scheme for fixed-offset GPR is presented that takes into account both the loss in the soil and the air–soil interface. The starting point is the forward model of [4], which is based upon the first Born approximation, the dyadic Green function for a two-layer medium, and an asymptotic approximation valid when the object is located deep (a few center wavelengths) in the soil. However, instead of inverting this forward model using the inverse FT, as done in [4] (and thus neglecting loss in the soil), the Tikhonov-regularized pseudo-inverse operator is used. Since the applied forward model is approximate the calculation of the filters in the filtering step is much less time consuming than the corresponding calculation in [6].

The remaining of the paper is organized as follows. In Section II the forward model is presented. The forward model applies to a fixed-offset GPR placed upon a planar interface separating lossy soil and air. It predicts, within the first Born approximation, the output $\delta_0$ of the receiving antenna due to the scattering by a 3-D buried object. Arbitrary GPR antennas are accounted for through the current density of the transmitting antenna and the plane-wave characteristic of the receiving antenna. The inversion of the forward model is performed in Sections III, III-A and III-B using the Tikhonov-regularized pseudo-inverse operator. In Section III-D, it is shown that the pseudo-inverse based inversion scheme reduces to the result of [4] when there is no loss in the soil. The special case of an infinitely long scattering object, referred to as 2.5-D, is considered in Section III-E. To carry out the inversion, it must be assumed that the contrast

Manuscript received August 8, 2000; revised June 6, 2001.  
The author is with the Ørsted-DTU, Electromagnetic Systems, Technical University of Denmark, DK-2800 Lyngby, Denmark (e-mail: pme@oersted.dtu.dk).  
Publisher Item Identifier S 0196-2892(01)09906-5.

0196-2892/01\$10.00 © 2001 IEEE

Authorized licensed use limited to: Danmarks Tekniske Informationscenter. Downloaded on March 23, 2010 at 10:16:38 EDT from IEEE Xplore. Restrictions apply.

2714

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 39, NO. 12, DECEMBER 2001

![img-0.jpeg](img-0.jpeg)

Fig. 1. Fixed-offset GPR configuration. The offset is described by the vector $\mathbf{r}_{\Delta} = \mathbf{R}_{\Delta} + \hat{\mathbf{z}} z_{\Delta}$.

in permittivity (i.e., the difference between the permittivities of the object and the soil) times the frequency is either much larger or much smaller than the contrast in conductivity. The first case is considered in Section III, except in Section III-F in which the second case applies. Numerical results for the 2.5-dimensional (2.5-D) case involving a circular cylinder buried deep in lossy soil is presented in Section IV. Finally, Section V draws conclusions and makes suggestions for future research.

## II. FORWARD MODEL

Consider the configuration in Fig. 1 in which a planar interface separates air and soil. A Cartesian $xyz$ coordinate system is introduced such that the $xy$ plane coincides with the interface and such that $z > 0$ is air. The air has the permittivity $\epsilon_0$ and the permeability $\mu_0$, whereas the soil has the permittivity $\epsilon_1$, conductivity $\sigma_1$, and permeability $\mu_0$. The constitutive parameters $\epsilon_0, \epsilon_1, \sigma_1$, and $\mu_0$ are all assumed to be real quantities and independent of both position and frequency $\omega$ over the bandwidth of the transmitted fields $\omega_{\min} < \omega < \omega_{\max}$. Thus, the propagation constant of air is $k_0(\omega) = \omega \sqrt{\mu_0 \epsilon_0}$ and that of soil is $k_1(\omega) = \omega \sqrt{\mu_0 (\epsilon_1 + i \sigma_1 / \omega)}$. A fixed-offset GPR configuration is considered in which the position of the receiving antenna is described by the vector $\mathbf{r}_r = \mathbf{R}_r + \hat{\mathbf{z}} z_r$ with $z_r \geq 0$. The position of the transmitting antenna is $\mathbf{r}_t = \mathbf{r}_r + \mathbf{r} \Delta D \epsilon t t a$ with the offset $\mathbf{r}_{\Delta} = \mathbf{R}_{\Delta} + \hat{\mathbf{z}} z_{\Delta}$ kept constant. The forward model to be presented in this section gives an expression for the output $s_o$ of the receiving antenna that is solely due to the field scattered by the buried object. Hence, $s_o$ does not include contributions from the reflection in the interface and from the direct field from the transmitting antenna. In [4], the first Born approximation and a plane-wave expansion of the dyadic Green function $\mathbf{G}(\mathbf{r}, \mathbf{r}', \omega)$ for a two-layer medium were used to derive an expression for the output $s_o$ when both the transmitting and receiving antennas are ideal dipoles [4, (12)]. In the following, a similar expression for $s_o$, valid for arbitrary transmitting and receiving antennas, is derived. To this end, the background field $\mathbf{E}_b$ in the soil, radiated by the transmitting antenna described by the current density $\mathbf{J}_{s_i}(\mathbf{r} - \mathbf{r}_t)^1$, is needed

$$\begin{aligned} \mathbf{E}_b(\mathbf{r}', \omega) &= i \omega \mu_0 \int_{-\infty}^{\infty} d^3\mathbf{r} \mathbf{G}(\mathbf{r}', \mathbf{r}, \omega) \\ &\quad \cdot \mathbf{J}_{s_i}(\mathbf{r} - \mathbf{r}_t) \\ &= i \omega \mu_0 \int_{-\infty}^{\infty} d^3\mathbf{r} \mathbf{J}_{s_i}(\mathbf{r} - \mathbf{r}_t) \\ &\quad \cdot \mathbf{G}(\mathbf{r}, \mathbf{r}', \omega) \quad z' < 0 \end{aligned} \quad (1)$$

$^1$The subscript $s_i$ on $\mathbf{J}_{s_i}$ indicates that the current density depends on the input signal $s_i$. The form of this dependence can be either measured or calculated. This matter is, however, not the concern of the present paper.

where the reciprocity relation $\mathbf{G}(\mathbf{r}', \mathbf{r}, \omega) \cdot \mathbf{J}_{s_i} = \mathbf{J}_{s_i} \cdot \mathbf{G}(\mathbf{r}, \mathbf{r}', \omega)$ is used. The dyadic Green function is written as a plane-wave spectrum as

$$\begin{aligned} \mathbf{G}(\mathbf{r}, \mathbf{r}', \omega) &= \frac{i}{8\pi^2} \int_{-\infty}^{\infty} d^3\mathbf{K}' \mathbf{F}(\mathbf{K}', \omega) \\ &\quad \cdot \exp(i \mathbf{k}_0(\mathbf{K}', \omega) \cdot \mathbf{r} - \mathbf{k}_1(\mathbf{K}', \omega) \cdot \mathbf{r}') \\ &\quad z > 0, z' < 0. \end{aligned} \quad (2)$$

In this expression, $\mathbf{k}_0(\mathbf{K}, \omega) = \mathbf{K} + \hat{\mathbf{z}} \gamma_0(\mathbf{K}, \omega)$, $\mathbf{K} = \hat{\mathbf{x}} k_x + \hat{\mathbf{y}} k_y$, $\gamma_0(\mathbf{K}, \omega) = \sqrt{k_0^2(\omega) - |\mathbf{K}|^2}$, and similarly for $\mathbf{k}_1(\mathbf{K}, \omega)$. The square roots in $\gamma_0$ and $\gamma_1$ have nonnegative real and imaginary parts. The dyadic $\mathbf{F}$ in (2), that accounts for the interface, is [4, (6)]

$$\begin{aligned} \mathbf{F}(\mathbf{K}, \omega) &= \frac{2}{(\gamma_0 + \gamma_1)(k_x^2 + k_y^2 + \gamma_0 \gamma_1)} \\ &\quad \cdot \left[ \hat{\mathbf{x}} \left( (k_y^2 + \gamma_0 \gamma_1) \hat{\mathbf{x}} - k_x k_y \hat{\mathbf{y}} \right. \right. \\ &\quad \left. \left. - k_x \gamma_0 \hat{\mathbf{z}} \right) \right. \\ &\quad + \hat{\mathbf{y}} \left( -k_x k_y \hat{\mathbf{x}} + (k_x^2 + \gamma_0 \gamma_1) \hat{\mathbf{y}} \right. \\ &\quad \left. - k_y \gamma_0 \hat{\mathbf{z}} \right) \\ &\quad + \hat{\mathbf{z}} \left( -k_x \gamma_1 \hat{\mathbf{x}} - k_y \gamma_1 \hat{\mathbf{y}} \right. \\ &\quad \left. \left. + (k_x^2 + k_y^2) \hat{\mathbf{z}} \right) \right] \end{aligned} \quad (3)$$

where it has not been explicitly indicated that $\gamma_0$ and $\gamma_1$ depend on $\mathbf{K}$ and $\omega$. When there is no interface, i.e., $k_1(\omega) = k_0(\omega)$, (3) reduces to $\mathbf{F}(\mathbf{K}, \omega) = (\mathbf{I} - \mathbf{k}_1(\mathbf{K}, \omega) \mathbf{k}_1(\mathbf{K}, \omega) / k_1^2(\omega)) / \gamma_1(\mathbf{K}, \omega)$. Inserting the plane-wave expansion (2) of the dyadic Green function into the expression (1) for the background field, one obtains

$$\begin{aligned} \mathbf{E}_b(\mathbf{r}', \omega) &= \frac{-\omega \mu_0}{8\pi^2} \int_{-\infty}^{\infty} d^3\mathbf{K}' \exp(-i \mathbf{k}_1(\mathbf{K}', \omega) \cdot \mathbf{r}') \\ &\quad \cdot \exp(i \mathbf{k}_0(\mathbf{K}', \omega) \cdot [\mathbf{r}_r + \mathbf{r}_{\Delta}]) \\ &\quad \cdot \mathbf{J}_{s_i}(-\mathbf{k}_0(\mathbf{K}', \omega)) \cdot \mathbf{F}(\mathbf{K}', \omega) \end{aligned} \quad (4)$$

where the relation $\mathbf{r}_t = \mathbf{r}_r + \mathbf{r}_{\Delta}$ has been employed. The quantity $\mathbf{J}_{s_i}$ is a spatial FT of the current density describing the transmitting antenna

$$\mathbf{J}_{s_i}(\mathbf{k}) = \int_{-\infty}^{\infty} d^3\mathbf{r} \mathbf{J}_{s_i}(\mathbf{r}) \exp(-i \mathbf{k} \cdot \mathbf{r}). \quad (5)$$

Using the first Born approximation, the scattered field $\mathbf{E}_s(\mathbf{r}_r, \omega)$, due to the presence of the buried object, is explicitly expressed in terms of the background field $\mathbf{E}_b$ as

$$\mathbf{E}_s(\mathbf{r}_r, \omega) = i \omega \mu_0 \int_{z' < 0} d^3\mathbf{r}' \mathbf{G}(\mathbf{r}_r, \mathbf{r}', \omega) \cdot \mathbf{E}_b(\mathbf{r}', \omega) O(\mathbf{r}', \omega) \quad (6)$$

where the object function $O(\mathbf{r}', \omega)$ is defined as

$$O(\mathbf{r}', \omega) = \sigma(\mathbf{r}') - \sigma_1 - i \omega(\epsilon(\mathbf{r}') - \epsilon_1) = \Delta \sigma(\mathbf{r}') - i \omega \Delta \epsilon(\mathbf{r}'). \quad (7)$$

Using this expression (6) for the scattered field, the plane-wave spectrum (2) of the dyadic Green function and the plane-wave

Authorized licensed use limited to: Danmarks Tekniske Informationscenter. Downloaded on March 23, 2010 at 10:16:38 EDT from IEEE Xplore. Restrictions apply.

MEINCKE: LINEAR GPR INVERSION

2715

characteristic $\mathbf{R}(\mathbf{K}, \omega)$ of the receiving antenna, the output $s_o$ of this antenna can be written as

$$\begin{aligned} s_o(\mathbf{r}_r, \omega) &= \frac{\omega^2 \mu_0^2}{64\pi^4} \int_{-\infty}^{\infty} d^2\mathbf{K} \int_{-\infty}^{\infty} d^2\mathbf{K}' \\ &\quad \cdot \exp\left(i \left[ (\mathbf{k}_0(\mathbf{K}, \omega) + \mathbf{k}_0(\mathbf{K}', \omega)) \cdot \mathbf{r}_r + \mathbf{k}_0(\mathbf{K}', \omega) \cdot \mathbf{r}_\Delta \right]\right) \\ &\quad \cdot \mathbf{R}(\mathbf{K}, \omega) \cdot \tilde{\mathbf{F}}(\mathbf{K}, \omega) \\ &\quad \cdot \tilde{\mathbf{J}}_{s_i}(-\mathbf{k}_0(\mathbf{K}', \omega)) \cdot \tilde{\mathbf{F}}(\mathbf{K}', \omega) \\ &\quad \cdot \int_{z' < 0} d^3\mathbf{r}' O(\mathbf{r}', \omega) \\ &\quad \cdot \exp\left(-i \left[ \mathbf{k}_1(\mathbf{K}, \omega) + \mathbf{k}_1(\mathbf{K}', \omega) \right] \cdot \mathbf{r}'\right). \end{aligned} \quad (8)$$

The plane-wave characteristic $\mathbf{R}(\mathbf{K}, \omega)$ is defined such that $\mathbf{R}(\mathbf{K}, \omega) \cdot \mathbf{E}(\mathbf{K}, \omega)$ is the output when the receiving antenna is located at $\mathbf{r} = 0$ and the incident electric field is the plane wave $\mathbf{E}(\mathbf{K}, \omega) \exp(i\mathbf{k}_0(\mathbf{K}, \omega) \cdot \mathbf{r})$ with $\mathbf{k}_0(\mathbf{K}, \omega) \cdot \mathbf{E}(\mathbf{K}) = 0$ [7], [8, p. 266].

Defining the FT $\tilde{s}_o(\mathbf{K}, z_r, \omega)$ with respect to the horizontal components $\mathbf{R}_r$ of the observation point as

$$\tilde{s}_o(\mathbf{K}, z_r, \omega) = \int_{-\infty}^{\infty} d^2\mathbf{R}_r s_o(\mathbf{r}_r, \omega) \exp(-i\mathbf{K} \cdot \mathbf{R}_r) \quad (9)$$

and using (8), the expression for $\tilde{s}_o$ can be written as

$$\begin{aligned} \tilde{s}_o(\mathbf{K}, z_r, \omega) &= \int_{-\infty}^{\infty} d^2\mathbf{K}' C(\mathbf{K}, \mathbf{K}', z_r, \omega) \\ &\quad \cdot \int_{z' < 0} d^3\mathbf{r}' O(\mathbf{r}', \omega) \\ &\quad \cdot \exp\left(-i \left[ \mathbf{k}_1(\mathbf{K} - \mathbf{K}', \omega) + \mathbf{k}_1(\mathbf{K}', \omega) \right] \cdot \mathbf{r}'\right) \end{aligned} \quad (10)$$

where

$$\begin{aligned} C(\mathbf{K}, \mathbf{K}', z_r, \omega) &= \frac{\omega^2 \mu_0^2}{16\pi^2} \mathbf{R}(\mathbf{K} - \mathbf{K}', \omega) \\ &\quad \cdot \tilde{\mathbf{F}}(\mathbf{K} - \mathbf{K}', \omega) \cdot \tilde{\mathbf{J}}_{s_i}(-\mathbf{k}_0(\mathbf{K}', \omega)) \\ &\quad \cdot \tilde{\mathbf{F}}(\mathbf{K}', \omega) \\ &\quad \cdot \exp\left(i \left[ (\gamma_0(\mathbf{K} - \mathbf{K}', \omega) + \gamma_0(\mathbf{K}', \omega)) z_r + \mathbf{k}_1(\mathbf{K}', \omega) \cdot \mathbf{r}_\Delta \right]\right). \end{aligned} \quad (11)$$

As shown in the Appendix of [4], the double integral over $\mathbf{K}'$ in (10) can be asymptotically evaluated when the object is located deep in the soil and the GPR antennas are close to the interface to yield

$$\begin{aligned} \tilde{s}_o(\mathbf{K}, z_r, \omega) &\sim D(\mathbf{K}, z_r, \omega) \\ &\quad \cdot \int_{-\infty}^{\infty} d^2\mathbf{R}' \int_{-\infty}^{0} dz' O_1(\mathbf{r}', \omega) \\ &\quad \cdot \exp(-i\mathbf{K} \cdot \mathbf{R}') \\ &\quad \cdot \exp\left(-i \sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} z'\right) \end{aligned} \quad (12)$$

with $O(\mathbf{r}', \omega) = O_1(\mathbf{r}', \omega)/z' = \Delta\sigma_1(\mathbf{r}') - i\omega\Delta\epsilon_1(\mathbf{r}') \cdot \mathbf{r}' = \mathbf{R}' + \mathbf{z} z'$, and

$$\begin{aligned} D(\mathbf{K}, z_r, \omega) &= \frac{i\omega^2 \mu_0^2}{64\pi k_1(\omega)} \left( 4k_1^2(\omega) - |\mathbf{K}|^2 \right) \\ &\quad \cdot \mathbf{R}\left(\frac{1}{2}\mathbf{K}, \omega\right) \cdot \tilde{\mathbf{F}}\left(\frac{1}{2}\mathbf{K}, \omega\right) \\ &\quad \cdot \tilde{\mathbf{J}}_{s_i}\left(-\mathbf{k}_0\left(\frac{1}{2}\mathbf{K}, \omega\right)\right) \cdot \tilde{\mathbf{F}}\left(\frac{1}{2}\mathbf{K}, \omega\right) \\ &\quad \cdot \exp\left(i \left[ \sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} \left(z_r + \frac{z_\Delta}{2} + \frac{1}{2}\mathbf{K} \cdot \mathbf{R}_\Delta \right]\right)\right). \end{aligned} \quad (13)$$

Equation (12) constitutes the 3-D forward model to be inverted in Section III. Although this forward model is derived using the assumption that the object is deep in the soil, it remains valid for surprisingly shallow objects. In [4] it is shown through numerical investigations that inversion schemes based on (12) give accurate images of objects buried just two center wavelengths from the interface. Unfortunately, the asymptotic evaluation in the Appendix of [4] becomes too inaccurate for $|\mathbf{K}| > 2\text{Re}k_1(\omega)$, and the forward model (12) should therefore only be used when $|\mathbf{K}| < 2\text{Re}k_1(\omega)$. Physically, this means that the forward model does include some of the evanescent plane waves in the air but it does not include any evanescent plane waves in the soil.

### III. INVERSION

To carry out the inversion, it is assumed that $\omega\Delta\epsilon \gg \Delta\sigma$ over the frequency interval of consideration $\omega_{\min} < \omega < \omega_{\max}$ (the case in which $\omega\Delta\epsilon \ll \Delta\sigma$ is dealt with in Section III-F). Then $O_1(\mathbf{r}') \approx -i\omega\Delta\epsilon_1(\mathbf{r}')$ and the forward model (12) can be written as

$$\begin{aligned} \tilde{s}_o(\mathbf{K}, z_r, \omega) &= (\mathcal{L}\Delta\epsilon_1)(\mathbf{K}, z_r, \omega) \\ &= -i\omega D(\mathbf{K}, z_r, \omega) \int_{-\infty}^{\infty} d^2\mathbf{R}' \int_{-\infty}^{0} dz' \\ &\quad \cdot \exp(-i\mathbf{K} \cdot \mathbf{R}') \\ &\quad \cdot \exp\left(-i \sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} z'\right) \\ &\quad \cdot \Delta\epsilon_1(\mathbf{r}') \end{aligned} \quad (14)$$

where $\mathcal{L}: U \to V$ is a linear operator mapping $U$ into $V$. $U$ is the space of square integrable functions of position $\mathbf{r}'$ confined within $z' < 0$. $V$ is the space of square integrable functions defined on $\{(\mathbf{K}, \omega)|\omega_{\min} < \omega < \omega_{\max} \wedge |\mathbf{K}| < 2\text{Re}k_1(\omega)\}$. The inner products in $U$ and $V$ are defined in the usual way

$$\begin{aligned} \langle\Delta\epsilon_1, \Delta\epsilon_2\rangle_U &= \int_{z<0} d^3\mathbf{r} \Delta\epsilon_1^*(\mathbf{r}) \Delta\epsilon_2(\mathbf{r}) \\ \langle\tilde{s}_{o1}, \tilde{s}_{o2}\rangle_V &= \int_{\omega_{\min}}^{\omega_{\max}} d\omega \\ &\quad \cdot \int_{|\mathbf{K}| < 2\text{Re}k_1(\omega)} d^2\mathbf{K} \\ &\quad \cdot \tilde{s}_{o1}^*(\mathbf{K}, \omega) \tilde{s}_{o2}(\mathbf{K}, \omega) \end{aligned} \quad (15)$$

Authorized licensed use limited to: Danmarks Tekniske Informationscenter. Downloaded on March 23, 2010 at 10:16:38 EDT from IEEE Xplore. Restrictions apply.

2716

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 39, NO. 12, DECEMBER 2001

where * denotes the complex conjugation. Introducing $K_m = 2\text{Re}k_1(\omega_{\max})$, it is seen that if $|\mathbf{K}| > K_m$, then $\tilde{s}_o(\mathbf{K}, \omega) = 0$ for $\omega_{\min} < \omega < \omega_{\max}$.

Due to the compactness of the kernel in the integral equation (14), the solution $\Delta\epsilon_1$ of the inverse problem defined in (14) is unstable [9], [10], that is, the solution is highly sensitive to noise in the radar data $\tilde{s}_o$. Regularization is therefore needed, in particular when dealing with noisy data, to obtain a stable and useful solution. In this work, Tikhonov regularization is applied and hence, a minimization problem of the form

$$\min_{\Delta\epsilon_1} \left( \|\mathcal{L}\Delta\epsilon_1 - \tilde{s}_o\|_2^2 + \lambda^2 \|\Delta\epsilon_1\|_2^2 \right) \quad (17)$$

is considered. This problem can also be formulated as $\min_{\Delta\epsilon_1} \|\mathcal{L}\Delta\epsilon_1 - \tilde{s}_o\|_2$ subject to $\|\Delta\epsilon_1\|_2 < \eta$, where $\eta$ depends on $\lambda$ [9, p. 85]. The regularization parameter $\lambda$ in (17) controls the amount of filtering applied to obtain the solution. The larger the value of $\lambda$, the more filtering. It is obvious that there exists an optimum value of $\lambda$—if $\lambda$ is too small, the residual norm $\|\mathcal{L}\Delta\epsilon_1 - \tilde{s}_o\|_2$ is small but the norm $\|\Delta\epsilon_1\|_2$ is too large because the solution is affected by noise. If $\lambda$ is too large on the other hand, the norm $\|\Delta\epsilon_1\|_2$ is small but the residual norm is too large. In fact, when $\lambda$ is large the high spatial frequencies of the solution $\Delta\epsilon_1$ are efficiently damped. Consequently, the spatial bandwidth of the solution is determined by $\lambda$. A discussion on the difficulties in choosing the optimum $\lambda$ for the inversion scheme of this paper is found in Section III-C.

The minimization problem (17) could at this stage be solved by discretizing the continuous operator $\mathcal{L}$ such that it becomes a matrix $A$ and then using standard techniques for solving discrete ill-posed problems by Tikhonov regularization [9, Section 5.1]. However, in this way the matrix $A$ becomes unpractically large and also, the advantage of having the operator in the convenient explicit form (14) is not taken into account. Therefore, the operator $\mathcal{L}$ is here kept in continuous form and in line with the procedure in [5], [6], the minimization problem (17) is solved by applying the Tikhonov-regularized pseudo-inverse operator [11, p. 88]

$$\Delta\epsilon_1 = \mathcal{L}^\dagger = \left( \mathcal{L}\mathcal{L}^\dagger + \lambda^2 I \right)^{-1} \tilde{s}_o \quad (18)$$

where the adjoint operator $\mathcal{L}^\dagger$ defined by $\langle \tilde{s}_o, \mathcal{L}\Delta\epsilon_1 \rangle_V = \langle \mathcal{L}^\dagger \tilde{s}_o, \Delta\epsilon_1 \rangle_U$ is

$$\begin{aligned} (\mathcal{L}^\dagger \tilde{s}_o)(t') &= U(-z') \int_{\omega_{\min}}^{\omega_{\max}} d\omega i \omega \\ &\quad \cdot \int_{|\mathbf{K}| < 2\text{Re}k_1(\omega)} d^2\mathbf{K} D^*(\mathbf{K}, z_r, \omega) \exp(i\mathbf{K} \cdot \mathbf{R}') \\ &\quad \cdot \exp\left(i\sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} z'\right) \tilde{s}_o(\mathbf{K}, z_r, \omega) \end{aligned} \quad (19)$$

and the unit step function $U(-z')$ serves as a masking function. It is seen that when applying $\mathcal{L}^\dagger$ to $\tilde{s}_o$, the output $s_o$ at the plane $z = z_r$ is backpropagated to the plane $z = z'$. To proceed, the filtered data $\tilde{s}_o^f$ are introduced as the solution to

$$\left( \mathcal{L}\mathcal{L}^\dagger + \lambda^2 I \right) \tilde{s}_o^f = \tilde{s}_o. \quad (20)$$

The spatial bandwidth of the filtered data is assumed to be the same as that of $\tilde{s}_o$, that is, $\tilde{s}_o^f(\mathbf{K}, \omega) = 0$ for $|\mathbf{K}| > 2\text{Re}k_1(\omega)$. Using the definition (20) along with (18), the contrast in permittivity is obtained from

$$\Delta\epsilon_1 = \mathcal{L}^\dagger \tilde{s}_o^f. \quad (21)$$

Hence, by solving (18) using the solution steps (20) and (21), the data are first filtered and then backpropagated to obtain the sought-for function $\Delta\epsilon_1$. In Section III-B it is shown how a priori information can be incorporated to give a better estimate of the object function.

The backpropagation (19) can be easily and efficiently calculated using fast Fourier transforms (FFTs). The filtering, on the other hand, is more complicated. The next section is devoted to this filtering step.

A. Filtering

The term $\mathcal{L}\mathcal{L}^\dagger \tilde{s}_o^f$ in the filtering step (20) can be explicitly expressed as

$$\begin{aligned} (\mathcal{L}\mathcal{L}^\dagger \tilde{s}_o^f)(\mathbf{K}, \omega) &= \omega D(\mathbf{K}, z_r, \omega) \\ &\quad \cdot \int_{-\infty}^{\infty} d^2\mathbf{R}' \int_{-\infty}^{0} dz' \int_{\omega_{\min}}^{\omega_{\max}} d\omega' \omega' \\ &\quad \cdot \int_{|\mathbf{K}'| < 2\text{Re}k_1(\omega')} d^2\mathbf{K}' D^*(\mathbf{K}', z_r, \omega') \\ &\quad \cdot \exp(i[\mathbf{K}' - \mathbf{K}] \cdot \mathbf{R}') \\ &\quad \cdot \exp\left(i \left[ \sqrt{4k_1^2(\omega') - |\mathbf{K}'|^2} \right. \right. \\ &\quad \left. \left. - \sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} \right] z' \right) \\ &\quad \cdot \tilde{s}_o^f(\mathbf{K}', z_r, \omega'). \end{aligned} \quad (22)$$

Using the fact that there is loss in the soil, $\text{Im}(k_1(\omega)) > 0$ and the integrations in (22) over $\mathbf{R}'$ and $z'$ can be evaluated to yield $(2\pi)^2 i \delta(\mathbf{K} - \mathbf{K}') / (\sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} - \sqrt{4k_1^2(\omega') - |\mathbf{K}'|^2^*})$. By subsequently evaluating the integration over $\mathbf{K}'$, the relation

$$\begin{aligned} (\mathcal{L}\mathcal{L}^\dagger \tilde{s}_o^f)(\mathbf{K}, \omega) &= (2\pi)^2 i \omega D(\mathbf{K}, z_r, \omega) \int_{\omega_{\min}}^{\omega_{\max}} d\omega' \omega' \\ &\quad \cdot D^*(\mathbf{K}, z_r, \omega') \frac{U(2\text{Re}k_1(\omega') - |\mathbf{K}|) \tilde{s}_o^f(\mathbf{K}, \omega')}{\sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} - \sqrt{4k_1^2(\omega') - |\mathbf{K}|^2}} \end{aligned} \quad (23)$$

is obtained. When inserting (23) into (20), an integral equation is obtained for the determination of the filtered data $\tilde{s}_o^f(\mathbf{K}, \omega)$ for each $\mathbf{K}$, satisfying $|\mathbf{K}| \leq K_m$, where $K_m$ is defined following (16)$^2$. To solve this integral equation numerically it must be transformed into a matrix equation by discretization. There are many ways to discretize such an integral equation. In this case, the discretization method should be chosen such that the resulting matrix A is self adjoint (Hermitian). The reason for this is that A reflects the self-adjoint operator $\mathcal{L}\mathcal{L}^\dagger$. This requirement is satisfied by using a simple quadrature rule. To this end, first

$^2$If $|\mathbf{K}| > K_m$, then $\tilde{s}_o^f(\mathbf{K}, \omega) = 0$ for $\omega_{\min} < \omega < \omega_{\max}$ and no integral equation must be solved.

Authorized licensed use limited to: Danmarks Tekniske Informationscenter. Downloaded on March 23, 2010 at 10:16:38 EDT from IEEE Xplore. Restrictions apply.

MEINCKE: LINEAR GPR INVERSION

2717

assume that the radar data $\tilde{s}_o$ are available at $N_\omega$ equidistant frequencies

$$\omega_p = (p-1)\Delta\omega + \omega_{\min} \quad p = 1, \dots, N_\omega \quad (24)$$

where $\Delta\omega = (\omega_{\max} - \omega_{\min}) / (N_\omega - 1)$. With $q(\mathbf{K})$ denoting the lowest integer in the range $1, \dots, N_\omega$ for which $\tilde{s}_o(\mathbf{K}, \omega_{q(\mathbf{K})}) \neq 0$, there are $q(\mathbf{K}) - 1$ values of the radar data $\tilde{s}_o(\mathbf{K}, \omega_p)$ and the filtered data $\tilde{s}_o^f(\mathbf{K}, \omega_p)$ that are zero and $N_{nz} = N_\omega - q(\mathbf{K}) + 1$ values that are nonzero. Second, a simple quadrature rule applied to (23) transforms the filtering step (20) into the following matrix equation:

$$\tilde{s}_o(\mathbf{K}, \omega_p) = \sum_{p'=q(\mathbf{K})}^{N_\omega} R_{pp'}(\mathbf{K}) \tilde{s}_o^f(\mathbf{K}, \omega_{p'}) \quad (25)$$

where $p = q(\mathbf{K}), \dots, N_\omega, |\mathbf{K}| \leq K_m$ and $\delta_{pp'}$ denotes Kronecker's delta. Moreover

$$R_{pp'}(\mathbf{K}) = (2\pi)^2 i \omega_p D(\mathbf{K}, z_r, \omega_p) W_{pp'}(\mathbf{K}) + \delta_{pp'} \lambda^2 \quad (26)$$

and

$$W_{pp'}(\mathbf{K}) = \frac{\Delta\omega D^*(\mathbf{K}, z_r, \omega_{p'}) \omega_{p'}}{\sqrt{4k_1^2(\omega_p) - |\mathbf{K}|^2} - \sqrt{4k_1^2(\omega_{p'}) - |\mathbf{K}|^2}}. \quad (27)$$

This completes the derivation of the inversion scheme. In summary, to obtain the image of the buried object one must first filter the radar data using (25) and subsequently backpropagate the filtered data employing (21).

B. Incorporating a Priori Information

Due to the fact that the buried object can be illuminated from one side only in a GPR survey, the obtained radar data does not contain enough information to estimate the correct value of $\Delta\epsilon_1$ using a linear inversion scheme. However, if a priori information about the object can be incorporated in the inversion scheme, a better estimate of $\Delta\epsilon_1$ can be obtained. This is the case in [4], in which the fact that the object function is real is used as a priori information. Unfortunately, the same procedure cannot be applied in an exact manner in this work because it requires that the soil is lossless. However, the procedure can be used approximately. To see this, consider the forward model (14). This model can be written as

$$\tilde{s}_o(\mathbf{K}, z_r, \omega) = -i\omega D(\mathbf{K}, z_r, \omega) \cdot \widetilde{\Delta\epsilon_1} \left( \mathbf{K} + \tilde{\mathbf{Z}} \sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} \right). \quad (28)$$

When there is no loss and $|\mathbf{K}| < 2k_1(\omega)$ the argument of $\widetilde{\Delta\epsilon_1}$ is real and thus, the forward model (28) can be inverted using the inverse spatial FT $\mathcal{F}^{-1}$. This is indeed the procedure of [4]. Hence, $\Delta\epsilon_1 = \mathcal{F}^{-1}(\widetilde{\Delta\epsilon_1})$. From (28), it is seen that the radar data only provides information about $\widetilde{\Delta\epsilon_1}(\mathbf{k})$ in the upper half space $k_z > 0$. To obtain the information in the lower half space, the relation $\widetilde{\Delta\epsilon_1}(\mathbf{k}) = \widetilde{\Delta\epsilon_1}^*(-\mathbf{k})$ is used, which holds for real functions $\Delta\epsilon_1$ and for real arguments $\mathbf{k}$. Using this a priori information yields

$$\begin{aligned} \Delta\epsilon_1 &= 2\text{Re} \left[ \mathcal{F}_{\text{up}}^{-1} \left( \widetilde{\Delta\epsilon_1} \right) \right] \\ &= 2\text{Re} \left[ \mathcal{F}_{\text{up}}^{-1} \left( \frac{\tilde{s}_o(\mathbf{K}, z_r, \omega)}{-i\omega D(\mathbf{K}, z_r, \omega)} \right) \right] \end{aligned} \quad (29)$$

where $\mathcal{F}_{\text{up}}^{-1}$ denotes the inverse FT with integration in the upper half space only. When loss is present in the soil the argument of $\widetilde{\Delta\epsilon_1}$ in (28) is no longer real, and the inverse FT cannot be used to accurately invert the forward model. The artifacts in Fig. 5 of [4] are the result of such an invalid application of the inverse FT. To get rid of the artifacts, the pseudo-inverse operator of this paper must be applied. Unfortunately, it is difficult to incorporate a priori information exactly using the pseudo-inverse operator. However, since the pseudo-inverse operator reduces to the inverse FT when there is no loss (see Section III-D) it is suggested to incorporate a priori information in the same way as done in (29). Hence, instead of using (21), it is suggested to use

$$\Delta\epsilon_1 = 2\text{Re} \left( \mathcal{L}^\dagger \tilde{s}_o^f \right) \quad (30)$$

to obtain a more accurate estimate of $\Delta\epsilon_1$.

C. Discussion

Although there exist many other and more accurate discretization methods the simple procedure outlined above turns out to give surprisingly good results even for low values of $N_\omega$, see the numerical example in Section IV. A more accurate method of moments approach with pulse expansion functions and point matching has been investigated [12]. The image quality of this method is not significantly better than that obtained from the simple quadrature rule of the present paper. The simple quadrature rule is preferred here due to its simplicity.

The FT $\tilde{s}_o(\mathbf{K}, z_r, \omega)$ in (9) is most conveniently calculated using FFTs. Hence, $\tilde{s}_o$ is available at $N_{\mathbf{K}}$ discrete values of $\mathbf{K}$ and for each of these values, (25) constitutes an $N_{nz}$ by $N_{nz}$ square matrix equation, where $N_{nz}$ defined following (24) depends on $\mathbf{K}$. When $|\mathbf{K}| = 0$, $N_{nz}$ is maximum and equals $N_\omega$, whereas $N_{nz}$ takes on the minimum value 1 when $|\mathbf{K}| = K_m$.

The filters $R_{pp'}$ depend on the properties of the GPR, i.e., the frequencies $(\omega_{\min}, \omega_{\max}, \Delta\omega)$, the offset $(\mathbf{r}_\Delta)$, the antennas $(\mathbf{J}_{s_1}, \mathbf{R}(\mathbf{K}, \omega))$ and the distance over the air-soil interface $(z_r)$. They also depend on the electromagnetic properties of the soil $(\epsilon_1, \sigma_1)$. All these quantities are independent of the radar data and $R_{pp'}$ can therefore be calculated in advance before data are to be processed.

There exist many methods for an efficient determination of the optimum regularization parameter $\lambda$, e.g., the generalized cross-validation and L-curve methods [9, Ch. 7]. It is important to note that these methods must be applied to the problem (18). They cannot be applied to the filtering step (20) because it does not satisfy the Picard condition [9, p. 9]. This is explained more carefully in the Appendix of this paper. Future research aims to find an efficient way to determine the optimum $\lambda$ for the special problem (18). Until this goal has been achieved, the regularization parameter $\lambda$ is to be determined by trial and error.

There are several differences between the pseudo-inverse based inversion scheme of this paper and that of [6]. First, the forward model of this paper takes into account the air-soil interface which, as mentioned in the Introduction, is not accounted for in [6]. Second, by using the asymptotic forward model (12) instead of the full model (10) the filters in the filtering step become much easier and faster to calculate. The application of the asymptotic forward model implies, however, that evanescent plane waves in the soil are neglected

Authorized licensed use limited to: Danmarks Tekniske Informationscenter. Downloaded on March 23, 2010 at 10:16:38 EDT from IEEE Xplore. Restrictions apply.

2718

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 39, NO. 12, DECEMBER 2001

and that the object must be buried a few center wavelengths from the interface. As illustrated in Section IV below, a high image quality is obtained despite these assumptions. Third, the frequency $\omega$ is assumed continuous in (14) and thereby, the filtering step consists of solving Fredholm integral equations of the first kind. It is thus evident that the accuracy of the filtering depends on the discretization method chosen to solve these integral equations. In [6], on the other hand, $\omega$ is assumed discrete from the very beginning and therefore, one specific discretization method is chosen and the fact that the filtering step is an integral equation does not become clear.

D. No Loss in the Soil

If $\sigma_1 = 0$, that is, the soil is lossless, the step from (22) to (23) does not hold. Instead, the integrations over $\mathbf{R}'$ and $z'$ in the expression (22) for $\mathcal{L}\mathcal{L}^\dagger$ can be evaluated to yield $8\pi^3\delta(\mathbf{K}-\mathbf{K}')\delta(\sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} - \sqrt{4k_1^2(\omega') - |\mathbf{K}'|^2})$. Using the relation $\delta(f(\omega)) = \delta(\omega - \omega_0)/|f'(\omega_0)|$, where $f(\omega_0) = 0$ and subsequently integrating over $\mathbf{K}'$ and $\omega'$ yields

$$(\mathcal{L}\mathcal{L}^\dagger \tilde{s}_0')(\mathbf{K}, \omega) = \frac{2\pi^3\omega^2}{k_1(\omega)\sqrt{\mu_0\epsilon_1}} |D(\mathbf{K}, z_r, \omega)|^2 \cdot \sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} \tilde{s}_0'(\mathbf{K}, \omega). \quad (31)$$

Hence, according to (30), the expression for $\Delta\epsilon = z\Delta\epsilon_1$ is as (32), shown at the bottom of the page. This result is identical to the one presented in [4, Eq. 20].

E. 2.5-D Case

Assume now that the object function is independent of $x$. This would be the case, for instance, when the buried object is an infinitely long $\hat{x}$-directed pipe. The solution steps (20) and (30) still hold in this case but to apply the other expressions in Section III, the relation $\mathbf{K} = \hat{y}k_y$ must be enforced and the expression (19) for the adjoint operator must be replaced by

$$(\mathcal{L}^\dagger \tilde{s}_0)(y', z') = 2\pi U(-z') \cdot \int_{\omega_{\min}}^{\omega_{\max}} d\omega \, i\omega \int_{|k_y|<2\pi\epsilon k_1(\omega)} dk_y D^*(k_y, z_r, \omega) \cdot \exp(ik_y y') \cdot \exp\left(i\sqrt{4k_1^2(\omega) - k_y^2} z'\right) \tilde{s}_0(k_y, z_r, \omega) \quad (33)$$

where $\tilde{s}_0(k_y, z_r, \omega)$ is the 1-D FT of the radar data defined by

$$\tilde{s}_0(k_y, z_r, \omega) = \int_{-\infty}^{\infty} dy \, s_0(y, z_r, \omega) \exp(-ik_y y) \quad (34)$$

and $D(k_y, z_r, \omega)$ is obtained from (13) with $\mathbf{K} = \hat{y}k_y$.

As an example, assume that the transmitting and receiving antennas are $\hat{x}$-directed ideal dipoles such that $\mathbf{R} = \hat{x}$ and $\mathbf{J} = I(\omega)\hat{x}$. Assume also that the antennas have the same $z$ and $x$ coordinates, i.e., $x_\Delta = z_\Delta = 0$. In this case, $D(k_y, z_r, \omega)$ becomes

$$D(k_y, z_r, \omega) = \frac{i\omega^2\mu_0^2 I(\omega)(4k_1^2(\omega) - k_y^2)}{4\pi k_1(\omega)\left(\sqrt{4k_0^2(\omega) - k_y^2} + \sqrt{4k_1^2(\omega) - k_y^2}\right)^2} \cdot \exp\left(i\left[\sqrt{4k_0^2(\omega) - k_y^2} z_r + \frac{1}{2}k_y y_\Delta\right]\right). \quad (35)$$

F. Case in Which $\omega\Delta\epsilon \ll \Delta\sigma$

When $\omega\Delta\epsilon \ll \Delta\sigma$ the object function can be approximated as $O_1(\mathbf{r}') \approx \Delta\sigma_1(\mathbf{r}')$ and the forward model (12) becomes

$$\tilde{s}_0(\mathbf{K}, z_r, \omega) = (\mathcal{L}\Delta\sigma_1)(\mathbf{K}, z_r, \omega) = D(\mathbf{K}, z_r, \omega) \int_{-\infty}^{\infty} d^2\mathbf{R}' \int_{-\infty}^{0} dz' \cdot \exp(-i\mathbf{K} \cdot \mathbf{R}') \cdot \exp\left(-i\sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} z'\right) \Delta\sigma_1(\mathbf{r}'). \quad (36)$$

The image of $\Delta\sigma_1$ is obtained using

$$\Delta\sigma_1 = 2\text{Re}(\mathcal{L}^\dagger \tilde{s}_0') \quad (37)$$

where the adjoint operator $\mathcal{L}^\dagger$ is

$$(\mathcal{L}^\dagger \tilde{s}_0)(\mathbf{r}') = U(-z') \cdot \int_{\omega_{\min}}^{\omega_{\max}} d\omega \int_{|\mathbf{K}|<2\pi\epsilon k_1(\omega)} d^2\mathbf{K} D^*(\mathbf{K}, z_r, \omega) \cdot \exp(i\mathbf{K} \cdot \mathbf{R}') \cdot \exp\left(i\sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} z'\right) \tilde{s}_0(\mathbf{K}, z_r, \omega). \quad (38)$$

In addition, in the matrix (25), $R_{pp'}$ must be

$$R_{pp'}(\mathbf{K}) = (2\pi)^2 i D(\mathbf{K}, z_r, \omega_p) W_{pp'}(\mathbf{K}) + \delta_{pp'} \lambda^2 \quad (39)$$

$$\Delta\epsilon(\mathbf{r}) = \text{Re}\left[ \frac{64z(\mu_0\epsilon_1)^{3/2}}{\pi^2\mu_0^2} \int_{\omega_{\min}}^{\omega_{\max}} d\omega \int_{|\mathbf{K}|<2\epsilon_1(\omega)} d^2\mathbf{K} \tilde{s}_0(\mathbf{K}, \omega) \cdot \exp\left(i\mathbf{K} \cdot \left[\mathbf{R} - \frac{1}{2}\mathbf{R}_\Delta\right]\right) \cdot \frac{\exp\left(i\left[\sqrt{4k_1^2(\omega) - |\mathbf{K}|^2} z - \sqrt{4k_0^2(\omega) - |\mathbf{K}|^2} (z_r + (1/2)z_\Delta)\right]\right)}{\omega(4k_1^2(\omega) - |\mathbf{K}|^2)^{3/2} \mathbf{R}((1/2)\mathbf{K}, \omega) \cdot \bar{\mathbf{F}}((1/2)\mathbf{K}, \omega) \cdot \bar{\mathbf{J}}_{s_1}(-k_0((1/2)\mathbf{K}, \omega)) \cdot \bar{\mathbf{F}}((1/2)\mathbf{K}, \omega)} \right]. \quad (32)$$

Authorized licensed use limited to: Danmarks Tekniske Informationscenter. Downloaded on March 23, 2010 at 10:16:38 EDT from IEEE Xplore. Restrictions apply.

MEINCKE: LINEAR GPR INVERSION

2719

![img-1.jpeg](img-1.jpeg)

Fig. 2. Configuration consisting of a circular cylinder located in lossy soil. The constitutive parameters are $(\epsilon_c, \sigma_c) = (8.1\epsilon_0, 0.01 \text{ S/m})$ and $(\epsilon_1, \sigma_1) = (8\epsilon_0, 0.01 \text{ S/m})$.

![img-2.jpeg](img-2.jpeg)

Fig. 3. Image of $\Delta\epsilon/\epsilon_0$ for the configuration shown in Fig. 2. The regularization parameter $\lambda = 0$.

with

$$W_{pp'}(\mathbf{K}) = \frac{\Delta\omega D^*(\mathbf{K}, z_r, \omega_{p'})}{\sqrt{4k_1^2(\omega_p) - |\mathbf{K}|^2} - \sqrt{4k_1^2(\omega_{p'}) - |\mathbf{K}|^2^*}}. \tag{40}$$

The equations for the 2.5-D case is straightforwardly obtained by following the same approached as that outlined in Section III-E.

#### IV. NUMERICAL EXAMPLES

To demonstrate the performance of the inversion scheme of this paper the 2.5-D configuration shown in Fig. 2 is considered. This configuration is similar to the one considered by Hansen and Meincke-Johansen in [4] and consists of an infinitely long $\hat{\mathbf{x}}$-directed circular cylinder with diameter 15 cm located at $(y, z) = (0, -1)$ m. In the first example, the constitutive parameters of the cylinder are $(\epsilon_c, \sigma_c) = (8.1\epsilon_0, 0.01 \text{ S/m})$, and those of the soil are $(\epsilon_1, \sigma_1) = (8\epsilon_0, 0.01 \text{ S/m})$. The GPR uses 60 frequencies equally spaced in the range 20 MHz < f < 1.3 GHz, where $f = \omega/(2\pi)$. Moreover, the ideal dipole antennas of the GPR are $\hat{\mathbf{x}}$ directed, have a fixed offset of $\Delta_y = -10$ cm and are located $z_r = 4$ cm above the interface. The synthetic scattering data are obtained from an exact method described in [13]. Fig. 3 shows the image of $\Delta\epsilon/\epsilon_0$ obtained from

![img-3.jpeg](img-3.jpeg)

Fig. 4. Image of $\Delta\epsilon/\epsilon_0$ for the configuration shown in Fig. 2. Gaussian noise with variance $10^{-4}$ is added and the regularization parameter $\lambda = 0$.

![img-4.jpeg](img-4.jpeg)

Fig. 5. Image of $\Delta\epsilon/\epsilon_0$ for the configuration shown in Fig. 2. Gaussian noise with variance $10^{-4}$ is added and the regularization parameter is given by $\lambda^2 = 5.10^{33}$.

(25), (30), (33) and (35) with $\lambda = 0$. It is noted that there are no artifacts below the pipe as was the case in [4, Fig. 5]. This shows that the method of this paper produces images of higher quality than that of [4] because the loss is rigorously taken into account. The example also shows that it is not necessary to regularize when $\sigma_1 = 0.01$ S/m and simultaneously, no noise is present in the data.

To show the need for regularization, consider again the configuration in Fig. 2 but for this second example, Gaussian noise with variance $10^{-4}$ is added to the radar data. Fig. 4 shows the image with $\lambda = 0$ and in Fig. 5, the regularization parameter is given by $\lambda^2 = 5 \cdot 10^{33}$. Clearly, the effect of increasing the regularization parameter is to reduce the impact of the noise. However, since also information about the object is filtered away when increasing $\lambda$, the estimate of the maximum value of $\Delta\epsilon/\epsilon_0$ is not as accurate as in Fig. 3 where no noise is present.

Authorized licensed use limited to: Danmarks Tekniske Informationscenter. Downloaded on March 23,2010 at 10:16:38 EDT from IEEE Xplore. Restrictions apply.

2720

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 39, NO. 12, DECEMBER 2001

![img-5.jpeg](img-5.jpeg)

Fig. 6. Image of $\Delta\sigma$ for the case in which the pipe in Fig. 2 is perfectly electrically conducting. The regularization parameter $\lambda = 0$.

In the final example, it is shown that the inversion scheme also can be used to detect perfectly electrically conducting (PEC) pipes, although the Born approximation in this case is violated.³ The configuration is the same as that shown in Fig. 2, except that the object is a PEC pipe. The image of $\Delta\sigma$, derived from the procedure described in Section III-F with $\lambda = 0$, is shown in Fig. 6. Of course, the maximum value of $\Delta\sigma$ is wrong, but a perfect estimate of the location of the PEC pipe is obtained. The center of the image is at the top surface of the pipe, as also was the case in [4].

# V. CONCLUSIONS AND FUTURE WORK

This paper presented a diffraction tomography inversion scheme for fixed-offset GPR that accounts for the loss in the soil and the planar air–soil interface. The inversion scheme was obtained by applying the Tikhonov-regularized pseudo-inverse operator to the approximate forward model (12). By using this forward model, which is valid for objects buried just a few center wavelengths from the air–soil interface, the filtering step becomes conveniently simple and consists of solving integral equations of the first kind. Through numerical examples, it was illustrated that a satisfactory image quality is obtained by solving these integral equations by simple quadrature. Indeed, the artifacts in the image produced by the method of [4] are no longer present when using the inversion scheme of this paper. The regularization parameter, however, is at present determined by trial and error. An efficient determination of the optimum regularization parameter is important to make the inversion scheme complete and future research will therefore address this problem. Another issue subject to future research is the derivation of an approximate forward model that also works for evanescent plane waves in the soil. With such an approximate forward model available images of higher resolution can be produced with the pseudo-inverse operator.

³In [14], it is explained why the linear inversion schemes based upon the Born approximation can be used to detect PEC objects.

# APPENDIX

This appendix explains why the various methods for determining the optimum regularization parameter $\lambda$ do not apply to the filtering step (20). The starting point is the singular value expansion (SVE) of the operator $\mathcal{L}$ in (14) [9, p. 6], [11, p. 86]

$$\mathcal{L}\Delta\epsilon_1 = \sum_{i=1}^{\infty} \mu_i v_i \langle \Delta\epsilon_1, u_i \rangle_U. \quad (41)$$

Herein, $\mu_i$ are the singular values and $u_i, v_i$ are the singular functions and the inner product in $U$ is defined in (15). The singular values $\mu_i$ are nonnegative and they can always be ordered in nonincreasing order such that $\mu_1 \geq \mu_2 \geq \mu_3 \geq \dots \geq 0$ [9, p. 7]. Similarly, the SVE of the adjoint operator $\mathcal{L}^\dagger$ is

$$\mathcal{L}^\dagger \tilde{s}_o = \sum_{i=1}^{\infty} \mu_i u_i \langle \tilde{s}_o, v_i \rangle_V \quad (42)$$

where the inner product in $V$ is defined in (16) and the SVE of $\mathcal{L}\mathcal{L}^\dagger$ is

$$\mathcal{L}\mathcal{L}^\dagger \tilde{s}_o = \sum_{i=1}^{\infty} \mu_i^2 v_i \langle \tilde{s}_o, v_i \rangle_V. \quad (43)$$

Consequently, the Tikhonov-regularized pseudo-inverse operator in (18) can in terms of the SVE be written as

$$\mathcal{L}^\dagger (\mathcal{L}\mathcal{L}^\dagger + \lambda^2 I)^{-1} \tilde{s}_o = \sum_{i=1}^{\infty} u_i \frac{\mu_i \langle \tilde{s}_o, v_i \rangle_V}{\mu_i^2 + \lambda^2}. \quad (44)$$

To obtain a square integrable solution $\Delta\epsilon_1$ from the Tikhonov-regularized pseudo-inverse operator, the summation over $i$ in (44) must converge. In fact, if there is no noise (such that the data $\tilde{s}_o$ belong to the range of $\mathcal{L}$), a square integrable solution must exist for $\lambda = 0$. Thus, to ensure convergence for $\lambda = 0$, the absolute value of the coefficients $\langle \tilde{s}_o, v_i \rangle_V$ in (44) must decay faster than the singular values $\mu_i$ for some $i$. This requirement is referred to as the Picard condition [9, p. 9].

Consider now the filtering step (20) and note that the operator $(\mathcal{L}\mathcal{L}^\dagger + \lambda^2 I)^{-1} \tilde{s}_o$ can be written as

$$(\mathcal{L}\mathcal{L}^\dagger + \lambda^2 I)^{-1} \tilde{s}_o = \sum_{i=1}^{\infty} v_i \frac{\langle \tilde{s}_o, v_i \rangle_V}{\mu_i^2 + \lambda^2}. \quad (45)$$

Since the Picard condition is satisfied for the original problem (18) as explained previously, the absolute value of the coefficients $\langle \tilde{s}_o, v_i \rangle_V$ are guaranteed to decay faster than the singular values $\mu_i$ of $\mathcal{L}$ for some $i$. However, they are not guaranteed to decay faster than $\mu_i^2$ for some $i$, and the summation in (45) will not converge for $\lambda = 0$. Consequently, the Picard condition for the filtering step (20) is violated and the methods for determining the optimum $\lambda$ can therefore not be applied to (20).

# ACKNOWLEDGMENT

The authors would like to thank the Danish Technical Research Council for supporting this work. Also, the author thanks Prof. A. J. Devaney and Prof. P. C. Hansen for helpful discussions on inverse problems and also Dr. T. B. Hansen for providing the synthetic data used in the numerical examples.

Authorized licensed use limited to: Danmarks Tekniske Informationscenter. Downloaded on March 23, 2010 at 10:16:38 EDT from IEEE Xplore. Restrictions apply.

MEINCKE: LINEAR GPR INVERSION

2721

# REFERENCES

[1] A. J. Devaney, "Geophysical diffraction tomography," IEEE Trans. Geosci. Remote Sensing, vol. GE-22, pp. 3-13, Jan. 1984.
[2] J. E. Molyneux and A. Witten, "Diffraction tomographic imaging in a monostatic measurement geometry," IEEE Trans. Geosci. Remote Sensing, vol. 31, pp. 507-511, Mar. 1993.
[3] A. Witten, J. E. Molyneux, and J. E. Nyquist, "Ground penetrating radar tomography: Algorithms and case studies," IEEE Trans. Geosci. Remote Sensing, vol. 32, pp. 461-467, Mar. 1994.
[4] T. B. Hansen and P. M. Johansen, "Inversion scheme for ground penetrating radar that takes into account the planar air-soil interface," IEEE Trans. Geosci. Remote Sensing, vol. 38, pp. 496-506, Jan. 2000.
[5] R. Deming and A. J. Devaney, "A filtered backpropagation algorithm for GPR," J. Environ. Eng. Geophys., pp. 113-123, Jan. 1996.
[6] ——, "Diffraction tomography for multi-monostatic ground penetrating radar imaging," Inv. Probl., pp. 29-45, Feb. 1997.
[7] D. M. Kerns, "Plane-wave scattering-matrix theory of antennas and antenna-antenna interactions," Tech. Rep. 162, Nat. Bureau Standards, Washington, DC, 1981.
[8] T. B. Hansen and A. D. Yaghjian, Plane-Wave Theory of Time-Domain Fields. New York: IEEE Press, 1999.
[9] P. C. Hansen, Rank-Deficient and Discrete Ill-Posed Problems. Philadelphia, PA: SIAM, 1997.
[10] G. M. Wing and J. D. Zahrt, A Primer on Integral Equations of the First Kind. The Problem of Deconvolution and Unfolding. Philadelphia, PA: SIAM, 1991.
[11] F. Natterer, The Mathematics of Computerized Tomography. New York: Wiley, 1986.
[12] P. M. Johansen, "A 2.5-D diffraction tomography inversion scheme for ground penetrating radar," in Proc. IEEE Antennas and Propagation Soc. Int. Symp., Orlando, FL, July 1999, pp. 2132-2135.
[13] T. B. Hansen and P. Meincke, "Scattering by a buried cylinder illuminated by a 3-D source," Radio Sci., to be published.
[14] B. Polat and P. Meincke, "A forward model for ground penetrating radar imaging of buried perfect electric conductors within the physical optics approximation," IEEE Trans. Geosci. Remote Sensing, to be published.

Peter Meincke was born in Roskilde, Denmark, on November 25, 1969. He received the M.S.E.E. and the Ph.D. degree from the Technical University of Denmark, Lyngby, in 1993 and 1996, respectively.

In the spring and summer of 1995, he was a Visiting Research Scientist with the Electromagnetics Directorate of Rome Laboratory, Hanscom Air Force Base, MA. In 1997, he was with a Danish cellular phone company, where he worked on theoretical aspects of radio wave propagation. In the spring and summer of 1998, he was visiting the Center for Electromagnetics Research, Northeastern University, Boston, MA, while holding a postdoctoral position from the Technical University of Denmark. In 1999, he became a Staff Member of Ørsted-DTU, Electromagnetic Systems, Technical University of Denmark, where he is now Associate Professor. His current teaching and research interests include electromagnetic theory, inverse problems, high-frequency and time-domain scattering, antenna theory, and ground penetrating radars.

Dr. Meincke won the first prize of the 1996 IEEE Antennas and Propagation Society student paper contest in Baltimore, MD, for his paper on uniform physical theory of diffraction equivalent edge currents. Also, he received the 2000 R. W. P. King paper award for his paper entitled "Time-domain version of the physical theory of diffraction" published in the February 1999 issue of the IEEE TRANSACTIONS ON ANTENNAS AND PROPAGATION.

Authorized licensed use limited to: Danmarks Tekniske Informationscenter. Downloaded on March 23, 2010 at 10:16:38 EDT from IEEE Xplore. Restrictions apply.