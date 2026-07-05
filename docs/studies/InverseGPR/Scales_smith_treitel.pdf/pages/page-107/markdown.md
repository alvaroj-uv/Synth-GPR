92

A Summary of Probability and Statistics

Suppose we have noisy observations of a smooth function, $f$, at the equidistant points $a \leq x_1 \leq \ldots \leq x_n \leq b$

$$y_i = f(x_i) + \epsilon_i, \quad i = 1, \ldots, n, \tag{6.59}$$

where the errors, $\epsilon_i$, are assumed to be $iid \ N(0, \sigma^2)^b$. We want to use these observations to estimate the derivative, $f'$. We define the estimator

$$\hat{f}'(x_{m_i}) = \frac{y_{i+1} - y_i}{h}, \tag{6.60}$$

where $h$ is the distance between consecutive points, and $x_{m_i} = (x_{i+1} + x_i)/2$. To measure the performance of the estimator (6.60) we use the mean square error (MSE), which is the sum of the variance and squared bias. The variance and bias of (6.60) are

$$\begin{array}{rcl} \text{Var}[\hat{f}'(x_{m_i})] & = & \frac{\text{Var}(y_{i+1}) + \text{Var}(y_i)}{h^2} = \frac{2\sigma^2}{h^2}, \\ \text{Bias}[\hat{f}'(x_{m_i})] & \equiv & \text{E}[\hat{f}'(x_{m_i}) - f'(x_{m_i})] \\ & = & \frac{f(x_{i+1}) - f(x_i)}{h} - f'(x_{m_i}) = f'(\alpha_i) - f'(x_{m_i}), \end{array}$$

for some $\alpha_i \in [x_i, x_{i+1}]$ (by the mean value theorem). We need some information on $f'$ to assess the size of the bias. Let us assume that the second derivative is bounded on $[a, b]$ by $M$

$$|f''(x)| \leq M, \quad x \in [a, b].$$

It then follows that

$$|\text{Bias}[\hat{f}'(x_{m_i})]| = |f'(\alpha_i) - f'(x_{m_i})| = |f''(\beta_i)(\alpha_i - \beta_i)| \leq Mh,$$

for some $\beta_i$ between $\alpha_i$ and $x_{m_i}$. As $h \to 0$ the variance goes to infinity while the bias goes to zero. The MSE is bounded by

$$\frac{2\sigma^2}{h^2} \leq \text{MSE}[\hat{f}'(x_{m_i})] = \text{Var}[\hat{f}'(x_{m_i})] + \text{Bias}[\hat{f}'(x_{m_i})]^2 \leq \frac{2\sigma^2}{h^2} + M^2 h^2. \tag{6.61}$$

It is clear that choosing the smallest $h$ possible does not lead to the best estimate; the noise has to be taken into account. The lowest upper bound is obtained with $h = 2^{1/4} \sqrt{\sigma/M}$. The larger the variance of the noise, the wider the spacing between the points.

We have used a bound on the second derivative to bound the MSE. It is a fact that some type of prior information, in addition to model (6.59), is required to bound derivative uncertainties. Take any smooth function, $g$, which vanishes at the points $x_1, \ldots, x_n$. Then, the function $\tilde{f} = f + g$ satisfies the same model as $f$, yet their derivatives could be very different. For example, choose an integer, $m$, and define

$$g(x) = \sin \left[ \frac{2\pi m(x - x_1)}{h} \right].$$

$^b$Independent, identically distributed random variables, normally distributed with mean 0 and variance $\sigma^2$.

0