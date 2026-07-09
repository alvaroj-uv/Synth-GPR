42

A Little Linear Algebra

the question naturally arises: which $p$ is best? There are two aspects of this question. The first is purely numerical. It turns out that some of the $\ell_p$ norms have more stable numerical properties than others.

In particular, as we will see, $p$ values near 1 are more stable than $p$ values near 2. On the other hand, there is an important statistical aspect of this question. When we are doing inverse calculations, the vector $\mathbf{y}$ is associated with our data. If our data have, say, a Gaussian distribution, then $\ell_2$ is optimal in a certain sense to be described shortly. On the other hand, if our data have the double-exponential distribution, then $\ell_1$ is optimal. This optimality can be quantified in terms of the entropy or *information content* of the distribution. For the Gaussian distribution we are used to thinking of this in terms of the variance or standard deviation. More generally, we can define the $\ell_p$ norm *dispersion* of a given probability density $\rho(x)$ as

$$(\sigma_p)^p \equiv \int_{-\infty}^{\infty} |x - x_0|^p \rho(x) \, dx \tag{4.48}$$

where $x_0$ is the center of the distribution. (The definition of the center need not concern us here. The point is simply that the dispersion is a measure of how spread out a probability distribution is.)

One can show (cf. [Tar87], Chapter 1) that for a fixed $\ell_p$ norm dispersion, the probability density with the minimum information content is given by the generalized gaussian

$$\rho_p(x) = \frac{p^{1-1/p}}{2\sigma_p \Gamma(1/p)} \exp \left( \frac{-1}{p} \frac{|x - x_0|^p}{(\sigma_p)^p} \right) \tag{4.49}$$

where $\Gamma$ is the Gamma function [MF53]. These distributions are shown in Figure 4.2 for four different values of $p$, 1, 2, 10, and $\infty$. The reason information content is so important is that being naturally conservative, we want to avoid jumping to any unduly risky conclusions about our data. One way to quantify simplicity is in terms of information content, or entropy: given two (or more) models which fit the data to the same degree, we may want to choose the one with the least information content in order to avoid over-interpreting the data. This is an important caveat for all of inverse theory. Later in the course we will come back to what it means to be “conservative” and see that the matter is more complicated than it might first appear.

## 4.3 Projecting Vectors Onto Other Vectors

Figure 4.3 illustrates the basic idea of projecting one vector onto another. We can always represent one, say $\mathbf{b}$, in terms of its components parallel and perpendicular to the other. The length of the component of $\mathbf{b}$ along $\mathbf{a}$ is $\|\mathbf{b}\| \cos \theta$ which is also $\mathbf{b}^T \mathbf{a} / \|\mathbf{a}\|$

$^b$This is a caveat for all of life too. It is dignified with the title *Occam’s razor* after William of Occam, an English philosopher of the early 14th century. What Occam actually wrote was: “Entia non sunt multiplicanda praeter necessitatem” (things should not be presumed to exist, or multiplied, beyond necessity).

0