Structural Safety 115 (2025) 102600

![img-0.jpeg](img-0.jpeg)

Contents lists available at ScienceDirect

Structural Safety

journal homepage: www.elsevier.com/locate/strusafe

![img-1.jpeg](img-1.jpeg)

# The probabilistic inverse problem and its solving method based on probability density evolution theory and convex optimization algorithms

Yuhan Zhu, Jie Li *

College of Civil Engineering, Tongji University, 1239 Siping Road, Yangpu District, Shanghai, 200092, Shanghai, China

ARTICLE INFO

Keywords:

Probabilistic inverse problem
Probability Density Evolution Theory
Convex optimization

ABSTRACT

A probabilistic inverse problem-solving method based on the framework of Probability Density Evolution Theory and convex optimization algorithms is proposed. This method reformulates the identification of the random source as a quadratic programming problem with linear constraints, identifying the probability density function of the random source in a physical stochastic system even when the distribution type of the random source is entirely unknown. Through singular value decomposition of the quadratic matrix, an error analysis is performed, revealing that the solvability of the probabilistic inverse problem fundamentally depends on the injectivity of the mapping from the random source space to the response space. Case studies confirm that the proposed method is not sensitive to prior information and does not require any predefined assumptions about the distribution type. Meanwhile, it can preliminarily determine whether the inverse problem is solvable before the computational process begins.

1. Introduction

The physical tradition in stochastic dynamical systems focuses on identifying the sources of randomness and analyzing the system from the perspective of random events [1]. It attributes randomness to a set of basic random variables, called the random source, based on physical laws. Stochastic systems modeled in this manner are referred to as physical stochastic systems. Li and Chen [2] introduced the principle of probability conservation, derived the Generalized Density Evolution Equation (GDEE), and developed the Probability Density Evolution Theory (PDEM) to track randomness from the random source to system responses.

One of the core of modeling physical stochastic systems is the identification of the probability density function (PDF) of the random source. In many cases, the PDF of the random source can be obtained through engineering or experimental measurement data statistics, such as the axial compressive strength of concrete. However, some random variables are unobservable, like the damping matrix in an MDOF system or surface roughness in boundary layer models. In such cases, when a system model is first established using physical laws, the unobservable variables should be identified through statistical analysis of observable responses. This leads to the concept of the probabilistic inverse problem: identifying the PDF of the random source from the stochastic response under deterministic test excitations.

System Identification, or inverse problem, refers to inferring unknown deterministic or random parameters of a system from finite-dimensional observations of the system's output variables [3]. Typical methods for solving inverse problems include Bayesian inference and optimization methods [4]. In the Bayesian inference approach, regardless of whether the parameters θ to be identified are random variables, their prior distributions π(θ) can be determined roughly based on engineers' judgment [5–7]. The certain outputs of the system are then specified, forming a vector X that represents the system's state. Subsequently, the system is subjected to n repeated test excitations, and n samples of the state vector X are recorded to form the observation data: D = {x1, x2, ..., xn}. According to Bayes' theorem, the posterior distribution of the parameters is derived:

$$p(\theta|D) = \frac{p(D|\theta)\pi(\theta)}{\int_{\Omega_\theta} p(D|\alpha)\pi(\alpha)\mathrm{d}\alpha} \quad (1)$$

where Ωθ denotes the random source space, p(D|θ) denotes the likelihood function, and p(θ|D) denotes the posterior distribution of θ. The likelihood function quantifies the deviation of observed data from the model's predictions due to model and measurement errors. Let ΩX denote the response space where the state vector X resides. Since the dimension of the joint vector space {ΩX} formed by the observation vectors is much higher than that of the random source space, the probability measure determined by the parameters becomes sharply

* Corresponding author.

E-mail address: lijie@tongji.edu.cn (J. Li).

https://doi.org/10.1016/j.strusafe.2025.102600

Received 12 December 2024; Received in revised form 5 April 2025; Accepted 7 April 2025

Available online 24 April 2025

0167-4730/© 2025 Elsevier Ltd. All rights are reserved, including those for text and data mining, AI training, and similar technologies.

Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

peaked around a tiny region within $(\Omega_X)^n$. This leads to great difficulty in numerically computing the integral in the denominator of Eq. (1) [6,8]. The issue can be alleviated by performing a Laplace approximation to the likelihood function [6,7] or by employing advanced Monte Carlo methods such as Markov Chain Monte Carlo (MCMC) [8–10], Hamiltonian Monte Carlo [3,11] and other related techniques. To date, advancements in Bayesian inference within civil engineering continue to evolve, focusing on various improvements. Methods to accelerate computations include combining Bayesian approaches with improved Monte Carlo sampling techniques, such as Transitional Markov Chain Monte Carlo [12], Transitional Ensemble Markov Chain Monte Carlo [13], Transport Map Accelerated Markov Chain Monte Carlo [14–16], the global pattern search algorithm [17], along with related methods. Additionally, surrogate models like the Kriging model [18–20] and polynomial chaos expansion [21] have been introduced to enhance the computational efficiency. In a parallel line of development, multi-level and multi-source uncertainties have been addressed through Hierarchical Bayesian models, which provide a systematic framework for incorporating diverse data and knowledge [3, 21–23].

It is worth mentioning that numerical singularity issues in high-dimensional probability density estimation for large-sample Bayesian methods are alleviated by manifold-based techniques, since data points typically concentrate near a low-dimensional manifold, determined by system parameters [24]. Manifold-based methods enable nonlinear system sampling and identification directly on the Riemannian submanifold embedded within the response space [25–27]. Probability measures can also be defined on Riemannian manifolds, where the probability density is defined as the Radon–Nikodym derivative of the probability measure with respect to the low-dimensional Riemannian volume element, rather than the Euclidean volume element in the high-dimensional space, avoiding sharply peaked density functions [28,29], allowing Bayesian inference to transition to Riemannian settings [30, 31]. Additionally, the manifold structures help address solution multiplicity or unidentifiable cases in inverse problems. For example, the tangential-projection (TP) algorithm [32] captures the manifold structure of parameter distribution when the Laplace approximation of the likelihood function results in a singular Hessian matrix [33].

The Bayesian method always requires a prior distribution, and the choice of prior distribution can influence the posterior distribution, a bias that can only be eliminated through a large amount of observational data [6]. This, in turn, inevitably leads to the curse of dimensionality, which is a fundamental challenge of the Bayesian approach. To overcome this difficulty, in addition to introducing manifold methods to capture the low-dimensional structure of the data, transforming inverse problems into optimization problems is another highly intuitive approach, underlying many traditional system identification algorithms, such as least squares [34] and maximum likelihood estimation [35]. It consists mainly of three steps: defining the optimization objective, forward computation, and optimization. For defining the optimization objective, an error functional representing the discrepancy of model prediction and the measured results is constructed. Forward computation is determined by the model itself. For the optimization computation, an appropriate optimization algorithm is specified, essentially adjusting the parameter values to minimize the error functional. Both traditional gradient-based algorithms and swarm intelligence optimization methods, such as genetic algorithms [36] and particle swarm optimization [37], are commonly used.

The probability conservation principle is proposed by Li and Chen [1,38], outlining the propagation law of randomness from the random source space to the response space of a physical system and stating that the probability information of the random source in a physical stochastic system is completely decoupled from the system's physical laws. In this paper, an alternative small-sample identification method based on the convex optimization algorithm and the probability conservation principle is proposed, where the dimension of the response space and

the random source space are identical, avoiding the numerical singularity issues in probability density estimation within high-dimensional spaces.

To formulate an optimization problem for the random source identification, the objective function needs to be defined as a metric measuring the discrepancy between the true probability density of the system response and the model prediction. Commonly used metrics include $L_p$ norms, members of the Bregman divergence family [39], and members of the f-divergence family. The Bregman divergence family, exemplified by Euclidean distance [40] and Mahalanobis distance [41], is based on statistical moments and cannot fully capture the differences in the probabilistic structure of random sources [36]. Metrics from the f-divergence family [42], including the Kullback–Leibler (KL) divergence [36,43], total variation distance [39] and analogous measures, are applied to probability density functions which can more accurately capture the differences in the probabilistic structure of random sources. However, certain members of the f-divergence family do not possess symmetry, smoothness, or relatively strong strict convexity. In contrast, the discrete form of the $L_2$ norm better aligns with the requirements of optimization computations, and it is the objective function employed in this study. Based on this, a quadratic programming problem can be formulated, which can be solved using many gradient-based optimization algorithms.

The process of forward computation in the proposed method is based on the numerical method in PDEM. The classical method in PDEM was proposed by Li and Chen [2]. Moreover, the $\delta$ Sequence Method, as introduced by Fan et al. [44], utilizes kernel function sequences with time-varying bandwidths to approximate the generalized function solution of the GDEE. Additionally, methods that accelerate computations using surrogate models have been proposed, such as densifying the representative point set using the Reproducing Kernel Particle Method (RKPM) [45] and Kriging interpolation [46]. These surrogate model-based methods provide more accurate predictions of nonlinear system responses. The method in this paper employs a numerical approach that combines the $\delta$ Sequence Method with the Kriging surrogate model for the forward computation.

The organization of this paper is as follows: Section 2 introduces the Probability Density Evolution Theory for physical stochastic systems and employs a numerical approach for forward computation. Section 3 presents a quadratic programming problem with linear constraints based on the discrete form of the $L_2$ norm to identify the random source. A corresponding error analysis theory is presented in Section 4 along with conditions under which the proposed quadratic objective function is strictly convex. Section 5 provides two numerical examples to validate the accuracy of the previously discussed algorithms and theoretical results. Finally, Section 6 summarizes the main findings of this study and discusses potential directions for future development of the proposed methods.

## 2. Theoretical framework of probability density evolution theory

### 2.1. The generalized density evolution equation

In physical stochastic systems, the system's evolution is modeled as a differential equation with random parameters. Let the output of the system be a multi-dimensional stochastic process $X(t) \in \Omega_X \subseteq \mathbb{R}^d$, and the multi-dimensional random source of the system be denoted as $\Theta \in \Omega_\Theta \subseteq \mathbb{R}^s$. The control equation of the system can then be written as:

$$\dot{X} = A(X, \Theta, t) \quad (2)$$

Given the system's deterministic initial conditions $X(0) = x_0$, the solution to the differential Eq. (2) can be expressed in the following form:

$$X(t) = H(x_0, \Theta, t) \quad (3)$$

2

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

where  \( H_{i} \)  is ith component of the formal solution of Eq. (2) when  \( \Theta = \theta \) . If only a single output is of interest, it can be directly obtained:

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

Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

![img-2.jpeg](img-2.jpeg)

Fig. 1. Partition and densification in the schematic 2-dimensional random source space.

The above algorithm can be extended to higher dimensions. To consider joint probability density  \( p_{X}(x,t) \) , a high-dimensional kernel function can be used to approximate the integration of the high-dimensional  \( \delta \)  function, such as the multivariate Gaussian kernel with a diagonal covariance matrix:

\[
\phi_ {h} (\boldsymbol {x}) = \frac {1}{(2 \pi) ^ {d / 2} \prod_ {i = 1} ^ {d} h _ {i} (t)} \exp \left(- \sum_ {i = 1} ^ {d} \frac {x _ {i} ^ {2}}{2 h _ {i} (t) ^ {2}}\right) = \prod_ {i = 1} ^ {d} \phi_ {h _ {i}} (x _ {i}) \tag {18}
\]

## 3. Theoretical framework of probabilistic inverse problems

### 3.1. Conditions for the uniqueness of solutions to the probabilistic inverse problem

The principle of probability conservation proposed by Li and Chen [1] is essentially the result of transferring the probability measure from an initial measure space to a new space via a measurable mapping. Therefore, the uniqueness of the solution to the probabilistic inverse problem can be determined based on the properties of the mapping. The random source space \(\Omega_{\theta}\) is typically a bounded measurable closed subset of a Euclidean space \(\mathbb{R}^s\), while the response space \(\Omega_X\) is usually taken as a Euclidean space \(\mathbb{R}^d\). In this context, the following proposition can be formulated:

Proposition 1. When there exists a continuous injection \(\mathcal{G}\) from a bounded measurable closed subset \(\Omega_{\theta} \subseteq \mathbb{R}^s\) with positive Lebesgue measure to \(\Omega_X = \mathbb{R}^d\), the probability density function \(p_{\theta}\) on \(\Omega_{\theta}\) can be uniquely determined by \(\mathcal{G}\) and the probability density function \(p_X\) on \(\Omega_X\).

Detailed proof and further explanation can be found in Appendix and only a brief explanation of the proposition is provided here. In simple terms, a measurable mapping from the random source space  \( \Omega_{\theta} \)  to the response space  \( \Omega_{X} \), along with a probability measure  \( Pr_{X} \), can define a unique probability measure on a family of measurable subsets A of  \( \Omega_{\theta} \). However, these subsets in A are too “coarse” to define a probability density, as they lack the fine structure needed for a Radon–Nikodym derivative with respect to the Lebesgue measure in Euclidean space. But if this mapping is a continuous injective function, then sets in A become sufficiently “refined” to define a probability density function.

### 3.2. Formulation of the optimization problem

The probabilistic inverse problem is essentially a best approximation problem that minimizes the discrepancy between the true probability density of the system response and the one calculated using a hypothesized random source distribution. To achieve this, a loss

functional needs to be constructed in the form  \( J(\hat{p}_{\theta}, p_{X}) \)  as the objective function for the optimization problem, where  \( \hat{p}_{\theta} \)  is the hypothesized random source distribution. The probability density of the system response can be approximated as follows based on the random source space partition:

\[
p _ {X} (\boldsymbol {x}, t) = \sum_ {q = 1} ^ {N _ {\mathrm{sel}}} \operatorname * {P r} _ {q} p _ {q} (\boldsymbol {x}, t) \tag {19}
\]

Here, the calculation of \( p_q(x,t) \) is based on Eq. (15).

By adjusting the assigned probabilities  \( Pr_{q} \) , the best approximation to the true probability density of the system response can be achieved. Therefore, the loss functional can be written as a function of the assigned probabilities:

\[
J = J \left(\operatorname * {P r} _ {1}, \operatorname * {P r} _ {2}, \dots , \operatorname * {P r} _ {N _ {\text {sel}}}\right) \tag {20}
\]

From the perspective of functional analysis, if the global probability density function  \( p_{X}(x,t_{k}) \)  and the local probability density function  \( p_{q}(x,t_{k}) \)  at a given time instant  \( t_{k} \)  are viewed as elements of a Hilbert space [51], then each assigned probability corresponds to the projection of the true global probability density onto the local probability density. The Hilbert space is typically infinite-dimensional, with a countable set of basis functions  \( \{e_{i}(x,t_{k}), i \in \mathbb{Z}^{+}\} \) . Consider the decomposition of the functions  \( p_{X}(x,t_{k}) \)  and  \( p_{q}(x,t_{k}) \)  in this basis:

\[
p _ {X} (\boldsymbol {x}, t _ {k}) = \sum_ {i = 1} ^ {\infty} \lambda_ {i} ^ {(k)} e _ {i} (\boldsymbol {x}, t _ {k}) \tag {21a}
\]

\[
p _ {q} (\boldsymbol {x}, t _ {k}) = \sum_ {i = 1} ^ {\infty} \mu_ {i q} ^ {(k)} e _ {i} (\boldsymbol {x}, t _ {k}), \quad q = 1, 2, \dots , N _ {\mathrm{sel}} \tag {21b}
\]

where \(\lambda_i^{(k)},\mu_{iq}^{(k)}\) denotes the expansion coefficients of \(p_X(x,t_k)\) and \(p_q(x,t_k)\). Eq. (19) indicates that:

\[
\sum_ {i = 1} ^ {\infty} \lambda_ {i} ^ {(k)} e _ {i} (\boldsymbol {x}, t _ {k}) = \sum_ {q = 1} ^ {N _ {\mathrm{sel}}} \sum_ {i = 1} ^ {\infty} \operatorname * {P r} _ {q} \mu_ {i q} ^ {(k)} e _ {i} (\boldsymbol {x}, t _ {k}) \tag {22}
\]

This holds if and only if:

\[
\lambda_ {i} ^ {(k)} = \sum_ {q = 1} ^ {N _ {\mathrm{sel}}} \operatorname * {P r} _ {q} \mu_ {i q} ^ {(k)}, \quad \forall i \in \mathbb {Z} ^ {+} \tag {23}
\]

To address practical considerations, a truncation of Eq. (21a) can be performed, replacing \( p_X(x,t_k) \) with a finite-dimensional vector \( f_{k} = (\lambda_1^{(k)},\lambda_2^{(k)},\dots,\lambda_{l_k}^{(k)})^{\top} \). As a result, Eq. (23) can be rewritten as a matrix equation:

\[
\boldsymbol {f} _ {k} = \left\{ \begin{array}{l} \lambda_ {1} ^ {(k)} \\ \lambda_ {2} ^ {(k)} \\ \dots \\ \lambda_ {l _ {k}} ^ {(k)} \end{array} \right\} = \left[ \begin{array}{c c c c} \mu_ {1 1} ^ {(k)} & \mu_ {1 2} ^ {(k)} & \dots & \mu_ {1 N _ {\mathrm{sel}}} ^ {(k)} \\ \mu_ {2 1} ^ {(k)} & \mu_ {2 2} ^ {(k)} & \dots & \mu_ {2 N _ {\mathrm{sel}}} ^ {(k)} \\ \dots & \dots & \dots & \dots \\ \mu_ {l _ {k} 1} ^ {(k)} & \mu_ {l _ {k} 2} ^ {(k)} & \dots & \mu_ {l _ {k} N _ {\mathrm{sel}}} ^ {(k)} \end{array} \right] \left\{ \begin{array}{l} \operatorname * {P r} _ {1} \\ \operatorname * {P r} _ {2} \\ \dots \\ \operatorname * {P r} _ {N _ {\mathrm{sel}}} \end{array} \right\} = \boldsymbol {P} _ {k} \boldsymbol {y} \tag {24}
\]

To avoid Eq. (24) from being underdetermined, it is necessary that  \( l_{k} \geq N_{sel} \) . It is recommended to make the number of truncated terms  \( l_{k} \)  much larger than the total number of subdomains  \( N_{sel} \) . Once the system of Eq. (24) becomes overdetermined, its least-squares solution can be obtained by minimizing the squared residual, leading to the following quadratic optimization function:

\[
J (\mathbf {y}) = \left\| f _ {k} - \boldsymbol {P} _ {k} \mathbf {y} \right\| ^ {2} = \mathbf {y} \boldsymbol {P} _ {k} ^ {\top} \boldsymbol {P} _ {k} \mathbf {y} - 2 f _ {k} ^ {\top} \boldsymbol {P} _ {k} \mathbf {y} + f _ {k} ^ {\top} f _ {k} \tag {25}
\]

As long as the quadratic matrix  \( P_{k}^{T}P_{k} \)  is symmetric and positive definite, the optimization function is strictly convex. Moreover, to improve computational accuracy, it is recommended to consider the global joint probability density over multiple time instants  \( p_{X}(x,t_{k}), k=1,2,\ldots,N_{1} \)  and use the extended vector  \( f_{\mathrm{ex}}=(f_{1}^{\mathrm{T}},f_{2}^{\mathrm{T}},\ldots,f_{N_{1}}^{\mathrm{T}})^{\mathrm{T}} \)  and the extended matrix  \( P_{ex}=[P_{1}^{T},P_{2}^{T},\ldots,P_{N_{1}}^{T}]^{\mathrm{T}} \)  to construct the quadratic form:

\[
J (\mathbf {y}) = \| f _ {\mathrm{ex}} - P _ {\mathrm{ex}} \mathbf {y} \| ^ {2} = \mathbf {y} P _ {\mathrm{ex}} ^ {\top} P _ {\mathrm{ex}} \mathbf {y} - 2 f _ {\mathrm{ex}} ^ {\top} P _ {\mathrm{ex}} \mathbf {y} + f _ {\mathrm{ex}} ^ {\top} f _ {\mathrm{ex}}
\]

4

Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

![img-3.jpeg](img-3.jpeg)

Fig. 2. The composition of the local probability density (left) and the global probability density (right) for one time instant.

\[
= y \left(\sum_ {k = 1} ^ {N _ {k}} P _ {k} ^ {\top} P _ {k}\right) y - 2 \left(\sum_ {k = 1} ^ {N _ {k}} f _ {k} ^ {\top} P _ {k}\right) y + \sum_ {k = 1} ^ {N _ {k}} f _ {k} ^ {\top} f _ {k} \tag {26}
\]

The assigned probabilities are non-negative and satisfy the normalization condition.

Therefore, the complete formulation of the optimization problem is:

min  \( J(y) = y^{\top} A y + b^{\top} y + c \)

s.t.  \( y_{i} \geq 0, i = 1, 2, \ldots, N_{\mathrm{sel}} \)

\[
\sum_ {i = 1} ^ {N _ {\mathrm{sel}}} y _ {i} - 1 = 0 \tag {27}
\]

where \(A = P_{\mathrm{ex}}^{\top}P_{\mathrm{ex}}, b = -2f_{\mathrm{ex}}^{\top}P_{\mathrm{ex}}, c = f_{\mathrm{ex}}^{\top}f_{\mathrm{ex}}\).

Similarly, to ensure that A is symmetric positive definite, the following condition must be satisfied:

\[
\sum_ {k = 1} ^ {N _ {k}} l _ {k} \geq N _ {\mathrm{sel}} \tag {28}
\]

Furthermore, it is recommended that the left-hand side of this equation be much larger than the right-hand side.

In practical computations, the global probability density function and local probability density functions of the system response at multiple time instants are stored as one-dimensional arrays, where the values are taken at discrete points:

\[
\boldsymbol {f} _ {k} = \left(p _ {\boldsymbol {X}} (\boldsymbol {x} _ {1}, t _ {k}), p _ {\boldsymbol {X}} (\boldsymbol {x} _ {2}, t _ {k}), \dots , p _ {\boldsymbol {X}} (\boldsymbol {x} _ {l _ {k}}, t _ {k})\right) ^ {\top} \tag {29a}
\]

\[
\boldsymbol {P} _ {k} ^ {(q)} = \left(p _ {q} (\boldsymbol {x} _ {1}, t _ {k}), p _ {q} (\boldsymbol {x} _ {2}, t _ {k}), \dots , p _ {q} (\boldsymbol {x} _ {l _ {k}}, t _ {k})\right) ^ {\top} \tag {29b}
\]

This process automatically selects an orthonormal basis for the global probability density function at each time instant, as well as for all local response probability density functions:

\[
e _ {1} = (1, 0, 0, \dots , 0) ^ {\top}
\]

\[
e _ {2} = (0, 1, 0, \dots , 0) ^ {\top}
\]

...

\[
e _ {l _ {k}} = (0, 0, 0, \dots , 1) ^ {\top} \tag {30}
\]

Therefore, the coefficient matrix and coefficient vector in the optimization problem (27) can be generated very simply:

\[
\boldsymbol {P} _ {k} = \left[ \boldsymbol {P} _ {k} ^ {(1)}, \boldsymbol {P} _ {k} ^ {(2)}, \dots , \boldsymbol {P} _ {k} ^ {\left(N _ {\mathrm{sel}}\right)} \right] \tag {31a}
\]

\[
\boldsymbol {P} _ {\mathrm{ex}} = \left[ \boldsymbol {P} _ {1} ^ {\top}, \boldsymbol {P} _ {2} ^ {\top}, \dots , \boldsymbol {P} _ {N _ {1}} ^ {\top} \right] ^ {\top} \tag {31b}
\]

\[
\boldsymbol {f} _ {\mathrm{ex}} = \left(\boldsymbol {f} _ {1} ^ {\top}, \boldsymbol {f} _ {2} ^ {\top}, \dots , \boldsymbol {f} _ {N _ {\mathrm{r}}} ^ {\top}\right) ^ {\top} \tag {31c}
\]

\[
\boldsymbol {A} = \boldsymbol {P} _ {\mathrm{ex}} ^ {\top} \boldsymbol {P} _ {\mathrm{ex}}, \boldsymbol {b} = - 2 f _ {\mathrm{ex}} ^ {\top} \boldsymbol {P} _ {\mathrm{ex}}, \boldsymbol {c} = f _ {\mathrm{ex}} ^ {\top} f _ {\mathrm{ex}} \tag {31d}
\]

The structure of  \( f_{ex} \) ,  \( P_{ex} \)  is illustrated in Fig. 3. It can be seen that, in this case, the optimization function in Eq. (27) is essentially the discrete form of the  \( L_{2} \)  norm of the discrepancy between the true PDF of the system response and the identified result.

### 3.3. Identification algorithm

This subsection discusses the identification method for the PDF of a multi-dimensional random source with independent components. The physical stochastic system affected by the s-dimensional random source  \( \xi \in R^{s} \)  can be represented by the following differential equation:

\[
\boldsymbol {Y} = \boldsymbol {A} (\boldsymbol {Y}, \xi , t) \tag {32}
\]

where the components of \(\xi\) are independent of each other. Select several components from the response vector \(Y(t)\) that are more sensitive to changes of \(\xi\), forming the vector \(X(t)\) for computation.

#### Preparation Stage Algorithm:

##### 1. Statistical Estimation:

First, collect multiple samples of  \( \boldsymbol{X}(t_{k}), k = 1, 2, \ldots, N_{\mathrm{t}} \)  at different time instants. Then, perform a multi-dimensional KDE to obtain  \( p_{\boldsymbol{X}}(\boldsymbol{x}, t_{k}) \) . For different time instants, select multiple coordinates  \( \{x_{1}, x_{2}, \ldots, x_{l_{k}}\} \) , and compute the vector  \( f_{ex} \)  using Eqs. (29a) and (31c).

##### 2. Model Training:

An initial hyperrectangle for the random source distribution is provided based on historical experience:

\[
\Omega_ {\xi} = \prod_ {i = 1} ^ {s} [ a _ {i}, b _ {i} ] \tag {33}
\]

Note that the selection of this range can be very coarse and broad, as long as it ensures that the values of the random variable are unlikely to exceed this range. For example, if the compressive strength of a concrete cube is the random variable to be solved, since it is at least a positive number and generally does not exceed 1000 MPa (which is a very weak conclusion), the initial range can be set as [0, 1000] MPa. Define the standardized random variable \(\Theta\) as follows:

\[
\Theta_ {i} = \frac {\xi_ {i} - a _ {i}}{b _ {i} - a _ {i}} \in [ 0, 1 ], \quad i = 1, 2, \dots , s \tag {34}
\]

Then, insert  \( N_{tr} \)  Sobol sequence points within an region slightly larger than  \( [0,1]^{s} \)  to generate a training point set  \( P_{tr} = \{\theta_{1}, \theta_{2}, \ldots, \theta_{N_{tr}}\} \) . For each of these points, solve the differential Eq. (32) to obtain multiple sample trajectories  \( \boldsymbol{H}(\theta_{i}, t_{k}), i = 1, 2, \ldots, N_{tr}, k = 1, 2, \ldots, N_{t} \)  of  \( \boldsymbol{X}(t) \)  and use this data to train a Kriging model at each time instants.

5

Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

\[
\boldsymbol {f} _ {\mathrm{ex}} = \left\{ \begin{array}{l} \boldsymbol {f} _ {1} \\ \boldsymbol {f} _ {2} \\ \dots \\ \boldsymbol {f} _ {k} \\ \dots \\ \boldsymbol {f} _ {N _ {s}} \end{array} \right\} \left\{ \begin{array}{l} p _ {\boldsymbol {x}} (\boldsymbol {x} _ {1}, t _ {k}) \\ p _ {\boldsymbol {x}} (\boldsymbol {x} _ {2}, t _ {k}) \\ p _ {\boldsymbol {x}} (\boldsymbol {x} _ {3}, t _ {k}) \\ \dots \\ p _ {\boldsymbol {x}} (\boldsymbol {x} _ {1}, t _ {k}) \end{array} \right\} \quad \boldsymbol {P} _ {\mathrm{ex}} = \left[ \begin{array}{c} \boldsymbol {P} _ {1} \\ \boldsymbol {P} _ {2} \\ \dots \\ \boldsymbol {P} _ {k} \\ \dots \\ \boldsymbol {P} _ {N _ {s}} \end{array} \right] \left[ \begin{array}{c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c} \end{array} \right] \left[ \begin{array}{c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c
\]

Fig. 3. Structures of \( f_{\mathrm{ex}} \) and \( P_{\mathrm{ex}} \).

Optimization Stage Algorithm: The initial parameters include the initial hyperrectangle  \( C^{s} = [0,1]^{s} \) , the current optimization iteration  \( n_{opt} = 1 \) , the maximum optimization iterations  \( N_{opt} \) , the number of Voronoi cells  \( N_{sel} \)  (which may change with optimization iterations), the interval of iterations for updating the Kriging model  \( n_{upd} \) , the objective function threshold  \( J_{thr} \) , and the objective function tolerance h. Then execute the following procedure (refer to Fig. 4 where the sketches are examples for a 2-dimensional case):

#### 1. Space Partitioning:

Generate \(N_{\mathrm{sel}}\) Sobol sequence points within the hyperrectangle \(C^s\), forming the initial partition point set \(P_{\mathrm{sel}} = \{\theta_1, \theta_2, \dots, \theta_{N_{\mathrm{sel}}}\}\), and partition the hyperrectangle \(C^s\) into multiple Voronoi cells.

#### 2. Local Computation:

Generate  \( N_{den} = N_{sel} n_{q} \)  densified points  \( \{\tilde{\theta}_{1}, \tilde{\theta}_{2}, \ldots, \tilde{\theta}_{N_{den}}\} \)  within  \( C^{s} \)  and ensured that each Voronoi cell contains  \( n_{q} \)  densified points. Then, use the trained Kriging model to predict the response of all densified points at each time instant. Compute  \( p_{q}(x, t) \) ,  \( P_{ex} \)  according to Eqs. (15), (31a) and (31b).

#### 3. Optimization Computation:

If  \( n_{opt} > 1 \) , extract the objective function value  \( J_{out}^{t} \)  from the previous iteration; otherwise, skip this step. Solve the optimization problem expressed in Eq. (27) and yield the assigned probability vector  \( y = (\Pr_{1}, \Pr_{2}, \ldots, \Pr_{N_{\mathrm{sel}}})^{\mathrm{T}} \)  for each Voronoi cell and the minimum objective function value  \( J_{out} \) . After computation, check if any of the following conditions are met:

\[
n _ {\text { opt }} \geq N _ {\text { opt }}, \quad J _ {\text { out }} \leq J _ {\text { thr }}, \quad | J _ {\text { out }} ^ {\prime} - J _ {\text { out }} | \leq h \tag {35}
\]

If any condition is satisfied, stop the computation and proceed to the post-processing stage. If not, update  \( n_{opt} \)  to  \( n_{opt} + 1 \) . Check whether the remainder of  \( n_{opt} \)  divided by  \( n_{upd} \)  is 0. If it is, update the Kriging model by adding all or some of the partition points into the training point set  \( P_{tr} \) ; otherwise, do not update the model. Then, check if the remainder is 1. If it is, proceed to Step; otherwise, proceed to Step 4.

#### 4. Point Set Densification:

Using the assigned probabilities as a weight, new partition points are added within each Voronoi cell, thereby expanding the set  \( P_{sel} \) . Let  \( N_{add} \)  denote the total number of added partition points in this step, then the number of new points added to the qth cell  \( N_{add,q} \)  is approximately  \( Pr_{q}N_{add} \) . This step ensures that Voronoi cells with higher assigned probabilities are subdivided into finer cells. Once this step is completed, return to Step 2.

#### 5. Point Set Reorganization:

Adjust the hyperrectangle  \( C^{s} \) : For the ith dimension, the probability centroid  \( \hat{\theta}_{i} \)  and standard deviation  \( \sigma_{i} \)  of that dimension are calculated based on the ith components of coordinates of partition points and the assigned probabilities. Then, the distribution range of the ith dimension for both the partition and densified points is adjusted to the new interval:

\[
I _ {i} = \left[ \max \left(\hat {\theta} _ {i} - a _ {i} \sigma_ {i}, 0\right), \min \left(\hat {\theta} _ {i} + a _ {i} \sigma_ {i}, 1\right) \right] \tag {36a}
\]

\[
\hat {\theta} _ {i} = \sum_ {q = 1} ^ {N _ {\mathrm{sel}}} \operatorname * {P r} _ {q} \theta_ {q, i}, \quad \sigma_ {i} = \sqrt {\sum_ {q = 1} ^ {N _ {\mathrm{sel}}} \operatorname * {P r} _ {q} (\theta_ {q , i} - \hat {\theta} _ {i}) ^ {2}} \tag {36b}
\]

where  \( \alpha_{i} \)  is a parameter related to the random source distribution characteristics. For Gaussian distribution,  \( \alpha = 3 \)  can be used. The hyperrectangle  \( C^{s} \)  is then updated to the Cartesian product of the new intervals for each dimension:

\[
C ^ {s} = I _ {1} \times I _ {2} \times \dots \times I _ {s} \tag {37}
\]

Once this step is completed, return to Step 1.

#### Post-processing Stage Algorithm:

The purpose of this step is to calculate the PDF of each component of the random source based on the assigned-probabilities.

#### 1. Calculation of the Empirical Distribution Function:

For ith component of randoms source, the empirical distribution function  \( \hat{F}_{i}(\theta_{i}) \)  can be obtained as follows:

\[
\hat {F} _ {i} (\theta_ {i}) = \sum_ {q = 1} ^ {N _ {\mathrm{sel}}} \operatorname * {P r} _ {q} I (\theta_ {q, i} \leq \theta_ {i}) \tag {38}
\]

where \(I(\bullet)\) is the indicator function.

#### 2. Adjustment:

The function \(\hat{F}_i\) exhibits discontinuous steps at each partition point \(\theta_{q,i}\), with the values corresponding to the respective assigned probabilities \(\mathrm{Pr}_q\). To smooth this, the function values at each point \(\theta_{q,i}\) are reduced by \(1/2\mathrm{Pr}_q\), with boundary values set to 0 and 1. This is equivalent to connecting the midpoints of each step in the empirical distribution function. The specific process is as follows:

\[
\hat {F} _ {i} ^ {\prime} \left(\theta_ {q, i}\right) = \left\{ \begin{array}{l l} 0, & q = 0 \\ \sum_ {m = 1} ^ {N _ {\mathrm{sel}}} \operatorname * {P r} _ {m} I \left(\theta_ {m, i} \leq \theta_ {q, i}\right) - \frac {1}{2} \operatorname * {P r} _ {q}, & 1 \leq q \leq N _ {\mathrm{sel}} \\ 1, & q = N _ {\mathrm{sel}} + 1 \end{array} \right. \tag {39}
\]

The boundary points are defined as:

\[
\theta_ {0, i} = \max (2 \theta_ {1, i} ^ {*} - \theta_ {2, i} ^ {*}, 0), \quad \theta_ {N _ {\mathrm{sel}} + 1, i} = \min (2 \theta_ {N _ {\mathrm{sel}}, i} ^ {*} - \theta_ {N _ {\mathrm{sel}} - 1, i} ^ {*}, 1) \tag {40}
\]

where \(\{\theta_{q,i}^{*}, q = 1,2,\dots,N_{\mathrm{sel}}\}\) are the result of sorting \(\{\theta_{q,i}, q = 1,2,\dots,N_{\mathrm{sel}}\}\) in ascending numerical order.

#### 3. Linear Interpolation and Smoothing:

The discrete points  \( \{(\theta_{q,i},\hat{F}_{i}^{\prime}(\theta_{q,i})),q=0,1,\ldots,N_{\mathrm{sel}}+1\} \)  are linearly interpolated over the interval  \( \theta_{i}\in[0,1] \) , and the interpolation results are then smoothed using a moving average filter. The length of the moving average can be set empirically, typically between 1/30 and 1/10 of the length of the interval  \( I_{i} \)  in Eq. (36). This yields the final distribution function calculation result  \( F_{i}(\theta_{i}) \) .

4. Numerical Differentiation: The function  \( F_{i}(\theta_{i}) \)  is numerically differentiated to obtain its derivative  \( \hat{p}_{i}(\theta_{i}) \) , and the result is processed to ensure non-negativity in the following manner:

\[
\hat {p} _ {i} ^ {\prime} (\theta_ {i}) = \max (0, \hat {p} _ {i} (\theta_ {i})) \tag {41}
\]

6

Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

![img-4.jpeg](img-4.jpeg)

Fig. 4. Diagram of the optimization stage of the independent multi-dimensional random source identification algorithm (The sketches are examples for a 2-dimensional case.).

Subsequently, smoothing and normalization are applied. The result is smoothed using a moving average filter, followed by the necessary corrections to obtain the final computed result:

\[
p _ {i} (\theta_ {i}) = \frac {p _ {i} ^ {\prime} (\theta_ {i})}{\int_ {0} ^ {1} p _ {i} ^ {\prime} (\theta_ {i}) \mathrm{d} \theta_ {i}} \tag {42}
\]

The relationship between original the random source  \( \xi \)  and the standardized random variable  \( \Theta \)  is used to derive the distribution function and probability density function of the original random variable:

\[
F _ {\mathcal {B}, i} (\xi_ {i}) = F _ {i} \left(\frac {\xi_ {i} - a}{b - a}\right) \tag {43}
\]

\[
p _ {\mathcal {B}, i} (\xi) = \frac {1}{b - a} p _ {i} \left(\frac {\xi_ {i} - a}{b - a}\right) \tag {44}
\]

It must be noted that the proposed identification algorithm is not only suitable for the random variables with independent components but also for those with correlated components, because the identification algorithm computes the probability measure of subsets of the

random source space, which means the joint distribution of the random variables is directly provided. To identify random variables with correlated components, it is sufficient to ensure that the rectangular region defined by Eq. (33) contains the region where the probability measure induced by the joint distribution of the random variables is primarily concentrated.

## 4. Error analysis

There exist four types of probability density functions of the system responses  \( \boldsymbol{X}(t) \) :  \( p_{\boldsymbol{X}}^{\mathrm{true}}(\boldsymbol{x},t) \) ,  \( p_{\boldsymbol{X}}^{\mathrm{kde}}(\boldsymbol{x},t) \) ,  \( p_{\boldsymbol{X}}^{\mathrm{par}}(\boldsymbol{x},t) \) ,  \( p_{\boldsymbol{X}}^{\mathrm{opt}}(\boldsymbol{x},t) \) , where  \( p_{\boldsymbol{X}}^{\mathrm{true}}(\boldsymbol{x},t) \)  denotes the true distribution of system responses;  \( p_{\boldsymbol{X}}^{\mathrm{kde}}(\boldsymbol{x},t) \)  denotes the distribution of system responses derived from KDE of the observed samples;  \( p_{\boldsymbol{X}}^{\mathrm{par}}(\boldsymbol{x},t) \)  denotes the computation result of Eq. (19) based on PDEM, where the random source space  \( \Omega_{\Theta} \)  is partitioned into Voronoi cells and the assigned probability  \( Pr_{q} \)  of each cell is calculated based on the true distribution of the random source;  \( p_{\boldsymbol{X}}^{\mathrm{opt}}(\boldsymbol{x},t) \)  is the PDF calculated by Eq. (19) where the assigned probabilities take values of the random source identification results.

7

Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

The solution error of the probabilistic inverse problem can be quantified by the discrepancy between the identification results and the true values of the assigned probability of each Voronoi cell:

\[
\text { error } = \sqrt {\sum_ {q = 1} ^ {N _ {\mathrm{sel}}} \left| \operatorname * {P r} _ {q} - \hat {\operatorname * {P r}} _ {q} \right| ^ {2}} = \| \mathbf {y} - \hat {\mathbf {y}} \| _ {2} \tag {45}
\]

where  \( \mathbf{y} = (\mathrm{Pr}_{1}, \mathrm{Pr}_{2}, \ldots, \mathrm{Pr}_{N_{\mathrm{sel}}})^{\top}, \hat{\mathbf{y}} = (\hat{\mathrm{Pr}}_{1}, \hat{\mathrm{Pr}}_{2}, \ldots, \hat{\mathrm{Pr}}_{N_{\mathrm{sel}}})^{\top} \)  denote the true assigned probability vector and the one derived from identification results.

Eq. (19) indicates that \( p_{\pmb{x}}^{\mathrm{par}}(\pmb{x},t) \) and \( p_{\pmb{x}}^{\mathrm{opt}}(\pmb{x},t) \) are assembled as follows:

\[
p _ {\boldsymbol {x}} ^ {\text { par }} (\boldsymbol {x}, t) = \sum_ {q = 1} ^ {N _ {\text { sel }}} \operatorname * {P r} _ {q} p _ {q} (\boldsymbol {x}, t), \quad p _ {\boldsymbol {x}} ^ {\text { opt }} (\boldsymbol {x}, t) = \sum_ {q = 1} ^ {N _ {\text { sel }}} \hat {\operatorname * {P r}} _ {q} p _ {q} (\boldsymbol {x}, t) \tag {46}
\]

Using an analogous method as described earlier, \( p_{\pmb{x}}^{\mathrm{par}}(\pmb{x},t), p_{\pmb{x}}^{\mathrm{opt}}(\pmb{x},t), p_{q}(\pmb{x},t) \) can be stored as vectors when different coordinate arrays \( x_{1}, x_{2}, \ldots, x_{l_{k}} \) are selected for different time instants \( t_k \):

\[
J _ {k} ^ {\text { par }} = \left(p _ {\boldsymbol {x}} ^ {\text { par }} (\boldsymbol {x} _ {1}, t _ {k}), p _ {\boldsymbol {x}} ^ {\text { par }} (\boldsymbol {x} _ {2}, t _ {k}), \dots , p _ {\boldsymbol {x}} ^ {\text { par }} (\boldsymbol {x} _ {l _ {k}}, t _ {k})\right) ^ {\top} \tag {47a}
\]

\[
J _ {k} ^ {\text { opt }} = \left(p _ {\boldsymbol {x}} ^ {\text { opt }} (\boldsymbol {x} _ {1}, t _ {k}), p _ {\boldsymbol {x}} ^ {\text { opt }} (\boldsymbol {x} _ {2}, t _ {k}), \dots , p _ {\boldsymbol {x}} ^ {\text { opt }} (\boldsymbol {x} _ {l _ {k}}, t _ {k})\right) ^ {\top} \tag {47b}
\]

\[
\boldsymbol {P} _ {k} ^ {(q)} = \left(p _ {q} (\boldsymbol {x} _ {1}, t _ {k}), p _ {q} (\boldsymbol {x} _ {2}, t _ {k}), \dots , p _ {q} (\boldsymbol {x} _ {l _ {k}}, t _ {k})\right) ^ {\top} \tag {47c}
\]

Thus, the discretized version of Eq. (46) can be obtained:

\[
J _ {\mathrm{ex}} ^ {\text { par }} = P _ {\mathrm{ex}} y, \quad J _ {\mathrm{ex}} ^ {\text { opt }} = P _ {\mathrm{ex}} \hat {y} \tag {48}
\]

where:

\[
J _ {\mathrm{ex}} ^ {\text { par }} = \left(\left(f _ {1} ^ {\text { par }}\right) ^ {\top}, \left(f _ {2} ^ {\text { par }}\right) ^ {\top}, \dots , \left(f _ {N _ {1}} ^ {\text { par }}\right) ^ {\top}\right) ^ {\top} \tag {49a}
\]

\[
J _ {\mathrm{ex}} ^ {\text { opt }} = \left(\left(f _ {1} ^ {\text { opt }}\right) ^ {\top}, \left(f _ {2} ^ {\text { opt }}\right) ^ {\top}, \dots , \left(f _ {N _ {1}} ^ {\text { opt }}\right) ^ {\top}\right) ^ {\top} \tag {49b}
\]

\[
\boldsymbol {P} _ {\mathrm{ex}} = \left[ \boldsymbol {P} _ {1} ^ {\top}, \boldsymbol {P} _ {2} ^ {\top}, \dots , \boldsymbol {P} _ {N _ {k}} ^ {\top} \right] ^ {\top}, \quad \boldsymbol {P} _ {k} = \left[ \boldsymbol {P} _ {k} ^ {(1)}, \boldsymbol {P} _ {k} ^ {(2)}, \dots , \boldsymbol {P} _ {k} ^ {(N _ {\mathrm{sel}})} \right] \tag {49c}
\]

The two equations in Eq. (48) form overdetermined systems of equations, and their exact solutions, i.e., the least squares solutions, can be written as:

\[
\mathbf {y} = \boldsymbol {A} ^ {- 1} \boldsymbol {P} _ {\mathrm{ex}} ^ {\top} \boldsymbol {J} _ {\mathrm{ex}} ^ {\text { par }}, \quad \hat {\mathbf {y}} = \boldsymbol {A} ^ {- 1} \boldsymbol {P} _ {\mathrm{ex}} ^ {\top} \boldsymbol {J} _ {\mathrm{ex}} ^ {\text { opt }}, \tag {50}
\]

where A represents  \( P_{ex}^{x}P_{ex} \) . The upper bound of the error expressed in Eq. (45) can be estimated as follows:

\[
\begin{array}{l} \text { error } = \| \mathbf {y} - \hat {\mathbf {y}} \| _ {2} \leq \| \mathbf {A} ^ {- 1} \| _ {2} \| \mathbf {P} _ {\mathrm{ex}} \| _ {2} \| J _ {\mathrm{ex}} ^ {\text { par }} - J _ {\mathrm{ex}} ^ {\text { opt }} \| _ {2} \\ = \frac {s _ {\max}}{s _ {\min} ^ {2}} \| J _ {\mathrm{ex}} ^ {\text { par }} - J _ {\mathrm{ex}} ^ {\text { opt }} \| _ {2} \\ \leq \frac {s _ {\max}}{s _ {\min} ^ {2}} (e _ {\text { par }} + e _ {\text { kde }} + e _ {\text { opt }} + e ^ {\prime}) \tag {51a} \\ \end{array}
\]

\[
e _ {\text { par }} = \| J _ {\mathrm{ex}} ^ {\text { par }} - J _ {\mathrm{ex}} ^ {\text { true }} \| _ {2}, \quad e _ {\mathrm{kde}} = \| J _ {\mathrm{ex}} ^ {\text { true }} - J _ {\mathrm{ex}} ^ {\mathrm{kde}} \| _ {2}, \quad e _ {\text { opt }} = \| J _ {\mathrm{ex}} ^ {\mathrm{kde}} - J _ {\mathrm{ex}} ^ {\text { opt }} \| _ {2} \tag {51b}
\]

where  \( s_{max} \) ,  \( s_{min} \)  is the maximum and minimal singular value of  \( P_{ex} \) ; the vectors  \( f_{ex}^{true} \) ,  \( f_{ex}^{kde} \)  are constructed in the same manner, as outlined in Eq. (49).  \( s_{max}/s_{min}^{2} \)  quantify the error amplification effect and  \( e_{par} \) ,  \( e_{kde} \) ,  \( e_{opt} \) ,  \( e' \)  represents errors arising from the random source space partition, the KDE of the observed samples of system responses, the random source identification algorithm, and additional factors, respectively. Among these,  \( e_{kde} \)  vanishes as sample size increases and  \( e_{opt} \)  is, in fact, the objective function of the random source identification algorithms. The analysis of  \( e_{par} \)  and the error amplification effect factor  \( s_{max}/s_{min}^{2} \)  is carried out as follows.

It is noted that the local probability density \( p_{q}(\pmb{x},t) \) converges to the Dirac function \( \delta [\pmb {x} - \pmb {H}(\theta_q,t)] \) when the size of each subdomain

\(\Omega_q\) vanishes. Therefore an asymptotic expression of \(e_{\mathrm{par}}\) is derived as follows:

\[
\begin{array}{l} e _ {\text { par }} = \sqrt {\sum_ {k = 1} ^ {N _ {1}} \sum_ {i = 1} ^ {l _ {k}} \left| p _ {\boldsymbol {x}} ^ {\text { true }} (\boldsymbol {x} _ {i} , t _ {k}) - p _ {\boldsymbol {x}} ^ {\text { par }} (\boldsymbol {x} _ {i} , t _ {k}) \right| ^ {2}} \\ = \sqrt {\sum_ {k = 1} ^ {N _ {1}} \sum_ {i = 1} ^ {l _ {k}} \left| \int_ {\Omega_ {\boldsymbol {\theta}}} \delta [ \boldsymbol {x} _ {i} - \boldsymbol {H} (\boldsymbol {\theta} , t _ {k}) ] p _ {\boldsymbol {\theta}} (\boldsymbol {\theta}) \mathrm{d} \boldsymbol {\theta} - \sum_ {q = 1} ^ {N _ {\text {sel}}} \operatorname * {P r} _ {q} p _ {q} (\boldsymbol {x} _ {i} , t _ {k}) \right| ^ {2}} \\ \approx \sqrt {\sum_ {k = 1} ^ {N _ {1}} \sum_ {i = 1} ^ {l _ {k}} \left| \int_ {\Omega_ {\boldsymbol {\theta}}} f (\boldsymbol {x} _ {i} , \boldsymbol {\theta} , t _ {k}) p _ {\boldsymbol {\theta}} (\boldsymbol {\theta}) \mathrm{d} \boldsymbol {\theta} - \sum_ {q = 1} ^ {N _ {\text {sel}}} \operatorname * {P r} _ {q} f (\boldsymbol {x} _ {i} , \boldsymbol {\theta} _ {q} , t _ {k}) \right| ^ {2}} \\ \leq D _ {\mathrm{EF}} \left(\mathcal {P} _ {\text {sel}}\right) \sqrt {\sum_ {k = 1} ^ {N _ {1}} \sum_ {i = 1} ^ {l _ {k}} \left[ T V \left(f \left(\boldsymbol {x} _ {i} , \bullet , t _ {k}\right)\right) \right] ^ {2}} \tag {52} \\ \end{array}
\]

where \(\Theta\) is the standardized the random source taking values in the hyperrectangle \(C^\gamma = [0,1]^{\gamma}\), \(f(x,\theta ,t) = \sum_{q = 1}^{N_1}p_q(x,t)I_{\Omega_q}(\theta)\) and \(I_{\Omega_q}\) is the indicator function of \(\Omega_q\).

The last line of the above equation is derived from the extended Koksma–Hlawka inequality for multi-dimensional case proposed by Chen et al. [52], where  \( D_{\mathrm{EF}}(\mathcal{P}_{\mathrm{sel}}) \)  represents the EF-discrepancy of  \( P_{sel} \)  and  \( TV(f(x_{i},\bullet,t_{k})) \)  denotes the total variation of  \( f(x_{i},\theta,t_{k}) \)  which is regarded as the function of  \( \theta \) . The expressions for these two are as follows [53]:

\[
D _ {\mathrm{EF}} \left(\mathcal {P} _ {\text {sel}}\right) = \sup _ {\theta \in \mathbb {R} ^ {d}} \left| \sum_ {q = 1} ^ {N _ {1}} \operatorname * {P r} _ {q} I \left(\theta_ {q} \leq \theta\right) - F _ {\boldsymbol {\theta}} (\theta) \right| \tag {53a}
\]

\[
T V (f (\boldsymbol {x} _ {i}, \bullet , t _ {k})) = \sum_ {\beta = 1} ^ {s} \sum_ {\alpha_ {1} + \alpha_ {2} + \dots + \alpha_ {s} = \beta} \int_ {C ^ {\gamma}} \left| \frac {\partial^ {\beta} f (\boldsymbol {x} _ {i} , \boldsymbol {\theta} , t _ {k})}{\partial \theta_ {1} ^ {\alpha_ {1}} \partial \theta_ {2} ^ {\alpha_ {2}} \dots \partial \theta_ {s} ^ {\alpha_ {s}}} \right| d \boldsymbol {\theta} \tag {53b}
\]

where \(F_{\theta}(\theta)\) is the CDF of \(\theta\).

In most cases, the total variation of  \( f(x_{i},\bullet,t_{k}) \)  is strongly related to the degree of the nonlinearity of the system and is nearly impossible to calculate, while the EF-discrepancy is controllable. As long as the density of the partition points is approximately proportional to the probability density function of the random source, the EF-discrepancy can be kept small, thereby effectively controlling the error term  \( e_{par} \) . This is also why the multi-dimensional random source identification algorithm densifies the partition point set using the assigned probabilities as weights.

In the upper bound error estimation expressed by Eq. (51), as the ill-conditioning of  \( P_{ex} \)  worsens, the error amplification factor grows, leading to a sharp decline in the accuracy of the random source identification algorithm. Let the number of rows of the matrix  \( P_{ex} \)  be M. By performing singular value decomposition(SVD), two real orthogonal matrices U and V can be found such that:

\[
\boldsymbol {P} _ {\mathrm{ex}} = \boldsymbol {U} \boldsymbol {S} \boldsymbol {V} ^ {\top} \tag {54a}
\]

\[
\boldsymbol {S} = \left[ \begin{array}{c} \boldsymbol {\Delta} _ {N _ {\mathrm{sel}} \times N _ {\mathrm{sel}}} \\ \boldsymbol {O} \end{array} \right], \quad \boldsymbol {\Delta} = \operatorname{diag} (s _ {1}, s _ {2}, \dots , s _ {N _ {\mathrm{sel}}}) \tag {54b}
\]

\[
\boldsymbol {U} = \left[ \boldsymbol {U} ^ {(1)}, \boldsymbol {U} ^ {(2)}, \dots , \boldsymbol {U} ^ {(M)} \right], \quad \boldsymbol {V} = \left[ \boldsymbol {V} ^ {(1)}, \boldsymbol {V} ^ {(2)}, \dots , \boldsymbol {V} ^ {(N _ {\mathrm{sel}})} \right] \tag {54c}
\]

where \( s_i, i = 1,2,\dots,N_{\mathrm{sel}} \) are the singular values of \( P_{\mathrm{ex}} \) arranged in descending order, and \( U^{(i)}, V^{(i)} \) represents the column vectors of \( U, V \). The SVD of \( P_{\mathrm{ex}} \) is rearranged as follows:

\[
\boldsymbol {S} \boldsymbol {V} ^ {\top} = \left[ \begin{array}{c} \boldsymbol {\Delta} _ {N _ {\mathrm{sel}} \times N _ {\mathrm{sel}}} \\ \boldsymbol {O} \end{array} \right] \left[ \begin{array}{c} \boldsymbol {V} ^ {(1) \top} \\ \boldsymbol {V} ^ {(2) \top} \\ \dots \\ \boldsymbol {V} ^ {(N _ {\mathrm{sel}}) \top} \end{array} \right] = \left[ \begin{array}{c} s _ {1} \boldsymbol {V} ^ {(1) \top} \\ s _ {2} \boldsymbol {V} ^ {(2) \top} \\ \dots \\ s _ {N _ {\mathrm{sel}}} \boldsymbol {V} ^ {(N _ {\mathrm{sel}}) \top} \\ \boldsymbol {O} \end{array} \right] = \left[ \begin{array}{c} \boldsymbol {D} _ {N _ {\mathrm{sel}} \times N _ {\mathrm{sel}}} \\ \boldsymbol {O} \end{array} \right] \tag {55a}
\]

\[
\boldsymbol {P} _ {\mathrm{ex}} = \left[ \boldsymbol {U} ^ {(1)}, \dots , \boldsymbol {U} ^ {(M)} \right] \left[ \begin{array}{l} \boldsymbol {D} \\ \boldsymbol {O} \end{array} \right] = \left[ \sum_ {i = 1} ^ {N _ {\mathrm{sel}}} \boldsymbol {U} ^ {(i)} D _ {i 1}, \dots , \sum_ {i = 1} ^ {N _ {\mathrm{sel}}} \boldsymbol {U} ^ {(i)} D _ {i N _ {\mathrm{sel}}} \right] \tag {55b}
\]

If, starting from \( s_i \), singular values are either zero or near zero, some rows of the matrix \( D \) in Eq. (55) become zero or nearly zero, leading to

8

Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

![img-5.jpeg](img-5.jpeg)

Fig. 5. The effect of \( P_{\mathrm{ex}} \) on \( y \).

the column space's maximal set of linearly independent vectors of \( P_{\mathrm{ex}} \) becoming (or approximately becoming) \( \{U^{(1)}, U^{(2)}, \dots, U^{1/-1}\} \), making the column vectors of \( P_{\mathrm{ex}} \) linearly dependent (or nearly linearly dependent) and leading to the ill-posedness of probabilistic inverse problem. The column vectors represent the local probability densities \( p_0(x, t) \) at different time instants and corresponding coordinate points, and their linear dependence arises from the excessive similarity between the local probability densities of different subdomains. This results from the high overlap of sample trajectories within different subdomains, caused by the non-injective mapping from the random source space \( \Omega_0 \) to the response space \( \Omega_X \).

The orthogonal matrix V in Eq. (54) represents a rotation or symmetry operation to the assigned probability vector y, resulting in another vector  \( y_{normal} = V^{\top}y \)  with the unchanged norm. This can be interpreted as transforming the original coordinate basis into a new one, where the components of  \( y_{normal} \)  represent the normalized coordinates of the assigned probability vector in the new basis. The column vectors  \( V^{(i)} \)  of V represent the new basis vectors. If S contains no zero or near-zero singular value, all components of  \( y_{normal} \) ; retain significant values, fully transmitting probabilistic information of the random source to system responses; otherwise some components of  \( y_{normal} \)  are compressed to zero or nearly zero, causing any variation in the corresponding directions of the normalized basis undetectable on  \( P_{ex} \)  and it is impossible to identify this variation. Fig. 5 illustrates this effect.

It should be noted that in the method proposed in this paper, the model prediction error and the measurement error are incorporated into  \( e^{par} \) ,  \( e^{hde} \)  and  \( e' \) . The impact of these errors on the final results is evaluated through the error analysis formula Eq. (51a). However, no measures were taken to mitigate their effects, making the methods primarily applicable to sufficiently reliable models and sufficiently accurate measurement results.

## 5. Numerical examples

### 5.1. Identification of the stochastic damping matrix for linear structures

In this subsection, a numerical example of the identification of one-dimensional random sources is provided. The equations of motion for a multi-degree-of-freedom (MDOF) linear elastic system subjected to an external excitation  \( F(t) \)  can always be written in the standard form:

\[
\boldsymbol {M} \ddot {\boldsymbol {X}} + \boldsymbol {C} \dot {\boldsymbol {X}} + \boldsymbol {K} \boldsymbol {X} = \boldsymbol {F} (t) \tag {56}
\]

where M, C, and K represent the mass, damping, and stiffness matrices of the system, respectively.

It is well-known that the physical mechanisms of the damping matrix are less understood than those of the mass and stiffness matrices and the random behavior of the damping matrix is a significant factor. The randomness arises from variations in the amount of energy dissipated, the components of dissipation, and the structure's state under each deterministic excitation leading to different observed damping matrix samples. Additionally, discretizing a continuous elastic body into multiple DOFs may introduce other unmodeled sources of randomness. Therefore, modeling a multi-DOF system with a stochastic damping matrix to account for all potential sources of randomness is a reasonable approach.

![img-6.jpeg](img-6.jpeg)

Fig. 6. The linear frame structure.

Table 1
Information of deterministic and random parameters(where m, E, h,  \( \xi_{1} \) ,  \( \xi_{2} \)  denote the mass of each story, the Young's modulus, the height of each story, the first and the second modal damping ratio. The PDF of  \( \xi_{1} \)  is  \( p_{\xi_{1}}(x)=0.4\varphi[(x-0.06)/0.1]+0.6\varphi[(x-0.1)/\sqrt{0.02}] \) , where  \( \varphi \)  denotes the PDF of a standard Gaussian random variable.)

|  Parameters | Is random | Values/Distributions  |
| --- | --- | --- |
|  m | False | \( 1 \times 10^{4} \) kg  |
|  E | False | \( 1 \times 10^{4} \) MPa  |
|  h | False | 3.6 m  |
|  \( \xi_{1} \) | True | \( Log\mathcal{N}(=3,0.1) \)  |
|  \( \xi_{2} \) | True | Irregular bimodal distribution  |

Let \(\varphi_{i}, i = 1,2,\ldots,n\) denote the mode shape vector of an n-DOFs system. In this section, the assumption of orthogonal damping is adopted, i.e.,

\[
\boldsymbol {\varphi} _ {i} ^ {\top} \boldsymbol {C} \boldsymbol {\varphi} _ {j} = 0, \quad \forall i \neq j \tag {57}
\]

The method for establishing the stochastic damping matrix in this subsection models the damping ratios of the first two modes as independent random variables. For higher modes, the damping ratios are modeled according to the approach proposed by Clough and Penzien [54].

Fig. 6 illustrates a 10-story, two-span shear frame structure. The mass of each story is \(1 \times 10^{4}\) kg, the material Young's modulus of the frame columns is \(1 \times 10^{4}\) MPa, the cross-sectional area is \(500\mathrm{mm} \times 400\mathrm{mm}\), and the story height is \(3.6\mathrm{m}\). The beam stiffness is assumed to be infinite. The damping ratios for the first two modes are modeled as independent random variables following different distributions. The damping ratio of the third mode is set to 0.1, and for higher modes, the damping ratios are assumed to be proportional to the corresponding modal natural frequencies, maintaining the same ratio as that of the third mode. The deterministic parameters and random variables are shown in Table 1. The true distributions of the random source are illustrated in Fig. 7.

The test excitation is set as an impact excitation distributed according to mass, with an intensity equal to the magnitude of gravitational acceleration  \( g \approx 9.8 \, m/s^{2} \) . The governing equations of the system are given by:

\[
\boldsymbol {M} \ddot {\boldsymbol {X}} + \boldsymbol {C} \dot {\boldsymbol {X}} + \boldsymbol {K} \boldsymbol {X} = \boldsymbol {M} \boldsymbol {L} g \dot {\boldsymbol {o}} (t), \quad \boldsymbol {L} = (1, 1, \dots , 1) _ {1 \times 1 0} ^ {\top} \tag {58}
\]

9

Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

![img-7.jpeg](img-7.jpeg)

(a)

![img-8.jpeg](img-8.jpeg)

(b)

Fig. 7. True distributions of the random source.

![img-9.jpeg](img-9.jpeg)

![img-10.jpeg](img-10.jpeg)

![img-11.jpeg](img-11.jpeg)

![img-12.jpeg](img-12.jpeg)

Fig. 8. The distribution of time instants.

A Monte Carlo numerical simulation is performed with 40,000 iterations, using the same test excitation expressed by Eq. (58), and 40 significant time instants \( t_k, k = 1,2,\dots,N_t = 40 \) are selected as a measured data in applications. These time instants are distributed within one-quarter of a cycle of the first two modal responses during the early stage of the system's evolution which are illustrated in Fig. 8. The absolute displacement samples of each story at all significant time instants \( X_j(t_k), j = 1,2,\dots,40000, k = 1,2,\dots,40 \) are then collected. Subsequently, modal response sample data are generated according to the following method:

\[
\boldsymbol {q} _ {j} (t _ {k}) = \boldsymbol {\Phi} ^ {- 1} \boldsymbol {X} _ {j} (t _ {k}), \quad j = 1, 2, \dots , 4 0 0 0 0, k = 1, 2, \dots , 4 0 \tag {59}
\]

where  \( \Phi = [\varphi_{1}, \varphi_{2}, \ldots, \varphi_{n}] \)  is the mode shape matrix. Kernel density estimation is performed on the data shown in Eq. (59) to generate the truncated probability density of the first two modal stochastic responses at the significant time instants, as illustrated in Fig. 9.

Based on the truncated probability density of the modal random responses at the significant time instants generated by KDE, a random

source identification algorithm is run to identify the damping ratios of the first two modes. Due to the simplicity of the one-dimensional problem, the point set densification step in the algorithm introduced in Section 3.3 is not required, and the Sobol sequence can be replaced with an equidistant distribution of points. The algorithm parameters are shown in Table 2. The variation in \( N_{\mathrm{ad}} \) in Table 2 is due to the reorganization step of the partition point set mentioned earlier. In this example, the number of new points to be added is controlled manually. The number of points \( N_{\mathrm{den}} \) used for the local computation is always kept 50 times the value of \( N_{\mathrm{ad}} \), ensuring that each cell contains 50 densified points. The final results of the algorithm are displayed in Fig. 10. The error between the identification results and the true probability density function of the random source is provided in Table 3. The error is represented in terms of the KL divergence, as shown below: Suppose that \( W \) is a random variable to be identified and let \( p_W, \hat{p}_W \) denote the true PDF and the identification results of the PDF of \( W \), respectively. The KL divergence is defined as follows:

\[
K L _ {\mathrm{f}} = \int_ {\mathbb {R}} p _ {W} (w) \ln \frac {p _ {W} (w)}{\hat {p} _ {W} (w)} \mathrm{d} w \tag {60a}
\]

10

Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

![img-13.jpeg](img-13.jpeg)

(a)

![img-14.jpeg](img-14.jpeg)

(b)

Fig. 9. The KDE results of PDFs of modal responses.

![img-15.jpeg](img-15.jpeg)

(a) The PDF of \(\xi_{1}\)

![img-16.jpeg](img-16.jpeg)

(b) The PDF of \(\xi_{2}\)

Fig. 10. The identification results.

Table 2
Parameters of the algorithm.

|  Parameters | Values  |
| --- | --- |
|  \( N_{\text{opt}} \) | 3  |
|  \( N_{\text{ad}} \) | [10,20,50]  |
|  \( N_{\text{don}} \) | [500,1000,2500]  |
|  \( n_{\text{apd}} \) | 2  |
|  \( J_{\text{thr}} \) | 1e-5  |
|  h | 1e-6  |

Table 3
Error of the identification results.

|  Error functions | Error in identifying \( \xi_1 \) | Error in identifying \( \xi_2 \)  |
| --- | --- | --- |
|  \( KL_f \) | 0.0394 | 0.0044  |
|  \( KL_b \) | 0.0028 | 0.0016  |

\[
K L _ {\mathrm{b}} = \int_ {\mathbb {R}} \hat {p} _ {W} (w) \ln \frac {\hat {p} _ {W} (w)}{p _ {W} (w)} \mathrm{d} w \tag {60b}
\]

where  \( KL_{f}, KL_{b} \)  denote the forward KL divergence and the backward KL divergence.

The iteration process for calculating the random source probability density functions and the cumulative distribution functions(CDF) as well as the distribution of the partition points and training points in each iteration of the optimization algorithm, are illustrated in Figs. 11 and 12. The comparison between the system's random response truncated probability density, obtained from the random source identification results, and the result estimated using KDE from the observed samples is presented in Fig. 13. The evolution of the objective function \( J(y) \) is illustrated in Fig. 14.

The total computation time was approximately 30 s, including the preparation stage, the optimization stage, and the post-processing stage. As can be seen from Fig. 10 and Table 3, the calculated results of the probability density functions for the first two modal damping ratios deviate slightly from the actual results, with the values of both forward and backward KL divergences reaching the order of  \( 1e-3\sim1e-2 \) . Moreover, the calculation results accurately reproduce the bimodal characteristics of the actual probability density functions, indicating that the algorithm proposed in this paper effectively captures the intricate features of the probability density function shapes.

### 5.2. Identification of Bouc–Wen hysteresis model parameters for nonlinear structures

In this subsection, a numerical example of the identification of an independent multi-dimensional random source is provided. Suppose there exists a frame with the same structural configuration as that illustrated in Fig. 6, where the material elastic modulus of the columns in each layer is \(2 \times 10^{4}\) MPa. The nonlinear behavior of the structure is modeled using the Bouc–Wen interlayer restoring force model, and the evolution relationship between the variables is given by Bouc [55] and Wen [56]:

\[
\left\{\begin{array}{l}g (X, \dot {X}) = \alpha K X + (1 - \alpha) K Z\\Z = \frac {A \dot {X} \rightarrow \left(\hat {\rho} | X Z ^ {n - 1} | Z + \gamma \dot {X} | Z | ^ {n}\right)}{\eta}\\\nu = 1 + d _ {\nu} \varepsilon\\\eta = 1 + d _ {\eta} \varepsilon\\\varepsilon = \int_ {0} ^ {t} Z X \mathrm{d} t\end{array}\right. \tag {61}
\]

11

Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

![img-17.jpeg](img-17.jpeg)

(a) The PDF of \(\xi_{1}\)

![img-18.jpeg](img-18.jpeg)

(b) The PDF of \(\xi_{2}\)

![img-19.jpeg](img-19.jpeg)

(c) The CDF of \(\xi_{1}\)

![img-20.jpeg](img-20.jpeg)

(d) The CDF of \(\xi_{2}\)

Fig. 11. The iteration process of PDFs and CDFs.

![img-21.jpeg](img-21.jpeg)

(a) The evolution of \(\mathcal{P}_{\mathrm{sel}}\) for \(\Theta_{1}\) (The (b) The evolution of \(\mathcal{P}_{\mathrm{sel}}\) for \(\Theta_{2}\) (The color of points represents values of as- color of points represents values of assigned probabilities) signed probabilities)

![img-22.jpeg](img-22.jpeg)

![img-23.jpeg](img-23.jpeg)

(c) The evolution of \(\mathcal{P}_{\mathrm{tr}}\) for \(\Theta_{1}\)

![img-24.jpeg](img-24.jpeg)

(d) The evolution of \(\mathcal{P}_{\mathrm{tr}}\) for \(\Theta_{2}\)

Fig. 12. The evolution of essential point sets.

12

Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

![img-25.jpeg](img-25.jpeg)

![img-26.jpeg](img-26.jpeg)

Fig. 13. The comparison of the truncated PDFs of responses.

![img-27.jpeg](img-27.jpeg)

(a) The evolution of the objective function for identifying \(\xi_{1}\)

![img-28.jpeg](img-28.jpeg)

(b) The evolution of the objective function for identifying \(\xi_{2}\)

Fig. 14. The evolution of the objective functions.

Table 4
Information of deterministic and random parameters(where m, E, h,  \( \xi_{1} \) ,  \( \xi_{2} \)  denote the mass of each story, the Young's modulus, the height of each story, the first and the second modal damping ratio).

|  Parameters | Is random | Values/Distributions  |
| --- | --- | --- |
|  m | False | \( 1 \times 10^{4} \) kg  |
|  E | False | \( 2 \times 10^{4} \) MPa  |
|  h | False | 4.0 m  |
|  \( \xi_{1} \) | False | 0.05  |
|  \( \xi_{2} \) | False | 0.05  |
|  \( \alpha \) | True | \( Log\mathcal{N}(-3.58, 0.39) \)  |
|  \( \beta \) | False | 60  |
|  \( \gamma \) | False | 10  |
|  \( d_{s} \) | False | 200  |
|  \( d_{d} \) | False | 200  |
|  A | True | \( \mathcal{N}(1, 0.1) \)  |

where  \( g(X, X) \)  represents the interlayer restoring force, and X, Z refers to the real and hysteretic displacements between layers, respectively. The parameters  \( \alpha \)  and A are set as independent random variables, while the remaining parameters are assigned deterministic values.

The damping of the frame is modeled using Rayleigh damping, where the damping matrix is expressed as a linear combination of the mass and stiffness matrices, with the combination coefficients determined based on the first and second-order modal damping ratios of 0.05. The specific values or distribution parameters of all frame parameters are provided in Table 4 and Fig. 15.

The excitation is modeled as an impact applied concentrically at the top of the frame:

\[
\boldsymbol {M} \dot {\boldsymbol {X}} + \boldsymbol {C} \dot {\boldsymbol {X}} + \boldsymbol {G} (\boldsymbol {X}, \dot {\boldsymbol {X}}) = 2 \boldsymbol {M} \boldsymbol {L} g \delta (t), \quad \boldsymbol {L} = (0, 0, \dots , 1) _ {l \times 1 0} ^ {T} \tag {62}
\]

A Monte Carlo numerical simulation is performed with 40,000 iterations, using the same test excitation expressed by Eq. (62), and 10 significant time instants \( t_k \), \( k = 1,2,\dots,N_t = 10 \) are selected to simulate the measured data in applications. 2-dimensional KDE is performed on the data of the displacement of the 10th story \( X_{10}(t) \) and the velocity of the 5th story \( V_5(t) \) to generate the truncated joint probability density functions at the significant time instants, as illustrated in Fig. 16.

Based on the truncated joint probability density of the displacement of the 10th story \( X_{10}(t) \) and the velocity of the 5th story \( V_{5}(t) \) at significant time instants generated by 2-dimensional KDE, a multidimensional independent the random source identification algorithm is run to identify the parameter \( \alpha, A \). The algorithm parameters are shown in Table 5. The variation in \( N_{\mathrm{sel}} \) in Table 5 is due to the densification step and the reorganization step of the partition point set mentioned earlier. In the densification step, the number of new partition points added in each cell is determined by the cell with the highest assigned probability, while the number of points added to other cells is proportional to the ratio of their assigned probabilities to that of the cell with the highest assigned probability. The total number of partition points after addition is automatically calculated by the program. In the reorganization step of the partition point set, the number of partition points will be set to 100 manually. The number of points \( N_{\mathrm{den}} \) used for the local computation is always kept 100 times the value of \( N_{\mathrm{sel}} \), ensuring that each cell contains 100 densified points. The final results of the algorithm are displayed in Fig. 17 and the error in the term of KL divergence between the identification results and the true probability density function is provided in Table 6.

The iteration process for calculating the random source probability density functions and the cumulative distribution functions(CDF) as well as the distribution of the partition points are illustrated in Figs. 18, 19. The evolution of the objective function \( J(y) \) is illustrated in

13

Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

![img-29.jpeg](img-29.jpeg)

(a)

![img-30.jpeg](img-30.jpeg)

(b)

Fig. 15. The true PDF of the random source.

![img-31.jpeg](img-31.jpeg)

(a)

![img-32.jpeg](img-32.jpeg)

(b)

![img-33.jpeg](img-33.jpeg)

(c)

![img-34.jpeg](img-34.jpeg)

(d)

![img-35.jpeg](img-35.jpeg)

(e)

![img-36.jpeg](img-36.jpeg)

(f)

![img-37.jpeg](img-37.jpeg)

(g)

![img-38.jpeg](img-38.jpeg)

(h)

![img-39.jpeg](img-39.jpeg)

(i)

![img-40.jpeg](img-40.jpeg)

(j)

Fig. 16. The joint PDFs derived from 2-dimensional KDE.

14

Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

![img-41.jpeg](img-41.jpeg)

(a) The PDF of \(\alpha\)

![img-42.jpeg](img-42.jpeg)

(b) The PDF of \(A\)

Fig. 17. The identification results.

Table 5
Parameters of the algorithm.

|  Parameters | Values  |
| --- | --- |
|  \( N_{\text{opt}} \) | 4  |
|  \( N_{\text{ad}} \) | [100,412,100,563]  |
|  \( N_{\text{den}} \) | [1e4,4.12e4,1e4,5.63e4]  |
|  \( n_{\text{opt}} \) | 2  |
|  \( J_{\text{thr}} \) | 1e-5  |
|  h | 1e-6  |

Table 6
Error of the identification results.

|  Error functions | Error in identifying \( \alpha \) | Error in identifying \( A \)  |
| --- | --- | --- |
|  \( KL_{f} \) | 0.0584 | 0.0028  |
|  \( KL_{b} \) | 0.0082 | 0.0033  |

Fig. 20. The truncated joint PDFs of system responses obtained from the random source identification results are presented in Fig. 21.

The total computation time was approximately 667 s. As can be seen from Fig. 17 and Table 6, the calculated results of the probability density functions for  \( \alpha \)  and A deviate slightly from the actual results, with the values of both forward and backward KL divergences reaching the order of 1e-3~1e-2.

## 6. Conclusion and further work

This paper presents a probabilistic inverse problem-solving method based on the probability conservation principle of physical stochastic systems and the theory of convex optimization. It can capture the fine features of the shape of the probability density function of random variables to be identified without requiring the specification of any prior distribution or the type of distribution, only the approximate range of the random source. Moreover, the method is capable of identifying the correlation structure between random variables, as it directly identifies the probability measure of the subsets of the random source space, which means that the joint distribution is directly provided. Additionally, a procedure is proposed to assess the well-posedness of the probabilistic inverse problem based on error analysis theory.

The challenge of the proposed method lies in finding a continuous injective mapping from the random source space to the response space. While increasing the dimension of the response space using large amounts of data of the system's outputs may help find the injective mapping, the probability distribution tends to concentrate on a low-dimensional manifold, leading to numerical singularities in the probability density mentioned earlier. Although the small-sample method proposed in this paper does not rely on increasing the dimension of the response space, thus avoiding the numerical singularities in the probability density, it requires careful determination of the

injective mapping for each specific problem because the dimension of the random source space and the response space is identical. This is why, to date, the work in this paper is limited to low-dimensional random sources. Future work will aim to extend the proposed method to Riemann manifolds to address the identification of higher-dimensional random sources. This approach allows for the construction of injective maps by simply increasing the dimension of the observational data, i.e., the dimension of the response space. Additionally, it enables to capture of the intrinsic manifold structure from noisy data, facilitating the inclusion of measurement error handling.

## CRediT authorship contribution statement

Yuhan Zhu: Writing – review & editing, Writing – original draft, Visualization, Validation, Software, Methodology, Formal analysis, Data curation, Conceptualization. Jie Li: Writing – review & editing, Writing – original draft, Supervision, Resources, Methodology, Investigation, Funding acquisition.

## Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## Acknowledgments

This work was supported by the National Natural Science Foundation of China (Grant No. 51538010).

## Appendix. Explanations for Proposition 1

Denote the Borel \(\sigma\)-algebra on \(\mathbb{R}^s, \mathbb{R}^d\) by \(B_s, B_d\). The subspace \(\sigma\)-algebra restricted to \(\Omega_\theta\) is defined as \(\Omega_\theta \cap B_s\) on which the Lebesgue measure \(\lambda\) can be well-defined. The explanation of this proposition is divided into two parts. The first part proves that the probability measure \(\operatorname{Pr}_\theta\) on \(\Omega_\theta \cap B_s\) can be uniquely determined by the continuous injection \(G\) and the probability measure \(\operatorname{Pr}_X\) on \(B_d\). The second part demonstrates the existence and the uniqueness of the probability density function \(p_\theta, p_X\) as the Radon-Nikodym derivative of the probability measure \(\operatorname{Pr}_\theta, \operatorname{Pr}_X\) with respect to the Lebesgue measure on \(\Omega_\theta \cap B_s\) and \(B_d\) after including generalized function.

15

Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

![img-43.jpeg](img-43.jpeg)

(a) The PDF of \(\alpha\)

![img-44.jpeg](img-44.jpeg)

(b) The PDF of \(A\)

![img-45.jpeg](img-45.jpeg)

(c) The CDF of \(\alpha\)

![img-46.jpeg](img-46.jpeg)

(d) The CDF of \(A\)

Fig. 18. The iteration process of PDFs and CDFs.

![img-47.jpeg](img-47.jpeg)

(a)

![img-48.jpeg](img-48.jpeg)

(b)

![img-49.jpeg](img-49.jpeg)

(c)

![img-50.jpeg](img-50.jpeg)

(d)

Fig. 19. The evolution of the partition point set (The color of points represents values of assigned probabilities).

16

Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

![img-51.jpeg](img-51.jpeg)

Fig. 20. The evolution of the objective function.

### A.1. The existence and uniqueness of the probability measure

First it is claimed that a probability measure  \( Pr_{\theta} \)  is uniquely determined on  \( \mathcal{G}^{-1}(B_{d}) \)  based on a pushforward measure  \( Pr_{X} \)  on  \( B_{d} \), because if there exists two measure  \( Pr_{\theta,1}.Pr_{\theta,2} \)  on  \( \mathcal{G}^{-1}(B_{d}) \)  inducing the same pushforward measure  \( Pr_{X} \), then for any  \( A \in \mathcal{G}^{-1}(B_{d}) \)  there exists  \( B \in B_{d} \)  such that:

\[
\operatorname * {P r} _ {\boldsymbol {\theta}, 1} (A) = \operatorname * {P r} _ {\boldsymbol {\theta}, 1} \circ \mathcal {G} ^ {- 1} (B) = \operatorname * {P r} _ {\boldsymbol {X}} (B) = \operatorname * {P r} _ {\boldsymbol {\theta}, 2} \circ \mathcal {G} ^ {- 1} (B) = \operatorname * {P r} _ {\boldsymbol {\theta}, 2} (A) \tag {A.1}
\]

Therefore \(\mathrm{Pr}_{\theta,1} = \mathrm{Pr}_{\theta,2}\). Additionally, it can be shown that \(\mathcal{G}^{-1}(B_d) = \Omega_\theta \cap B_s\), then the domain of the measure \(\mathrm{Pr}_\theta\) can be extended from \(\mathcal{G}^{-1}(B_d)\) to \(\Omega_\theta \cap B_s\) where the Lebesgue measure is well defined, thereby allowing the definition of the probability density function. The explanation is as follows.

Let \( T_{s}, T_{d} \) be the topology of \( R^{s}, R^{d} \) induced by Euclidean metric, then the topology of the subspace \( \Omega_{\theta} \subseteq R^{s} \) is defined as \( \Omega_{\theta} \cap T_{s} \). It can be shown that \( \Omega_{\theta} \cap T_{s} \) is the generator of \( \Omega_{\theta} \cap B_{s} \). According to measure theory, the continuity of a function implies its measurability [57], therefore it can be concluded that:

\[
\mathcal {G} ^ {- 1} (T _ {d}) \subseteq \Omega_ {\theta} \cap T _ {s} \rightarrow \mathcal {G} ^ {- 1} (B _ {d}) \subseteq \Omega_ {\theta} \cap B _ {s} \tag {A.2}
\]

It is clear that \(\mathcal{G}\) is a bijection between \(\Omega_{\theta}\) and \(\mathcal{G}(\Omega_{\theta})\). The bounded measurable closed subset \(\Omega_{\theta}\) itself is a compact space and \(\mathcal{G}(\Omega_{\theta})\) is a Hausdorff space as the subspace of \(\mathbb{R}^d\). Point set topology implies that any continuous bijection from a compact space to a Hausdorff space is a homeomorphism [58], which means:

\[
\mathcal {G} (\Omega_ {\theta} \cap T _ {s}) \subseteq \mathcal {G} (\Omega_ {\theta}) \cap T _ {d} \tag {A.3}
\]

That is, for any  \( A \in T_{s} \)  there exists  \( B \in T_{d} \)  such that:

\[
\mathcal {G} (\Omega_ {\theta} \cap A) = \mathcal {G} (\Omega_ {\theta}) \cap B \tag {A.4}
\]

Since \(\mathcal{G}\) is injective, it follows that:

\[
\mathcal {G} ^ {- 1} [ \mathcal {G} (\Omega_ {\theta} \cap A) ] = \Omega_ {\theta} \cap A = \mathcal {G} ^ {- 1} [ \mathcal {G} (\Omega_ {\theta}) \cap B ] = \mathcal {G} ^ {- 1} (B) \in \mathcal {G} ^ {- 1} (T _ {d}) \tag {A.5}
\]

That is to say:

\[
\mathcal {G} ^ {- 1} (T _ {d}) \supseteq \Omega_ {\theta} \cap T _ {s} \rightarrow \mathcal {G} ^ {- 1} (B _ {d}) \supseteq \Omega_ {\theta} \cap B _ {s} \tag {A.6}
\]

In summary,  \( \mathcal{G}^{-1}(B_{d}) = \Omega_{\theta} \cap B_{s} \) . Therefore, a probability measure  \( Pr_{\theta} \)  is uniquely determined on  \( \Omega_{\theta} \cap B_{s} \) .

### A.2. The existence and uniqueness of the probability density function

Suppose there exists a measurable subset \(\Omega\) of a Euclidean space \((\mathbb{R}^n,B_n)\) with a positive Lebesgue measure; then the Lebesgue measure \(\lambda\) can be well-defined on \(\Omega \cap B_{n}\). Denote \(C\) as the function space containing

all the continuous functions with compact support on \(\Omega\). For any \(\varphi \in C\) and any measure \(\mu\) on \(\Omega \cap B_n\), denote \(\mu(\varphi)\) as the following integral:

\[
\mu (\varphi) = \int_ {\Omega} \varphi \mathrm{d} \mu \tag {A.7}
\]

It is clear that the above equation defines a linear functional on \(C\). In addition, the Riesz theorem states that for any continuous linear functional on \(C\), there exists a unique measure such that the expression (A.7) holds [59]. Thus any measure \(\mu\) on \(\Omega \cap B_n\) itself can be regarded as a continuous linear functional on \(C\). Denote \(C'\) as the space containing all the continuous linear functions on \(C\) or all the measures on \(\Omega \cap B_n\).

According to measure theory, for any measure \(\mu\) on \(\Omega \cap B_{n}\) that is absolutely continuous with respect to the Lebesgue measure \(\lambda\), there exists a unique Radon-Nikodym(R-N) derivative \(p\) [57] such that for any \(\varphi \in C\) it is satisfied that:

\[
\mu (\varphi) = \int_ {\Omega} \varphi p \mathrm{d} \lambda = \int_ {\Omega} \varphi (x) p (x) \mathrm{d} x \tag {A.8}
\]

which means \( p(x) \), i.e., the density function, and the corresponding measure \( \mu \) are bijectionally related. Thus the density function \( p(x) \) constructs a continuous linear functional identical to the ones constructed by \( \mu \). Denote \( C_{\mathrm{BC}}' \) as the space containing all the measure on \( \Omega \cap B_n \) which is absolutely continuous with respect to \( \lambda \), and it can be concluded that \( C_{\mathrm{BC}}' \subseteq C' \). It is reasonable to regard \( C_{\mathrm{BC}}' \) as the space containing all the density function \( p(x) \) of an absolutely continuous measure with respect to \( \lambda \) in the sense of a linear isomorphism.

According to the theory of distributions, the definition of a function can be given by its action as a functional on other functions [59]. Therefore, although the measure \(\mu\) in \(C' - C_{\mathrm{BC}}'\) does not have a R-N derivative in the classical sense, the definition of the R-N derivative can be extended to \(C'\), without specifying their explicit expressions (which, in fact, cannot be explicitly given). Formally, the expression (A.8) can still be written. The elements of \(C'\) can be referred to as the generalized R-N derivatives.

The introduction of the generalized R–N derivative allows handling cases where the measure is concentrated on a Lebesgue null set. First, the definition of a measure  \( \mu \)  or its generalized R–N derivative p being zero when regarded as a functional is: for any  \( \varphi \in C' \) , if its support is contained within some open set A, then  \( \mu(\varphi) = 0 \) , and it is said that  \( \mu \)  or p is zero on A. The support of  \( \mu \)  or p is defined as the complement of the largest open set A where  \( \mu \)  is zero. For the case where the measure is concentrated on a Lebesgue null set N, it is clear that for any  \( \varphi \in C' \)  whose support is contained with  \( N^{c} \) , the following holds:

\[
\mu (\varphi) = \int_ {\Omega} \varphi \mathrm{d} \mu = \int_ {N} \varphi \mathrm{d} \mu = 0 \tag {A.9}
\]

Therefore, it is said that the support of p is N, which means p is “zero” on  \( N^{c} \)  and is “non-zero” on N. A widely used example is the Dirac function, which is the generalized R–N derivative of the Dirac measure  \( \delta \)  in Euclidean space. The Dirac measure concentrated at the origin satisfies the following condition:

\[
\delta (\{\mathbf {0} \}) = 1, \quad \delta (A) = 0 \quad \forall A \in B _ {n} \quad \text { s.t. } \quad \mathbf {0} \notin A \tag {A.10}
\]

Combining the concept of the support of a measure and the generalized R–N derivatives leads to the following well-known conclusion regarding the Dirac  \( \delta \)  function, commonly found in scientific papers:

\[
\delta (x) = \left\{ \begin{array}{l l} + \infty , & x = \mathbf {0} \\ 0, & x \neq \mathbf {0} \end{array} \right. \quad \int_ {\mathbb {R} ^ {n}} \delta (x) \mathrm{d} x = 1 \tag {A.11}
\]

In the case where the measure is concentrated on an irregular Lebesgue null set, it is not possible to express such a simplified generalized R-N derivative in a formal manner. Therefore, it is sufficient to declare the existence of its density function in the functional form expressed as Eq. (A.8) without specifying its explicit form.

For any measure \(\mu\) on \(B_{n}\), it can always be decomposed into two parts \(\mu = \mu_{\mathrm{BC}} + \mu_{\mathrm{S}}\) according to the Lebesgue decomposition [57]: \(\mu_{\mathrm{BC}}\) is absolutely continuous with respect to the Lebesgue measure, and

17

Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

![img-52.jpeg](img-52.jpeg)

(a)

![img-53.jpeg](img-53.jpeg)

(b)

![img-54.jpeg](img-54.jpeg)

(c)

![img-55.jpeg](img-55.jpeg)

(d)

![img-56.jpeg](img-56.jpeg)

(e)

![img-57.jpeg](img-57.jpeg)

(f)

![img-58.jpeg](img-58.jpeg)

(g)

![img-59.jpeg](img-59.jpeg)

(h)

![img-60.jpeg](img-60.jpeg)

(i)

![img-61.jpeg](img-61.jpeg)

(j)

Fig. 21. The truncated PDFs of responses obtained by identification results.

\( \mu_{s} \) that is mutually singular with respect to it, which means a R–N derivative \( p(\boldsymbol{x}) \) in the classical sense of \( \mu_{sc} \) can be uniquely determined and there exists a measurable set N such that \( \lambda(N)=0 \), \( \mu_{s}(N^{c})=0 \), thus a generalized R–N derivative \( \dot{p}(\boldsymbol{x}) \) supported on N can be uniquely determined.

Through the previous discussion, it can be concluded that the probability density function  \( p_{X}(x) \)  (which may be a generalized function) on  \( R^{d} \)  uniquely determines the probability measure  \( Pr_{X} \)  on  \( B_{d} \), and that by taking this measure as the pushforward under a continuous injection  \( g : \Omega_{\theta} \to R^{d} \), the probability measure  \( Pr_{\theta} \)  on  \( \Omega_{\theta} \cap B_{s} \)  is uniquely determined, which in turn uniquely determines a probability density function  \( p_{\theta}(\theta) \) (which may be a generalized function) on  \( \Omega_{\theta} \).

## Data availability

The data that has been used is confidential.

## References

[1] Li J, Chen J. Stochastic dynamics of structures. John Wiley & Sons; 2009.

[2] Li J, Chen J. The probability density evolution method for dynamic response analysis of non-linear stochastic structures. Internat J Numer Methods Engrg 2006;65(6):882–903.

[3] Nagel JB, Sudret B. Hamiltonian Monte Carlo and borrowing strength in hierarchical inverse problems. ASCE-ASME J Risk Uncertain Eng Syst Part A: Civ Eng 2016;2(3):B4015008.

[4] Ye N, Roosta-Khorasani F, Cui T. Optimization methods for inverse problems. In: de Gier J, Praeger CE, Tao T, editors. 2017 MATRIX annals. Springer; 2019, p. 121–40.

[5] Collins JD, Hart GC, Hasselman T, Kennedy B. Statistical identification of structures. AIAA J 1974;12(2):185–90.

[6] Beck JL, Katafygiotis LS. Updating models and their uncertainties. I: Bayesian statistical framework. J Eng Mech 1998;124(4):455–61.

[7] Guan X, He J, Jha R, Liu Y. An efficient analytical Bayesian method for reliability and system response updating based on Laplace and inverse first-order reliability computations. Reliab Eng Syst Saf 2012;97(1):1–13.

[8] Beck JL, Au S-K. Bayesian updating of structural models and reliability using Markov chain Monte Carlo simulation. J Eng Mech 2002;128(4):380–91.

[9] Hastings WK. Monte Carlo sampling methods using Markov chains and their applications. Biometrika 1970;57(1):97–109.

[10] Ching J, Muto M, Beck JL. Structural model updating and health monitoring with incomplete modal data using Gibbs sampler. Comput-Aided Civ Infrastruct Eng 2006;21(4):242–57.

18

Y. Zhu and J. Li

Structural Safety 115 (2025) 102600

[11] Hoffman MD, Gelman A, et al. The No-U-Turn sampler: adaptively setting path lengths in Hamiltonian Monte Carlo. J Mach Learn Res 2014;15(1):1593–623.

[12] Ching J, Chen Y. Transitional Markov chain Monte Carlo method for Bayesian model updating, model class selection, and model averaging. J Eng Mech 2007;133(7):816–32.

[13] Lye A, Cicirello A, Patelli E. An efficient and robust sampler for Bayesian inference: Transitional ensemble Markov chain Monte Carlo. Mech Syst Signal Process 2022;167:108471.

[14] Spantini A, Bigoni D, Marzouk Y. Inference via low-dimensional couplings. J Mach Learn Res 2018;19(66):1–71.

[15] Furno MD, Marzouk YM. Transport map accelerated Markov chain Monte Carlo. SIAM/ASA J Uncertain Quantif 2018;6(2):645–82.

[16] Grashorn J, Broggi M, Chamoin L, Beer M. Efficiency comparison of MCMC and Transport Map Bayesian posterior estimation for structural health monitoring. Mech Syst Signal Process 2024;216:111440.

[17] Dierksen N, Holmeister B, Hübler C. The Bayesian pattern search, a deterministic acceleration of Bayesian model updating in structural health monitoring. Mech Syst Signal Process 2025;225:112259.

[18] Liu Y, Li L, Zhao S. Efficient Bayesian updating with two-step adaptive Kriging. Struct Saf 2022;95:102172.

[19] Jiang X, Lu Z. Adaptive Kriging-based Bayesian updating of model and reliability. Struct Saf 2023;104:102362.

[20] Yoshida I, Nakamura T, Au S-K. Bayesian updating of model parameters using adaptive Gaussian process regression and particle filter. Struct Saf 2023;102:102328.

[21] Li Q, Du X, Ni P, Han Q, Xu K, Bai Y. Improved hierarchical Bayesian modeling framework with arbitrary polynomial chaos for probabilistic model updating. Mech Syst Signal Process 2024;215:111409.

[22] Behmanesh I, Moaveni B, Lombaert G, Papadimitriou C. Hierarchical Bayesian model updating for structural identification. Mech Syst Signal Process 2015;64:360–76.

[23] Rizqiansyah A, Caprani CC. Hierarchical Bayesian modeling of highway bridge network extreme traffic loading. Struct Saf 2024;111:102503.

[24] Tenenbaum JB, Silva Vd, Langford JC. A global geometric framework for nonlinear dimensionality reduction. Sci 2000;290(5500):2319–23.

[25] Peeters RLM. Identification on a manifold of systems. Technical report 1992-7, Faculty of Economics and Business Administration, Vrije Universiteit Amsterdam; 1992.

[26] Boots B, Gordon G. Two-manifold problems with applications to nonlinear system identification. 2012, arXiv preprint arXiv:1206.4648.

[27] Chen W, Wang Z, Broccardo M, Song J. Riemannian manifold Hamiltonian Monte Carlo based subset simulation for reliability analysis in non-Gaussian space. Struct Saf 2022;94:102134.

[28] Pelletier B. Kernel density estimation on Riemannian manifolds. Statist Probab Lett 2005;73(3):297–304.

[29] Henry G, Munoz A, Rodriguez D. Locally adaptive density estimation on Riemannian manifolds. SORT-Stat Oper Res Trans 2013;111–30.

[30] Bhattacharya A, Dunson DB. Nonparametric Bayesian density estimation on manifolds with applications to planar shapes. Biometrika 2010;97(4):851–65.

[31] Graham MM, Thiery AH, Beskos A. Manifold Markov chain Monte Carlo methods for Bayesian inference in diffusion models. J R Stat Soc Ser B Stat Methodol 2022;84(4):1229–56.

[32] Lam H-F. Structural model updating and health monitoring in the presence of modeling uncertainties. Hong Kong University of Science and Technology (Hong Kong); 1999.

[33] Katafagiotis LS, Lam H-F. Tangential-projection algorithm for manifold representation in unidentifiable model updating problems. Earthq Eng Struct Dyn 2002;31(4):791–812.

[34] Goodwin GC. Dynamic system identification: experiment design and data analysis. Math Sci Eng 1977;136.

[35] Akaike H. A new look at the statistical model identification. IEEE Trans Autom Control 1974;19(6):716–23.

[36] Chen X, Li J. Identification of probabilistic distribution parameters for the mesoscopic stochastic fracture model. Probabilistic Eng Mech 2023;71:103415.

[37] Deng X. System identification based on particle swarm optimization algorithm. In: 2009 international conference on computational intelligence and security, vol. 1, IEEE; 2009, p. 259–63.

[38] Li J, Chen J. The principle of preservation of probability and the generalized density evolution equation. Struct Saf 2008;30(1):65–77.

[39] Venturini GM, García AM. Statistical distances and probability metrics for multivariate data, ensembles and probability distributions (Ph.D. thesis), Universidad Carlos III de Madrid; 2015.

[40] Bi S, Prabhu S, Cogan S, Atamturktur S. Uncertainty quantification metrics with varying statistical information in model calibration and validation. AIAA J 2017;55(10):3570–83.

[41] Mahalanobis PC. On the generalized distance in statistics. Sankhyā: Indian J Stat Ser A 2018;(2008-) 80:S1–7.

[42] Ali SM, Silvey SD. A general class of coefficients of divergence of one distribution from another. J R Stat Soc Ser B Stat Methodol 1966;28(1):131–42.

[43] Sullivan TJ. Introduction to uncertainty quantification, vol. 63, Springer; 2015.

[44] Fan W, Chen J, Li J. Solution of generalized density evolution equation via a family of  \( \delta \)  sequences. Comput Mech 2009;43:781–96.

[45] Wang D, Li J. A reproducing kernel particle method for solving generalized probability density evolution equation in stochastic dynamic analysis. Comput Mech 2020;65:597–607.

[46] Zhou J, Li J. IE-AK: A novel adaptive sampling strategy based on information entropy for kriging in metamodel-based reliability analysis. Reliab Eng Syst Saf 2023;229:108824.

[47] Kudela J, Matousek R. Recent advances and applications of surrogate models for finite element method computations: a review. Soft Comput 2022;26(24):13709–33.

[48] Krige DG. A statistical approach to some basic mine valuation problems on the Witwatersrand. J South Afr Inst Min Met 1951;52(6):119–39.

[49] Matheson G. Principles of geostatistics. Econ Geol 1963;58(8):1246–66.

[50] Botev ZI, Grotowski JF, Kroese DP. Kernel density estimation via diffusion. Ann Stat 2010;38(5):2916–57.

[51] Yosida K. Functional analysis, vol. 123, Springer Science & Business Media; 2012.

[52] Chen J, Yang J, Li J. A GF-discrepancy for point selection in stochastic seismic response analysis of structures with uncertain parameters. Struct Saf 2016;59:20–31.

[53] Chen J, Zhang S. Improving point selection in cubature by a new discrepancy. SIAM J Sci Comput 2013;35(5):A2121–49.

[54] Clough R, Penzien J. Dynamics of structures. McGraw-Hill NY, USA; 1975.

[55] Bouc R. Forced vibrations of mechanical systems with hysteresis. In: Proc. of the fourth conference on nonlinear oscillations, Prague, 1967. 1967.

[56] Wen Y-K. Method for random vibration of hysteretic systems. J Eng Mech Div 1976;102(2):249–63.

[57] Yan J. Lecture notes on measure theory. Scientific and natural sciences, Beijing: Science Press; 2004, p. 289, (in Chinese).

[58] Xiong J. Lecture notes on point set topology. Textbook for higher education, Beijing: Higher Education Press; 2003, p. 315, (in Chinese).

[59] Schwartz L. Theory of distributions. Beijing: Higher Education Press; 2010, (in Chinese).

19