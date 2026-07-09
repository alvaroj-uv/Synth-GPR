6.8 Correlation of Sequences

93

Then, $f(x_i) + g(x_i) = f(x_i)$ and

$$\tilde{f}'(x) = f'(x) + \frac{2\pi m}{h} \cos \left[ \frac{2\pi m(x - x_1)}{h} \right].$$

By choosing $m$ large enough, we can make the difference, $\tilde{f}'(x_{m_i}) - f'(x_{m_i})$, as large as we want; without prior information the derivative can not be estimated with finite uncertainty.

## 6.8 Correlation of Sequences

Many people think that “random” and uncorrelated are the same thing. Random sequences need not be uncorrelated. Correlation of sequences is measured by looking at the correlation of the sequence with itself, the autocorrelation. If this is approximately a $\delta$-function, then the sequence is uncorrelated. In a sense, this means that the sequence does not resemble itself for any lag other than zero. But suppose we took a deterministic function, such as $\sin(x)$, and added small (compared to 1) random perturbations to it. The result would have the large-scale structure of $\sin(x)$ but with a lot of random junk superimposed. The result is surely still random, even though it will not be uncorrelated.

If the autocorrelation is not a $\delta$-function, then the sequence is correlated. Figure 6.6 shows two pseudo-random Gaussian sequences with approximately the same mean, standard deviation and 1D distributions: they look rather different. In the middle of this figure are shown the autocorrelations of these two sequences. Since the autocorrelation of the right-hand sequence drops off to approximately zero in 10 samples, we say the correlation length of this sequence is 10. In the special case that the autocorrelation of a sequence is an exponential function, the the correlation length is defined as the (reciprocal) exponent of the best-fitting exponential curve. In other words, if the autocorrelation can be fit with an exponential $e^{-z/\ell}$, then the best-fitting value of $\ell$ is the correlation length. If the autocorrelation is not an exponential, then the correlation length is more difficult to define. We could say that it is the number of lags of the autocorrelation within which the autocorrelation has most of its energy. It is often impossible to define meaningful correlation lengths from real data.

A simple way to generate a correlated sequence is to take an uncorrelated one (this is what pseudo-random number generators produce) and apply some operator that correlates the samples. We could, for example, run a length-$\ell$ smoothing filter over the uncorrelated samples. The result would be a series with a correlation length approximately equal to $\ell$. A fancier approach would be to build an analytic covariance matrix and impose it on an uncorrelated pseudo-random sample.

From the convolution theorem, it follows that the autocorrelation is just the inverse Fourier transform of the periodogram (absolute value squared of the Fourier transform).

0