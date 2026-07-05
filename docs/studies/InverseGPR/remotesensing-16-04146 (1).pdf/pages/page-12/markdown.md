Remote Sens. 2024, 16, 4146

12 of 19

the background relative permittivity and conductivity distributions, ultimately resulting in poor imaging quality. This is due to the cycle-skipping phenomenon caused by large initial model errors, trapping the parameter inversion in local minima. However, when the $W_2$ distance is used as the misfit function, although some artifacts are still present, the inversion quality improves significantly. This improvement is attributed to the $W_2$ distance interpreting the misfit as a transportation cost, inherently capturing time-shift information and overall signal variation, thereby alleviating the local minima problem.

In synthetic data, an initial model with minimal error can be established with known information. However, in field data, only limited information is available to construct an approximate initial model, which often differs significantly from the actual subsurface conditions. Therefore, the low initial model dependence and favorable convexity of the $W_2$ distance FWI method is highly beneficial for GPR parameter inversion.

Additionally, tests showed that incorporating data with higher frequencies did not enhance the inversion results, so this study only presents the iterative inversion results for the frequency batches up to 120 MHz.

### 3.2. Example 2: Dependence Analysis of Noise Sensitivity

One of the excellent attributes of the $W_2$-based method is its low sensitivity to noise. Ground-penetrating radar data collected in the field are always contaminated by various noise signals, which decreases the quality of the final inversion results. The application of the Wasserstein distance in seismic velocity FWI inversion has demonstrated that $W_2$ distance, as a misfit function, possesses noise robustness [24] compared to the traditional $L_2$ norm.

According to the mismatch function Formulas (3) and (4), when zero-mean noise is added to the effective signal, the impact on the total transportation cost of the signal can be negligible. Here, let $f$ be the effective signal and $\delta$ be the random noise. The signal affected by noise $g$ can be represented as follows:

$$
g = f + \delta \tag{15}
$$

The random noise $\delta$ has a mean of 0 and a variance of $\eta$. The signal is discretized into n sampling points. For the $L_2$ norm, the following equation is used:

$$
\mathrm{E}|f - g|^2 = \mathrm{O}(\eta) \tag{16}
$$

For the $W_2$ distance, the expected value is as follows:

$$
\mathrm{E}W_2(f, g) = \mathrm{O}\left(\frac{1}{n}\right) \tag{17}
$$

According to Equation (17), if the number of sampling points $n$ is sufficiently large, the impact of noise on the $W_2$ distance mismatch function can be negligible, even if the noise is very strong. Detailed derivations are discussed in [32]. From Equations (16) and (17), it can be seen that compared to the traditional $L_2$ norm, the $W_2$ distance has lower noise sensitivity. The following experiment compares the noise sensitivity of the two methods using the same model in the first section. All experimental methods and settings are the same as in the first section, except that the observation data used for inversion and model I (Figure 4) are used as the initial model.

In this numerical experiment, clean forward simulation signals were first obtained (as shown in Figure 10a). Random noise was then added, with a signal-to-noise ratio (SNR) of 20 dB. The SNR is defined based on the signal power and noise power, and the calculation formula is as follows:

$$
\mathrm{SNR}(\mathrm{dB}) = 10 \log_{10} \frac{P_{\text{signal}}}{P_{\text{noise}}} \tag{18}
$$

Figure 10b shows the observation data for a single source with multiple receivers after adding noise. Figures 11 and 12 compare the results of relative permittivity and conductivity