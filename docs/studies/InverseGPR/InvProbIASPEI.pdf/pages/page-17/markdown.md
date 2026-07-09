### 3.5 Convergence Issues

When has a random walk visited enough points in the space so that a probability density has been sufficiently sampled? This is a complex issue, and it is easy to overlook its importance. There is no general rule: each problem has its own 'physics', and the experience of the 'implementer' is, here, crucial.

Many methods that work for low dimension completely fail when the number of dimensions is high. Typically, a random walk select a random direction and, then, a random step along that direction. The notion of 'direction' in a high-dimensional space is far from the intuitive one we get in the familiar three-dimensional space. Any serious discussion on this issue must be problem-dependent, so we don't even attempt one here.

Obviously, a necessary condition for adequate sampling is that any 'output' from the algorithm must 'look stationary'.

## 4 Probabilistic Formulation of Inverse Problems

A so-called 'inverse problem' arises when a usually complex measurement is made, and information on unknown parameters of the physical system is sought. Any measurement is indirect (we may weigh a mass by observing the displacement of the cursor of a balance), and therefore a possibly nontrivial analysis of uncertainties must be done. Any guide describing good experimental practice (see, for instance ISO's Guide to the expression of uncertainty in measurement [ISO, 1993] or the shorter description by Taylor and Kuyatt, 1994) acknowledges that a measurement involves, at least, two different sources of uncertainties: those estimated using statistical methods, and those estimated using subjective, common-sense estimations. Both are described using the axioms of probability theory, and this article clearly takes the probabilistic point of view for developing inverse theory.

### 4.1 Model Parameters and Observable Parameters

Although the separation of all the variables of a problem in two groups, 'directly observable parameters' (or 'data') and 'model parameters', may sometimes be artificial, we take this point of view here, since it allows us to propose a simple setting for a wide class of problems.

We may have in mind a given physical system, like the whole Earth, or a small crystal under our microscope. The system (or a given state of the system) may be described by assigning values to a given set of parameters $\mathbf{m} = \{m^1, m^2, \ldots, m^{\mathrm{NM}}\}$ that we will name the model parameters.

Let us assume that we make observations on this system. Although we are interested in the parameters $\mathbf{m}$, they may not be directly observable, so we make indirect measurements like obtaining seismograms at the Earth's surface for analyzing the Earth's interior, or making spectroscopic measurements for analyzing the chemical properties of a crystal. The set of (directly) observable parameters (or, by language abuse, the set of data parameters) will be represented by $\mathbf{d} = \{d^1, d^2, \ldots, d^{\mathrm{ND}}\}$.

We assume that we have a physical theory that can be used to solve the forward problem, i.e., that given an arbitrary model $\mathbf{m}$, it allows us to predict the theoretical data values $\mathbf{d}$ that an ideal measurement should produce (if $\mathbf{m}$ was the actual system). The generally nonlinear function that associates to any model $\mathbf{m}$ the theoretical data values $\mathbf{d}$ may be represented by a notation like

$$d^i = f^i(m^1, m^2, \ldots, m^{\mathrm{NM}}) \quad ; \quad i = 1, 2, \ldots, \mathrm{ND} \ , \tag{32}$$

or, for short,

$$\mathbf{d} = \mathbf{f}(\mathbf{m}) \ . \tag{33}$$

It is in fact this expression that separates the whole set of our parameters into the subsets $\mathbf{d}$ and $\mathbf{m}$, although sometimes there is no difference in nature between the parameters in $\mathbf{d}$ and the parameters in $\mathbf{m}$. For instance, in the classical inverse problem of estimating the hypocenter coordinates of an earthquake, we may put in $\mathbf{d}$ the arrival times of the seismic waves at seismic observatories, and we need to put in $\mathbf{m}$, besides the hypocentral coordinates, the coordinates defining the location of the seismometers —as these are parameters that are needed to compute the travel times—, although we estimate arrival times of waves and coordinates of the seismic observatories using similar types of measurements.

17