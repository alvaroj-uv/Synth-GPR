$$d = \sqrt{(x - x_T - \frac{\delta x}{2})^2 + (y + r)^2} - r \tag{4.1}$$

$$\phi = \arctan \frac{x - (x_T + \frac{\delta x}{2})}{y + r} \tag{4.2}$$

$$h = y + r(1 - \cos \phi) \tag{4.3}$$

$$x_0 = x - r \sin \phi \tag{4.4}$$

Finally, $d_T$ and $d_R$ are calculated using (4.5) and (4.6), respectively. Considering the medium around the rebar to be homogeneous with relative permittivity $\epsilon$, the two-way travel time of the EM pulse diffracted from rebar, $t_{TO'R}$, is obtained from (4.7), where $c$ is the speed of light in free space and $t_0$ is the effective time zero at which the pulse leaves the transmitter.

$$d_T = \sqrt{(x_0 - x_T)^2 + h^2} \tag{4.5}$$

$$d_R = \sqrt{(x_0 - x_T - \frac{\delta x}{2})^2 + h^2} \tag{4.6}$$

$$t_{TO'R} = \frac{d_T + d_R}{c / \sqrt{(\epsilon)}} + t_0 \tag{4.7}$$

The rebar diameter and rebar location can be calculated by finding the radius, position, and concrete permittivity that best fits the ray travel times in (4.7). However, the accuracy of this is limited if data are noisy or if hyperbola picking is performed inaccurately (Sham and Lai (2016); Jazayeri et al. (2018)). These values are thus used here as the initial estimates for the FWI process.

14