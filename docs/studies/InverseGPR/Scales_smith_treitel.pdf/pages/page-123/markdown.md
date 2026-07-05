108

Linear Inverse Problems With Uncertain Data

is that $A^{\dagger}A$ can have no component in the null space. So, apart from the noise, the matrix $A^{\dagger}A$ acts as a filter through which we see the Earth.

We proved in Section 4.9 that a projection operator onto the null space is

$$V_{0}V_{0}^{T}=I-V_{r}^{T}V_{r}^{T} \tag{7.2}$$

and therefore

$$(A^{\dagger}A-I)\mathbf{m}_{\mathrm{T}}=-[\mathbf{m}_{\mathrm{T}}]_{\mathrm{null}}. \tag{7.3}$$

The null space components of the true model have a special statistical significance. In statistics, the bias of an estimator of some parameter is defined to be the expectation of the difference between the parameter and the estimator (see Section 6.7):

$$B[\hat{\theta}]\equiv E[\hat{\theta}-\theta] \tag{7.4}$$

where $\hat{\theta}$ is the estimator of $\theta$. In a sense, we want the bias to be small so that we have a faithful estimate of the quantity of interest. For instance, it follows from the linearity of the expectation that the sample mean $\bar{\mathbf{x}}$ is an unbiased estimator of the population mean $\mu$:

$$E[\bar{\mathbf{x}}]=\mu \tag{7.5}$$

and hence $E[\bar{\mathbf{x}}-\mu]=0$.

Using the previous result we can see that the bias of the generalized inverse solution as an estimator of the true earth model is just (minus) the projection of the true model onto the null space of the forward problem:

$$\begin{array}{rl} B(\mathbf{m}^{\dagger}) & \equiv E[\mathbf{m}^{\dagger}-\mathbf{m}_{\mathrm{true}}] \\ & = E[A^{\dagger}\mathbf{d}-\mathbf{m}_{\mathrm{true}}] \\ & = E[A^{\dagger}A\mathbf{m}_{\mathrm{true}}+A^{\dagger}\epsilon-\mathbf{m}_{\mathrm{true}}] \\ & = (A^{\dagger}A-I)E[\mathbf{m}_{\mathrm{true}}]+A^{\dagger}E[\epsilon] \end{array} \tag{7.6}$$

and so, assuming that the noise is zero mean ($E[\epsilon]=0$), we can see that the bias is simply the projection of the true model's expected value onto the null-space. If we assume that the true model is non-random, then $E[\mathbf{m}_{\mathrm{true}}]=\mathbf{m}_{\mathrm{true}}$. The net result is that the bias associated with the generalized inverse solution is the component of the true model in the null space of the forward problem. Inverse problems with no null-space are automatically unbiased. But the existence of a null-space does not automatically lead to bias since the true model could be orthogonal to the null-space. If the expected value of the true model is a constant, then this orthogonality is equivalent to having the row sums of the matrix $A^{\dagger}A-I$ be zero. In fact, the requirement that the row sums of this matrix be zero is sometimes stated as the definition of unbiasedness [OP95], but as we have just seen, such a definition would, in general, be inconsistent with the standard statistical use of this term.

1