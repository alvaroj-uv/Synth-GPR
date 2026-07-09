7.1 The World's Second Smallest Inverse Problem

109

### 7.0.1 Model Covariances

Estimators are functions of the data and therefore random variables. The covariance of a random variable $\mathbf{x}$ is the second central moment:

$$C = E[(\mathbf{x} - E[\mathbf{x}])(\mathbf{x} - E[\mathbf{x}])^T]. \tag{7.7}$$

The covariance of the generalized inverse estimate $\mathbf{m}^\dagger \equiv A^\dagger \mathbf{d}$ is easy to compute. First realize that if $\mathbf{d}$ has zero mean than so does $\mathbf{m}^\dagger$ $^a$ and therefore assuming zero mean errors

$$\text{Cov}(\hat{\mathbf{m}}) = \text{E}[\mathbf{m}^\dagger \mathbf{m}^\dagger^T] = A^\dagger \text{Cov}(\mathbf{d}) A^\dagger^T \tag{7.8}$$

If the data are uncorrelated, then $\text{Cov}(\mathbf{d})$ is a diagonal matrix whose elements are the standard deviations of the data. If we go one step further and assume that all these standard deviations are the same, $\sigma_d^2$, $^b$ then the covariance of the generalized inverse estimate takes on an especially simple form:

$$\text{Cov}(\mathbf{m}^\dagger) = \sigma_d^2 A^\dagger A^\dagger = \sigma_d^2 V_r \Lambda_r^{-2} V_r^T.$$

We can see that the uncertainties in the estimated model parameters (expressed as $\text{Cov}(\delta \mathbf{m}^\dagger)$) are proportional to the data uncertainties and inversely proportional to the squared singular values. This is as one would expect: as the noise increases, the uncertainty in our parameter estimates increases; and further, the parameters associated with the smallest singular values will be less well resolved than those associated with the largest.

## 7.1 The World's Second Smallest Inverse Problem

Suppose we wanted to use sound to discover the depth to bedrock below our feet. We could set off a loud bang at the surface and wait to see how long it would take for the echo from the top of the bedrock to return to the surface. Then, assuming that the geologic layers are horizontal, can we compute the depth to bedrock $z$ from the travel time of the reflected bang $t$? Suppose we do not know the speed with which sounds propagates beneath us, so that all we can say is that the travel time must depend both on this speed and on the unknown depth

$$t = 2z/c.$$

Since this toy problem involves many of the complications of more realistic inverse calculations, it will be useful to go through the steps of setting up and solving the calculation. We can absorb the factor of two into a new sound speed $c$ and write

$$t = z/c. \tag{7.9}$$

$^a$Why? since $\mathbf{m}^\dagger = A^\dagger$, $E[\mathbf{m}^\dagger] = A^\dagger E[d]$.

$^b$I.e., assume that the data are $iid$ with mean zero and standard deviation $\sigma_d$.

1