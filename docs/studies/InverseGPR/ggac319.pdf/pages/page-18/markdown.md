FWI of GPR data in frequency-dependent media

521

# APPENDIX B: GRADIENT CALCULATION

For consistency with Papadopoulos & Rekanos (2011), we present the gradients as the zero-lag cross-correlation of forward wavefield u and adjoint wavefield ũ in the following. Note that we actually replace ũ(t) in eq.(23) by ũ(T - t) which is given by the same forward solver. By doing so, the cross-correlation of ũ(t) and u(t) becomes the convolution of ũ(t) and u(t).

Thus, we obtain the gradients of the electrical parameters as follows:

$$\frac{\partial \Phi}{\partial \varepsilon_{\infty}^e} = \int_0^T \left( \hat{E}_x \partial_t E_x + \hat{E}_y \partial_t E_y + \hat{E}_z \partial_t E_z \right) dt,$$

$$\frac{\partial \Phi}{\partial \sigma_{\infty}^e} = \int_0^T \left( \hat{E}_x E_x + \hat{E}_y E_y + \hat{E}_z E_z \right) dt,$$

$$\frac{\partial \Phi}{\partial \varepsilon_s} = - \frac{L r_{\varepsilon\sigma}}{\varepsilon_s^2 \tau_e},$$

$$\frac{\partial \Phi}{\partial \tau_e} = - \frac{L r_{\varepsilon\sigma}}{\varepsilon_s \tau_e^2}, \tag{B1}$$

where

$$r_{\varepsilon\sigma} = \int_0^T \sum_{l=1}^L \tau_{Dl} (\tau_{Dl} r_{zl} + r_{zl}) dt,$$

$$r_{zl} = (\hat{r}_{xl} \partial_t r_{xl} + \hat{r}_{yl} \partial_t r_{yl} + \hat{r}_{zl} \partial_t r_{zl}),$$

$$r_{zl} = (\hat{r}_{xl} r_{xl} + \hat{r}_{yl} r_{yl} + \hat{r}_{zl} r_{zl}). \tag{B2}$$

Eq. (B2) can be simplified by the following equation, based on eq.(A2) where $\tau_{Dl}(\tau_{Dl} \partial_t \mathbf{r}_l + \mathbf{r}_l) = -\frac{\varepsilon_s \tau_e}{L} \mathbf{E}$:

$$r_{\varepsilon\sigma} = -\frac{\varepsilon_s \tau_e}{L} \int_0^T \sum_{l=1}^L (\hat{r}_{xl} E_x + \hat{r}_{yl} E_y + \hat{r}_{zl} E_z) dt. \tag{B3}$$

Then the gradient of $\varepsilon_s$ and $\tau_e$ are rewritten as:

$$\frac{\partial \Phi}{\partial \varepsilon_s} = \frac{1}{\varepsilon_s} \int_0^T \sum_{l=1}^L (\hat{r}_{xl} E_x + \hat{r}_{yl} E_y + \hat{r}_{zl} E_z) dt,$$

$$\frac{\partial \Phi}{\partial \tau_e} = \frac{1}{\tau_e} \int_0^T \sum_{l=1}^L (\hat{r}_{xl} E_x + \hat{r}_{yl} E_y + \hat{r}_{zl} E_z) dt, \tag{B4}$$

According to eq. (A5) and the chain rule, we convert the gradients of the objective function from the parameter class $\mathbf{m} = (\varepsilon_{\infty}^e, \sigma_{\infty}^e, \varepsilon_s, \tau_e)$ to $\mathbf{m}' = (\varepsilon_s', \sigma_s, \tau_e', \tau_\sigma)$ where $\varepsilon_s' = \varepsilon_s$ and $\tau_e' = \tau_e$.

$$\frac{\partial \Phi}{\partial \varepsilon_s'} = (1 - \tau_e) \frac{\partial \Phi}{\partial \varepsilon_{\infty}^e} + \tau_e \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}} \frac{\partial \Phi}{\partial \sigma_{\infty}^e} + \frac{\partial \Phi}{\partial \varepsilon_s},$$

$$\frac{\partial \Phi}{\partial \sigma_s} = \tau_\sigma \frac{\partial \Phi}{\partial \varepsilon_{\infty}^e} + \frac{\partial \Phi}{\partial \sigma_{\infty}^e},$$

$$\frac{\partial \Phi}{\partial \tau_e'} = -\varepsilon_s \frac{\partial \Phi}{\partial \varepsilon_{\infty}^e} + \varepsilon_s \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}} \frac{\partial \Phi}{\partial \sigma_{\infty}^e} + \frac{\partial \Phi}{\partial \tau_s},$$

$$\frac{\partial \Phi}{\partial \tau_\sigma} = \sigma_s \frac{\partial \Phi}{\partial \varepsilon_{\infty}^e}. \tag{B5}$$

For the reference angular frequency $\omega_0$, we have

$$\begin{cases} \varepsilon^e(\omega_0) = a\varepsilon_s + \sigma_s \tau_e \\ \sigma^e(\omega_0) = \sigma_s + b\varepsilon_s \end{cases} \Leftrightarrow \begin{cases} \varepsilon_s = [\varepsilon^e(\omega_0) - \sigma^e(\omega_0)\tau_e]/(a - b\tau_e) \\ \sigma_s = \sigma^e(\omega_0) - b\varepsilon_s \end{cases}, \tag{B6}$$

with

$$a = 1 - \tau_e \frac{1}{L} \sum_{l=1}^L \frac{\omega_0^2 \tau_{Dl}^2}{1 + \omega_0^2 \tau_{Dl}^2} = 1 - \tilde{a}\tau_e,$$

$$b = \tau_e \frac{1}{L} \sum_{l=1}^L \frac{\omega_0^2 \tau_{Dl}}{1 + \omega_0^2 \tau_{Dl}^2} = \tilde{b}\tau_e. \tag{B7}$$

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022