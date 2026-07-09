508 T. Qin, T. Bohlen and N. Allroggen

where $0_3$ is the $3 \times 3$ zero matrix and $I_3$ the $3 \times 3$ unit matrix. The superscript * is the transpose conjugate operator which is equivalent to transpose operator $T$ for real variables. When deriving the transpose conjugate of A, we use the zero-valued boundary condition, i.e. equations 54 and 55 in Yang et al. (2016).

## 2.2 Inverse problem

The objective function $\Phi$ that we use in GPR FWI is

$$\Phi(\mathbf{m}) = \Phi(\mathbf{u}) = \frac{1}{2} ||R\mathbf{u}(\mathbf{m}) - \mathbf{d}^{\mathrm{obs}}||_2^2 = \frac{1}{2} ||\Delta\mathbf{d}||_2^2, \quad (18)$$

where the synthetic data are extracted from the forward wavefield $\mathbf{u}$ at the receiver position by the restriction operator $R$; $\Delta\mathbf{d} = R\mathbf{u}(\mathbf{m}) - \mathbf{d}^{\mathrm{obs}}$ is the residual between the synthetic data and observed data $\mathbf{d}^{\mathrm{obs}}$. The FWI seeks to iteratively reconstruct the model parameters $\mathbf{m}$ by minimizing $\Phi$ as follows:

$$\mathbf{m}_{k+1} = \mathbf{m}_k + \lambda \Delta\mathbf{m}_{k+1}, \quad (19)$$

$$\Delta\mathbf{m}_{k+1} = -\mathbf{P} \frac{\partial \Phi}{\partial \mathbf{m}} + \gamma \Delta\mathbf{m}_k, \quad (20)$$

where the step length $\lambda$ is calculated by line search (Pica et al. 1990). Considering the different sensitivities of model parameters to the objective function, we use an individual step length for each parameter (Ernst et al. 2007b). The model update direction for the $(k+1)$th iteration $\Delta\mathbf{m}_{k+1}$ is computed by the conjugate-gradient method, where $\gamma$ is the scale factor (Polak & Ribiere 1969) and $\mathbf{P}$ is the pre-conditioner (Plessix & Mulder 2004). We use a multiscale strategy to avoid cycle skipping in FWI (Bunks et al. 1995). In the following, we show how to calculate the model gradient $\partial\Phi/\partial\mathbf{m}$.

Due to that $\mathbf{M}_1$, $\mathbf{M}_2$ and $\mathbf{A}$ are self-adjoint, we obtain the adjoint-state equations as follows (Plessix 2006):

$$-\mathbf{M}_1 \partial_t \dot{\mathbf{u}} + \mathbf{M}_2 \dot{\mathbf{u}} - \mathbf{A} \dot{\mathbf{u}} = -R^* \Delta\mathbf{d},$$
$$\dot{\mathbf{u}} = \left( \hat{H}_x, \hat{H}_y, \hat{H}_z, \hat{E}_x, \hat{E}_y, \hat{E}_z, \hat{r}_{x1}, \hat{r}_{y1}, \hat{r}_{z1}, \dots, \hat{r}_{xL}, \hat{r}_{yL}, \hat{r}_{zL} \right)^T, \quad (21)$$

where the waveform residual $R^* \Delta\mathbf{d}$ is used as the adjoint sources for backpropagation and $\dot{\mathbf{u}}$ is the adjoint wavefield. In contrast to the forward problem, the computation of eq. (21) is done backward from the recording time $T$ to 0. Hence we reverse the time by substituting $t' = T - t$, $\dot{\mathbf{u}}'(t') = \dot{\mathbf{u}}(T - t)$ and $\Delta\mathbf{d}'(t') = \Delta\mathbf{d}(T - t)$ in the above equation and get the self-adjoint-state equations as below:

$$\mathbf{M}_1 \partial_t \dot{\mathbf{u}}' + \mathbf{M}_2 \dot{\mathbf{u}}' - \mathbf{A} \dot{\mathbf{u}}' = -R^* \Delta\mathbf{d}',$$
$$\dot{\mathbf{u}}' = \left( \hat{H}_x', \hat{H}_y', \hat{H}_z', \hat{E}_x', \hat{E}_y', \hat{E}_z', \hat{r}_{x1}, \hat{r}_{y1}, \hat{r}_{z1}, \dots, \hat{r}_{xL}, \hat{r}_{yL}, \hat{r}_{zL} \right)^T. \quad (22)$$

Then we cross-correlate the forward wavefield $\mathbf{u}$ and the back-propagating wavefield $\dot{\mathbf{u}}$ to compute the model gradient

$$\frac{\partial \Phi}{\partial \mathbf{m}} = \int_0^T \dot{\mathbf{u}}(t) \left( \frac{\partial \mathbf{M}_1}{\partial \mathbf{m}} \partial_t \mathbf{u}(t) + \frac{\partial \mathbf{M}_2}{\partial \mathbf{m}} \mathbf{u}(t) \right) dt$$
$$= \int_0^T \dot{\mathbf{u}}'(T - t) \left( \frac{\partial \mathbf{M}_1}{\partial \mathbf{m}} \partial_t \mathbf{u}(t) + \frac{\partial \mathbf{M}_2}{\partial \mathbf{m}} \mathbf{u}(t) \right) dt. \quad (23)$$

Eqs (22) and (23) indicate two advantages of our modification in eq. (15). One advantage is that we can use the same forward solver for the forward and back-propagating wavefield simulations without any additional programming works. Another advantage is that all model parameters are distributed at the diagonal positions of $\mathbf{M}_1$ and $\mathbf{M}_2$, which means that the form of model gradients is very simple (see Appendix B for details).

Theoretically, in eq. (23), $\mathbf{m}$ can be any model parameter of eq. (15). However, we are only interested in the electrical parameters $\mathbf{m} = (\varepsilon_{\infty}^e, \sigma_{\infty}^e, \varepsilon_s, \tau_s)$ in GPR FWI. According to eq. (12) and the chain rule, we convert the gradient of the objective function from the parameter class $\mathbf{m} = (\varepsilon_{\infty}^e, \sigma_{\infty}^e, \varepsilon_s, \tau_s)$ to $\mathbf{m}' = (\varepsilon_s', \sigma_s, \tau_s', \tau_s)$ where $\varepsilon_s' = \varepsilon_s$ and $\tau_s' = \tau_s$ (see Appendix B for details):

$$\frac{\partial \Phi}{\partial \mathbf{m}'} = \frac{\partial \Phi}{\partial \mathbf{m}} \frac{\partial \mathbf{m}}{\partial \mathbf{m}'} \quad (24)$$

In this study, we use the real effective permittivity $\varepsilon^e$ and real effective conductivity $\sigma^e$ at the reference angular frequency $\omega_0$ as the input and output parameters of GPR FWI, where $\omega_0$ is set as the peak frequency of the source wavelet. Thus we ensure the physical consistency of the results obtained by frequency-dependent GPR FWI and frequency-independent GPR FWI, similar to the correction for the phase velocity in viscoacoustic FWI (Kurzmann et al. 2013). In the following sections, $\varepsilon^e(\omega_0)$ and $\sigma^e(\omega_0)$ will be referred to as the permittivity $\varepsilon$ (or relative permittivity $\varepsilon_r$) and the conductivity $\sigma$ for convenience if not explicitly stated. In frequency-dependent GPR FWI, one can update the static parameters ($\varepsilon_s$ and $\sigma_s$) using the gradients calculated by eq. (24), or update the effective parameters ($\varepsilon$ and $\sigma$) by applying the chain rule again based on eq. (13) (see eq. B8 for details).

Downloaded from https://academic.oup.com/gj/article/2/32/1/504/6670780 by KIT Library user on 25 October 2022