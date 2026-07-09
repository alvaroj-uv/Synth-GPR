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

32

G. Meles et al. / Journal of Applied Geophysics 78 (2012) 31–43

inversion as a non-linear iterative problem, albeit in two dimensions. Kuroda et al. (2007) inverted only for the relative permittivity εr, Ernst et al. (2007a) used a stepped (cascaded) inversion scheme, whereby the εr distribution was first updated while the σ distribution was held fixed, and then the σ values were updated holding the εr values fixed. Both approaches used a finite-difference time-domain solution of Maxwell's equations and a gradient-based algorithm. Rather than calculating the sensitivities explicitly, as in a Gauss–Newton inversion approach, they used the zero-lag cross-correlation between the forward propagated field and the back-propagated residual field at the receivers to calculate the gradient directions. Ernst et al. (2007b) successfully applied the technique to observed data from two field sites.

Earlier and parallel developments occurred in biomedical microwave tomography in both the time domain and the frequency domain, using iterative and distorted Born approaches (Wang and Chew, 1989), as well as other more refined procedures (Fhager et al., 2005; Fhager and Persson, 2005; Gustafson and He, 2000; Hashemzadeh et al., 2006; Rubaek et al., 2007; Tanaka et al., 1999). State-of-the-art microwave imaging is described by Dubois et al. (2009), Rubaek et al. (2009) and Solvodieri (2010). It should be appreciated that in the microwave case, the target lies in either air or de-ionised water (i.e., homogeneous media) and is completely surrounded (360°) by the antennas. This is almost never the case in GPR, where the host material is heterogeneous and the angular coverage is limited. Furthermore, it is assumed in microwave imaging that the transmitters and receivers are polarised in the 2D medium-invariant transverse or y-direction, such that the EM equations (transverse electric or TE case) for a line source simplify considerably to scalar wave equations involving a single E-field component (Ey). This is only applicable in GPR for surface recording in which the antennae are directed perpendicular (y direction) to the profile (x) direction and the geology is two dimensional. For antennae oriented in the sagittal plane or for 3D media, such equations cannot be used, thus seriously limiting such approach for more general GPR applications. Some of the microwave imaging algorithms developed in recent times (e.g., Dubois et al., 2009) make the further assumption that the scattered field can be isolated from the total field. As a consequence, the incident field is known because measurements can be made with and without the target (object) present (Fhager et al., 2005). Separating the direct wave from the scattered field is sometimes possible with careful time gating of surface GPR data, but it is extremely problematic with crosshole data, in which the various arrivals overlap. Moreover, the subsurface targets cannot be “removed” in earth science applications.

The transverse magnetic (TM) case with the electric field polarised in the x-z plane of propagation and the magnetic field in the transverse or y-direction, requires a full-vector treatment (Ex and Ez components). This was recently given by Meles et al. (2010), thus enabling for the first time, the joint inversion of surface data (antennae oriented in the x direction) and crosshole data (antennae oriented in the z direction). These authors also described a new scheme that simultaneously updates εr and σ estimates, leading to improved performance and efficiency over the cascaded scheme of Ernst et al. (2007a, b). Although the Ernst et al. (2007a, b) and Meles et al. (2010) schemes both offer sub-wavelength resolution when the target coverage is favourable, it should be appreciated that the full-waveform GPR inverse problem is both ill-posed and non-linear. Notwithstanding the sophistication of the new schemes, the non-linearity of the forward problem can cause them to fail to provide a satisfactory picture of the subsurface. It is well known that the non-linearity is mainly associated with multiple scattering (Mora, 1987), being particularly severe when the differences between the true model and the current (starting or guessed) model are large in terms of the target contrasts (εr and σ) and target size. Large anomalous bodies having appreciable velocity contrasts with their surroundings cause significant traveltime differences between the observed traces

and those computed for the background model. When the time shifts exceed more than half a period, the inversion can get trapped in local minima.

One solution to the local minimum problem is the frequency hopping method used in microwave imaging (Chew and Lin, 1995; Dubois et al., 2009). The inversion starts at a low frequency and progressively moves to a higher frequency, using the model from the previous frequency inversion as the starting model for the next higher frequency. A similar approach has been proposed for frequency-domain seismic inversion (Maurer et al., 2009; Pratt et al., 1998; Zhou and Greenhalgh, 2003), in which inversions are carried out one frequency at a time. In realistic situations, the low frequency data may be contaminated by noise, such that the frequency hopping approach is unstable. Until now, the alternative was to work in the time domain with wide-band transient signals and to impose prior constraints to the model space while retaining the full bandwidth of the data. Imposing smoothness constraints on the model space addresses the second issue of ill-posedness of the geophysical inverse problem, but it does not resolve the non-linearity problem; it simply stabilises or regularises the problem. To simulate the non-linearity issue, one may invoke a priori information on the εr and σ distributions so that the initial model is close to reality. This can work well in biomedical applications (Fhager and Persson, 2007), in which reasonable knowledge exists on the shape, location, and likely contrasts of the targets (e.g., organs) and surrounding structures. Unfortunately, for most GPR applications, such information is not available. One approach (Ernst et al., 2007a) that attempts to take into account prior information is to use the results of traveltime and amplitude tomography (e.g., Fullagar et al., 2000; Musil et al., 2006) as the starting model. This helps in some cases, but our numerous synthetic experiments demonstrate that such an approach yields unsatisfactory results for complex models due to the inherent limitations of ray-based methods (maximum achievable resolution, difficulties in mapping large velocity contrast inclusions and certain types of low velocity structure). An alternative approach is therefore required.

We present here a new full-waveform inversion scheme for GPR data that is based on a combined frequency-time-domain approach. It requires no specific assumptions about the model to be used. The essence of the method is to progressively expand the bandwidth of the data as iterations proceed, starting with low frequencies and successively adding higher frequencies. Only in the final stages of the inversion is the full bandwidth of the data utilised. Although the applications presented here are for 2D models and combined surface-crosshole configurations, the method is theoretically valid for 2D and 3D problems and data collected in any source-receiver configuration. The current application to only 2D problems is imposed by the excessive CPU/memory costs for 3D simulations (i.e., not by any theoretical assumption in the derivation of the forward/inversion scheme). The results of the synthetic examples presented in this paper clearly show that the new method can provide detailed and reliable images of the investigated media, even for high contrast and complex-shaped inclusions.

## 2. Inversion of GPR data

The minimum set of electrical parameters required to characterise the subsurface completely comprises the permittivity εr, conductivity σ and permeability μ distributions. Throughout this paper, permeability is assumed to be constant and equal to the free space value μ0. Least-squares full-waveform tomographic inversion schemes involve finding the spatial distributions of εr and σ that minimise a cost function that is the squared norm of the misfit between the simulated and the observed GPR traces. In the next section, we briefly introduce a recently developed full-waveform time-domain inversion scheme and discuss its limitations in terms of spectral coverage and stability. Subsequently, we present a very simple yet illustrative example of

G. Meles et al. / Journal of Applied Geophysics 78 (2012) 31–43

33

this inversion scheme that leads to an entirely new approach to waveform tomography, which forms the subject matter and purpose of the rest of the paper.

# 2.1. Gradient-based full-waveform time-domain inversion

The inversion algorithm of Meles et al. (2010), which is based on a vector formulation and solves for the εr and σ distributions simultaneously, uses a gradient-type iterative scheme that for every iteration computes the cost function gradients and updates the model along them by defined step lengths. Because the entire frequency content of the data is used from the very first iteration, we refer to this inversion scheme as full bandwidth initial data, or FBID.

The inversion algorithm includes the following steps:

1) Determine a good initial input model using an inexpensive inversion scheme (e.g., traveltime tomography or a plausible homogeneous distribution).
2) Based on this initial model, simulate data at each receiver location for every transmitter position and calculate the misfit with the observed data (1st calculation of the forward problem).
3) Back-propagate the misfit wavefield and cross-correlate the results with the forward-propagated electric fields to yield the εr and σ gradients of the cost function (2nd calculation of the forward problem).

4) Estimate the εr and σ step lengths used to move along the gradient directions until a local minimum is found (3rd and 4th calculations of the forward problem).
5) Update the model parameters according to the computed gradients and step-lengths.
6) Repeat the inversion scheme until convergence to a pre-defined cost function minimum is achieved.

Mathematical details of the above-mentioned inversion algorithm, including all essential equations for calculating gradients and step lengths, as well as information on its computational costs and applications to synthetic data, can be found in Meles et al. (2010). Inversion of an observed data set using this algorithm is given in Klotzsche et al. (2010).

# 2.2. Spectral coverage and stability

Under the assumption of weak scattering and crosshole recording, it is possible to identify the area of spatial wavenumber coverage in the model space from a single frequency source (Mora, 1989; Wu and Toksoz, 1987). It is known that the higher the frequency content of the source, the better the coverage in the spatial wavenumber domain. However, the assumption of weak scattering is rarely valid and more often, especially at the very early stages of inversion, instability may occur because of the large differences between the true and the current

![img-0.jpeg](img-0.jpeg)

![img-1.jpeg](img-1.jpeg)

Fig. 1. (a) Three models A, B and C comprising a single embedded block of identical size and position but of different anomalous permittivity values (εr = 80, 4.5 and 3.5 respectively) set within a uniform background of εr = 4. Conductivity σ is constant for all models at 0.1 mS/m. A synthetic crosshole radar synthetic experiment involving the transmitters (shown by crosses) and receivers (shown by circles) is performed for all three models to generate three data sets D(A), D(B) and D(C). (b) The data sets are successively filtered with increasing bandwidth and the data misfits (cost functions) Φ between the model pairs A and B, and A and C are plotted as a function of the high frequency limit of the filter (solid blue and red curves). The differences between the two curves, amplified by a factor of 10, are plotted as the thick black curve. The dashed blue and red horizontal curves along the top represent the data set differences for the full bandwidth data. The trend of the misfit in the data space is the same as the trend in the model space only for low frequency components of the data sets (i.e., negative values of the thick black curve).

34

G. Meles et al. / Journal of Applied Geophysics 78 (2012) 31–43

model, with the result that the inversion fails to converge to the true solution. This is usually associated with cycle-skipping, in the sense that the time difference between the observed and the synthetic data is larger than half the period. This phenomenon is obviously more severe for high frequencies than for low frequencies. In the next section, we provide an example of a realistic problem that can be encountered when inverting radar traces collected in standard configurations.

### 2.3. Non-linearity of the forward problem

We present here a very simple example of instability related to the non-linearity of the forward problem. Fig. 1a shows models A, B and C. All three models involve a square anomaly of identical shape but different relative permittivity ($\varepsilon_r = 80, 4.5$ and $3.5$ for models A, B and C, respectively), embedded in an identical homogeneous background of relative permittivity $\varepsilon_r = 4$. The conductivity is assumed to be uniform ($\sigma = 1$ mS/m) for the 3 models. Note, that model C is more distant (different) from model A than is model B.

For the same crosshole recording configuration (crosses and circles in Fig. 1a), we compute sets of synthetic radar traces for all models. These data sets are referred to as D(A), D(B) and D(C). The effective source pulse for this and other synthetic data sets presented in this paper is a differentiated Gaussian of bipolar form, having an asymmetric bell-shaped amplitude spectrum from 5–600 MHz with a dominant frequency of ~200 MHz (see Fig. 2). It yields a dominant wavelength of ~0.75 m in the background medium of the models in Fig. 1. We now compute the misfit-cost functions

$$\Phi = \sum_i [D_i^A - D_i^B]^2. \tag{1}$$

with j = B or C, as the squared norm of the data differences for all samples i between models A, B and C, treating model A as the reference or true model and models B and C as possible updated models. Despite model B being closer than model C to model A in the model space, D(C) is closer than D(B) to D(A) in the data space. This is illustrated schematically towards the top of Fig. 1b by the horizontal dashed blue and red lines, which represent the respective misfits $\Phi[D(A), D(B)]$ and $\Phi[D(A), D(C)]$ of $10.7 \times 10^{-6}$ and $10.5 \times 10^{-6}$, respectively for the full bandwidth data (these values really only apply for the far right end of the diagram, but are shown over the whole frequency range simply for readability purposes). Due to the highly non-linear nature of the forward problem, the trend of the

![img-2.jpeg](img-2.jpeg)

Fig. 2. Source spectrum and the different band-pass filters (shown schematically by the black and red horizontal bars) applied to the signal as iterations proceed, starting at low frequency and gradually expanding the bandwidth (after every 4th iteration) by increasing the high cut corner frequency. After the centre frequency of 200 MHz is reached, all subsequent iterations use the full bandwidth of the data.

misfit in the data space is opposite to the trend of the misfit in the model space. This can be critical in an actual inversion. It may happen, for example, that during the first iterations, the gradient detects the shape of the anomaly, but because the step-length updates the model in the wrong direction, the anomaly is mapped as a low permittivity feature when it should be high permittivity. This would occur because the step-length is determined by minimizing the cost function along the gradient direction of the data misfit.

### 3. Taming the non-linearity problem in full-waveform inversion

In our previous full-waveform inversion approach, as described in Section 2.1, the entire frequency content of the data is used from the very first iteration to update the model, but in our new approach (referred to as progressive bandwidth expansion of data, or PBED) we progressively increase the frequency content (starting at a low frequency) as the iterations proceed. This involves bandpass filtering the original radargrams in gradual steps, and successively expanding the bandwidth.

A somewhat similar frequency selection approach is often used in microwave inverse scattering, where it is referred to as the frequency hopping method (Chew and Lin, 1995) which does not use cumulative frequencies (actual frequency bands), just one frequency at a time. Similarly, in Gauss–Newton frequency-domain seismic inversion (Maurer et al., 2009; Pratt et al., 1998; Sirgue and Pratt, 2004), only a small number of well chosen single frequencies are used, one at a time.

To support our argument for the proposed approach, we present in Fig. 1b an elaboration of what was discussed in the previous section. For the full bandwidth data set depicted in the upper far right of the curves, the distance between D(A) and D(B) (here shown as a constant value along the whole frequency range—the dashed dark blue line) is larger than that between D(A) and D(C) (the dashed red line). This means that despite being further away from the true solution in the model space, the difference between the radargrams (data space) for the full bandwidth data is actually less and there is an opposite trend between the data space and the model space. Such non-linearity is characteristic of many geophysical forward problems.

To overcome this non-linearity, we progressively filter the data with a simple bandpass filter, keeping the low cut frequency at 10 MHz and allowing the high-cut frequency to gradually grow in increments of 10 MHz until the maximum frequency of 600 MHz is reached.

The differences of the filtered datasets D(B) and D(C), relative to D(A), are shown in Fig. 1b as the solid blue and solid red lines, respectively. The thick black line drawn at the bottom of the diagram is an amplification, by a factor 10, of the differences between the blue and the red lines. Note the oscillatory nature of the differences. For broad-band data, the difference curve is uniformly positive, meaning that there is a larger difference in the data cost functions for models A and B than for models A and C. This shows that there is an opposite trend between the data space and the model space. But when only the low frequency data are used (i.e., 10–90 MHz), the data misfit is entirely negative, meaning that the data for model B is closer to the data for model A than is the data for model C. This indicates that the trend in the data space is the same as the trend in the model space.

Thus, for the specific inverse problem under consideration here when working with low frequency data, iterative updates in the $\varepsilon_r$ value of the anomalous block will be in a direction towards the true solution, corresponding to a reduction in the data misfit. For this reason, we expect the inversion to avoid getting trapped in local minima if we invert, at least during the early steps of the inversion, only the low frequency content of the data.

### 3.1. An illustrative example of a one-parameter inversion

We now consider in more detail a simplified one-parameter inversion problem in the context of the model presented in Fig. 1a. Let

G. Meles et al. / Journal of Applied Geophysics 78 (2012) 31–43

35

A and D(A) be the true model and the synthetically generated “observed” traces for this model. We invert only for the εᵣ value in the anomalous block by assuming that we know its location and shape. Because only one parameter can be updated, the problem is a one-parameter inversion. Fig. 3 shows the cost functions of this problem for different data sets. The black curve corresponds to the cost function for the entire full bandwidth dataset. Local minima occur at εᵣ values of about 2, 55, 80 and beyond 95. The global minimum (true solution) occurs at the correct value of 80. As a consequence, in order to avoid getting trapped in a local minimum, the inversion should start with a model block εᵣ value somewhere between 65 and 95. The red and light blue curves correspond to cost functions for which 10–20 MHz and 10–44 MHz bandpass filters are applied to the datasets, respectively. Whereas the red and the blue curves also exhibit local minima, the width of each global minimum is much broader in terms of the model (permittivity) values. Local minimum trapping can be avoided by successively using these two data sets. For example, if we start with εᵣ=4 for the anomalous body (corresponding to a homogenous starting model equal to the background medium), by using the 10–20 MHz data set, we would reach the local minimum at εᵣ~35. Then, by starting the next phase of the inversion at this εᵣ value and using the 10–44 MHz dataset, we would finally and rapidly reach the global minimum at εᵣ=80. This simple example, far from demonstrating and establishing a general methodology, suggests a different approach to inversion in which different frequency contents of the data are used at different stages of the inversion. The key is to start at low frequency, where stability is more likely, and gradually add the higher frequency components of the data as iterations proceed. Because low-frequency content data are inverted first, the relative importance of the starting model is much diminished.

### 4. A new frequency-time-domain full-waveform inversion scheme

Following the ideas presented in the previous section, the original FBID algorithm of Meles et al. (2010; Fig. 4a) is modified as follows (Fig. 4b):

1) Determine a good initial input model using an inexpensive inversion scheme (e.g., traveltime tomography or even a homogenous model).

![img-3.jpeg](img-3.jpeg)

Fig. 3. Cost functions for data sets simulated for the configuration presented in Fig. 1a. The true data set D(A) is compared with data sets computed for different values assigned to the inclusion permittivity εᵣ. The data sets are then filtered and the misfits displayed as a function of εᵣ. The black curve corresponds to the full bandwidth data, whereas the red and blue curves correspond to band-pass filtered data in the ranges 10–20 MHz and 10–44 MHz, respectively. Trapping in local minima can be avoided and the true solution reached by combining the different data sets, starting at the point SP (homogeneous model) with the 10–20 MHz data until the first local minimum is reached (see dotted curve), then jumping to the new start point (NSP) and using the 10–44 MHz data to arrive at the global minimum.

2) Based on this initial model, compute the frequency-filtered data at each receiver location and calculate the misfit with the observed data (1st calculation of the forward problem).
3) Back-propagate the misfit or residual wavefield and cross-correlate the results with the filtered forward-propagated electric field to yield the εᵣ and σ gradients of the cost function (2nd calculation of the forward problem). Due to the orthogonality properties of the Fourier base, the residual fields do not need to be filtered (any frequency component not common to both data sets—forward and back-propagated residual—will be eliminated in the cross-correlation process).
4) Estimate the step lengths required to move along the gradient directions until a local minimum is found (3rd and 4th calculations of the forward problem).
5) Update the model parameters according to the computed gradients and step-lengths.
6) Repeat the inversion scheme, updating the frequency content of the data at specified intervals. This part of the scheme is illustrated schematically in Fig. 2, which shows the source signal and the bandpass filter applied to it at various stages. The bandwidth is expanded progressively by increasing the high cut frequency in fixed increments and keeping the low cut frequency constant. When the high cut frequency reaches the central frequency of the source pulse, stability is likely because any time shifts between the observed and computed data for the current model will be less than half a period. So, for all remaining iterations the full bandwidth of the data can be used.
7) Once the full frequency content of the data is inverted, repeat the inversion until convergence is reached.

Following Pica et al. (1990), we have introduced dynamic scaling of the perturbation factors as inverse functions of the maximum magnitudes of the gradients. This was needed to provide proper linearization for the determination of the step-lengths (see Meles et al. (2010) for more details). The amplitudes of the gradients can vary by several orders of magnitude during the inversion process due to the different frequency contents of the data and the convergence in the data space at different stages of the PBED. The perturbation factors need to be adjusted to compensate for this effect.

The new scheme retains all of the equations described by Meles et al. (2010). The essential and distinguishing feature of the new PBED scheme is that it exploits a range of imaging wavelengths in a controlled manner. Because the medium comprises inhomogeneities of various sizes (and contrasts), from quite small to moderately large (relative to each wavelength), it can be more effectively sampled and interrogated by multiple wavelengths in each expanded frequency band sequentially.

### 5. Synthetic data inversion tests

In this section, we compare the results of applying the FBID and PBED inversion schemes to a number of synthetic examples. The 2D TM mode input data (with the electric field in the plane of the section) are simulated using a FDTD algorithm and inverted on a cluster of computers. To ensure stability and avoid numerical grid dispersion in our simulations, we had to consider the medium properties and the frequency content of the source(s) in setting the grid spacing and time steps. In all synthetic tests, we employ an optimal recording configuration, with sources and receivers placed along all four sides of the model domain. Although uncommon in GPR, such geometries are possible at a mine site, for example, where two tunnels at different depths or positions are linked by two vertical or horizontal boreholes. The choice of such good target coverage was driven by our intention to provide the best possible configuration for both inversion schemes. Our goal is to demonstrate that the limitations of current FBID methods (Ernst et al., 2007a, b; Meles et al., 2010) are not associated with limited target coverage provided by conventional crosshole recording configurations, but rather, are

36

G. Meles et al. / Journal of Applied Geophysics 78 (2012) 31–43

![img-4.jpeg](img-4.jpeg)

Fig. 4. Flow diagrams for the (a) current FBID and (b) new PBED inversion algorithms. The new scheme starts with low frequency data, expands the bandwidth after every 4th iteration, finally moving to the full bandwidth data after 64 iterations (i.e., when the central frequency of the source pulse is reached).

symptoms of an intrinsic problem. Furthermore, standard crosshole data sets satisfactorily inverted with the original FBID scheme (i.e. for models having only small contrasts, and hence less afflicted by non-linearity issues) were also inverted with the new PBED algorithm. In these cases, the new PBED method showed only minor improvements over the existing FBID scheme (results not shown here for space economy). The main benefits of PBED are in dealing with high contrast media.

### 5.1. Model 1—small and large block inclusions of high/low permittivity and conductivity

With our first synthetic example (Figs. 5a, 6a and g), we wish to express the non-linearity problem in terms of time shifts between the “observed” radar data (i.e., that computed for the true model) and radargrams computed for the starting model. We consider two square permittivity/conductivity inclusions embedded in a homogeneous background medium. The size of the larger low permittivity low conductivity body ($\varepsilon_r = 1$ and $\sigma = 0.1$ mS/m) is $120 \times 120$ cm, whereas that of the smaller high permittivity high conductivity body ($\varepsilon_r = 8$ and $\sigma = 10$ mS/m) is $30 \times 30$ cm. The dominant wavelengths within the background medium ($\varepsilon_r = 4$, $\sigma = 3$ mS/m) and the larger block are -0.75 and 1.5 m, respectively. Therefore, even the larger inclusion is of sub-wavelength dimension. The synthetic data were generated using 10 sources and 30 receivers placed along each side of the model of dimensions $10.6 \times 10.6$ m (shown by crosses and circles in the plots, respectively).

### 5.1.1. Starting models

Uniform distributions of $\varepsilon_r$ and $\sigma$ values were used as starting models for the new PBED scheme, whereas for the FBID inversion, the

model obtained from traveltime tomography was also tested. In Fig. 5, we show the differences between traces corresponding to paths along the two lines AA' and BB', computed with the true model (Fig. 5a) and the starting model for the FBID scheme (in this case the result of traveltime inversion, Fig. 5b). As expected, traveltime inversion provides a rather blurred image of the larger low permittivity anomaly (Fig. 5b) and no indication of the smaller high permittivity inclusion. Ray-tomography is based on the high frequency approximation, in which the imaging wavelength is assumed to be very much less than the target size. This is clearly not valid for this model. Moreover, the permittivity contrasts are very large (300%), further exacerbating the non-linearity of the inverse problem (traveltime tomography is usually only applied to much smaller contrast features, typically less than 20%). Nevertheless, traveltime tomography does a reasonable job in recovering the shape and position of the larger low permittivity (high velocity) block, but the relative permittivity of the anomalous block is poorly estimated (i.e., $\varepsilon_r \approx 3$ instead of the correct value of 1). Note, that we have compressed the range of the colour bar in Fig. 5b to exploit the dynamic range of values and yield a more favourable picture. Fig. 5c shows the superposition of the observed trace (true model) and the computed trace (traveltime tomography starting model) for source–receiver configuration AA'. Because of the large difference in the model along the direction AA', the traces are very different. Not only is multiple scattering different for the two models, but also the traveltime difference is large because traveltime tomography severely under-estimates the permittivity contrast of the body. More specifically, the time-shift between the traces is larger than half the period of the dominant frequency of the signal. A half-period time shift is the critical situation and a sufficient condition to cause failure of

G. Meles et al. / Journal of Applied Geophysics 78 (2012) 31–43

37

(a)

![img-5.jpeg](img-5.jpeg)

(b)

![img-6.jpeg](img-6.jpeg)

(c)

![img-7.jpeg](img-7.jpeg)

(d)

![img-8.jpeg](img-8.jpeg)

Fig. 5. (a) True model yielding “observed data”. (b) Model obtained by traveltime tomography (TTT), (c) and (d) compare observed traces (red curve) and simulated traces (blue curve) using the TTT model along the source–receiver lines AA' and, BB', respectively. The traveltime difference is large in diagram (c) due to the size/permittivity contrast of the anomalous body, but it is negligible in diagram (d) because the body is very small. The critical time difference of more than half the dominant period of the pulse can cause trapping by a local minimum and failure of the FBID inversion. The PBED starts at low frequency, for which the time difference is a much smaller fraction of the dominant period, such that stability is more likely.

FBID. Under such circumstances, cycle skipping can occur, and PBED is required because it lengthens the effective period of the pulse. Fig. 5d shows the corresponding traces for source–receiver configuration BB'. For these traces, the traveltime difference is negligible; the only noticeable difference is the reflection from the low permittivity inclusion at later times. For this case, cycle skipping does not occur.

Obviously, with much lower frequency data (i.e., filtered versions), the time shift between the two traces in Fig. 5c would be a much smaller fraction of the dominant period of the signal and so any inversion would be less affected by it. However, having a time shift of less than half the dominant period of FBID is a necessary but not sufficient condition to guarantee success of the FBID inversion scheme. It can fail under other circumstances, as shown in a later example.

### 5.1.2. FBID inversions

Fig. 6b and h show the results of inversion when the FBID scheme is applied with homogeneous εᵣ and σ starting models. A minimum

source–receiver distance of 7 m was set for the waveform inversion in order to prevent artefacts from strong direct arrivals, which would otherwise dominate the gradients.

The large body (anomaly 1) is located correctly, but improperly characterised. Instead of a homogeneous block of low permittivity and low conductivity, a ring-shaped feature of low permittivity and a block of high conductivity are incorrectly mapped. The situation improves for the smaller body (anomaly 2), with good reconstruction both in terms of resolution and physical properties. As expected from simple analysis of the observed and simulated traces prior to the inversion, only the large anomaly is troubled by the non-linearity. The use of a traveltime tomography starting model does not improve the inversion significantly (see Fig. 6c and i).

### 5.1.3. PBED inversion

For all models analysed in this paper, the frequency content of the data used for the different iterations of PBED was assigned before the

38

G. Meles et al. / Journal of Applied Geophysics 78 (2012) 31–43

![img-9.jpeg](img-9.jpeg)

![img-10.jpeg](img-10.jpeg)

![img-11.jpeg](img-11.jpeg)

![img-12.jpeg](img-12.jpeg)

![img-13.jpeg](img-13.jpeg)

![img-14.jpeg](img-14.jpeg)

![img-15.jpeg](img-15.jpeg)

![img-16.jpeg](img-16.jpeg)

![img-17.jpeg](img-17.jpeg)

![img-18.jpeg](img-18.jpeg)

Fig. 6. (a) True relative permittivity and (g) conductivity distributions of Model 1. Crosses and circles represent the sources and receivers employed in the 4-sided experiment. The resulting tomograms for the synthetic full-waveform inversion experiment are shown for three separate inversion approaches: (b) and (h) for FBID using homogeneous starting models, (c) and (i) for FBID using starting models based on traveltime tomography, and (d) and (l) for PBED using homogeneous starting models. Permittivity cross sections along line CC are shown in (e) and conductivity cross sections along the same line are shown in (f).

beginning of each inversion. The filtering was applied to the source signal rather than to the actual radargrams. Different filtered versions of the source signal in Fig. 2 were used for the first steps of the inversion. By applying a tapered bandpass filter with a fixed lower cut of 15 MHz and a variable higher cut, pulses of dominant frequency in the range of 50–200 MHz at 10 MHz spacing were selected and progressively implemented for 4 iterations before the whole bandwidth signal was used. We did not include frequencies less than 15 MHz because such spectral values are often small in real data cases and subject to noise capture. Coarser grid spacings could be profitably used at the first stages of the inversion when dealing with lower frequencies (hence longer wavelengths). This would reduce the computational effort in the forward modelling, but for our tests, the main emphasis was on scientific effectiveness and simplicity, not computational efficiency, so the same grid spacing was used at all steps of the inversion. The PBED algorithm should be made suitable for both field data applications as well as synthetic experiments. At the high cut frequency of 200 MHz (central frequency of the source signal), stability was anticipated and therefore the remaining iterations used the full frequency spectrum of the source. This scheme may of course be enhanced by implementing an optimised choice of the frequency, possibly by taking into account the trend of the error curve. For the purposes of this paper (i.e., to indicate the benefits of starting the inversion at low frequency and expanding the bandwidth as iterations proceed), we consider the adopted approach satisfactory.

Fig. 6d, e, f and l show the PBED inversion results. In this case, the low permittivity of anomaly 1 is well reconstructed, but its conductivity contrast with the background medium is underestimated. It is properly characterised as being significantly less conductive than the background, but because of its very limited sensitivity, the magnitude of the anomalous conductivity is not fully recovered. The characteristics of the smaller feature are equally well recovered (Fig. 6l), demonstrating that there are no drawbacks in the application of the new method to cases where the FBID scheme works well (also found for many other examples not reported in the present paper).

### 5.1.4. RMS Curves

Fig. 7 shows the RMS misfit curves for model 1 calculated according to the formula

$$RMS = \sqrt{\sum_{1}^{N} (D_i^{obs} - D_i^{cal})^2 / N}, \tag{2}$$

where D is the amplitude data at a particular time sample on a given trace, and subscripts "obs" and "cal" denote observed and calculated data (for the current model). The summation N is over all samples i for all traces (i.e., $N = N_S \times N_T \times N_R$, where $N_S$ is the number of samples per trace, $N_T$ is the number of transmitters and $N_R$ is the number of

G. Meles et al. / Journal of Applied Geophysics 78 (2012) 31–43

39

receivers). The observed data remain the same for both FBID and PBED but the calculated data will involve much smaller amplitudes for PBED than for FBID because only a limited part of the spectrum is used in the former case. The dark blue and the green curves represent the RMS trends for the FBID inversions when traveltime tomography and homogenous starting models are used, respectively. Rather surprisingly, at the first FBID iteration, the RMS is larger for the traveltime tomogram starting model than for the homogenous starting model.

The black and red curve represents the RMS function for the new PBED scheme (using a homogeneous starting model); the different colours indicating that different expanded data are used each time the colour changes. For each successive bandwidth, four iterations are executed and then the frequency content is expanded. This continues up until iteration 64 as stability is approached (see Fig. 2 and Section 4). Note the precipitous drop in the RMS at this point, when the full bandwidth is employed. The difference in the size of the RMS values between the PBED and FBID results to the left of this point (with the PBED values being larger than those of FBID) is purely related to the way the RMS error is defined—only a fraction of the frequencies (albeit increasing) are used in the computed data for PBED, but for FBID all frequencies are employed. From Parseval's Theorem, this makes the computed data (trace amplitudes) for FBID larger and more comparable to the observed values. Therefore, in forming the squared difference between the first and second terms in Eq. (2), the net result is smaller in the case of FBID than for PBED. This is true only up to the point at which the PBED scheme uses the full bandwidth data. After this point, the convergence for the dark blue and green curves (FBID) is much worse than for the red and black curve (PBED), indicating that FBID is trapped in severe local minima. This issue is highlighted by the light blue curve, which shows the FBID convergence curve computed according to model updates made during the PBED inversions. The highly oscillatory nature of the light blue curve between iterations 1 and 16 shows the non-linear nature of the FBID inversion. The RMS values actually increase with increasing iterations over portions of this range. The only way to jump out of the local minima and to reach the global minimum is to start with a low frequency successively expanded data set, thus avoiding the "hills" in the FBID curve. Although not very noticeable at the scale plotted,

![img-19.jpeg](img-19.jpeg)

Fig. 7. RMS misfit curves for Model 1. The green and dark blue curves represent the convergence behaviour for the FBID inversion when the homogeneous and traveltime-tomography-based starting models are used, respectively. The black and red curve represents the convergence behaviour for the new PBED inversion scheme; the changing colours identify the bandwidth expansions (the inversion runs for 4 iterations for each bandwidth (as represented by each colour)). The light blue curve was computed for the FBID misfit, but updating the model was made according to the PBED results. This curve shows the oscillatory nature (increasing and decreasing RMS) and highly non-linear behaviour of the process up to around iteration 25. Clearly, FBID when used alone gets trapped in local minima. In contrast, PBED converges uniformly to the global minimum.

every one of the red and black segments of the PBED curve shows a slight downward trend, in contrast to the light blue FBID curve. Note, that at iteration number 20, the light blue curve reaches the same RMS value as for the starting model (green curve), and thereafter falls monotonically to the global minimum.

The new scheme needs twice as many iterations as the FBID scheme. The final RMS for the PBED results is ~25% of that for the FBID results.

Fig. 8 shows a selection of radargrams generated by a source placed at 3.3 m depth in the left borehole of model 1 and receivers located in the right borehole. For clarity, only traces for even numbered receiver positions are displayed. Four sets of colour-coded traces are presented. The red traces correspond to the synthetic observed data, the blue traces are the synthetic response for the traveltime tomogram, the green traces are those corresponding to the final model obtained by FBID inversion (based on the traveltime tomogram starting model) and the black traces are those for the final model obtained by PBED inversion. Note the excellent match between the black (PBED results) and red traces and the rather poor match between the green (FBID result) and red ones (the traces have been normalised and a linear time gain function applied).

### 5.2. Model 2—two cross-shaped anomalies of contrasting permittivity and conductivity

Next, we consider a more complex model involving two cross-shaped anomalies embedded in a homogeneous background (Fig. 9a and d). The background of model 2 is characterised by εr=4 and σ=3 mS/m. For anomaly 1, εr=1 and σ=0.1 mS/m, whereas for anomaly 2, εr=8 and σ=10 mS/m. The increased difficulty in imaging this very high contrast model does not simply consist of more complex structures (crosses instead of square blocks), but also in the mutual interactions caused by the embedded inclusions (scattering effects), present in at least some of the traces shown in Fig. 10. The data were generated using the same recording geometry as for model 1 and inverted using the FBID and the new PBED schemes.

The crosses within model 2 are large enough in terms of size and contrast to cause time-shifts between the traces comparable to half the period of the dominant frequency. For this reason, the FBID scheme is unable to locate and characterise either body (Fig. 9b and e). The result shown are for homogeneous starting models, but no improvement is obtained by using the traveltime tomograms as the starting models. In contrast, the PBED scheme based on homogeneous starting models is able to image both crosses (Fig. 9c and f). The permittivity image is

![img-20.jpeg](img-20.jpeg)

Fig. 8. For model 1, radargrams for a source at 3.3 m depth in the left borehole and all receivers in the right borehole of Fig. 6. Results are given for the observed traces (red), initial model using traveltime tomography (blue), final model obtained by FBID inversion (green) and final model obtained by PBED inversion (black). A time-variant gain has been applied, along with trace normalization. Note the excellent agreement between the red and black curves (they mostly overlap).

40

G. Meles et al. / Journal of Applied Geophysics 78 (2012) 31–43

![img-21.jpeg](img-21.jpeg)

![img-22.jpeg](img-22.jpeg)

![img-23.jpeg](img-23.jpeg)

![img-24.jpeg](img-24.jpeg)

![img-25.jpeg](img-25.jpeg)

![img-26.jpeg](img-26.jpeg)

Fig. 9. (a) Permittivity and (d) conductivity distributions for the second synthetic model experiment involving two anomalous cross-shaped inclusions of low and high permittivity and conductivity in a uniform intermediate background. The "x" and "o" symbols stand for transmitters and receivers employed in the 4-sided experiment. The results of FBID inversion applied to the noise-free traces are shown in (b) and (e), whereas those of PBED inversion are shown in (c) and (f).

particularly good (Fig. 9c), whereas the conductivity image is somewhat contaminated by small-scale fluctuations, especially around the low conductivity feature (Fig. 9f). The data misfit corresponding to the final PBED inverted model is about 20% of that for the final FBID inverted model.

A selection of radargrams for the source at 5.3 m depth in one borehole and receivers in the opposite borehole is shown in Fig. 10. The colour coding is the same as for Fig. 8. The match between the black and red traces is again very good, much better than that between the green and red ones, demonstrating the clear superiority of the PBED over the FBID inversion results. What is especially impressive is the close match of the black and red traces along their entire lengths, including the back-scattered and reflected signals from the two crosses. The FBID scheme fails to fit the weaker later reflected arrivals, which are particularly diagnostic of the presence of the anomalous bodies.

### 5.3. Model 3—composite double embedded high and low permittivity/conductivity blocks in a homogeneous background

Model 3 is even more complex and challenging (Fig. 11). It includes two squares enclosed in two larger squares. The pairs of squares have different dimensions. The inner squares of the pairs have a relative permittivity εr=1 and a conductivity σ=0.1 mS/m, whereas the outer squares have εr=8 and σ=10 mS/m. The homogeneous background medium has εr=4 and σ=3 mS/m (Fig. 11a and f). The contrasts are again very large. For this model, the mutual interaction of the embedded inclusions is predominant in most of the traces (not shown).

The data were generated using the same recording geometry as for model 1 and inverted using the standard FBID and the new PBED schemes. Despite the size of the anomalous blocks involved, the time-shift differences between the traces are small compared to the critical value (i.e., half the dominant period) because of the compensating effects of the high and low permittivities (i.e., low and high velocity anomalies). Fig. 11b and g show the final FBID inversion results. The

conductivity image contains the correct relative features, but the permittivity image is seriously distorted. In fact, it appears as an indistinct slightly higher permittivity feature with no evidence for the central high. The inversion was repeated (not shown) using the traveltime tomogram as the starting model, but no improvements were observed. These double high/low permittivity (low/high velocity) blocks are slightly high permittivity (low velocity) features in the traveltime tomogram and are never updated in the right direction during the FBID inversion. This is an example where despite the time shifts between the observed and starting model being less than half the period (the necessary condition mentioned in

![img-27.jpeg](img-27.jpeg)

Fig. 10. For model 2, radargrams for a source at 5.3 m depth in the left borehole and all receivers in the right borehole of Fig. 9. Results are given for the observed traces (red), initial model using traveltime tomography (blue), final model obtained by FBID inversion (green) and final model obtained by PBED inversion (black). A time-variant gain has been applied, along with trace normalization. Note the excellent agreement between the red and black curves (they mostly overlap), including for the later scattered/reflected signals, whereas the green traces do not match the observed data nearly as well.

G. Meles et al. / Journal of Applied Geophysics 78 (2012) 31–43

41

![img-28.jpeg](img-28.jpeg)

![img-29.jpeg](img-29.jpeg)

![img-30.jpeg](img-30.jpeg)

![img-31.jpeg](img-31.jpeg)

![img-32.jpeg](img-32.jpeg)

![img-33.jpeg](img-33.jpeg)

![img-34.jpeg](img-34.jpeg)

![img-35.jpeg](img-35.jpeg)

Fig. 11. Model 3 synthetic experiment (a) and (f), involving two composite embedded high permittivity/high conductivity blocks of different sizes, each having their own inclusion of low permittivity/low conductivity material. Crosses and circles represent the sources and receivers employed in the 4-sided experiment. The results of FBID inversion applied to the noise-free traces are shown in (b) and (g), whereas those of PBED inversion are shown in (c) and (h). Permittivity cross sections along line CC' are shown in (e) and conductivity cross sections along the same line are shown in (e). Note how the inner inclusions have been recovered in (c) and (h).

Section 5.1.1), it is not sufficient to prevent the FBID inversion from failing.

Application of PBED inversion (Fig. 11c and h) yields high resolution images of both the inner and outer squares, with sharp boundaries in both the permittivity and conductivity displays. The inner square relative permittivity of 1 (air) is fully recovered. We also show vertical cross sections CC' passing through the two bodies as Fig. 11d and e. They highlight the close fit in the model space between the true and inverted distributions for PBED. In contrast, the fit is quite poor for the FBID inversion, with neither the shapes nor the magnitudes of the anomalies being properly recovered.

The radargrams for the final PBED model (not shown) match the observed data closely, with the later arriving scattered signals being correctly predicted (e.g., as for model 2 in Fig. 10). The new PBED method not only yields a good fit in the model space but also in the data space.

### 5.4. Model 4–layered model with stochastic fluctuations and multiple embedded low permittivity and low conductivity

Our final model (Fig. 12a and e) is more realistic and complicated than the previous ones, presenting a major challenge for full-waveform tomography. It comprises a three layer structure of contrasting permittivities and conductivities with superimposed

stochastic variations and multiple inclusions bodies of low permittivity ($\varepsilon_r=1$; high velocity) and low conductivity ($\sigma=0.1$ mS/m) located within the middle layer. The physical property contrasts of the inclusions are again very large and expected to create major difficulties (non-linearity issues) for most inversion schemes. The three small inclusions are sub-wavelength in dimension, whereas the larger one is not, but its size and large velocity contrast with the background means that significant time differences are expected to exist between the observed data and that computed for the starting model for paths that intersect the anomaly. A somewhat similar 3-layered model was investigated by Ernst et al. (2007a) and Meles et al. (2010), but it comprised inclusions of high permittivity/high conductivity, the latter being less challenging for GPR inversion. In this example, the borehole depths are 20.6 m and there are 10 source positions (crosses in the figure) and 10 receiver positions (circles in the figure) in each borehole, with an additional 5 sources along both the top and bottom edges of the model. The receivers surround the model on all four sides, with 80 receivers located in each borehole and 40 along the top and bottom of the model. The permittivity image that results from application of the FBID inversion scheme reveals some of the small inclusions not seen in the ray-based image and is therefore a slight improvement over that provided by traveltime tomography (compare Fig. 12b with Fig. 12c). However, both the ray-based and the FBID inversion schemes produce very poor

42

G. Meles et al. / Journal of Applied Geophysics 78 (2012) 31–43

![img-36.jpeg](img-36.jpeg)

![img-37.jpeg](img-37.jpeg)

![img-38.jpeg](img-38.jpeg)

![img-39.jpeg](img-39.jpeg)

![img-40.jpeg](img-40.jpeg)

![img-41.jpeg](img-41.jpeg)

![img-42.jpeg](img-42.jpeg)

![img-43.jpeg](img-43.jpeg)

Fig. 12. (a) Relative permittivity and (e) conductivity distributions for Model 4. The resulting tomograms obtained by applying travel time and amplitude tomography are shown in (b) and (f). Diagrams (c) and (g) give the relative permittivity and conductivity tomograms after applying FBID inversion, while (d) and (h) are the companion tomograms obtained by applying PBED inversion. The PBED images are a significant improvement over FBID using TTT as the starting model.

conductivity images (Fig. 12f and g), with the FBID result showing more artefacts.

The full-waveform PBED algorithm does a much better job in recovering the shapes and permittivities of the inclusions (Fig. 12d), but the conductivity image (Fig. 12h) is less than ideal, primarily because the anomalies are small and of low conductivity (loss of sensitivity). Nevertheless, it is a considerable improvement over the FBID conductivity inversion result.

## 6. Conclusions

We have presented a new full-waveform time-domain inversion scheme for GPR data based on a gradual and progressive expansion of the frequency content (starting at low frequency), as the iterations proceed. It is designed to tame the non-linearity problem that bedevils most inverse scattering problems, especially when the target contrasts are large. The performance of the new algorithm has been compared to that of our state-of-the-art scheme that inverts the full bandwidth data set from the first inversion stages. The synthetic results shown here clearly demonstrate that the new scheme can markedly improve the quality of the inversion results, largely avoiding local minima and strong artefacts in the permittivity and conductivity images. These results suggest that an approach solely based on full-waveform time-domain analysis is too unstable for many models that include high physical property contrasts.

The next steps will be to examine the behaviour of the new inversion algorithm on data contaminated by noise, both white and coloured, and to apply it to real data.

## Acknowledgements

This work was supported by grants from ETH Zurich and the Swiss National Science Foundation. We benefited from stimulating discussions with Dr Jacques Ernst and are indebted to Anja Klotzsche for providing the traveltime tomography starting models for some waveform inversions. We thank Dr Thomas Hansen and an anonymous reviewer for their helpful and insightful reviews of the paper.

## References

Carlsten, S., Johansson, S., Worman, A., 1995. Radar techniques for indicating internal erosion in embankment dams. J. Appl. Geophys. 33, 143–156.

Charara, M., Barnes, C., Tarantola, A., 1996. The state of affairs in inversion of seismic data: An OVSP example, 66th Ann. Internat. Mtg. Soc. Expl. Geophys., 1999–2002.

Charara, M., Barnes, C., Tarantola, A., 2000. Fullwaveform inversion of seismic data for a visco-elastic medium. Methods and Applications of Inversion, Lectures Notes in Earth Sciences, 92. Springer-Verlag, New York.

Chew, W.C., Wang, Y.M., 1990. Reconstruction of two-dimensional permittivity distribution using the distorted Born iterative method. IEEE Trans. Med. Imaging 9, 218–225.

Chew, W.C., Lin, J.H., 1995. A frequency-hopping approach for microwave imaging of large inhomogeneous bodies. IEEE Microwave Guided Wave Lett. 5, 439–441.

Clement, W.P., Barrash, W., 2006. Crosshole radar tomography in a fluvial aquifer near Boise, Idaho. J. Environ. Eng. Geophys. 11, 171–184.

Claerbout, J., 1985. Imaging the Earth's Interior. Blackwell Publishers.

Dubois, A., Belkebir, K., Catapano, I., Saillard, M., 2009. Iterative solution of the electromagnetic inverse scattering problem for the transient scattered field. Radio Sci. 44 (RS1007).

Ernst, J., Maurer, H., Green, A.G., Holliger, K., 2007a. Full-waveform inversion of crosshole radar data based on 2-D finite-difference time-domain (FDTD) solutions of Maxwell's equations. IEEE Trans. Geosci. Remote Sens. 45, 2807–2828.

Ernst, J., Green, A.G., Maurer, H., Holliger, K., 2007b. Application of a new 2-D time-domain full-waveform inversion scheme to crosshole radar data. Geophysics 72, J53–J64.

G. Meles et al. / Journal of Applied Geophysics 78 (2012) 31–43

43

Fear, E.C., Stuchly, M.A., 2000. Microwave detection of breast cancer. IEEE Trans. Microwave Theory Tech. 48, 1854–1863.

Fhager, A., Persson, M., 2005. Comparison of two image reconstruction algorithms for microwave tomography. Radio Sci. 40 (3) RS3017.

Fhager, A., Hashemzadeh, P., Baath, L., Persson, M., 2005. Microwave imaging for mammography using an iterative time-domain reconstruction algorithm: initial experiments. Proceedings of the 16th International Zurich Symposium on Electromagnetic compatibility: Topical Meetings, pp. 65–70.

Fhager, A., Persson, M., 2007. Using a priori data to improve the reconstruction of small objects in microwave tomography. IEEE Trans. Microwave Theory Tech. 55, 2454–2462.

Fullagar, P.K., Livelybrooks, D.W., Zhang, P., Calvert, A.J., Wu, Y.K., 2000. Radio tomography and borehole radar delineation of the McConnell nickel sulfide deposit, Sudbury, Ontario, Canada. Geophysics 51, 1387–1403.

GPR Conference 2010, Lecce, 2010. Extended Abstracts.

Gustafson, M., He, S., 2000. An optimization approach to two-dimensional time domain electromagnetic inverse problems. Radio Sci. 35, 525–536.

Hagness, S.C., Taflove, A., Bridges, J.E., 1998. Two-dimensional FDTD analysis of a pulsed microwave confocal system for breast cancer detection: fixed focus and antenna-array sensors. IEEE Trans. Biomed. Eng. 45, 1470–1479.

Hashemzadeh, P., Fhager, A., Persson, M., 2006. Experimental investigation of an optimization approach to microwave tomography. Electromagn. Biol. Med. 25, 1–12.

Heinke, B., Gren, A.G., van der Kruk, J., Horstmeyer, H., 2005. Acquisition and processing strategies for 3-D georadar surveying a region characterized by rugged topography. Geophysics 70, K53–K61.

Klotzsche, A., van der Kruk, J., Meles, G., Doetsch, J., Maurer, H., 2010. Full-waveform inversion of crosshole ground penetrating radar data to characterise a gravel aquifer close to the River Thur, Switzerland. Near Surface Geophysics 8, 635–649.

Kuroda, S., Takeuchi, M., Kim, H., 2007. Full-waveform inversion algorithm for interpreting crosshole radar data: a theoretical approach. Korean Geosci. J. 11, 211–217.

Maurer, H., Greenhalgh, S.A., Latzel, S., 2009. Frequency and spatial sampling strategies for acoustic crosshole full waveform inversion experiments. Geophysics 74 WCC79-WCC89.

Meles, G., van der Kruk, J., Greenhalgh, S., Ernst, J., Maurer, H., Green, A.G., 2010. A new vector waveform inversion algorithm for simultaneous updating of conductivity and permittivity parameters from combination crosshole/borehole-to-surface GPR data. IEEE Trans. Geosci. Remote Sens. 48, 3391–3407.

Mora, P., 1987. Nonlinear two-dimensional elastic inversion of multioffset seismic data. Geophysics 52, 1211–1228.

Mora, P., 1989. Inversion = migration + tomography. Geophysics 54, 1575–1586.

Musil, M., Maurer, H., Holliger, K., Green, A.G., 2006. Internal structure of an alpine rock glacier based on crosshole georadar traveltimes and amplitudes. Geophys. Prospect. 54, 273–285.

Olsson, O., Falk, L., Forslund, O., Lundmark, L., Sanberg, E., 1992. Borehole radar applied to the characterization of hydraulically conductive fracture zones in crystalline rock. Geophys. Prospect. 40, 109–142.

Pica, A., Diet, J.P., Tarantola, A., 1990. Nonlinear inversion of seismic reflection data in a laterally invariant medium. Geophysics 55, 284–292.

Plessis, R.E. 2008. Introduction: Towards a full waveform inversion. Geophys. Prosp. 56, 761–763 (entire issue No. 6, 761–906, is devoted to full waveform inversion).

Pratt, R.G., Shin, C., Hicks, G.J., 1998. Gauss–Newton and full Newton methods in frequency-space seismic waveform inversion. Geophys. J. Int. 133, 341–362.

Rubaek, T., Meaney, P.M., Meincke, P., Paulsen, K.D., 2007. Nonlinear microwave imaging for breast-cancer screening using Gauss–Newton's method and the CGLS inversion algorithm. IEEE Trans. Antennas Propag. 55 (8), 2320–2331.

Rubaek, T., Kim, O.S., Meincke, P., 2009. Computational validation of a 3-D microwave imaging system for breast-cancer screening. IEEE Trans. Antennas Propag. 57 (7), 2105–2115.

Sirgue, L., Pratt, R.G., 2004. Efficient waveform inversion and imaging: a strategy for selecting temporal frequencies. Geophysics 69, 231–248.

Solvodieri, F., 2010. Advanced signal processing, inversion and tomography. Invited talk, 13th International Conference on Ground Penetrating Radar, Lecce, Italy, 21–25 June 2010 (CD Rom of Proceedings).

Streich, R., van der Kruk, J., Green, A.G., 2006. Three-dimensional multicomponent georadar imaging of sedimentary structures. Near Surf. Geophys. 4, 39–48.

Tanaka, T., Takenaka, T., He, S., 1999. An FDTD approach to the time-domain inverse scattering problem for an inhomogeneous cylindrical object. Microwave Opt. Technol. Lett. 20, 72–77.

Tarantola, A., 1986. A strategy for nonlinear elastic inversion of seismic reflection data. Geophysics 51, 1893–1903.

Tronicke, J.D., Tweeton, D.R., Dietrich, P., Appel, E., 2001. Improved crosshole radar tomography by using direct and reflected arrival times. J. Appl. Geophys. 47, 97–105.

Van der Kruk, J., Wapenaar, C.P., Fokkema, J.T., van der Berg, P.M., 2003. Three dimensional imaging of multicomponent ground penetrating radar data. Geophysics 68, 1241–1256.

Wang, Y.M., Chew, W.C., 1989. An iterative solution of the two-dimensional electromagnetic inverse scattering problem. Int. J. Imaging Syst. Technol. 1, 100–108.

Wu, R., Toksoz, N., 1987. Diffraction tomography and multisource holography applied to seismic imaging. Geophysics 52, 11–25.

Yilmaz, O., Doherty, S.M., 2001. Seismic data analysis: processing, inversion and interpretation of seismic data. Society of Exploration Geophysicists, Investigations in Geophysics No. 10, 2. Tulsa.

Zhou, B., Greenhalgh, S.A., 2003. Crosshole seismic inversion with normalized full-waveform amplitude data. Geophysics 68, 1320–1330.