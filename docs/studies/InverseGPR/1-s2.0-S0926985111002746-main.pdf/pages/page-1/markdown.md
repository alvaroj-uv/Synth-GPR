Journal of Applied Geophysics 78 (2012) 31–43

ELSEVIER

Contents lists available at ScienceDirect

Journal of Applied Geophysics

journal homepage: www.elsevier.com/locate/jappgeo

APPLIED GEOPHYSICS

# Taming the non-linearity problem in GPR full-waveform inversion for high contrast media☆

Giovanni Meles a,*, Stewart Greenhalgh a,b, Jan van der Kruk c, Alan Green a, Hansruedi Maurer a

a Institute of Geophysics, ETH Zurich, Sonneggstrasse 5, 8092, Zurich, Switzerland

b Department of Physics, University of Adelaide, 5005 Adelaide, South Australia

c Forschungszentrum Jülich, 52425 Jülich, Germany

# ARTICLE INFO

Article history:

Received 18 October 2010

Accepted 3 January 2011

Available online 26 December 2011

Keywords:

GPR

FDTD

Inversion

Time-domain

Frequency-domain

Bandwidth expansion

Stability

# ABSTRACT

We present a new algorithm for the inversion of full-waveform ground-penetrating radar (GPR) data. It is designed to tame the non-linearity issue that afflicts inverse scattering problems, especially in high contrast media. We first investigate the limitations of current full-waveform time-domain inversion schemes for GPR data and then introduce a much-improved approach based on a combined frequency-time-domain analysis. We show by means of several synthetic tests and theoretical considerations that local minima trapping (common in full bandwidth time-domain inversion) can be avoided by starting the inversion with only the low frequency content of the data. Resolution associated with the high frequencies can then be achieved by progressively expanding to wider bandwidths as the iterations proceed. Although based on a frequency analysis of the data, the new method is entirely implemented by means of a time-domain forward solver, thus combining the benefits of both frequency-domain (low frequency inversion conveys stability and avoids convergence to a local minimum; whereas high frequency inversion conveys resolution) and time-domain methods (simplicity of interpretation and recognition of events; ready availability of FDTD simulation tools).

© 2011 Published by Elsevier B.V.

# 1. Introduction

Ground-penetrating radar (GPR) finds wide application in diverse areas of civil engineering and environmental investigations, such as buried utilities mapping, concrete and pavement inspection, rail track surveillance, UXO detection, hydrology, sedimentology, etc. The technique is also popular in archaeology and glaciology, as witnessed by the large number of such papers recently presented at the 13th International GPR conference in Lecce, Italy (GPR, 2010). Surface implementations of the technique largely rely on migration algorithms (Heinke et al., 2005; Streich et al., 2006; van der Kruk et al., 2003) to image the geometry of buried targets from the scattered signals. Such reflector detection and delineation schemes are akin to wavefield migration procedures commonly used in the more mature field of seismic exploration (Claerbout, 1985; Yilmaz and Doherty, 2001) and to focussed-lag sum processors used in the early days of microwave medical imaging (Fear and Stuchly, 2000; Hagness et al., 1998). These migration-style schemes use the full waveforms, but they stop short of an actual inversion in that

they do not fully recover the medium (electrical) properties. By contrast, crosshole GPR studies have been mainly based on first arrival traveltime and amplitude tomography using the direct transmitted arrivals to image the relative permittivity εr and conductivity σ variations in the interhole medium (e.g., Carlsten et al., 1995; Clement and Barrash, 2006; Fullagar et al., 2000; Musil et al., 2006; Olsson et al., 1992; Tronicke et al., 2001). Because such image reconstruction procedures use only a small amount of the available information, they provide only limited resolution. Imaging low velocity (high permittivity) zones is especially difficult because first arrival raypaths tend to by-pass such features. Full-waveform inversion offers the promise of far better imaging capabilities. Early versions of full-waveform electromagnetic (EM) inversion (both radar and microwave) were based on the Born approximation of weak scattering (i.e., for low contrast targets), thus neglecting secondary interactions between obstacles (Chew and Wang, 1990; Wang and Chew, 1989). This linearised the problem. Furthermore, it was often assumed that the background medium was homogeneous, for which analytic Green's functions were available. Similar assumptions were incorporated in early seismic inversion approaches. The pioneering seismic waveform papers by Tarantola (1986) and Mora (1987) did not impose such restrictions. These fully elastodynamic seismic inversion schemes suffered from limited computational resources available at the time, and were not adopted until 10–20 years later (Charara et al., 1996, 2000; Plessix, 2008).

Kuroda et al. (2007) and Ernst et al. (2007a) were among the first researchers to tackle theoretically, crosshole full-waveform GPR

☆ A publishers' error resulted in this article appearing in the wrong issue. The article is reprinted here for the reader's convenience and for the continuity of the special issue. For citation purposes, please use the original publication details: Meles, G., et al., Taming the non-linearity problem in GPR full-waveform inversion for high contrast media, J. Appl. Geophys. (2011), doi:10.1016/j.jappgeo.2011.01.001.

* Corresponding author.

E-mail address: meles@aug.ig.erdw.ethz.ch (G. Meles).

0926-9851/$ – see front matter © 2011 Published by Elsevier B.V.

doi:10.1016/j.jappgeo.2011.12.001