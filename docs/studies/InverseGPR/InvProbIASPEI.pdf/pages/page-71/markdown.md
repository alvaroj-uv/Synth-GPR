i.e., when the functions $x(t)$ have zero value and zero derivative value at the initial time and the functions $\hat{\gamma}(t)$ have zero value and zero derivative value at the final time.

This is the sort of boundary conditions found when working with the wave equation, as it contains second order time derivatives. Further details are given in section M.7 below.

As an exercise, the reader may try to understand why the quite obvious property

$$\left(\frac{\partial}{\partial x^i}\right)^T = -\left(\frac{\partial}{\partial x^i}\right) \tag{289}$$

corresponds, in fact, to the properties

$$\mathbf{grad}^T = -\mathrm{div} \quad ; \quad \mathrm{div}^T = -\mathbf{grad} \tag{290}$$

(hint: if an operator maps $\mathcal{E}$ into $\mathcal{F}$, its transpose maps $\hat{\mathcal{F}}$ into $\hat{\mathcal{E}}$; the dual of an space has the same 'variables' as the original space).

Let us formally demonstrate that the operator representing the acoustic wave equation is symmetric. Starting from$^{37}$

$$\mathbf{L} = \frac{1}{\kappa(\mathbf{x})} \frac{\partial^2}{\partial t^2} - \mathrm{div} \frac{1}{\rho(\mathbf{x})} \mathbf{grad}, \tag{291}$$

we have

$$\begin{aligned} \mathbf{L}^T &= \left(\frac{1}{\kappa(\mathbf{x})} \frac{\partial^2}{\partial t^2} - \mathrm{div} \frac{1}{\rho(\mathbf{x})} \mathbf{grad}\right)^T \\ &= \left(\frac{1}{\kappa(\mathbf{x})} \frac{\partial^2}{\partial t^2}\right)^T - \left(\mathrm{div} \frac{1}{\rho(\mathbf{x})} \mathbf{grad}\right)^T. \tag{292} \end{aligned}$$

Using the property $(\mathbf{A}\mathbf{B})^T = \mathbf{B}^T \mathbf{A}^T$, we arrive at

$$\mathbf{L}^T = \left(\frac{\partial^2}{\partial t^2}\right)^T \left(\frac{1}{\kappa(\mathbf{x})}\right)^T - (\mathbf{grad})^T \left(\frac{1}{\rho(\mathbf{x})}\right)^T (\mathrm{div})^T. \tag{293}$$

Now, (i) the transposed of a scalar is the scalar itself; (ii) the second derivative (as we have seen) is a symmetric operator; (iii) we have (as it has been mentioned above) $\mathbf{grad}^T = -\mathrm{div}$ and $\mathrm{div}^T = -\mathbf{grad}$. We then have

$$\mathbf{L}^T = \frac{\partial^2}{\partial t^2} \frac{1}{\kappa(\mathbf{x})} - \mathrm{div} \frac{1}{\rho(\mathbf{x})} \mathbf{grad}, \tag{294}$$

and, as the uncompressibility $\kappa$ is assumed to be independent on time,

$$\mathbf{L}^T = \frac{1}{\kappa(\mathbf{x})} \frac{\partial^2}{\partial t^2} - \mathrm{div} \frac{1}{\rho(\mathbf{x})} \mathbf{grad} = \mathbf{L}, \tag{295}$$

and we see that the acoustic wave operator is symmetric. As we have seen above, this conclusion has to be understood with the condition that the wavefields $p(\mathbf{x},t)$ on which acts $\mathbf{L}$ satisfy boundary conditions that are dual with those satisfied by the fields $\hat{p}(\mathbf{x},t)$ on which acts $\mathbf{L}^T$. Typically the fields $p(\mathbf{x},t)$ satisfy initial conditions of rest, and the fields $\hat{p}(\mathbf{x},t)$ satisfy final conditions of rest.

Tarantola (1988) demonstrates that the transposed of the operator corresponding to the 'wave equation with attenuation' corresponds to the wave equation with 'anti-attenuation'. But it has to be understood that any physical or numerical implementation of the operator $\mathbf{L}^T$ is made 'backwards in time', so, in that sense of time, we face an ordinary attenuation: there is no difficulty in the implementation of $\mathbf{L}^T$.

**Example 31 The Kernel of the Transposed Operator** *If the explicit expression of the equation*

$$\mathbf{f} = \mathbf{G} \mathbf{e} \tag{296}$$

$^{37}$Here, and below, an expression like $\mathbf{A}\mathbf{B}\mathbf{C}$, means, as usual, $\mathbf{A}(\mathbf{B}\mathbf{C})$. This means, for instance, that the div operator in this equation is to be understood as being applied not to $1/\rho(\mathbf{x})$ only, but to 'everything at its right'.

71