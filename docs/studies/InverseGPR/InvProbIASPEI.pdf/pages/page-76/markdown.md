### M.9 Tangent Application of Data With Respect to Parameters

In the context of an inverse problem, assume that we observe the pressure field $p(\mathbf{x},t)$ at some points $\mathbf{x}_i$ inside the volume. The solution of the forward problem is obtained by solving the wave equation, or by using the Green's function. We are here interested in the tangent linear application. Let us write the first order perturbation $\delta p(\mathbf{x}_i,t)$ of the pressure wavefield produced when the logarithmic uncompressibility is perturbed by the amount $\delta \kappa^{*}(\mathbf{x})$ as (linear tangent application)

$$\delta \mathbf{p} = \mathbf{F} \, \delta \boldsymbol{\kappa}^{*} \, , \tag{337}$$

or, introducing the kernel of the Fréchet derivative $\mathbf{F}$ ,

$$\delta p(\mathbf{x}_i, t) = \int_V dV(\mathbf{x}') \, F(\mathbf{x}_i, t; \mathbf{x}') \, \delta \kappa^{*}(\mathbf{x}') \, . \tag{338}$$

Let us express the kernel $F(\mathbf{x}_i, t; \mathbf{x}')$ .

We have seen that a perturbation $\delta \kappa^{*}$ is equivalent, up to the first order, to have the secondary Born source (equation 331)

$$S_{\text{Born}}(\mathbf{x}, t) = \frac{\delta \kappa^{*}(\mathbf{x})}{\kappa_0(\mathbf{x})} \, \ddot{p}_0(\mathbf{x}, t) \, . \tag{339}$$

Then, using the Green function,

$$\begin{aligned} \delta p(\mathbf{x}_i, t) &= \int_V dV(\mathbf{x}') \int_{t_2}^{t_1} dt' \, G(\mathbf{x}_i, t; \mathbf{x}', t') \, S_{\text{Born}}(\mathbf{x}', t') \\ &= \int_V dV(\mathbf{x}') \int_{t_2}^{t_1} dt' \, G(\mathbf{x}_i, t; \mathbf{x}', t') \, \frac{\delta \kappa^{*}(\mathbf{x}')}{\kappa_0(\mathbf{x}')} \, \ddot{p}_0(\mathbf{x}', t') \, . \end{aligned} \tag{340}$$

The last expression can be rearranged into the form used in equation 338, this showing that $F(\mathbf{x}_i, t; \mathbf{x}', t')$ is given by

$$F(\mathbf{x}_i, t; \mathbf{x}') = \frac{1}{\kappa_0(\mathbf{x}')} \int_{t_2}^{t_1} dt' \, G(\mathbf{x}_i, t; \mathbf{x}', t') \, \ddot{p}_0(\mathbf{x}', t') \tag{341}$$

This is the kernel of the Fréchet derivative of the data with respect to the parameter $\kappa^{*}(\mathbf{x})$ .

### M.10 The Transpose of the Fréchet Derivative Just Computed

Now that we are able to understand the expression $\delta \mathbf{p} = \mathbf{F} \, \delta \boldsymbol{\kappa}^{*}$ , let us face the dual problem. Which is the meaning of an expression like

$$\delta \widehat{\boldsymbol{\kappa}}^{*} = \mathbf{F}^T \, \delta \widehat{\mathbf{p}} \, ? \tag{342}$$

Denoting by $F^T(\mathbf{x}'; \mathbf{x}_i, t)$ the kernel of $\mathbf{F}^T$ , such an expression writes

$$\delta \widehat{\kappa}(\mathbf{x}') = \sum_i \int_{t_2}^{t_1} dt \, F^T(\mathbf{x}'; \mathbf{x}_i, t) \, \delta \widehat{p}(\mathbf{x}_i, t) \, , \tag{343}$$

but we know that the kernel of the transpose operator equals the kernel of the original operator, with variables transposed, so that we can write this equation as

$$\delta \widehat{\kappa}(\mathbf{x}') = \sum_i \int_{t_2}^{t_1} dt \, F(\mathbf{x}_i, t; \mathbf{x}') \, \delta \widehat{p}(\mathbf{x}_i, t) \, , \tag{344}$$

where $F(\mathbf{x}_i, t; \mathbf{x}')$ is the kernel given in equation 341. Replacing the kernel by its expression gives

$$\delta \widehat{\kappa}^{*}(\mathbf{x}') = \sum_i \int_{t_2}^{t_1} dt \, \frac{1}{\kappa_0(\mathbf{x}')} \int_{t_2}^{t_1} dt' \, G(\mathbf{x}_i, t; \mathbf{x}', t') \, \ddot{p}_0(\mathbf{x}', t') \, \delta \widehat{p}(\mathbf{x}_i, t) \, , \tag{345}$$

and this can be rearranged into (note that primed and nonprimed variables have been exchanged)

$$\delta \widehat{\kappa}^{*}(\mathbf{x}) = \frac{1}{\kappa_0(\mathbf{x})} \int_{t_2}^{t_1} dt \, \psi(\mathbf{x}, t) \, \ddot{p}_0(\mathbf{x}, t) \, , \tag{346}$$

76