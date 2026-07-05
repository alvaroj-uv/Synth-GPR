The 9th International Conference on Environmental and Engineering Geophysics

IOP Publishing

IOP Conf. Series: Earth and Environmental Science 660 (2021) 012047 doi:10.1088/1755-1315/660/1/012047

# A Co-offset GPR Data Inversion Based on Ray Theory

Meiqi Xue¹, Sixin Liu¹,²,*, Qi Lu¹, Hongqing Li¹, Yuanxin Wang¹

¹ School of Earth Exploration Science and Technology, Jilin University, Changchun, China

² Science and Technology on Near-Surface Detection Laboratory, Wuxi
E-mail: liusixin@jlu.edu.cn

Abstract. We use Monte Carlo method to establish a randomly undulating homogeneous layered medium model. Then the co-offset GPR data for the built geological model is simulated by FDTD. The ray-tracing based inversion is applied for interval velocity estimation. During the inversion, the offset between antennas, the velocity value of the first layer, the picked amplitudes values of each reflection layer and reference amplitude are the input data. The thickness and velocity of each layer are calculated by this recursive method. It is proved that this inversion method is feasible for the layered geological model with random undulation, and the fact that undulation, i.e. RMS height and correlation length, influences the inversion results is discussed.

## 1. Introduction

GPR is a high-resolution geophysical technology based on the propagation of electromagnetic wave in the frequency range between 1MHz and 3GHz [1]. In seismic research, velocity models are usually obtained by analyzing data collected at multiple source-receiver offsets [2]. However, most commercial GPR systems are equipped with a single receiver antenna, so the acquisition of multiple offset data sets is very demanding [3]. GPR data collection in common offset is simple, fast, and can be used for large-scale survey along the gird or line. The obtained data show the change of the physical properties of the underground medium within a certain range. Therefore, we can use the co-offset GPR data to estimate velocity.

## 2. Method

### 2.1. Monte Carlo method for stochastic rough surface modeling

The basic idea of Monte Carlo method is to filter it with power spectrum in frequency domain, do inverse fast Fourier transform (IFFT) to get the height fluctuation of rough surface. Figure 1 and Figure 2 show the samples of random rough surface under different RMS height and correlation length. The RMS height and the correlation length related to the scale of the rough surface in the vertical and the horizontal direction respectively.

### 2.2. Forward method based on FDTD

FDTD method differentiates Maxwell equation in time domain and space domain. Using leap-frog---alternating calculation of electric and magnetic fields in space domain, and the change of electromagnetic field is simulated by updating in the time domain to achieve the purpose of numerical calculation [4]. FDTD method is relatively simple in concept, accurate for any complex model [5-6]. This paper uses MATLAB code based on FDTD and PML absorbing boundary provided by Irving and Knight in 2006.

CC BY

Content from this work may be used under the terms of the Creative Commons Attribution 3.0 licence. Any further distribution of this work must maintain attribution to the author(s) and the title of the work, journal citation and DOI.

Published under licence by IOP Publishing Ltd

1