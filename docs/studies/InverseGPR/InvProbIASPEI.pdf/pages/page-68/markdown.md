Equations 250–251 can equivalently be written

$$\widehat{\mathbf{f}} = \mathbf{W} \mathbf{f} \tag{254}$$

and

$$\widehat{f}(x) = \int dx' W(x, x') f(x) \ . \tag{255}$$

If the duality product between $\widehat{\mathbf{f}}_1$ and $\mathbf{f}_2$ is written

$$\langle \widehat{\mathbf{f}}_1 \ , \ \mathbf{f}_2 \ \rangle = \int dx \widehat{f}_1(x) f_2(x) \ , \tag{256}$$

the scalar product, as defined by equation 249, becomes

$$\begin{array}{l} ( \mathbf{f}_1 \ , \ \mathbf{f}_2 \ ) \ = \ \langle \widehat{\mathbf{f}}_1 \ , \ \mathbf{f}_2 \ \rangle = \langle \mathbf{C}^{-1} \mathbf{f}_1 \ , \ \mathbf{f}_2 \ \rangle = \langle \mathbf{W} \mathbf{f}_1 \ , \ \mathbf{f}_2 \ \rangle \\ \quad = \ \int dx \left( \int dx' W(x, x') f_1(x') \right) f_2(x) \\ \quad = \ \int dx \int dx' \ f_1(x) W(x, x') f_2(x') \ . \end{array} \tag{257}$$

The norm of $\mathbf{f}$, denoted $\| \mathbf{f} \|$ and defined as

$$\| \mathbf{f} \|^2 = ( \mathbf{f} \ , \ \mathbf{f} \ ) \ , \tag{258}$$

is expressed, in this example, as

$$\| \mathbf{f} \|^2 = \int dx \int dx' \ f(x) W(x, x') f(x') \ . \tag{259}$$

This is the $L_2$ norm of the function $f(x)$ (the case where $W(x, x') = \delta(x - x')$ being a very special case).

One final remark. If $\widehat{f}(x)$ is a random realization of a Gaussian white noise with zero mean, then, the function $f(x)$ defined by equation 251 is a random realization of a Gaussian process with zero mean and covariance function $C(x, x')$. This means that if the space $\mathcal{F}$ is the space of all the random realizations of a Gaussian process with covariance operator $\mathbf{C}$, then, its dual, $\widehat{\mathcal{F}}$, is the space of all the realizations of a Gaussian white noise.

**Example 28** *Consider the covariance operator $\mathbf{C}$, with covariance function $C(x, x')$,*

$$\mathbf{f} = \mathbf{C} \widehat{\mathbf{f}} \quad \iff \quad f(x) = \int_{-\infty}^{+\infty} dx \, C(x, x') \widehat{f}(x') \quad , \tag{260}$$

*in the special case where the covariance function is the exponential function,*

$$C(x, x') = \sigma^2 \ \exp \left( - \frac{|x - x'|}{X} \right) \ , \tag{261}$$

*where $X$ is a constant. The results of this example are a special case of those demonstrated in Tarantola (1987, page 572). The inverse covariance operator is*

$$\widehat{\mathbf{f}} = \mathbf{C}^{-1} \mathbf{f} \quad \iff \quad \widehat{f}(t) = \frac{1}{2 \sigma^2} \left( \frac{1}{X} \ f(x) - X \ \ddot{f}(x) \right) \quad , \tag{262}$$

*where the double dot means second derivative. As noted above, if $f(x)$ is a random realization of a Gaussian process having the exponential covariance function considered here, then, the $\widehat{f}(x)$ given by this equation is a random realization of a white noise. Formally, this means that the weighting function (kernel of $\mathbf{C}^{-1}$) is $W(x, x') = \frac{1}{2 \sigma^2} \left( \frac{1}{X} \ \delta(x) - X \ \ddot{\delta}(x) \right)$. The squared norm of a function $f(x)$ is obtained integrating by parts:*

$$\| \mathbf{f} \|^2 = \langle \widehat{\mathbf{f}} \ , \ \mathbf{f} \ \rangle = \frac{1}{2 \sigma^2} \left( \frac{1}{X} \int_{-\infty}^{+\infty} dx \ f^2(x) + X \int_{-\infty}^{+\infty} dx \ \dot{f}^2(x) \right) \ . \tag{263}$$

*This is the usual norm in the so-called Sobolev space $H^1$. [END OF EXAMPLE.]*

68