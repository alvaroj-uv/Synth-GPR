[LOGO]

UNIVERSITÀ
DEGLI STUDI
DI TRIESTE

UD4d

# Statement of the problem/Motivation: is it possible to directly use GPR amplitudes?

We tried to estimate the dielectric permittivity from EM amplitude, considering the reflectivity of the subsurface (i.e. the series of reflection coefficients). This approach is somehow similar to the one normally used for TDR measurements.

In a simple case,

for just two homogeneous and isotropic media (1 and 2) and vertical incidence:

$$R = \frac{\sqrt{\varepsilon_1} - \sqrt{\varepsilon_2}}{\sqrt{\varepsilon_1} + \sqrt{\varepsilon_2}} \Rightarrow \varepsilon_2 = \varepsilon_1 \left( \frac{1 + R}{1 - R} \right)^2$$

and

$$R = \frac{A_R}{A_I}$$

From ($\varepsilon$) we can derive the EM velocity by applying the well known formulas:

In a NOT DISPERSIVE

(i.e. NOT CONDUCTIVE) medium:

In a LOSSY

(i.e. CONDUCTIVE) medium:

$$v_m = \frac{1}{\sqrt{\varepsilon_m \mu_m}} = \frac{1}{\sqrt{\varepsilon_0 \varepsilon_r \mu_0 \mu_r}} = \frac{c}{\sqrt{\varepsilon_r \mu_r}} \cong \frac{c}{\sqrt{\varepsilon_r}}$$

$$v_m = \frac{c}{\sqrt{\frac{\varepsilon_r \mu_r}{2} \left[ \sqrt{1 + p^2} + 1 \right]}}$$

where $$p = \tan \delta = \frac{\sigma' + \omega \varepsilon''}{\omega \varepsilon' - \sigma''} \cong \frac{\varepsilon''}{\varepsilon'} + \frac{\sigma_{DC}}{\omega \varepsilon'}$$

MEMAG A.A. 2021-2022

12