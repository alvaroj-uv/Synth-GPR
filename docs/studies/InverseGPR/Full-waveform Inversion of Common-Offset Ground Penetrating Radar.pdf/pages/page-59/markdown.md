FWI of common-offset GPR using PEST

H39

synthetic data pulses are offset less than a half wavelength from the measured traces. For the clean synthetic data, this criteria can be met with a model that assumes a permittivity within 50% of the correct value, and the inversion proceeds toward a permittivity closer to the correct value. For the field data case in which two diffracted hyperbolas are recorded, ray theory can provide good starting model parameters for the FWI process. In the cases of gas-filled pipes (or very narrow liquid-filled cylinders, such as tree roots) that are likely to generate just one diffraction hyperbola, the ray theory fails to provide good starting models; in this case, the best judgment of the user must be used to set the initial model parameters. In this sense, a successful inversion confirms the initial guess, whereas a failure to converge or a small reduction in cost function suggests a poor starting model.

## CONCLUSION

This paper introduces a new method for FWI of common-offset GPR data, particularly targeting the dimensions and infilling material of buried pipes. The method is designed to be used in which clear isolated diffraction hyperbolas indicate the presence of a pipe, but pipe dimensions and filling may be unknown. The method consists of five main steps: GPR data processing, ray-based analysis to set a good initial model, 3D to 2D transformation of data, effective SW estimation, and FWI. The method combines two freely available software packages: PEST for the inversion and gprMax for forward modeling of the GPR data.

This method is applied on a synthetic 3D data set and two 800 MHz GPR profiles collected over a PVC pipe buried in clean sands. In the synthetic and water-filled and air-filled pipe field cases, good initial estimates of the depth and diameter of the pipe from the ray-based analysis are improved after FWI. The tests show that although the initial estimate of pipe diameter is within 30%–50% of the true value, the inversion yields estimates with < 8% error. For the field data, the requirement of a good starting model can, in practice, confirm or deny a starting assumption about the pipe-filling material.

Ray-based analysis is essential to set up the starting model, particularly to estimate the pipe location and average soil permittivity and conductivity. Although ray-based conductivity estimates are possible, improvement in the conductivity would require the SW to be updated after each iteration in the FWI procedure. Iterations on the SW during the FWI process, as in Busch et al. (2012, 2014), are beyond the scope of this study.

The method in its present form is only effective for isolated hyperbolas, and it assumes that GPR surveys are conducted with broadside antenna geometry along profiles perpendicular to horizontal pipes. Furthermore, the soil is assumed to be locally homogeneous. Relaxation of these conditions is the subject of ongoing research.

## ACKNOWLEDGMENTS

The authors are very grateful to J. van der Kruk for very constructive comments, S. Esmaeili and C. Downs for field assistance, D. Voytenko and N. Voss for their introduction to PEST, A. Giannopoulos and C. Warren for their help with gprMax, and A. Green for assistance implementing algorithms on the USF Research Computing cluster. S. Busch, G. Tsofias, B. Schneider, and three

anonymous reviewers gave productive reviews that greatly improved the manuscript.

## APPENDIX A

### RAY BASED ANALYSIS TO ESTIMATE CONDUCTIVITY VALUES

Assuming homogeneous soil, the amplitude of the GPR wave decays due to geometric spreading and soil attenuation. The combination of these two effects can be described with wave amplitude proportional to $e^{-\alpha r}/r$ in 3D media, in which the attenuation term $\alpha$ can be described as

$$\alpha = \frac{\sigma}{2} \sqrt{\frac{\mu}{\varepsilon}}, \tag{A-1}$$

where $\sigma$ is the soil conductivity, $\mu$ is the magnetic permeability, and $\varepsilon$ is the mean absolute electrical permittivity of the soil.

To estimate the conductivity of the soil, the peak amplitudes of the first pipe diffraction hyperbola arrivals are picked and used in a least-squares inversion for the attenuation term, and thereby the soil conductivity. Assuming far-field amplitudes, a uniform antenna radiation pattern, and a uniform reflection coefficient from all parts of the pipe, the amplitude $A$ of the wave having traveled a distance $r$ is expressed as

$$A = A_0 \frac{e^{-\alpha r}}{r}, \tag{A-2}$$

where $A_0$ is a constant. The term $e^{-\alpha r}$ can be replaced the first two terms of its Taylor series expansion, $1 + \alpha r$, leaving $A = A_0(1/(e^{\alpha r})r) \approx A_0(1/(1 + \alpha r)r)$. Rearranging,

$$\left(\frac{1}{A_0}\right)Ar + \left(\frac{\alpha}{A_0}\right)Ar^2 = 1. \tag{A-3}$$

By picking the peak amplitude and computing the travel distance for each trace in the diffraction hyperbola, the Jacobian matrix $\mathbf{J}$ is created. Then, the unity vector $\mathbf{I}$ and parameter vector $\mathbf{p}$ are calculated via

$$\mathbf{J} = \begin{bmatrix} A_1 r_1 & A_1 r_1^2 \\ \vdots & \vdots \\ A_n r_n & A_n r_n^2 \end{bmatrix}; \quad \mathbf{p} = \begin{bmatrix} p_1 \\ p_2 \end{bmatrix}; \quad \mathbf{I} = \begin{bmatrix} 1 \\ \vdots \\ 1 \end{bmatrix}. \tag{A-4}$$

The parameter vector $\mathbf{p}$ can be estimated with the least-squares solution ($\mathbf{p} = (\mathbf{J}^T \mathbf{J})^{-1} \mathbf{J}^T \mathbf{I}$) of these systems using equation A-4. The attenuation term $\alpha$ is estimated as

$$\alpha = p_2/p_1. \tag{A-5}$$

We note that the simplifying assumptions about far-field amplitudes, radiation patterns, and uniform scattering are not strictly valid in real scenarios. However, tests showed that more complicated models did not yield conductivity estimates that consistently produced better inversion results.

Downloaded 01/15/19 to 131.247.224.4. Redistribution subject to SEG license or copyright; see Terms of Use at http://library.seg.org/

49