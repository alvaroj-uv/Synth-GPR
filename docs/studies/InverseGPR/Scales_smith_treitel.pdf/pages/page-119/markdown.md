104

A Summary of Probability and Statistics

Answer: The exponential integral is ubiquitous. You should remember the following trick.

$$H = \int_{-\infty}^{\infty} e^{-x^2} \, dx$$

$$H^2 = \left[ \int_{-\infty}^{\infty} e^{-x^2} \, dx \right] \left[ \int_{-\infty}^{\infty} e^{-y^2} \, dy \right] = \int_{-\infty}^{\infty} \int_{-\infty}^{\infty} e^{x^2+y^2} \, dx \, dy.$$

Therefore

$$H^2 = \int_0^{\infty} \int_0^{2\pi} e^{-r^2} r \, dr \, d\theta = \frac{1}{2} \int_0^{\infty} \int_0^{2\pi} e^{-\rho} \, d\rho \, d\theta = \pi$$

So $H = \sqrt{\pi}$

More complicated integrals, such as

$$\int_{-\infty}^{\infty} e^{-(x^2 - xx_0 + x_0^2)} \, dx$$

appearing in the homework are just variations on a theme. First complete the square. So

$$e^{-(x^2 - xx_0 + x_0^2)} = e^{-(x - x_0/2)^2 - 3/4x_0^2}.$$

And therefore

$$\int_{-\infty}^{\infty} e^{-(x^2 - xx_0 + x_0^2)} \, dx = e^{-3/4x_0^2} \int_{-\infty}^{\infty} e^{-(x - x_0/2)^2} \, dx$$
$$= e^{-3/4x_0^2} \int_{-\infty}^{\infty} e^{-z^2} \, dz = \sqrt{\pi} e^{-3/4x_0^2}.$$

So the final result is that

$$\rho(x) = \frac{1}{\sqrt{\pi}} e^{3/4x_0^2} e^{-(x^2 - xx_0 + x_0^2)}$$

is a normalized probability.

Now compute the mean.

$$\bar{x} = \frac{1}{\sqrt{\pi}} e^{3/4x_0^2} \int_{-\infty}^{\infty} x e^{-(x^2 - xx_0 + x_0^2)} \, dx.$$

But this is not as bad as it looks since once we complete the square, most of the normalization disappears

$$\bar{x} = \frac{1}{\sqrt{\pi}} \int_{-\infty}^{\infty} x e^{-(x - x_0/2)^2} \, dx.$$

Changing variables, we get

$$\bar{x} = \frac{1}{\sqrt{\pi}} \int_{-\infty}^{\infty} (x + x_0/2) e^{-x^2} \, dx$$

0