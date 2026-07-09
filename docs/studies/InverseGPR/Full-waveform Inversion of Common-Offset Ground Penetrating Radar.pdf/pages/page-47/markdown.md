GEOPHYSICS, VOL. 83, NO. 4 (JULY-AUGUST 2018): P. H27–H41, 17 FIGS., 2 TABLES.
10.1199/G0202017-0617.1

Check for updates

# Improving estimates of buried pipe diameter and infilling material from ground-penetrating radar profiles with full-waveform inversion

Sajad Jazayeri¹, Anja Klotzsche², and Sarah Kruse¹

# ABSTRACT

Ground-penetrating radar (GPR) is a widely used tool for the detection and location of buried utilities. Buried pipes generate characteristic diffraction hyperbolas in raw GPR data. Current methods for analyzing the shapes and timing of the diffraction hyperbolas are very effective for locating pipes, but they are less effective for determining the diameter of the pipes, particularly when the pipes are smaller than the radar wavelengths, typically a few tens of centimeters. A full-waveform inversion (FWI) method is described for improving estimates of the diameter of a pipe and confirming the infilling material (air/water/etc.) for the simple case of an isolated diffraction hyperbola on a profile run perpendicular to a pipe with antennas in broadside mode (parallel to the pipe). The technique described here can improve a good initial guess of the pipe diameter (within 30%–50% of the true value) to a better estimate (less than approximately 8% misfit). This method is developed by combining two freely available software packages with a deconvolution method for GPR effective source wavelet estimation. The FWI process is run with the PEST algorithm (model-independent parameter estimation and uncertainty analysis). PEST iteratively calls the gprMax software package for forward modeling of the GPR signal as the model for the pipe and surrounding soil is refined.

# INTRODUCTION

Modern life depends on subsurface pipelines used to carry water, oil, gas, sewage, and other fluids. Civil engineering and construction industries face the challenge of maintaining and repairing existing pipelines as well as laying new pipes. Increasing demand

for new buried utilities increases the risk of damaging existing utilities (Lester and Bernold, 2007). As infrastructure ages, the demand for repairs and replacement requires knowledge of the locations and connectivities of multiple utility systems installed at different times, using different materials, in increasingly dense networks, in which records are often incomplete. In such scenarios, simply detecting a pipe at a given location may not be sufficient information. Ground-penetrating radar (GPR) resolution of not only the presence of the pipe but also the pipe diameter, pipe material, or pipe-filling material (e.g., air, water) could be a way to distinguish and map different generations or types of utilities.

GPR has become one of the primary tools of choice for mapping the locations of pipes in urban settings. The transmitting antenna emits an electromagnetic (EM) pulse that propagates into the subsurface. The EM pulse travels through the subsurface material, and it is reflected, scattered, and attenuated. The reflection or scattering occurs when the pulse encounters a subsurface inhomogeneity, in particular, soil heterogeneities or targets with contrasting dielectric properties (permittivity). (We note that the permittivity here is expressed as relative permittivity, which is the ratio of the material permittivity to the permittivity of free space.) The pulse attenuation is primarily controlled by the electrical conductivity of the soil. Reflected energy is recorded by the receiving antenna. The signal recorded at the receiving antenna contains a combination of the energy traveling in air and along the ground surface, reflected and refracted energy from soil inhomogeneities, buried targets (in this case, pipes), and noise. A buried pipe generates a characteristic diffraction hyperbola because of its shape and contrast in EM properties with the background soil. The diffraction hyperbolas of pipes in GPR profiles are sufficiently distinctive that they can be displayed and interpreted in real time; hence, GPR is widely used for on-the-spot utility detection.

GPR responses expected from underground utilities, drums, tanks, and cables have been described in the literature. Early modeling by Zeng and McMechan (1997) describes responses for a variety of utility scenarios, with air-filled, water-filled, and partially

Manuscript received by the Editor 14 September 2017; revised manuscript received 4 December 2017; published ahead of production 09 March 2018; published online 25 April 2018.

¹University of South Florida, School of Geosciences, Tampa, Florida, USA. E-mail: sjazayeri@mail.usf.edu; skruse@usf.edu.

²Institute of Bio- and Geosciences, Agrosphere (IBG-3), Forschungszentrum Jülich, Jülich, Germany. E-mail: a.klotzsche@fz-juelich.de.

© 2018 Society of Exploration Geophysicists. All rights reserved.

H27

Downloaded 01/15/19 to 131.247.224.4. Redistribution subject to SEG license or copyright; see Terms of Use at http://library.seg.org/

37