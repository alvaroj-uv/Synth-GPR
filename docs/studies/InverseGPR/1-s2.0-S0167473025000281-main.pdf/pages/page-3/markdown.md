Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

In many cases, the system's initial conditions are implicitly assumed to be a deterministic value, such as zero. Therefore, the solution to the equation can be simplified as follows:

\[
\boldsymbol {X} (t) = \boldsymbol {H} (\boldsymbol {\Theta}, t) \tag {4}
\]

where \(H(\bullet, t)\) or \(H_{i}\) is referred to as the forward operator.

The Generalized Probability Density Evolution Equation (GDEE) of the system described by Eq. (2) can be derived based on the principle of probability conservation [38]:

\[
\frac {\partial p _ {X \boldsymbol {\Theta}} (\boldsymbol {x} , \boldsymbol {\theta} , t)}{\partial t} + \sum_ {i = 1} ^ {d} H _ {i} (\boldsymbol {\theta}, t) \frac {\partial p _ {X \boldsymbol {\Theta}} (\boldsymbol {x} , \boldsymbol {\theta} , t)}{\partial x _ {i}} = 0 \tag {5}
\]

where \(H_{i}\) is \(i\)th component of the formal solution of Eq. (2) when \(\Theta = \theta\). If only a single output is of interest, it can be directly obtained:

\[
\frac {\partial p _ {X \boldsymbol {\Theta}} (x , \boldsymbol {\theta} , t)}{\partial t} + H (\boldsymbol {\theta}, t) \frac {\partial p _ {X \boldsymbol {\Theta}} (x , \boldsymbol {\theta} , t)}{\partial x} = 0 \tag {6}
\]

This is a first-order linear partial differential equation. The joint probability density  \( p_{X\Theta}(x,\theta,t) \)  can be calculated by solving the differential Eq. (6) under the initial condition and the boundary condition expressed in the following form:

\[
p _ {X \boldsymbol {\Theta}} (x, \theta , 0) = \delta (x - x _ {0}) p _ {\boldsymbol {\Theta}} (\theta), \quad \forall x \in \Omega_ {X} \tag {7a}
\]

\[
\lim _ {\| x \| \rightarrow \infty} p _ {X \boldsymbol {\Theta}} (x, \theta , t) = 0, \quad \forall t \in \mathbb {R} ^ {+} \tag {7b}
\]

Using the method of characteristics [1], the analytical solution of \( p_{X\Theta}(x,\theta ,t) \) can be determined under certain conditions expressed in Eqs. (7a) and (7b):

\[
p _ {X \boldsymbol {\Theta}} (x, \theta , t) = \delta [ x - H (\theta , t) ] p _ {\boldsymbol {\Theta}} (\theta) \tag {8}
\]

The marginal probability density of the output can be obtained by the following integral:

\[
p _ {X} (x, t) = \int_ {\Omega_ {\Theta}} p _ {X \Theta} (x, \theta , t) \mathrm{d} \theta = \int_ {\Omega_ {\Theta}} \delta [ x - H (\theta , t) ] p _ {\Theta} (\theta) \mathrm{d} \theta \tag {9}
\]

For the multi-dimensional response case, the solution of the joint probability density of the outputs follows the same form:

\[
p _ {X} (\boldsymbol {x}, t) = \int_ {\Omega_ {\Theta}} p _ {X \Theta} (\boldsymbol {x}, \theta , t) \mathrm{d} \theta = \int_ {\Omega_ {\Theta}} \delta [ \boldsymbol {x} - \boldsymbol {H} (\theta , t) ] p _ {\Theta} (\theta) \mathrm{d} \theta \tag {10}
\]

where \(\delta (\bullet)\) is Dirac function for the multi-dimensional case:

\[
\delta (\boldsymbol {x}) = \prod_ {i = 1} ^ {d} \delta (x _ {i}) \tag {11}
\]

### 2.2. Numerical solving methods for GDEE:  \( \delta \)  sequence method with Kriging surrogate model

The solution of inverse problems through optimization methods involves a significant number of repetitive forward computations. Considering computational cost and accuracy, it is essential to introduce surrogate models to alleviate the computational burden of deterministic analysis [47]. The Kriging model used in this paper was first proposed by Krige for the prediction of spatial mine [48] and then theorized by Matheron [49]. It is a statistical modeling technique for spatial interpolation that treats the system output as a function of system inputs. This function consists of a deterministic regression component and a stationary random field, capturing the spatial correlation between data points to estimate unknown values at unsampled locations. Suppose there exists a system with random parameters \(\Theta\). When \(\Theta\) takes the value \(\theta\), one of the system's responses \(X\) at a given time instant \(t_k\) can be expressed as \(X = H(\theta, t_k)\) as shown in Eq. (4). By performing several times of deterministic analyses of the system, numerical solutions \(X_i = H(\theta_i, t_k), i = 1, 2, \ldots\) are obtained at specific points \(\theta_i\). A Kriging model is trained by the data \(\{\theta_i, X_i, i = 1, 2, \ldots\}\) and is then employed to predict the response \(X\) at a new point \(\theta^*\), avoiding the need for repeated

deterministic analyses. By training many Kriging models at various time instants \( t_1, t_2, \ldots \), a time history of \( H(\theta^*, t) \) is generated through interpolation with respect to the time variable \( t \).

The  \( \delta \)  sequence method proposed in [44] could be employed to accelerate the computation as well, avoiding solving the GDEE. In this paper, a  \( \delta \)  sequence method combined with the Kriging Surrogate Model is applied to efficiently compute the probability density of the system response, leading to the following algorithm:

#### Algorithm:

1. A set of representative points  \( P_{sel} = \{\theta_{1}, \theta_{2}, \ldots, \theta_{N_{sel}}\} \)  is selected in the random source space  \( \Omega_{\theta} \) . Then partition the random source space into multiple subdomains  \( \Omega_{q}, q = 1, 2, \ldots, N_{sel} \)  using the Voronoi cells generated by  \( P_{sel} \) :

\[
\Omega_ {q} = \{\theta \in \Omega_ {\Theta}: \| \theta - \theta_ {q} \| \leq \| \theta - \theta_ {s} \|, \forall \theta_ {s} \in \mathcal {P} _ {\mathrm{sel}} \} \tag {12}
\]

where  \( \|\cdot\| \)  denotes the Euclidean norm. The assigned probability of each representative point, i.e., the probability measure  \( Pr_{q} \)  of each subdomain to which each representative point belongs, is computed as follows:

\[
\operatorname * {P r} _ {q} = \int_ {\Omega_ {q}} p _ {\boldsymbol {\Theta}} (\boldsymbol {\theta}) \mathrm{d} \boldsymbol {\theta} \tag {13}
\]

2. Perform a deterministic analysis of the system at each point in  \( P_{sel} \) , yielding a series of numerical solutions  \( H(\theta_{q}, t), q = 1, 2, \ldots, N_{\mathrm{sel}} \) . Based on  \( P_{sel} \)  and the corresponding sample trajectories  \( H(\theta_{q}, t), q = 1, 2, \ldots, N_{\mathrm{sel}} \) , a Kriging interpolation model is trained at each time step. It is approximated that the probability density of the random source within each subdomain is the average value of its PDF in that subdomain. Therefore, the probability density of the system response can be expressed as:

\[
\begin{array}{l} p _ {X} (x, t) = \int_ {\Omega_ {\Theta}} p _ {X \theta} (x, \theta , t) \mathrm{d} \theta = \sum_ {q = 1} ^ {N _ {\text {sel}}} \int_ {\Omega_ {q}} \delta [ x - H (\theta , t) ] p _ {\theta} (\theta) \mathrm{d} \theta \\ \approx \sum_ {q = 1} ^ {N _ {\mathrm{sel}}} \operatorname * {P r} _ {q} \cdot \frac {1}{V _ {q}} \int_ {\Omega_ {q}} \delta [ x - H (\theta , t) ] \mathrm{d} \theta = \sum_ {q = 1} ^ {N _ {\mathrm{sel}}} \operatorname * {P r} _ {q} p _ {q} (x, t) \tag {14} \\ \end{array}
\]

where \( V_{q} \) represents the Lebesgue measure of the subdomain \( \Omega_{q} \). The term \( p_{q}(x,t) \) is referred to as the local probability density which reflects the PDF of the system response generated by each subdomain, and \( p_{X}(x,t) \) is referred to as the global probability density correspondingly.

3. A set of uniformly distributed densified points \(\{\tilde{\theta}_1,\tilde{\theta}_2,\dots ,\tilde{\theta}_{n_q}\}\) is generated within each subdomain to handle the \(\delta\) function integral in Eq. (14):

\[
p _ {q} (x, t) = \frac {1}{V _ {q}} \int_ {\Omega_ {q}} \delta [ x - H (\theta , t) ] \mathrm{d} \theta \approx \frac {1}{n _ {q}} \sum_ {i = 1} ^ {n _ {q}} \phi_ {h} [ x - H (\tilde {\theta} _ {i}, t) ] \tag {15}
\]

where  \( \phi_{h}(\bullet) \)  is a kernel function, i.e., the  \( \delta \)  sequence with bandwidth parameter h. It is recommended to use a Gaussian kernel with time-varying bandwidth:

\[
\phi_ {h} (x) = \frac {1}{\sqrt {2 \pi} h (t)} \exp \left(- \frac {x ^ {2}}{2 h (t) ^ {2}}\right) \tag {16}
\]

where the bandwidth can be determined using the Plug-in Method (Improved Sheather-Jones Method) as described in [50]. The response at the densified points \( H(\tilde{\theta}_i, t) \) can then be predicted using the corresponding Kriging model at each time step. The process described in Eqs. (14) and (15) are illustrated in Figs. 1 and 2 where the random sources space is depicted as a schematic 2-dimensional space.

4. The global probability density can be assembled according to the following equation:

\[
p _ {X} (x, t) = \sum_ {q = 1} ^ {N _ {\mathrm{sel}}} \operatorname * {P r} _ {q} p _ {q} (x, t) \tag {17}
\]

3