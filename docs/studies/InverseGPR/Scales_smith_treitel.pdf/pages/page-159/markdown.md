144

Bayesian versus Frequentist Methods of Inference

## 10.3 Priors in High Dimensional Spaces: The Curse of Dimensionality

As we have just seen, most probability distributions usually have more information than implied by a hard constraint. To say, for instance, that any model with $\|\mathbf{m}\| \leq 1$ is feasible is certainly not the same thing as saying that all models with $\|\mathbf{m}\| \leq 1$ are equally likely. And while we could look for the most conservative or least favorable such probabilistic assignment, Backus [Bac88] makes an interesting argument against any such probabilistic replacement in high- or infinite-dimensional model spaces. His point can be illustrated with a simple example. Suppose that all we know about an $n$-dimensional model vector, $\mathbf{m}$, is that its length, $m \equiv \|\mathbf{m}\|$, is less than some particular value-unity for the sake of definiteness. In other words, suppose we know a priori that $\mathbf{m}$ is constrained to be within the $n$-dimensional unit ball, $B_n$. Backus considers various probabilistic replacements of this hard constraint; this is called 'softening' the constraint. We could for example choose a prior probability on $\mathbf{m}$ which is uniform on $B_n$. Namely, the probability that $\mathbf{m}$ will lie in some small volume, $\delta V \in B_n$, shall be equal to $\delta V$ divided by the volume of $B_n$. Choosing this uniform prior on the ball, it is not difficult to show that the expectation of $m^2$ for an $n$-dimensional $\mathbf{m}$ is

$$\mathrm{E}(m^2) = \frac{n}{n+2}$$

which converges to 1 as $n$ increases. Unfortunately, the variance of $m^2$ goes as $1/n$ for large $n$, and thus we seem to have introduced a piece of information that was not implied by the original constraint; namely that for large $n$, the only likely vectors, $\mathbf{m}$, will have length equal to one. The reason for this apparently strange behavior has to do with the way volumes behave in high dimensional spaces. The volume, $V_n(R)$, of the $R$-diameter ball in $n$ dimensional space is

$$V_n(R) = C_n R^n,$$

where $C_n$ is a constant that depends only on the dimension $n$, not on the radius. [This is a standard result in statistical mechanics; e.g., Becker [Bec67].] If we compute the volume, $V_{\epsilon,n}$, of an $n$-dimensional shell of thickness $\epsilon$ just inside an $R$-diameter ball we can see that

$$\begin{aligned} V_{\epsilon,n} \equiv V_n(R) - V_n(R - \epsilon) &= C_n(R^n - (R - \epsilon)^n) \\ &= V_n(R) \left(1 - \left(1 - \frac{\epsilon}{R}\right)^n\right). \end{aligned} \quad (10.2)$$

Now, for $\epsilon/R \ll 1$ and $n \gg 1$ we have

$$V_{\epsilon,n} \approx V_n(R) \left(1 - e^{-n\epsilon/R}\right).$$

This says that as $n$ gets large, nearly all of the volume of the ball is compressed into a thin shell just inside the radius.

1