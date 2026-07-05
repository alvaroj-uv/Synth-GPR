#### Example: Realistic ‘Uncertainty Bars’ Around a Functional Relation

In the approximation of a constant gravity field, with acceleration \(\mathbf{g}\), the position at time \(t\) of an apple in free fall is \(\mathbf{r}(t) = \mathbf{r}_0 + \mathbf{v}_0 t + \frac{1}{2} \mathbf{g} t^2\), where \(\mathbf{r}_0\) and \(\mathbf{v}_0\) are, respectively, the position and velocity of the object at time \(t = 0\). More simply, if the movement is 1D,

\[
x (t) = x _ {0} + v _ {0} t + \frac {1}{2} g t ^ {2}. \tag {62}
\]

Of course, or many reasons this equation can never be exact: air friction, wind effects, inhomogeneity of the gravity field, effects of the Earth rotation, forces from the Sun and the Moon (not to mention Pluto), relativity (special and general), etc.

It is not a trivial task, given very careful experimental conditions, to estimate the size of the leading uncertainty. Although one may think of an equation  \( x = x(t) \)  as a line, infinitely thin, there will always be sources of uncertainty (at least due to the unknown limits of validity of general relativity): looking at the line with a magnifying glass should reveal a fuzzy object of finite thickness. As a simple example, let us examine here the mathematical object we arrive at when assuming that the leading sources of uncertainty in the relation  \( x = x(t) \)  are the uncertainties in the initial position and velocity of the falling apple. Let us assume that:

- the initial position of the apple is random, with a Gaussian distribution centered at \( x_0 \), and with standard deviation \( \sigma_x \);
- the initial velocity of the apple is random, with a Gaussian distribution centered at \( v_0 \), and with standard deviation \( \sigma_v \);

Then, it can be shown that at a given time \( t \), the possible positions of the apple are random, with probability density

\[
\vartheta (x | t) = \frac {1}{\sqrt {2 \pi} \sqrt {\sigma_ {x} ^ {2} + \sigma_ {v} ^ {2} t ^ {2}}} \exp \left(- \frac {1}{2} \frac {\left(x - \left(x _ {0} + v _ {0} t + \frac {1}{2} g t ^ {2}\right)\right) ^ {2}}{\sigma_ {x} ^ {2} + \sigma_ {v} ^ {2} t ^ {2}}\right). \tag {63}
\]

This is obviously a conditional probability density for \( x \), given \( t \). Should we have any reason to choose some marginal probability density \( \vartheta_t(t) \), then, the 'law' for the fall of the apple would be

\[
\vartheta (x, t) = \vartheta (x | t) \vartheta_ {t} (t). \tag {64}
\]

See appendix C for more details.

#### 4.6.2 Inverse Problems

We have seen that the result of measurements can be represented by a probability density  \( \rho_{d}(\mathbf{d}) \)  in the data space. We have also seen that the a priori information on the model parameters can be represented by another probability density  \( \rho_{m}(\mathbf{m}) \)  in the model space. When we talk about ‘measurements’ and about ‘a priori information on model parameters’, we usually mean that we have a joint probability density in the  \( (\mathcal{M},\mathcal{D}) \)  space, that is  \( \rho(\mathbf{m},\mathbf{d}) = \rho_{m}(\mathbf{m}) \rho_{d}(\mathbf{d}) \) . But let us consider the more general situation where for the whole set of parameters  \( (\mathcal{M},\mathcal{D}) \)  we have some information that can be represented by a joint probability density  \( \rho(\mathbf{m},\mathbf{d}) \) . Having well in mind the interpretation of this information, let us use the simple name of ‘experimental information’ for it

\[
\rho (\mathbf {m}, \mathbf {d}) \quad \text {(experimental information)}. \tag {65}
\]

We have also seen that we have information coming from physical theories, that predict correlations between the parameters, and it has been argued that a probabilistic description of these correlations is well adapted to the resolution of inverse problems \( ^{18} \) . Let  \( \vartheta(\mathbf{m},\mathbf{d}) \)  be the probability density representing this ‘theoretical information’:

\[
\vartheta (\mathbf {m}, \mathbf {d}) \quad \text {(theoretical information)}. \tag {66}
\]

A quite fundamental assumption is that in all the spaces we consider, there is a notion of volume which allows to give sense to the notion of ‘homogeneous probability distribution’ over the space. The corresponding probability density is not constant, but is proportional to the volume element of the space (see section 2.2):

\[
\mu (\mathbf {m}, \mathbf {d}) \quad \text {(homogeneous probability distribution)}. \tag {67}
\]

\( ^{18} \) Remember that, even if we wish to use a simple method based on the notion of conditional probability density, an analytic expression like  \( \mathbf{d} = \mathbf{f}(\mathbf{m}) \)  needs some ‘thickness’ before going to the limit defining the conditional probability density. This limit crucially depends on the ‘thickness’, i.e., on the type of uncertainties the theory contains.

24