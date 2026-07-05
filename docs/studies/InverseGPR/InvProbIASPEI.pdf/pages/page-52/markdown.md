To be complete, let us mention that in a change of variables $x^i \rightleftharpoons x^I$, a metric $g_{ij}$ changes to

$$g_{IJ} = \Lambda_I^i \Lambda_J^j g_{ij} = \frac{\partial x^i}{\partial x^I} \frac{\partial x^j}{\partial x^J} g_{ij} \quad . \tag{200}$$

The metric 193 then transforms into

$$\begin{pmatrix} g_{YY} & g_{Y\sigma} \\ g_{\sigma Y} & g_{\sigma\sigma} \end{pmatrix} = \begin{pmatrix} \frac{2}{Y^2} & \frac{2}{(1-2\sigma)Y} - \frac{1}{(1+\sigma)Y} \\ \frac{2}{(1-2\sigma)Y} - \frac{1}{(1+\sigma)Y} & \frac{4}{(1-2\sigma)^2} + \frac{1}{(1+\sigma)^2} \end{pmatrix} \quad . \tag{201}$$

The surface element is

$$dS_{Y\sigma}(Y, \sigma) = \sqrt{\det g} \, dY \, d\sigma = \frac{3 \, dY \, d\sigma}{Y (1+\sigma)(1-2\sigma)} \quad , \tag{202}$$

a result from which expression 198 can be inferred.

Although the Poisson ratio has a historical interest, it is not a simple parameter, as shown by its theoretical bounds $-1 < \sigma < 1/2$, or the form of the homogeneous probability density (figure 21). In fact, the Poisson ratio $\sigma$ depends only on the ratio $\kappa/\mu$ (incompressibility modulus over shear modulus), as we have

$$\frac{1+\sigma}{1-2\sigma} = \frac{3}{2} \frac{\kappa}{\mu} \, . \tag{203}$$

The ratio $J = \kappa/\mu$ of two Jeffreys parameters being a Jeffreys parameter, a useful pair of Jeffreys parameters may be $\{\kappa, J\}$. The ratio $J = \kappa/\mu$ has a physical interpretation easy to grasp (as the ratio between the uncompressibility and the shear modulus), and should be preferred, in theoretical developments, to the Poisson ratio, as it has simpler theoretical properties. As the name of the nearest metro station to the university of one of the authors (A.T.) is Jussieu, we accordingly call $J$ the Jussieu's ratio.

### H.3 Longitudinal and Transverse Wave Velocities

Equation 191 gives the probability density representing the homogeneous homogeneous probability distribution of elastic media, when parameterized by the uncompressibility modulus and the shear modulus:

$$f_{\kappa\mu}(\kappa, \mu) = \frac{1}{\kappa \mu} \quad . \tag{204}$$

Should we have been interested, in addition, to the mass density $\rho$, then we would have arrived (as $\rho$ is another Jeffreys parameter), to the probability density

$$f_{\kappa\mu\rho}(\kappa, \mu, \rho) = \frac{1}{\kappa \mu \rho} \quad . \tag{205}$$

This is the starting point for this section.

What about the probability density representing the homogeneous probability distribution of elastic materials when we use as parameters the mass density and the two wave velocities? The longitudinal wave velocity $\alpha$ and the shear wave velocity $\beta$ are related to the uncompressibility modulus $\kappa$ and the shear modulus $\mu$ through

$$\alpha = \sqrt{\frac{\kappa + 4\mu/3}{\rho}} \quad ; \quad \beta = \sqrt{\frac{\mu}{\rho}} \, , \tag{206}$$

and a direct use of the Jacobian rule transforms the probability density 205 into

$$f_{\alpha\beta\rho}(\alpha, \beta, \rho) = \frac{1}{\rho \, \alpha \, \beta \left( \frac{3}{4} - \frac{\beta^2}{\alpha^2} \right)} \quad . \tag{207}$$

which is the answer to our question.

That this function becomes singular for $\alpha = \frac{2}{\sqrt{3}}\beta$ is just due to the fact that the "boundary" $\alpha = \frac{2}{\sqrt{3}}\beta$ can not be crossed: the fundamental inequalities $\kappa > 0$ ; $\mu > 0$ impose that the two velocities are linked by the inequality constraint

$$\alpha > \frac{2}{\sqrt{3}} \beta \quad . \tag{208}$$

52