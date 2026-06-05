Journal of Applied Geophysics 99 (2013) 83-90

ELSEVIER

Contents lists available at ScienceDirect

Journal of Applied Geophysics

journal.homepage: www.elsevier.com/locate/jappgeo

CARNES

# Characterizing the energy distribution around GPR antennas

Nectaria Diamanti a,\*, A. Peter Annan b

a Aristotle University of Thessaloniki, School of Geology, Department of Geophysics, GR-54 124, PO Box 352-1, Thessaloniki, Greece
b Sensors &amp; Software Inc., 1040 Stacey Court, Mississauga, L4W 2X8, ON, Canada

# ARTICLE INFO

Article history:

Received 22 December 2012

Accepted 2 August 2013

Available online 8 August 2013

Keywords:

Radiation patterns

Realistic 3D antenna numerical modeling

FDTD

Dipole antennas

Radiated energy

GPR

# ABSTRACT

Antenna height, orientation, shielding and subsurface properties all impact GPR responses. Although the basic concepts are generally understood, clarifying the key relationships can aid interpretation. Our long term goal is to develop easily parameterized models of transmitting and receiving components of GPR systems that will provide for quantitative interpretation of data acquired with real systems. Our first step was to develop modeling capacity and response presentation tools to help with development; the initial results have been both informative and forced a better understanding of near and far field.

We are using three-dimensional (3D) finite-difference time-domain (FDTD) modeling. Model results can be presented in a variety of forms. In this paper, we focus on presenting the emitted energy characteristics and use radiation pattern display format for infinitesimal dipoles, resistively loaded dipoles and shielded dipoles. Patterns are computed for a range of environments such as free-space and over loss-less half-spaces with various properties. The energy distribution patterns are presented to investigate the behavior with distance away from the transmitter feed point, and as a function of height above the ground surface.

The numerical simulations provide expected insights plus demonstrate the benefit of ground-coupling and the impact of shielding on GPR responses. Further, using the total radiated energy parameter is a novel method for displaying directivity, for GPR transient emissions.

© 2013 Elsevier B.V. All rights reserved.

# 1. Introduction

Antennas are the most important hardware components of a ground penetrating radar (GPR) system since they control the electromagnetic signal generated and detected. Optimum GPR performance requires antennas that transmit and receive broad frequency content with minimal phase shift when using short duration electromagnetic pulses.

Antenna characteristics change due to the interaction between the antenna system and the ground (and any other objects in close proximity, such as shields and support structure). The antenna's spatial and temporal (or amplitude and phase versus frequency) characteristics are thus controlled by the ground's proximity and material properties (Annan et al., 1975; Arcone, 1995; Diamanti et al., 2012; Engheta et al., 1982; Galagedara et al., 2005; Lampe and Holliger, 2005; Lampe et al., 2003; Oguz and Gurel, 2002; Radzevicius et al., 2003; Rutledge and Muha, 1982; Smith, 1984; Warren and Giannopoulos, 2011). Material property heterogeneity as well as surface irregularity can also be important but are not addressed here (Giannopoulos and Diamanti, 2005, 2008; Lampe and Holliger, 2003; van der Kruk et al., 2012).

Optimizing GPR antenna systems requires minimum energy transfer into the air and maximum energy into the ground, while at the same

time minimizing changes in the frequency response of the antenna with changes in height and ground properties. In a simplified sense, the main signal paths recorded during a GPR survey are signals "A" and "B" of Fig. 1, and the desired behavior of a GPR system would be to minimize signal "A" but maximize signal "B." Minimizing the emitted energy ("A") into the air is very important, since it addresses governmental spectrum management concerns over GPR radio frequency interference. Minimizing the upwardly emitted energy also reduces GPR responses from above ground clutter. While the basic physical behavior is understood from analytical solutions and numerical modeling for infinitesimal dipoles, characterizing real finite-sized antennas with shielding structures is challenging and not easily parameterized.

While the response of a real antenna and shield structure can be simulated, the computation time and computer memory needs currently make full simulation impractical for anything but specialized research needs. Our long term goal is to develop a standardized means of parameterizing ground-coupled antennas that can help to both optimize system design as well as provide parameterized transfer functions (or impulse responses) of the antenna system, enabling quantitative GPR interpretations without the need of substantial computational resources. A successful attempt was performed by Lambot et al. (2010) who modeled the near field of bowties using a series of infinitesimal electric dipole sources.

In this paper, we use finite-difference time-domain (FDTD) (Taflove, 1995; Yee, 1966) numerical modeling to explore system responses to changes in soil permittivity and height above the subsurface. For the

0926-9851/$ - see front matter © 2013 Elsevier B.V. All rights reserved.

http://dx.doi.org/10.1016/j.jappgeo.2013.08.001

N. Diamanti, A.P. Annan / Journal of Applied Geophysics 99 (2013) 83-90

![img-0.jpeg](img-0.jpeg)
Fig. 1. Oversimplified signal paths of a GPR survey. "A" represents the emitted energy into air and "B" is the radiated signal from subsurface targets, which is recorded by the GPR receiver.

antenna system, we modeled infinitesimal dipoles, resistively loaded dipoles and shielded resistively loaded dipoles, all having a center frequency equal to $1000\mathrm{MHz}$. The center frequency is largely immaterial in these discussions since physical size and frequency scale, in the low-loss examples considered. A center frequency of $1000\mathrm{MHz}$ was selected to allow comparison with physical model data which can be acquired in a controlled small scale setting (the physical modeling is not addressed in this paper and is part of a later phase of the project).

FDTD models generate a large amount of data. Many aspects of the response can be displayed, depending on the desired point of view. Since a diagnostic indicator is the direction that energy is transmitted, we chose to display the model results in a directivity (radiation pattern) display format. Size limitations placed on the numerical models by computer memory and computation speed only allowed us to explore field behavior in the transition region from near to far-field. Since most of the GPR targets are in the near to intermediate distance from the antenna system, understanding the near and intermediate field behavior is often more relevant than the far field.

# 2. Antenna radiation pattern definition

An antenna radiation pattern is defined as a mathematical function or a graphical representation of the radiated power from an antenna or radiating object as a function of spatial direction. The radiation pattern is normally determined in the far-field region and is usually represented as a function of angular direction in spherical polar coordinates (Balanis, 2008; IEEE, 1983). While far-field assumption is seldom applicable for GPR, as previously mentioned, radiation patterns display concepts are very useful. We developed the following protocol for displaying our results that are described below.

First, we defined the spherical polar coordinates based on the source being a dipole type antenna. Since we are focusing on horizontal dipole antennas, the vertical plane containing the antenna is called $E$-plane for the electric field and the vertical plane perpendicular to the antenna axis is the $H$-plane for the magnetic field. Fig. 2 shows a typical dipole, the $E$- and $H$-planes, the spherical polar angles $\theta$ and $\varphi$, and the Cartesian coordinate system $(x,y,z)$ used.

Since we were limited to a finite sized numerical model, there is finite limit on the distance that we could compute the fields from the antenna. Understanding what behavior the fields should have at the

![img-1.jpeg](img-1.jpeg)
Fig. 2. $E$- and $H$-planes of a dipole oriented along the $y$-axis.

maximum distance from the source constrained by this limit is helpful. According to Kraus (1988) the space around an antenna can be divided into three regions (Fig. 3):

- The region immediately surrounding the antenna, the reactive near-field region (the reactive field - stored energy/standing waves - is dominant).
- The near-field or Fresnel zone region (radiation fields are dominant and the field distribution is dependent on the distance from the antenna).
- The far-field or Fraunhofer region (field distributions are assumed to be independent of the distance from the antenna - and are outwardly propagating waves).

The boundary between the far-field and the near-field Fresnel region can be taken to be at a distance $R$ from the antenna feed, which is equal to

$$
R = \frac {2 d ^ {2}}{\lambda} \tag {1}
$$

where $\lambda$ is the wavelength in meters, and $d$ is the largest dimension of the antenna, or it is equal to $\lambda$, whichever is greater. That means that the boundary between the far-field and the Fresnel region for an antenna that is short relative to the wavelength $\lambda$ is normally taken to be at a distance $2\lambda$ from the antenna feed (Kraus, 1988). For an ultra-wideband (UWB) pulse, with a wavelength $\lambda_{\mathrm{c}}$ at the center frequency, the typical spectrum of wavelengths would span approximately $2\lambda_{\mathrm{c}}$ to $\lambda_{\mathrm{c}} / 2$. Thus,

![img-2.jpeg](img-2.jpeg)
Fig. 3. Antenna field regions (modified from Kraus, 1988).

N. Diamanti, A.P. Annan / Journal of Applied Geophysics 99 (2013) 83-90

for GPRs a more appropriate choice for the distance from the antenna feed to the start of the far-field would be $4\lambda_{\mathrm{c}}$. For GPR systems, we need to consider $\lambda$ in the air and the subsurface.

Our FDTD modeling generated transient responses on a three-dimensional (3D) mesh at defined Cartesian coordinate locations. We transformed the model data to a spherical polar component form, so we could display responses in a radiation pattern format. Since we would be primarily in the intermediate to far-field, we felt it permissible to ignore the radial component of the electric field and focus on the tangential field components $E_{\theta}$ and $E_{\varphi}$.

To characterize the $E$-plane pattern (i.e., $yz$-slices), we used the $E_{\theta}$ field component, which is given in Cartesian coordinates by

$$
E _ {\theta} = E _ {y} \frac {z}{\sqrt {y ^ {2} + z ^ {2}}} - E _ {z} \frac {y}{\sqrt {y ^ {2} + z ^ {2}}} \quad \text{at} \quad \varphi = 9 0 ^ {\circ}, 2 7 0 ^ {\circ} \tag {2}
$$

Similarly, for the $H$-plane patterns (i.e., $xz$-slices) the $E_{\varphi}$ field component was employed, which in Cartesian coordinates is equal to

$$
E _ {\varphi} = E _ {y} \quad \text{at} \quad \varphi = 0 ^ {\circ}, 1 8 0 ^ {\circ} \tag {3}
$$

Since we normally work in time-domain, we needed to define how we would create a time independent pattern. It is important to remark that displaying an antenna pattern at a single frequency is traditional but not helpful, nor entirely trustworthy for typical UWB GPR signals, as it will be presented in a later section. We decided that displaying total emitted energy in a given angular direction, obtained by integrating over time would provide the most representative display parameter, $\varepsilon(r,\theta)$, where

$$
\varepsilon (r, \theta) = \int_ {0} ^ {\infty} \frac {E (r , \theta) ^ {2}}{Z} d t \tag {4}
$$

with $E$ being either tangential component of the field and $Z$ is the electromagnetic impedance. Given that parts of the volume are above the ground and parts below the ground, we need to consider using both the air and subsurface impedance depending on observation angle. The use of total energy defined by Eq. (4) for display in radiation pattern form is a novel means of presenting transient data (note that wideband data in frequency domain can use a similar construct where the integration is over all frequencies rather than presenting the field for a single frequency).

To scale or normalize the total energy parameter, we took different approaches for the infinitesimal and finite sources. For the infinitesimal Hertzian dipoles we present the radiated energy per steradian for the whole time window of the simulation. For the radiation patterns of the finite size shielded and/or unshielded resistively loaded dipoles, we display the energy as a directivity gain, where the radiated energy per steradian is divided by the input energy at the source. In all cases, the pattern is at a defined radial distance, $r$, from the center of the transmit antenna. In the true far field $\varepsilon(r,\theta) \rightarrow \varepsilon(\theta)$, as $r \rightarrow \infty$.

# 3. GPR numerical models

To obtain our numerical results, we used GprMax3D (Giannopoulos, 2005) software. This is a well-known GPR simulator that employs 3D FDTD numerical modeling (Taflove, 1995; Yee, 1966) and which has been applied to various cases, from modeling pavement cracks (Diamanti and Redman, 2012), rough interfaces and subsurface heterogeneities (Giannopoulos and Diamanti, 2008; van der Kruk et al., 2012), to modeling real GPR antenna systems (Diamanti et al., 2012; Warren and Giannopoulos, 2011) and assisting GPR data interpretation (Allred and Redman, 2010).

For the Hertzian point dipoles, the excitation current was the first derivative of a Gaussian pulse of unit amplitude with the pulse width selected to give a $1000\mathrm{MHz}$ center frequency spectrum. When we modeled

resistively loaded dipoles, with and without a shield, we used a voltage source at the transmitting dipole $(T_{\mathrm{a}})$ feed point that was a Gaussian waveform. A model structure for the shielded dipoles is shown in Fig. 4. Both $T_{\mathrm{a}}$ and $R_{\mathrm{a}}$ dipoles are placed on a potted printed circuit board (PCB).

For all 3D models we employed a uniform $1\mathrm{mm}$ spatial-step to mesh the computational domain. Such a small spatial mesh is needed to model all the fine details in the real antenna structure. The receiving dipole $(R_{\mathrm{e}})$ was set $70~\mathrm{mm}$ from the $T_{\mathrm{a}}$ in the positive $x$-direction and both dipoles are oriented along the $y$-direction. We modeled all media as non-magnetic with constitutive properties that are independent of frequency.

We created patterns for the $E$- and $H$-planes using the field components at two degrees $(2^{\circ})$ intervals in $\theta$. For most of the results presented here, we used $r = 0.25\mathrm{m}$, unless otherwise stated. According to Eq. (1), which yields $R = 0.6\mathrm{m}$ (i.e., $2\lambda$ at a $1000\mathrm{MHz}$ in air) for our dipoles in free-space, we are measuring the electromagnetic fields in the radiating near-field region (our modeling results suggest that the transition to the far-field region occurs beyond $10\lambda$ away from the dipole). With UWB GPR signal bandwidth spanning 1 to 3 octaves, the definition of near and far-field is indeed fuzzy for impulsive UWB systems.

# 4. Modeling results

## 4.1. Free-space

Even though free-space radiation patterns are of little practical use, our first goal was to confirm consistent results in the simplest case of a homogeneous space, in this case air or free-space. Further, we used the infinitesimal Hertzian dipole results to compare with the analytically computable response. The point dipole response shown in Fig. 5 displays the classic dipole directivity behavior, in both $E$- and $H$-planes. Even though the radiation patterns of infinitesimal dipoles are of limited use for most real GPR data, we often use them to:

a. check reliably our numerical modeled energy, and
b. to explore larger radial distances by using a coarser grid (a finer, computationally expensive grid is needed to emulate the real antenna structure details).

Figs. 6 and 7 show the response for (a) a $T_{\mathrm{a}} - R_{\mathrm{e}}$ unshielded dipole antenna system and for (b) a shielded finite resistive dipole antenna

![img-3.jpeg](img-3.jpeg)
Fig. 4. Schematic of a shielded antenna system with each of the $T_{\mathrm{a}}$ (left) and $R_{\mathrm{e}}$ (right) located on a potted PCB.

N. Diamanti, A.P. Annan / Journal of Applied Geophysics 99 (2013) 83-90

![img-4.jpeg](img-4.jpeg)

![img-5.jpeg](img-5.jpeg)

![img-6.jpeg](img-6.jpeg)
Fig. 5. Energy per steradian for an infinitesimal dipole located in free-space. (a)  $E$ -plane and (b)  $H$ -plane.

![img-7.jpeg](img-7.jpeg)
Fig. 6. Energy directivity gain for an unshielded dipole antenna configuration located in free-space. (a)  $E$ -plane and (b)  $H$ -plane.

configuration, respectively. A model structure for the shielded dipoles is shown in Fig. 4. The radiation patterns of unshielded dipoles (Fig. 6) and the infinitesimal dipoles are almost identical (Fig. 5). In Fig. 7, it is clear that the presence of the shield greatly reduces the energy going up, as expected. The asymmetry in the  $H$ -plane in both Figs. 6 and 7 is also expected since the  $R_{a}$  antenna and the shield, when present, are not symmetric with respect to the  $T_{a}$  feed point. Currents are induced to flow on the shield and the  $R_{n}$ , and contribute to the emitted energy in a nonsymmetric fashion.

# 4.2. Lossless half-space: permittivity impact

The lossless half space illustrates the impact of permittivity and height changes. Again, the behavior of point dipoles is understood but the effect

of finite antennas with shielding is less clear. For the numerical models, the  $T_{a} - R_{a}$  pair is placed at a height  $h$  (default being  $2\mathrm{cm}$  unless otherwise stated) above the air-ground interface. The half-space has various values of relative permittivity  $(c_{s})$ .

Fig. 8 illustrates the energy for the case of resistively loaded dipoles without a shield and for a range of half-space permittivities. The results when the shield is added are shown in Fig. 9. The results are presented as gain in dB (i.e., logarithmic form) since the air component is very small in both cases and not readily visible on a linear plot. Note that the  $E$ -plane patterns exhibit a spike at the air-ground interface owing to the discontinuity of the vertical electric field at the interface; the energy computation requires selecting a single value of  $Z$  and since we are dealing with a discretized mesh and transforming to polar angle coordinates, the point of transition from above to below ground is not

N. Diamanti, A.P. Annan / Journal of Applied Geophysics 99 (2013) 83-90

![img-8.jpeg](img-8.jpeg)

![img-9.jpeg](img-9.jpeg)
Fig. 7. Energy directivity gain for a shielded antenna system located in free-space. (a)  $E$ -plane and (b)  $H$ -plane.

cleanly defined and can yield an indeterminant value as a point spike since wrong value of impedance may be applied. The spiky nature in the polar display can be disconcerting but is only an artifact of discrete nature of the calculations and presentation.

The impact of the lower half-space is clearly visible. The vast majority of the energy is pulled into the ground. The shield is only a minor contributor to getting the majority of energy to go into the ground. As expected, increasing permittivity increases the energy transmitted downward. Moreover, the energy lobe in the half-space becomes narrower as  $\varepsilon_{\mathrm{r}}$  is increased, for both the  $E-$  and  $H$  -plane patterns, as expected. For the unshielded dipoles, the energy radiated in air changes little with  $\varepsilon_{\mathrm{r}}$ . When the shield is present (Fig. 9), energy propagating up into the air is reduced when compared to the unshielded dipole case (Fig. 8) but increases slightly as  $\varepsilon_{\mathrm{r}}$  increases which is somewhat counter intuitive indicative of current flow on the shield. Further, the  $E$  -plane

![img-10.jpeg](img-10.jpeg)

![img-11.jpeg](img-11.jpeg)
Fig. 8. Energy directivity gain in dB for bare resistively loaded dipoles located above a half-space with various values of  $\varepsilon_{\mathrm{r}}$ . (a)  $E$ -plane and (b)  $H$ -plane.

directionality is substantially different indicating that currents are flowing on the shield and these currents increase in strength as the half space permittivity increases.

Traditionally, radiation patterns are displayed at a single frequency. For GPR, the frequency chosen to be representative is the antenna center frequency. Using this approach makes it difficult to have representative display of wideband signals such as UWB GPR signals. An example is shown in Fig. 10, where we display the  $E$ -plane radiation patterns for two different dielectrics and at a single frequency of  $1000\mathrm{MHz}$ . In this modeled  $E$ -plane pattern, there are multiple lobes associated with interfering signals which disappear when we use the total radiated energy over the whole frequency range of the simulation (Fig. 9a).

# 4.3. Lossless half-space: radial distance impact

The far-field behavior for dipoles over half-space known from analytical solutions (Engheta et al., 1982) was not observed from our numerical results of the previous section. We decided to move our observation

N. Diamanti, A.P. Annan / Journal of Applied Geophysics 99 (2013) 83-90

![img-12.jpeg](img-12.jpeg)

![img-13.jpeg](img-13.jpeg)
Fig. 9. Energy directivity gain in dB for a shielded antenna system located above a half-space with various dielectric properties. (a)  $E$ -plane and (b)  $H$ -plane.

radius around the  $T_{s}$  dipole further out. We computed radiation patterns at various radial distances, ranging from  $r = 0.25\mathrm{m}$  to  $r = 1.9\mathrm{m}$ . Due to computational constraints, it was not possible to explore the behavior of the finite antenna system at such large distances. So, we explored radial distance impact using infinitesimal Hertzian dipoles.

With the ground relative permittivity of 9 and we computed the  $E$ - and  $H$ -plane patterns for a point dipole for radial distances  $r$  of 0.25, 1.0 and  $1.9\mathrm{m}$  away from the source. Fig. 11 shows the normalized field patterns. When we are at a distance of  $0.25\mathrm{m}$ , our radiation patterns do not exhibit far-field behavior. This radius represents a distance of  $2.5\lambda_{c}$  in the half-space of relative permittivity equal to 9, and according to Eq. (1) we should be at the boundary of near-field and far-field. For the case of  $r = 1.0\mathrm{m}$ , the patterns start to behave more like the asymptotic analytical solutions. At a radius of  $1.9\mathrm{m}$ , the expected far-field radiation pattern behavior is apparent. While we have not explored a large number of cases, this general behavior is consistent with all the modeling and confirms what we previously believed, that far-field transition really occurs at a greater distance than might traditionally be thought.

![img-14.jpeg](img-14.jpeg)
Fig. 10. Power in dB for a shielded antenna system located above a half-space (E-plane). Only in this figure, the radiation pattern is plotted for a single frequency (i.e.,  $1000\mathrm{MHz}$ ).

# 4.4. Lossless half-space: elevation impact

The impact of height of the antenna system over the ground is known to be large. Asymptotic analytical solutions provided good indications of the change in directivity but the change in gain or absolute signal level is not as well understood. Our current modeling system limited the maximum radial distance for the fully modeled antenna and shield system to less than  $0.3\mathrm{m}$ . Larger models proved too computationally expensive in both memory requirements and execution time. To see the change in pattern directivity predicted from asymptotic solutions we needed to use a larger model that enabled getting out to radial distances of  $\sim 2.0\mathrm{m}$ . As shown in the previous section, at a distance of  $\sim 0.3\mathrm{m}$ , there is still substantial evanescent energy present and the directivity change with antenna height does not develop as clearly.

We illustrate the impact of height using infinitesimal dipoles at a radial distance of  $1.9\mathrm{m}$  in Fig. 12 (note that this plot has a linear scale, not a logarithmic). The lossless ground had an  $\varepsilon_{c}$  equal to 9 for all cases, while the antenna height ranged from 0 to  $21~\mathrm{cm}$ . There are four immediate observations:

1. Energy at and beyond the critical angle  $(-160^{\circ}$  and  $200^{\circ}$ ) decreases rapidly as height increases (this energy is evanescent in the air).
2. The bore sight (straight down at  $180^{\circ}$ ) always decreases with height.
3. The main lobes (straight down at  $180^{\circ}$ ) become more focused and directive with height
4. The energy entering the air increases with height.

The above confirms the observation by Smith (1984), that the antenna height above the ground surface should be less than  $0.1\lambda_0$  (where,  $\lambda_0$  is the free-space wavelength), to achieve good ground coupling and downward directivity.

# 5. Discussion and conclusions

We have established a modeling platform to allow quantitative exploration of a variety of factors that affect GPR responses. We have also developed a novel, systematic means for displaying UWB antenna radiation patterns that have broad utility. We decided that showing the total radiated energy over the whole pulse frequency spectrum is clearer and more representative than displaying field amplitude at a single frequency, as it has been conventionally done to date.

N. Diamanti, A.P. Annan / Journal of Applied Geophysics 99 (2013) 83-90

![img-15.jpeg](img-15.jpeg)

![img-16.jpeg](img-16.jpeg)

![img-17.jpeg](img-17.jpeg)
Fig. 11. Normalized energy per steradian for infinitesimal dipoles located over a lossless half-space with  $\varepsilon_{\mathrm{r}} = 9$ , at various radial distances  $r$ . (a)  $E$ -plane and (b)  $H$ -plane.

![img-18.jpeg](img-18.jpeg)
Fig. 12. Energy per steradian for infinitesimal dipoles located at various heights  $h$  over a lossless half-space with  $\varepsilon_{\mathrm{r}} = 9$ . (a)  $E$ -plane and (b)  $H$ -plane.

We presented radiation patterns of GPR dipoles - infinitesimal, unshielded and shielded - located in free-space and over a range of lossless half-spaces. Further, we displayed the total emitted energy at a range of radial distances away from  $T_{\mathrm{n}}$ , and at various heights over the air-ground interface. Our FDTD antenna model dealt with all the detailed geometry and main components of a real antenna system. This is a step forward, as most of the former studies addressed in the literature mainly focus on simplistic numerical models.

The most interesting concluding observations from work to date are:

- The transition to far-field behavior is at a much larger distance (typically  $\sim 10\lambda_0$ ) than previously thought. This has considerable implications for GPR interpretation.
- Shielding is not needed to get substantial energy into the ground but can slightly decrease energy emitted into the air.

- The shield and  $R_{\mathrm{s}}$  also contribute to transmitted signals and since these elements are asymmetrical in position with respect to the  $T_{\mathrm{s}}$  feed, an asymmetric directivity results.
- Keeping antenna height to a minimum is highly beneficial in assuring that energy goes into the subsurface.

This study is the start of a longer term project to develop parameterized transfer functions that will enable rapid quantitative interpretation. We are currently working in studying the change of the pulse shape with angle and looking more closely at near-field versus far-field results. Future work also includes comparing modeled results with measured data.

# Acknowledgment

The authors would like to thank J.D. Redman for the fruitful discussions and for his valuable contribution to this study.

90
N. Diamanti, A.P. Annan / Journal of Applied Geophysics 99 (2013) 83-90

# References

Allred, B.J., Redman, J.D., 2010. Location of agricultural drainage pipes and assessment of agricultural drainage pipe conditions using ground penetrating radar. Journal of Environmental and Engineering Geophysics 15, 119-134.
Annan, A.P., Waller, W.M., Strangway, D.W., Rossiter, J.R., Redman, J.D., Watts, R.D., 1975. The electromagnetic response of a low-loss two-layer dielectric earth for horizontal electric dipole excitation. Geophysics 40, 285-298.
Arcone, S.A., 1995. Numerical studies of the radiation patterns of resistively loaded dipoles. Journal of Applied Geophysics 33, 39-52.
Balanis, C.A., 2008. Modern Antenna Handbook. John Wiley &amp; Sons.
Diamanti, N., Redman, J.D., 2012. Field observations and numerical models of GPR response from vertical pavement cracks. Journal of Applied Geophysics 81, 106-116.
Diamanti, N., Annan, A.P., Redman, J.D., 2012. Quantifying GPR Responses. Proceedings of the 14th International Conference on Ground Penetrating Radar, GPR2012.
Engheta, N., Papas, C., Elachi, C., 1982. Radiation patterns of interfacial dipole antennas. Radio Science 17, 1557-1566.
Galagedara, L., Redman, J.D., Parkin, G., Annan, A.P., Endres, A., 2005. Numerical modeling of GPR to determine the direct ground wave sampling depth. Vadose Zone Journal 4, 1096-1106.
Giannopoulos, A., 2005. Modelling of ground penetrating radar using GprMax. Construction and Building Materials 19, 755-762.
Giannopoulos, A., Diamanti, N., 2005. Modelling the effects of subsurface heterogeneity on ground penetrating radar signals. Proceedings of the 11th Meeting of Environmental and Engineering Geophysics, Expanded Abstracts.
Giannopoulos, A., Diamanti, N., 2008. Numerical modeling of Ground Penetrating Radar response from rough subsurface interfaces. Near Surface Geophysics 6, 357-369.
IEEE, 1983. Standard Definitions of Terms for Antennas. IEEE Std 145-1983.
Kraus, J.D., 1988. Antennas. McGraw-Hill International Editions.

Lambot, S., Andre, F., Jadoon, K., Slob, E., Vereecken, H., 2010. Full-waveform modeling of ground-coupled GPR antennas for wave propagation in multilayered media: the problem solved? Proceedings of the 13th International Conference on Ground Penetrating Radar, GPR2010, pp. 898-902.
Lampe, B., Holliger, K., 2003. Effects of fractal fluctuations in topographic relief, permittivity and conductivity on ground-penetrating radar antenna radiation. Geophysics 68, 1934-1944.
Lampe, B., Holliger, K., 2005. Resistively loaded antennas for ground-penetrating radar: a modeling approach. Geophysics 70, K23-K32.
Lampe, B., Holliger, K., Green, A.G., 2003. A finite-difference time-domain simulation tool for ground-penetrating radar antennas. Geophysics 68, 971-987.
Oguz, U., Gurel, L., 2002. Frequency responses of ground-penetrating radars operating over highly lossy grounds. IEEE Transactions on Geoscience and Remote Sensing 40, 1385-1394.
Radzevicius, S.S., Chen, C.C., Peters, L.J., Daniels, J.J., 2003. Near-field radiation dynamics through FDTD modeling. Journal of Applied Geophysics 52, 75-91.
Rutledge, D., Muha, M., 1982. Imaging antenna arrays. IEEE Transactions on Antennas and Propagation 30, 535-540.
Smith, G.S., 1984. Directive properties of antennas for transmission into a material half-space. IEEE Transactions on Antennas and Propagation 32, 232-246.
Taflove, A., 1995. Computational Electrodynamics: The Finite-Difference Time-Domain Method. Artech House.
van der Kruk, J., Diamanti, N., Giannopoulos, A., Vereecken, H., 2012. Inversion of waveguide induced dispersive GPR data including heterogeneities, interface roughness and dipping interfaces. Journal of Applied Geophysics 81, 88-96.
Warren, C., Giannopoulos, A., 2011. Creating finite-difference time-domain models of commercial ground-penetrating radar antennas using Taguchi's optimization method. Geophysics 76, G37-G47.
Yee, K.S., 1966. Numerical solution of initial boundary value problems involving Maxwell's equations in iso-tropic media. IEEE Transactions on Antennas and Propagation 14, 302-307.