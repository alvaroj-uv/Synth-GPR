wavelength from the true values (Meles et al. (2010)).) The final SW is fed into the FWI process.

The final reflectivity structure that comes out of the SBD can be considered as a model of data in which the effect of the pulse shape and much of the noise are removed. Therefore, the hyperbolas in the estimated reflectivity model are clear and are used to perform the ray-based analysis associated with equations 2-7. The ray-estimated rebar locations and diameters and concrete permittivity are used as the FWI starting model. Details on the FWI process are described in step 5 of Jazayeri et al. (2018).

### 4.5 Results

We evaluate the performance of the proposed method on one synthetic and two real data examples acquired with different instruments in different experiments.

#### 4.5.1 Synthetic data, reinforced concrete

For the synthetic test, we create 3D data with the first derivative of a Ricker wavelet with 35° phase rotation as the source wavelet (following Jazayeri et al. (2019, 2018)). The antenna is a Hertzian dipole with 3 cm transmitter-receiver offset and nominal frequency of 2.4 GHz. Four metallic rebars are placed at depths between 2.7 and 4 cm (see Table 4.1 and Figure 4.3) in uniform concrete. High and low frequency noise are added to the data with a Gaussian distribution of high-frequency noise centered at 3 GHz and peak value of 25% of the pulse amplitude, and lower frequency noise (1.5 MHz) added at a lower level (15% of pulse amplitude) (Figure 4.1). Parts of the diffracted signal, specifically for the rebar #4 are mixed with the direct wave. Realistic modeling of the direct wave is challenging due to the fact that it falls in the near-field zone. To avoid including the direct wave in the analysis, a background removal filter (an average trace removal across the whole profile) is applied to the data (Figure 4.5).

To define the initial source wavelet required for the SBD algorithm sections of data in proximity to the hyperbola apexes are carefully selected, time-shifted in order to maximize

16