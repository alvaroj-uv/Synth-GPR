6.12 Computer Exercise

105

$$= \frac{1}{\sqrt{\pi}} \int_{-\infty}^{\infty} x e^{-x^2} \, dx + \frac{1}{\sqrt{\pi}} x_0 / 2 \int_{-\infty}^{\infty} e^{-x^2} \, dx.$$

The first integral is exactly zero, while the second (using our favorite formula) is just $x_0/2$, so $\bar{x} = x_0/2$.

Similarly, to compute the variance we need to do

$$\sigma^2 = \frac{1}{\sqrt{\pi}} \int_{-\infty}^{\infty} (x - x_0/2)^2 e^{-(x-x_0/2)^2} \, dx = \frac{1}{\sqrt{\pi}} \int_{-\infty}^{\infty} z^2 e^{-z^2} \, dz.$$

Anticipating an integration by parts, we can write this integral as

$$-\frac{1}{2} \int_{-\infty}^{\infty} z d\left(e^{-z^2}\right) = \frac{1}{2} \int_{-\infty}^{\infty} e^{-z^2} \, dz = \frac{1}{2} \sqrt{\pi}$$

using, once again, the exponential integral result. So the variance is just $1/2$.

some common exponential integrals[Dwi61]

$$\int_0^{\infty} e^{-r^2 x^2} \, dx = \frac{\sqrt{\pi}}{2r} \quad r > 0 \text{ throughout this box} \tag{6.69}$$

$$\int_0^{\infty} x e^{-r^2 x^2} \, dx = \frac{1}{2r^2} \tag{6.70}$$

$$\int_0^{\infty} x^{2a+1} e^{-r^2 x^2} \, dx = \frac{a!}{2r^{2a+2}} \quad a = 1, 2, \dots \tag{6.71}$$

$$\int_0^{\infty} x^{2a} e^{-r^2 x^2} \, dx = \frac{1 \cdot 3 \cdot 5 \cdots (2a-1)}{2^{a+1} r^{2a+1}} \sqrt{\pi} \quad a = 1, 2, \dots \tag{6.72}$$

$$\text{Normal probability integral} \equiv \frac{1}{\sqrt{2\pi}} \int_{-x}^{x} e^{-t^2/2} \, dt = \operatorname{erf} \frac{x}{\sqrt{2}} \tag{6.73}$$

$$\text{Error function} \equiv \operatorname{erf} x \equiv \frac{2}{\sqrt{\pi}} \int_0^x e^{-t^2/2} \, dt = \frac{2x}{\sqrt{\pi}} \left[ 1 - \frac{x^2}{1!3} + \frac{x^4}{2!5} - \frac{x^6}{3!7} \cdots \right] \tag{6.74}$$

$$\operatorname{erf} x \approx 1 - \frac{e^{-x^2}}{x \sqrt{\pi}} \left[ 1 - \frac{2!}{1!(2x)^2} + \frac{4!}{2!(2x)^4} + \frac{6!}{3!(2x)^6} \cdots \right] \tag{6.75}$$

## 6.12 Computer Exercise

Write a program that computes the sample covariance matrix of repeated recordings of a time series. To test your code, generate 25 correlated time series of length 100 and use these as data. In other words the sample size will be 25 and the covariance matrix will be of order 100.

0