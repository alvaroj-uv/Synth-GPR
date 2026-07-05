520 T. Qin, T. Bohlen and N. Allroggen

# APPENDIX A: CONVOLUTION CALCULATION

The convolution of the dielectric permittivity $\varepsilon$ and the electric field $\mathbf{E}$ is

$$\begin{aligned} \varepsilon(t) * \partial_t \mathbf{E} &= \partial_t \Psi_r(t) * \partial_t \mathbf{E} = \left\{ \partial_t \left[ \varepsilon_s \left( 1 - \tau_c \frac{1}{L} \sum_{l=1}^L e^{-t/\tau_{Dl}} \right) H(t) \right] \right\} * \partial_t \mathbf{E} \\ &= \left\{ \varepsilon_s \left[ \left( 1 - \tau_c \frac{1}{L} \sum_{l=1}^L e^{-t/\tau_{Dl}} \right) \delta(t) + \tau_c \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}} e^{-t/\tau_{Dl}} H(t) \right] \right\} * \partial_t \mathbf{E} \\ &= \varepsilon_s (1 - \tau_c) \partial_t \mathbf{E} + \left\{ \varepsilon_s \tau_c \frac{1}{L} \left[ \sum_{l=1}^L \frac{1}{\tau_{Dl}} e^{-t/\tau_{Dl}} H(t) \right] \right\} * \partial_t \mathbf{E} \\ &= \varepsilon_s (1 - \tau_c) \partial_t \mathbf{E} + \left\{ \varepsilon_s \tau_c \frac{1}{L} \partial_t \left[ \sum_{l=1}^L \frac{1}{\tau_{Dl}} e^{-t/\tau_{Dl}} H(t) \right] \right\} * \mathbf{E} \\ &= \varepsilon_s (1 - \tau_c) \partial_t \mathbf{E} + \left\{ \varepsilon_s \tau_c \frac{1}{L} \left[ \sum_{l=1}^L \frac{1}{\tau_{Dl}} e^{-t/\tau_{Dl}} \delta(t) - \sum_{l=1}^L \frac{1}{\tau_{Dl}^2} e^{-t/\tau_{Dl}} H(t) \right] \right\} * \mathbf{E} \\ &= \varepsilon_s (1 - \tau_c) \partial_t \mathbf{E} + \varepsilon_s \tau_c \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}} \mathbf{E} - \left[ \varepsilon_s \tau_c \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}^2} e^{-t/\tau_{Dl}} H(t) \right] * \mathbf{E} \\ &= \varepsilon_s (1 - \tau_c) \partial_t \mathbf{E} + \varepsilon_s \tau_c \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}} \mathbf{E} + \sum_{l=1}^L \mathbf{r}_l. \end{aligned} \tag{A1}$$

Therefore, we define the memory variable $\mathbf{r}_l$ of the $l$th mechanism corresponding to $\mathbf{E}$ as

$$\begin{aligned} \mathbf{r}_l &= - \left[ \frac{\varepsilon_s \tau_c}{L \tau_{Dl}^2} e^{-t/\tau_{Dl}} H(t) \right] * \mathbf{E}, \\ \partial_t \mathbf{r}_l &= - \left[ \frac{\varepsilon_s \tau_c}{L \tau_{Dl}^2} e^{-t/\tau_{Dl}} \delta(t) - \frac{\varepsilon_s \tau_c}{L \tau_{Dl}^2} e^{-t/\tau_{Dl}} H(t) \right] * \mathbf{E} \\ &= - \frac{\varepsilon_s \tau_c}{L \tau_{Dl}^2} \mathbf{E} + \left[ \frac{\varepsilon_s \tau_c}{L \tau_{Dl}^2} e^{-t/\tau_{Dl}} H(t) \right] * \mathbf{E} \\ &= - \frac{\varepsilon_s \tau_c}{L \tau_{Dl}^2} \mathbf{E} - \frac{1}{\tau_{Dl}} \mathbf{r}_l. \end{aligned} \tag{A2}$$

The convolution of the conductivity $\sigma$ and $\mathbf{E}$ is

$$\begin{aligned} \sigma(t) * \mathbf{E} &= \partial_t \Psi_\sigma(t) * \mathbf{E} \\ &= \partial_t \{ \sigma_s [H(t) + \tau_\sigma \delta(t)] \} * \mathbf{E} \\ &= \sigma_s [\delta(t) * \mathbf{E} + \tau_\sigma \delta(t) * \partial_t \mathbf{E}] \\ &= \sigma_s (\mathbf{E} + \tau_\sigma \partial_t \mathbf{E}). \end{aligned} \tag{A3}$$

We sum the two convolutions and get

$$\begin{aligned} \varepsilon(t) * \partial_t \mathbf{E} + \sigma(t) * \mathbf{E} &= \varepsilon_s (1 - \tau_c) \partial_t \mathbf{E} + \varepsilon_s \tau_c \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}} \mathbf{E} + \sum_{l=1}^L \mathbf{r}_l \\ &\quad + \sigma_s (\mathbf{E} + \tau_\sigma \partial_t \mathbf{E}) \\ &= [\varepsilon_s (1 - \tau_c) + \sigma_s \tau_\sigma] \partial_t \mathbf{E} \\ &\quad + \left[ \sigma_s + \varepsilon_s \tau_c \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}} \right] \mathbf{E} + \sum_{l=1}^L \mathbf{r}_l \\ &= \varepsilon_\infty^\sigma \partial_t \mathbf{E} + \sigma_\infty^\sigma \mathbf{E} + \sum_{l=1}^L \mathbf{r}_l, \end{aligned} \tag{A4}$$

where

$$\varepsilon_\infty^\sigma = \varepsilon_s (1 - \tau_c) + \sigma_s \tau_\sigma, \quad \sigma_\infty^\sigma = \sigma_s + \varepsilon_s \tau_c \frac{1}{L} \sum_{l=1}^L \frac{1}{\tau_{Dl}}. \tag{A5}$$

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022