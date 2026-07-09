This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING

1

# Sparse Blind Deconvolution of Ground Penetrating Radar Data

Sajad Jazayeri, Nasser Kazemi, and Sarah Kruse

Abstract—We propose an effective method for sparse blind deconvolution (SBD) of ground penetrating radar data. The SBD algorithm has no constraints on the phase of the wavelet, but the initial wavelet must be carefully captured from the data. The data are considered a convolution product of an unknown source wavelet and unknown sparse reflectivity series. The algorithm developed here is an alternating minimization technique that updates the reflectivity series and the wavelet iteratively. The reflectivity update is solved as an $\ell_2 - \ell_1$ problem with the alternating split Bregman iteration technique. The wavelet update is solved as an $\ell_2 - \ell_2$ problem with Wiener deconvolution. The algorithm converges to a local minimum. In order to increase the likelihood so that convergence coincides with the desired local minimum, special steps are taken to provide a proper initial wavelet. Synthetic and real data examples show that both subsurface reflectivity series and wavelet (amplitude and phase) can be estimated efficiently. The SBD method presented appears robust and compares favorably to previous studies in its resistance to noise.

Index Terms—Deconvolution, ground penetrating radar (GPR), reflectivity, source wavelet, sparsity.

# I. INTRODUCTION

DECONVOLUTION is a popular deblurring technique used in signal and image processing, with applications in photography, remote sensing, astronomy, medical imaging, geophysics, and more [1], [2]. When successfully applied to blurry or distorted matrices, the result is a clearer image with more details. In geophysics, particularly in exploration seismology, the goal of deconvolution is higher resolution subsurface images [3]. Deconvolution works by removing the signature of the propagated waveform. Ideally, what is left is a representation of the subsurface pattern of reflection coefficients, which present a high-resolution subsurface image [4].

Deconvolution of ground penetrating radar (GPR) data is used to estimate the reflectivity series [5]–[13], to produce a higher resolution subsurface image or a clean reflectivity series that can be used for ray-based travel-time analysis. GPR deconvolution is also used to extract the shape of the transmitted pulse [14]–[16], for use in modeling procedures

Manuscript received April 27, 2018; revised August 10, 2018 and September 23, 2018; accepted November 18, 2018. (Corresponding author: Sajad Jazayeri.)

S. Jazayeri and S. Kruse are with the School of Geosciences, University of South Florida, Tampa, FL 33620 USA (e-mail: sjazayeri@mail.usf.edu; skruse@usf.edu).

N. Kazemi is with the Department of Chemical and Petroleum Engineering, University of Calgary, Calgary, AB T2N 1N4, Canada (e-mail: nasser.kazeminojadeh@ucalgary.ca).

Digital Object Identifier 10.1109/TGRS.2018.2886741

such as full-waveform inversion (FWI). Factors such as antenna-ground coupling and Earth's filtering effects due to soil's characteristics alter the shape of the wavelet [10], which make it challenging to estimate the waveform and reflectivity series.

The widely used Wiener deconvolution [17], [18] has some disadvantages when applied to GPR data. Wiener deconvolution assumes that the reflectivity series has an ideal statistical property, i.e., it is white noise, and the wavelet has a minimum phase characteristics [17], [18]. However, Ricker [19] shows that due to the earth filtering, the average wavelet is different from the near-source signature. We show, here, that when using the Wiener deconvolution method, we can only estimate a smooth reflectivity series and a residual wavelet; any difference between the actual wavelet and its minimum phase equivalent remains untouched in the recovered reflectivity series. Fortunately, a body of literature shows the possibility of estimating nonminimum phase wavelets by imposing a sparsity constraint instead of a white noise assumption (i.e., Gaussian distribution) on the reflectivity series [20]–[25].

The alternative deconvolution method is referred to as sparse blind deconvolution (SBD). A sparsity assumption is imposed on the matrix of reflection coefficients. The process begins "blindly" in that it is formulated to start without requiring a starting model of reflection coefficients, or without a starting model for the source wavelet. The sparsity assumption is well adapted to enhancing the resolution of thin layers and isolated buried objects. The method thus holds promise particularly for both layered geological features and engineering, archeological, or tree root applications where finite objects produce distinctive returns within a background of soil structure. Few studies have applied a sparsity assumption while performing deconvolution on GPR data [26], [27]. The method presented by Chahine et al. [26] improves image resolution in the presence of thin layers by sparsity maximization in the reflectivity series with results similar to spiking deconvolution. Their method requires a minimum phase wavelet and is sensitive to noise. Li [27] introduces an alternating iterative method to solve the nonconvex optimization problem, with a threshold maximum for the reflector amplitudes to avoid trapping the solution in local minima. Tested only on synthetic data, Li's algorithm struggles to recover the shape and the phase of the source wavelet in the presence of noise.

In this paper, we propose an alternating SBD method targeting GPR data, which may be more robust in the presence of noise. The algorithm estimates both the wavelet and the

0196-2892 © 2019 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission. See http://www.ieee.org/publications_standards/publications/rights/index.html for more information.

56