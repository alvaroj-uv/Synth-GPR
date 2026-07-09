522 T. Qin, T. Bohlen and N. Allroggen

Alternatively, we can convert the gradients of the objective function from the parameter class $\mathbf{m}' = (\varepsilon_s', \sigma_s, \tau_s', \tau_\sigma)$ to $\mathbf{m}'' = (\varepsilon^\sigma, \sigma^\sigma, \tau_\sigma'', \tau_\sigma')$ where $\tau_\sigma'' = \tau_\sigma'$ and $\tau_\sigma'' = \tau_\sigma$.

$$\frac{\partial \Phi}{\partial \varepsilon^\sigma} = \frac{\partial \varepsilon_s'}{\partial \varepsilon^\sigma} \frac{\partial \Phi}{\partial \varepsilon_s'} + \frac{\partial \sigma_s}{\partial \varepsilon^\sigma} \frac{\partial \Phi}{\partial \sigma_s},$$

$$\frac{\partial \Phi}{\partial \sigma^\sigma} = \frac{\partial \varepsilon_s'}{\partial \sigma^\sigma} \frac{\partial \Phi}{\partial \varepsilon_s'} + \frac{\partial \sigma_s}{\partial \sigma^\sigma} \frac{\partial \Phi}{\partial \sigma_s},$$

$$\frac{\partial \Phi}{\partial \tau_\sigma''} = \frac{\partial \varepsilon_s'}{\partial \tau_\sigma''} \frac{\partial \Phi}{\partial \varepsilon_s'} + \frac{\partial \sigma_s}{\partial \tau_\sigma''} \frac{\partial \Phi}{\partial \sigma_s} + \frac{\partial \Phi}{\partial \tau_\sigma'},$$

$$\frac{\partial \Phi}{\partial \tau_\sigma''} = \frac{\partial \varepsilon_s'}{\partial \tau_\sigma''} \frac{\partial \Phi}{\partial \varepsilon_s'} + \frac{\partial \sigma_s}{\partial \tau_\sigma''} \frac{\partial \Phi}{\partial \sigma_s} + \frac{\partial \Phi}{\partial \tau_\sigma}, \quad (B8)$$

where

$$\frac{\partial \varepsilon_s'}{\partial \varepsilon^\sigma} = \frac{1}{a - b\tau_\sigma}, \quad \frac{\partial \sigma_s}{\partial \varepsilon^\sigma} = -b \frac{\partial \varepsilon_s'}{\partial \varepsilon^\sigma},$$

$$\frac{\partial \varepsilon_s'}{\partial \sigma^\sigma} = -\frac{\tau_\sigma}{a - b\tau_\sigma}, \quad \frac{\partial \sigma_s}{\partial \sigma^\sigma} = 1 - b \frac{\partial \varepsilon_s'}{\partial \sigma^\sigma},$$

$$\frac{\partial \varepsilon_s'}{\partial \tau_\sigma''} = \frac{\varepsilon^\sigma - \sigma^\sigma \tau_\sigma}{(a - b\tau_\sigma)^2} (\tilde{a} + \tilde{b}\tau_\sigma), \quad \frac{\partial \sigma_s}{\partial \tau_\sigma''} = -b \frac{\partial \varepsilon_s'}{\partial \tau_\sigma''},$$

$$\frac{\partial \varepsilon_s'}{\partial \tau_\sigma''} = \frac{b\varepsilon^\sigma - a\sigma^\sigma}{(a - b\tau_\sigma)^2}, \quad \frac{\partial \sigma_s}{\partial \tau_\sigma''} = -b \frac{\partial \varepsilon_s'}{\partial \tau_\sigma''}. \quad (B9)$$

Downloaded from https://academic.oup.com/gj/article/232/1/504/6670780 by KIT Library user on 25 October 2022