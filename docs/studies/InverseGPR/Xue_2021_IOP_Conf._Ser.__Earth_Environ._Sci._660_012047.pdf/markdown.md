IOP Conference Series:
Earth and
Environmental Science

PURPOSE-LED
PUBLISHING™

PAPER • OPEN ACCESS

# A Co-offset GPR Data Inversion Based on Ray Theory

To cite this article: Meiqi Xue et al 2021 IOP Conf. Ser.: Earth Environ. Sci. 660 012047

View the article online for updates and enhancements.

You may also like

- 3D imaging and temporal evolution recognition of concrete internal defects based on GPR
Zhengfang Wang, Bo Li, Ming Lei et al.
- GPR background removal using a directional total variation minimisation approach
Essam A Rashed
- A review of deep learning applications in ground penetrating radar for urban subsurface object detection
Wenxing Shi, Feng Yang, Suping Peng et al.

This content was downloaded from IP address 181.42.18.171 on 30/06/2026 at 02:27

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

The 9th International Conference on Environmental and Engineering Geophysics

IOP Publishing

IOP Conf. Series: Earth and Environmental Science 660 (2021) 012047 doi:10.1088/1755-1315/660/1/012047

![img-0.jpeg](img-0.jpeg)

(a)

![img-1.jpeg](img-1.jpeg)

(b)

Figure1. (a). Rough surface corresponding to different RMS height with the same correlation length (lc = 2m); (b). Rough surface corresponding to different correlation length with the same RMS height(rms = 0.5m).

### 2.3. Inversion method based on geometric ray theory

The velocity analysis method we used was proposed by Forte et al. in 2014. We assume that the propagation signal is a plane EM wave. Near each trace location, the underground medium is assumed to be homogeneous, isotropic, non-magnetic ( \( \mu_{r}=1 \) ), non-conductive ( \( \sigma=0 \) ), and non-dispersible. The changes of antenna coupling, inherent attenuation and scattering effect are ignored. Normal GPR surveys are performed in transverse electric (TE) broadside configuration. Therefore, we only consider the TE mode (Forte et al., 2014). According to these assumptions, the proposed method requires offset(x), velocity of the first layer medium ( \( v_{1} \) ), amplitude of direct wave ( \( Ai_{1} \) ), amplitude of reflected wave ( \( As_{i} \) ) and travel time ( \( TWT_{i} \) ).

Given the first layer velocity \((v_{1})\), offset(x), and travel time of the first layer \((TWT_{1})\), we can get the thickness of the first layer \((h_{1})\) by equation (1):

\[
h _ {1} = \frac {1}{2} \sqrt {\left(v _ {1} T W T _ {1}\right) ^ {2} - x ^ {2}} \tag {1}
\]

Then the angle of incidence is obtained by equation(2):

\[
\theta_ {1} = \operatorname{Arctan} \left(\frac {x}{2 h _ {1}}\right) \tag {2}
\]

Using the amplitude values picked up ( \( As_{1} \)  and  \( Ai_{1} \) ), the reflection coefficient of the first layer  \( R_{1} \)  can be obtained by equation (3).

\[
R _ {1} = \frac {A s _ {1}}{A i _ {1}} \tag {3}
\]

Then Snell equation gives the velocity of GPR signal in the second layer:

\[
v _ {2} = \frac {\sin (\theta_ {2})}{\sin (\theta_ {1})} v _ {1} \tag {4}
\]

Where \(\theta_{2}\) is obtained by rearranging the Fresnel equation of TE mode [1]:

\[
\theta_ {2} = \operatorname{Arctan} \left(\frac {1 + R _ {1}}{1 - R _ {1}} \tan \theta_ {1}\right) \tag {5}
\]

If we know the thickness of the first n - 1 layers, the GPR signal velocities of the first n layers and the  \( TWT_{n} \)  of the nth interface reflected wave, then the thickness of the nth layer ( \( h_{n} \) ) is the only positive solution of the following third-degree equation [1]:

\[
a h _ {n} ^ {3} + b h _ {n} ^ {2} + c h _ {n} + d = 0 \tag {6}
\]

where

\[
a = \frac {4}{v _ {n}} \tag {7}
\]

\[
\mathrm{b} = \frac {4}{v _ {n} ^ {2}} \sum_ {i = 1} ^ {n - 1} v _ {i} h _ {i} + 8 \sum_ {i = 1} ^ {n - 1} \frac {h _ {i}}{v _ {i}} \tag {8}
\]

2

The 9th International Conference on Environmental and Engineering Geophysics

IOP Publishing

IOP Conf. Series: Earth and Environmental Science 660 (2021) 012047 doi:10.1088/1755-1315/660/1/012047

$$c = \frac{x^2}{v_n} + \frac{8}{v_n} \left( \sum_{i=1}^{n-1} v_i h_i \right) \left( \sum_{i=1}^{n-1} \frac{h_i}{v_i} \right) + 4 v_n (\sum_{i=1}^{n-1} \frac{h_i}{v_i})^2 - v_n T W T_n^2 \tag{9}$$

In horizontally layered media, the incident angle of the $k$th interface is equal to the transmitted angle of the $(k - 1)$th interface. Such angle $(\theta_k)$ is related to the horizontal projection $(\Delta x_k)$ of the travel path in the kth layer (Fig.2) through the following equation:

$$\text{Tan}(\theta_k) = \frac{\Delta x_k}{h_k} \tag{10}$$

Considering the small value of $\theta_k$ and the Snell's equation, we obtain:

$$\Delta x_k = \frac{v_k h_k}{v_{k-1} h_{k-1}} \Delta x_{k-1} \tag{11}$$

According to geometric conditions:

$$\sum_{i=1}^{n} \Delta x_i = \frac{x}{2} \tag{12}$$

Then, we can use the Fresnel equation for TE antenna configuration to calculate the first $n - 1$ reflection and transmission coefficients relative to the nth reflected wave:

$$R_k = \frac{\sin(\theta_{k+1} - \theta_k)}{\sin(\theta_{k+1} + \theta_k)} \tag{13}$$

$$T_k = 1 + R_k \tag{14}$$

with $k = 1, 2, \cdots, n - 1$.

![img-2.jpeg](img-2.jpeg)

Figure 2. Schematic diagram of electromagnetic wave ray path in horizontally layered media (take three-layer medium as an example). S represents the transmitter, R represents the receiver, x is the offset, $h_i$ and $v_i$ are respectively the thicknesses and EM velocities of the layers, $\theta_i$ and $\Delta x_i$ are respectively the incident angles and the horizontal projections of the travel path.

Considering the symmetry of the travel path (Fig.2), and using the above coefficients and amplitudes we picked ($As_n$ and $Ai_1$), we can obtain the incident and reflected amplitudes of the nth interface by the follow equation:

$$\text{Ai}_n = \prod_{i=1}^{n-1} T_i \tag{15}$$

$$\text{Ar}_n = \frac{\text{As}_n}{\prod_{i=1}^{n-1} (2 - T_i)} \tag{16}$$

Then, the reflection coefficient of the $n$ th interface is given by:

$$R_n = \frac{\text{Ar}_n}{\text{Ai}_n} \tag{17}$$

The velocity in the $(n + 1)$th layer is given by the Snell's equation:

3

The 9th International Conference on Environmental and Engineering Geophysics

IOP Publishing

IOP Conf. Series: Earth and Environmental Science 660 (2021) 012047 doi:10.1088/1755-1315/660/1/012047

\[
v _ {n + 1} = \frac {\sin (\theta_ {n + 1})}{\sin (\theta_ {n})} v _ {n} \tag {18}
\]

with

\[
\theta_ {n + 1} = \operatorname{Arctan} \left(\frac {1 + R _ {n}}{1 - R _ {n}} \tan \theta_ {n}\right) \tag {19}
\]

By iterating this method for all the interpreted reflections in a GPR trace, we can obtain the thicknesses and velocities of all the imaged layers.

### 2.4. Numerical examples

First, we established three undulating stratum models of size  \( 10m \times 5m \) , with the same correlation length and different RMS heights. The specific parameters are shown in Table 1.

Table 1. Parameters of models used in forward modeling.

|   | Relative permittivity |   |   |   | L(m) | cl(m) | rms(m)  |
| --- | --- | --- | --- | --- | --- | --- | --- |
|   |  Layer 1 | Layer 2 | Layer 3 | Layer 4  |   |   |   |
|  Model 1 | 5 | 10 | 15 | 20 | 15 | 10 | 0.4  |
|  Model 2 | 5 | 10 | 15 | 20 | 15 | 10 | 0.3  |

Then, numerical simulation is performed on the established model with the following parameters:

Table 2. Parameters of forward simulation.

|  Frequency of transmitting antenna |   | 100MHz  |
| --- | --- | --- |
|  dt |   | 0.04ns  |
|  t |   | 120ns  |
|  Transmitting antenna | Start position | 0.5m  |
|   |  End position | 8.5m  |
|   |  Moving step | 0.25m  |
|  Receiving antenna | Start position | 1.0m  |
|   |  End position | 0.25m  |
|   |  Moving step | 9.0m  |

After obtaining the forward results, we pick up the reflection amplitude, perform the above iterative inversion on all traces of data, and perform linear interpolation on the space between the two tracks. The figures of numerical models and calculated results are as follows:

![img-3.jpeg](img-3.jpeg)

(a)

![img-4.jpeg](img-4.jpeg)

(b)

4

The 9th International Conference on Environmental and Engineering Geophysics

IOP Publishing

IOP Conf. Series: Earth and Environmental Science 660 (2021) 012047 doi:10.1088/1755-1315/660/1/012047

![img-5.jpeg](img-5.jpeg)

(c)

![img-6.jpeg](img-6.jpeg)

(d)

![img-7.jpeg](img-7.jpeg)

(e)

![img-8.jpeg](img-8.jpeg)

(f)

Figure 3. (a). Diagram of numerical model(rms = 0.4m); (b). Diagram of calculated model(rms = 0.4m); (c). Diagram of numerical model(rms = 0.3m); (d). Diagram of calculated model(rms = 0.3m); (e). Diagram of numerical model(rms = 0.2m); (f). Diagram of calculated model(rms = 0.2m);

The top blue layer of the diagram of models is air. The transmitting and receiving antennas are located at 0m on the y-axis.

Due to the position setting of transmitting antenna and the receiving antenna, we can only calculate the dielectric constant of the medium between 0.75m – 8.75m.

It can be seen from above examples that this method can be used for the inversion of co-offset GPR data. It can perfectly distinguish the shape and position of the reflection interface, but as the RMS increases, the calculation error of the permittivity of the medium is also increasing.

Then, we established three undulating stratum models with the same RMS heights and different correlation length. The specific parameters are shown in Table 3.

Table 3. Parameters of models used in forward modeling.

|   | Relative permittivity |   |   |   | L(m) | cl(m) | rms(m)  |
| --- | --- | --- | --- | --- | --- | --- | --- |
|   |  Layer 1 | Layer 2 | Layer 3 | Layer 4  |   |   |   |
|  Model 4 | 5 | 10 | 15 | 20 | 15 | 3 | 0.1  |
|  Model 5 | 5 | 10 | 15 | 20 | 15 | 4 | 0.1  |
|  Model 6 | 5 | 10 | 15 | 20 | 15 | 6 | 0.1  |

The figures of numerical models and calculated results are as follows:

![img-9.jpeg](img-9.jpeg)

(a)

![img-10.jpeg](img-10.jpeg)

(b)

5

The 9th International Conference on Environmental and Engineering Geophysics

IOP Publishing

IOP Conf. Series: Earth and Environmental Science 660 (2021) 012047 doi:10.1088/1755-1315/660/1/012047

![img-11.jpeg](img-11.jpeg)

(c)

![img-12.jpeg](img-12.jpeg)

(d)

![img-13.jpeg](img-13.jpeg)

(e)

![img-14.jpeg](img-14.jpeg)

(f)

Figure 4. (a). Diagram of initial model ($\zeta$cl = 3m); (b). Diagram of calculated model ($\zeta$cl = 3m); (c). Diagram of initial model ($\zeta$cl = 4m); (d). Diagram of calculated model ($\zeta$cl = 4m); (e). Diagram of initial model ($\zeta$cl = 6m); (f). Diagram of calculated model ($\zeta$cl = 6m);

It can be seen from above examples, as the correlation length increases, the calculation error of the permittivity of the medium is also decreasing.

### 3. Conclusions

It is proved that the ray-tracing based inversion is feasible in the layered geological model with random undulation, as the RMS increases, that is, the degree of undulation of the reflection interface increases, the calculation error of the permittivity of the medium is also increasing; as the correlation length increases, that is, the degree of undulation of the reflection interface decreases, the calculation error of the permittivity of the medium is also decreasing.

### References

[1] Forte E, Dossi M, Pipan M and Colucci R R 2014 Velocity analysis from common offset GPR data inversion: theory and application to synthetic and real data Geophysical Journal International 197 1471-1483

[2] Yilmaz Ö 2001 Seismic data analysis: Processing, inversion, and interpretation of seismic data Society of exploration geophysicists

[3] Pipan M, Baradello L, Forte E, Prizzon A and Finetti I 1999 2-D and 3-D processing and interpretation of multi-fold ground penetrating radar data: a case history from an archaeological site Journal of Applied geophysics 41 271-292

[4] Taflove A and Hagness S C 2005 Computational electrodynamics: the finite-difference time-domain method Artech house

[5] Irving J and Knight R 2006 Numerical modeling of ground-penetrating radar in 2-D using MATLAB Computers & Geosciences 32 1247-1258

[6] Balanis C A 1999 Advanced engineering electromagnetics John Wiley & Sons

6