As an example, using the normal probability density $f(x) = k \exp \left(-\frac{(x-x_0)^2}{2\sigma^2}\right)$, for a Jeffreys parameter is not consistent. Note that it would assign a finite probability to negative values of a positive parameter that, by definition, is positive. More technically, this would violate our postulate 1. Using the log-normal probability density for a Jeffreys parameter is consistent.

There is a problem of terminology in the Bayesian literature. The homogeneous probability distribution is a very special distribution. When the problem of selecting a 'prior' probability distribution arises in the absence of any information, except the fundamental symmetries of the problem, one may select as prior probability distribution the homogeneous distribution. But enthusiastic Bayesians do not call it 'homogeneous', but 'noninformative'. We cannot recommend using this terminology. The homogeneous probability distribution is as informative as any other distribution, it is just the homogeneous one (see appendix D).

In general, each time we consider an abstract parameter space, each point being represented by some parameters $\mathbf{x} = \{x^1, x^2 \dots x^n\}$, we will start by solving the (sometimes nontrivial) problem of defining a distance between points that respects the necessary symmetries of the problem. Only exceptionally this distance will be a quadratic expression of the parameters (coordinates) being used (i.e., only exceptionally our parameters will correspond to 'Cartesian coordinates' in the space). From this distance, a volume element $dV(\mathbf{x}) = v(\mathbf{x}) d\mathbf{x}$ will be deduced, from where the expression $f(\mathbf{x}) = k v(\mathbf{x})$ of the homogeneous probability density will follow. Sometimes, we can directly define volume element, without the need of a distance. We emphasize the need of defining a distance —or a volume element— in the parameter space, from which the notion of homogeneity will follow. With this point of view we slightly depart from the original work by Jeffreys and Jaynes.

## 2.3 Conjunction of Probabilities

We shall here consider two probability distributions $P$ and $Q$. We say that a probability $R$ is a product of the two given probabilities, and is denoted $(P \wedge Q)$ if

- $P \wedge Q = Q \wedge P$;
- for any subset $\mathcal{A}$, $(P \wedge Q)(\mathcal{A}) \neq 0 \implies P(\mathcal{A}) \neq 0$ and $Q(\mathcal{A}) \neq 0$;
- if $M$ denotes the homogeneous probability distribution, then $P \wedge M = P$.

The realization of these conditions leading to the simplest results can easily be expressed using probability densities (see appendix G for details). If the two probabilities $P$ and $Q$ are represented by the two probability densities $p(\mathbf{x})$ and $q(\mathbf{x})$, respectively, and if the homogeneous probability density is represented by $\mu(\mathbf{x})$, then the probability $P \wedge Q$ is represented by a probability density, denoted $(p \wedge q)(\mathbf{x})$, that is given by

$$(p \wedge q)(\mathbf{x}) = k \frac{p(\mathbf{x}) q(\mathbf{x})}{\mu(\mathbf{x})} \quad , \tag{13}$$

where $k$ is a normalization constant$^8$.

The two left columns of figure 1 represent these probability densities.

Example 2 On the surface of the Earth, using geographical coordinates (latitude $\vartheta$ and longitude $\varphi$), the homogeneous probability distribution is represented by the probability density $\mu(\vartheta, \varphi) = \frac{1}{4\pi} \cos \vartheta$. An estimation of the position of a floating object at the surface of the sea by an airplane navigator gives a probability distribution for the position of the object corresponding to the probability density $p(\vartheta, \varphi)$, and an independent, simultaneous estimation of the position by another airplane navigator gives a probability distribution corresponding to the probability density $q(\vartheta, \varphi)$. How do we 'combine' the two probability densities $p(\vartheta, \varphi)$ and $q(\vartheta, \varphi)$ to obtain a 'resulting' probability density? The answer is given by the conjunction of the two probability densities:

$$(p \wedge q)(\vartheta, \varphi) = k \frac{p(\vartheta, \varphi) q(\vartheta, \varphi)}{\mu(\vartheta, \varphi)} \quad . \tag{14}$$

[END OF EXAMPLE.]

$^8$Assume that $p(\mathbf{x})$ and $q(\mathbf{x})$ are normalized by $\int_{\mathcal{X}} d\mathbf{x} \, p(\mathbf{x}) = 1$ and $\int_{\mathcal{X}} d\mathbf{x} \, q(\mathbf{x}) = 1$. Then, irrespective of the normalizability of $\mu(\mathbf{x})$ (as explained above, $p(\mathbf{x})$ and $q(\mathbf{x})$ are assumed to be absolutely continuous with respect to the homogeneous distribution), $(p \wedge q)(\mathbf{x})$ is normalizable, and its normalized expression is $(p \wedge q)(\mathbf{x}) = \frac{p(\mathbf{x}) q(\mathbf{x}) / \mu(\mathbf{x})}{\int_{\mathcal{X}} d\mathbf{x} \, p(\mathbf{x}) q(\mathbf{x}) / \mu(\mathbf{x})}$.

10