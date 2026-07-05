M. Sun et al. / Signal Processing 132 (2017) 272–283

283

time delay) and the noise being a Gaussian white noise with zero mean and variance $\sigma^2$. Referring to Eq. (1), the joint probability density function for all observations can be calculated:

$$f(\mathbf{r}, b_k) = \frac{1}{(\pi \sigma^2)^N} \exp \left\{ - \frac{\sum_{i=1}^N |r(f_i) - \sum_{k=1}^K s_k e(f_i) \exp(-j2\pi f_i \hat{t}_k - b_k f_i^2)|^2}{\sigma^2} \right\}$$

In practice, MLE is obtained by maximizing a log-likelihood function $L(\mathbf{r}, b_k)$ instead of the joint density function $f(\mathbf{r}, b_k)$ as follows:

$$L(\mathbf{r}, b_k) = \ln f(\mathbf{r}, b_k)$$

$$= - \frac{\sum_{i=1}^N |r(f_i) - \sum_{k=1}^K s_k e(f_i) \exp(-j2\pi f_i \hat{t}_k - b_k f_i^2)|^2}{\sigma^2} - N \ln(\pi \sigma^2)$$

The optimal estimation (for the roughness parameters $b_k$) is obtained by finding the solution of $\frac{d(\mathbf{r}, b_k)}{db_k} = 0$.

# References

[1] A.P. Annan, N. Diamanti, J.D. Redman, S.R. Jackson, Ground-penetrating radar for assessing winter roads, Geophysics 81 (2016) WA101–WA109.

[2] A. Benedetto, L. Pajewski, Civil Engineering Applications of Ground Penetrating Radar, Springer International Publishing, Switzerland, 2015.

[3] A.S. Venkatachalam, X. Xu, D. Huston, T. Xia, Development of a new high speed dual-channel impulse ground penetrating radar, IEEE J. Sel. Top. Appl. Earth Obs. Remote. Sens. 7 (2014) 753–760.

[4] D.H. Chen, F. Hong, W. Zhou, P. Ying, Estimating the hotmix asphalt air voids from ground penetrating radar, NDT E Int. 68 (2014) 120–127.

[5] H. Liu, M. Sato, In situ measurement of pavement thickness and dielectric permittivity by GPR using an antenna array, NDT E Int. 64 (2014) 65–71.

[6] J. Lee, C. Nguyen, T. Scullion, A novel, compact, low-cost, impulse ground-penetrating radar for nondestructive evaluation of pavement, IEEE Trans. Instrum. Meas. 53 (2004) 1502–1509.

[7] T. Saarenketo, T. Scullion, Road evaluation with ground penetrating radar, J. Appl. Geophys. 43 (2000) 119–138.

[8] S. Lee, E. Millos, R. Greiner, J. Rossiter, A. Venetsanopoulos, On the machine analysis of radar signals for ice profiling, Signal Process. 18 (1989) 371–386.

[9] U. Spagnolini, V. Rampa, Multitarget detection/tracking for monostatic ground penetrating radar: application to pavement profiling, IEEE Trans. Geosci. Remote. Sens. 37 (1) (1999) 383–394.

[10] I.L. Al-Qadi, S. Lahouar, Measuring layer thickness with GPR-theory to practice, Constr. Build. Mater. 19 (10) (2005) 763–772.

[11] S. Lahouar, I.L. Al-Qadi, Automatic detection of multiple pavement layers from GPR data, NDT E Int. 41 (2) (2008) 69–81.

[12] C. Le Bastard, V. Baltazart, Y. Wang, J. Saillard, Thin-pavement thickness estimation using GPR with high-resolution and super resolution methods, IEEE Trans. Geosci. Remote. Sens. 45 (2007) 2511–2519.

[13] N. Pinel, C. Le Bastard, V. Baltazart, C. Bourlier, Y. Wang, Influence of layer roughness for road survey by ground penetrating radar at nadir: theoretical study, IET Radar, Sonar Navig. 5 (2011) 650–656.

[14] K. Luo, A. Manikas, Superresolution multitarget parameter estimation in MIMO radar, IEEE Trans. Geosci. Remote. Sens. 51 (6) (2013) 3683–3693.

[15] D. Kurrant, E. Fear, Technique to decompose near-field reflection data generated from an object consisting of thin dielectric layers, IEEE Trans. Antennas

Propag. 60 (8) (2012) 3684–3692.

[16] C. Le Bastard, V. Baltazart, Y. Wang, Modified ESPRIT (M-ESPRIT) algorithm for time delay estimation in both any noise and any radar pulse context by a GPR radar, Signal Process. 90 (2010) 173–179.

[17] K. Chahine, V. Baltazart, Y. Wang, Interpolation-based matrix pencil method for parameter estimation of dispersive media in civil engineering, Signal Process. 90 (2010) 2567–2580.

[18] N. Pinel, C. Le Bastard, C. Bourlier, M. Sun, Asymptotic modeling of coherent scattering from random rough layers: application to road survey by GPR at nadir, Int. J. Antennas Propag. (2012), Article ID 874840.

[19] M. Sun, N. Pinel, C. Le Bastard, V. Baltazart, A. Ilhamouten, Y. Wang, Time delay and interface roughness estimation by subspace algorithms for pavement survey by radar, Surf. Geophys. 13 (2015) 279–287.

[20] M. Sun, C. Le Bastard, N. Pinel, Y. Wang, J. Li, Road surface layers geometric parameters estimation by ground penetrating radar using estimation of signal parameters via rotational invariance techniques method, IET Radar, Sonar Navig. 10 (2016) 603–609.

[21] L. Qu, Q. Sun, T. Yang, L. Zhang, Y. Sun, Time-delay estimation for ground penetrating radar using ESPRIT with improved spatial smoothing preprocessing, IEEE Geosci. Remote. Sens. Lett. 11 (2014) 1315–1319.

[22] A. Schatzberg, A.J. Devaney, A.J. Witten, Estimating target location from scattered field data, Signal Process. 40 (1994) 227–237.

[23] N. Déchamps, N. De Beaucoudrey, C. Bourlier, S. Toutain, Fast numerical method for electromagnetic scattering by rough layered interfaces: propagation-inside-layer expansion method, J. Opt. Soc. Am. A 23 (2006) 359–369.

[24] C. Bourlier, G. Kubické, N. Déchamps, Fast method to compute scattering by a buried object under a randomly rough surface: PILE combined with FB-SA, J. Opt. Soc. Am. A 5 (2009) 260–263.

[25] C. Bourlier, C. Le Bastard, V. Baltazart, Generalization of PILE method to the EM scattering from stratified subsurface with rough interlayers: application to the detection of debondings within pavement structure, IEEE Trans. Geosci. Remote. Sens. 53 (2015) 4104–4115.

[26] F. Koudogbo, P.F. Combes, H.J. Mametsa, Numerical and experimental validations of IEM for bistatic scattering from natural and manmade rough surfaces, Progress. Electromagn. Res. 46 (2004) 203–244.

[27] E. Li, K. Sarabandi, Low grazing incidence millimeter-wave scattering models and measurements for various road surfaces, IEEE Trans. Antennas Propag. 47 (1999) 851–861.

[28] C. Fauchard, Utilisation de radars très hautes fréquences: application à lausculation non destructive des chaussées, PhD thesis, University of Nantes, France, 2001.

[29] D. Daniel, Ground Penetrating Radar, 2nd edn, IEE Press, London, 2004.

[30] X. Li, R. Wu, An efficient algorithm for time delay estimation, IEEE Trans. Signal Process. 46 (1998) 2231–2235.

[31] M. Sun, C. Le Bastard, Y. Wang, N. Pinel, Time delay estimation using ESPRIT with extended improved spatial smoothing techniques for radar signals, IEEE Geosci. Remote. Sens. Lett. 13 (2016) 73–77.

[32] B. Friedlander, A.J. Weiss, Direction finding using spatial smoothing with interpolated arrays, IEEE Trans. Aerosp. Electron. Syst. 28 (1982) 574–587.

[33] A.J. Weiss, B. Friedlander, performance analysis of spatial smoothing with interpolated arrays, IEEE Trans. Signal Process. 41 (1993) 1881–1892.

[34] S. Marcos, J. Sanchez-Araujo, Méthodes linéaires haute résolution pour l'estimation de directions d'arrivée de sources performances asymptotiques et complexité, Trait. Du. Signal 14 (1997) 99–116.

[35] T.J. Shan, M. Wax, T. Kailath, On spatial smoothing for direction-of-arrival estimation of coherent signals, IEEE Trans. Acoust., Speech Signal Process. 33 (1985) 806–811.

[36] F. Ge, D. Shen, Y. Peng, V.O.K. Li, Super-resolution time delay estimation in multipath environments, IEEE Trans. Circuits Syst. 54 (2007) 1977–1986.

[37] F. Ge, Q. Wan, X. Wang, Y. Peng, Frequency estimation of the sinusoidal signals with lowpass envelopes based on the eigenanalysis, in: Proceedings of the IEEE Radar Conference, 2002, pp. 453–458.