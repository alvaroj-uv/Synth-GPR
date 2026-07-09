FWI of common-offset GPR using PEST

H31

Adapting this approach to common-offset data is beyond the scope of this paper, and we thus expect errors associated with the SW amplitude estimation and the conductivities in the inversion process. We recognize this limitation in the method by eliminating soil conductivity as an inversion parameter (it remains fixed at the initial value), and reducing the impact of the soil conductivity on the inversion process by normalizing traces individually when calculating the cost (objective) functions at each inversion step.

5) FWI: As the fifth and final step, the GPR returns from the pipe are inverted to improve on the initial model of soil and pipe. In this paper, the inversion procedure is designed using two software packages that are freely available. The first, the PEST (model-independent parameter estimation and uncertainty analysis) package (Doherty, 2017), is used for inverting the data to find the best model parameters (Doherty, 2015). The second, gprMax 2D (Giannopoulos, 2005; Warren et al., 2016), is used to compute the GPR readings expected at each step as the model parameters are updated (Jazayeri and Kruse, 2016). Because small cell sizes are necessary for the inversion to accurately recover the pipe dimensions, a 3D forward model, although clearly preferable, was too computationally expensive for this study.

PEST, prepared by John Doherty and released in 1994, is a package developed for groundwater and surface-water studies (Doherty, 2017), but it can be linked to any forward-modeling problem. PEST uses the Gauss-Marquardt-Levenberg nonlinear estimation method (Doherty, 2010, 2015).

The relationship between the model parameters (e.g., pipe radius and soil permittivity) and the model-generated observation data (GPR returns) is represented by the model function **M** that maps the $n$-dimensional parameter space into $m$-dimensional space, where $m$ is the number of observational data points **d**. The term **M** should be differentiable with respect to all model parameters (Doherty, 2010). A set of parameters, $\mathbf{p}_0$ thus generate the model observations $\mathbf{d}_0$ (equation 1). Although generating another set of data $d$ from a **p** vector slightly different from $\mathbf{p}_0$, the Taylor expansion provides equation 2 as an approximation, where **J** is the **M**s Jacobian matrix:

$$\mathbf{d}_0 = \mathbf{M}(\mathbf{p}_0), \quad (1)$$

$$\mathbf{d} = \mathbf{d}_0 + \mathbf{J}(\mathbf{p} - \mathbf{p}_0). \quad (2)$$

The best fitting model is the one that produces the minimum of the cost function $\varphi$ (equation 3), where **d** is the real data collected and **Q** is an $m \times m$ diagonal weights matrix:

$$\varphi = (\mathbf{d} - \mathbf{d}_0 - \mathbf{J}(\mathbf{p} - \mathbf{p}_0))^T \mathbf{Q} (\mathbf{d} - \mathbf{d}_0 - \mathbf{J}(\mathbf{p} - \mathbf{p}_0)). \quad (3)$$

If **u** is denoted as the parameter upgrade vector, $\mathbf{u} = \mathbf{p} - \mathbf{p}_0$, it can be written as

$$\mathbf{u} = (\mathbf{J}^T \mathbf{Q} \mathbf{J})^{-1} \mathbf{J}^T \mathbf{Q} \mathbf{R}, \quad (4)$$

where **R** is the nonnormalized vector of residuals for the parameter set, $\mathbf{R} = \mathbf{d} - \mathbf{d}_0$.

This approach needs to be given a set of starting model parameters ($\mathbf{p}_0$), which will be updated to find the global minimum of the cost function ($\varphi$) in the time domain. The optimization process can benefit from adjusting equation 4 by adding a Marquardt parameter ($\alpha$). The new form of the upgrade vector can be rewritten as equation 5, where **I** is the $n \times n$ identity matrix:

$$\mathbf{u} = (\mathbf{J}^T \mathbf{Q} \mathbf{J} + \alpha \mathbf{I})^{-1} \mathbf{J}^T \mathbf{Q} \mathbf{R}. \quad (5)$$

For problems with parameters with greatly different magnitudes, terms in the Jacobian matrix can be vastly different in magnitude. The round-off errors associated with this issue can be eliminated through the use of an $n \times n$ diagonal scaling matrix **S**. The $i$th element of the scaling matrix is defined as

$$\mathbf{S}_{ii} = (\mathbf{J}^T \mathbf{Q} \mathbf{J})_{ii}^{-1/2}. \quad (6)$$

Finally, equation 6 can be rewritten as

$$\mathbf{S}^{-1} \mathbf{u} = ((\mathbf{J} \mathbf{S})^T \mathbf{Q} \mathbf{J} \mathbf{S} + \alpha \mathbf{S}^T \mathbf{S})^{-1} (\mathbf{J} \mathbf{S})^T \mathbf{Q} \mathbf{R}. \quad (7)$$

The largest element of $\alpha \mathbf{S}^T \mathbf{S}$ is often denoted as the Marquardt Lambda ($\lambda$), and it can be specified to help control the parameter upgrade vector **u** and optimize the upgrade process.

To start the inversion, PEST makes an initial call to gprMax to compute the initial GPR data set expected from the starting model $\mathbf{p}_0$ with the corrected SW (Figure 2, step 5). The Marquardt $\lambda$ value is set to 20, and PEST computes the initial cost function $\varphi$. Then, a lower $\lambda$ value is set and the cost function is recalculated. This process is repeated until a minimum cost function is found. If a lower cost function is not observed by $\lambda$ reduction, a higher lambda will be tested. Parameters **p** are then updated using the $\lambda$ value that yields the minimum cost function, and the next iterations starts, with gprMax called again from PEST to compute the new corresponding GPR readings $\mathbf{d}_0$. PEST then computes the residuals **R** between the updated model and real data. The next iteration starts with the best Marquardt $\lambda$ from the previous iteration. If, in the next iteration, a lower cost function is not achieved, a new vector of updated parameters will nevertheless be tested. This process continues until the step at which a lower cost function is not found after $N$ iterations. The $N$ in this process was set to six. The user can also specify upper and lower bounds for the parameters **p**. In this study, the relative permittivity is restricted between 1 and 90, and pipe diameters are bounded between 0 and 20 cm.

A concern in any inversion process is that the algorithm leads to a local minimum rather than the global minimum solution. For the real data, we cannot unambiguously identify the global minimum. To avoid local minima trapping, we follow, to the extent possible, the recommendation described above that the initial synthetic data set is offset less than a half wavelength from the measured data (e.g., Meles et al., 2012; Klotzsche et al., 2014). Then to qualitatively assess the likelihood that our results presented represent a local minimum, we run the inversion process with multiple sets of initial model parameters $\mathbf{p}_0$, and compute the cost function $\varphi$ at the conclusion of each run. The selection of initial models is described below. Runs that terminate with variable best-fit parameters **p** and differing cost functions $\varphi$ are suggestive of termination at local minima.

Downloaded 01/15/19 to 131.247.224.4. Redistribution subject to SEG license or copyright; see Terms of Use at http://library.seg.org/

41