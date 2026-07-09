There are three monographs in the area of Inverse Problems (from the view point of data interpretation). In Tarantola (1987), the general, probabilistic formulation for nonlinear inverse problems is proposed. The small book by Menke (1984) covers several viewpoints on discrete, linear and nonlinear inverse problems, and is easy to read. Finally, Parker (1994) exposes his view of the general theory of linear problems.

Recently, the interest in Monte Carlo methods, for the solution of Inverse Problems, has been increasing. Mosegaard and Tarantola (1995) proposed a generalization of the Metropolis algorithm (Metropolis et al., 1953) for analysis of general inverse problems, introducing explicitly prior probability distributions, and they applied the theory to a synthetic numerical example. Monte Carlo analysis was recently applied to real data inverse problems by Mosegaard et al. (1997), Dahl-Jensen et al. (1998), Mosegaard and Rygaard-Hjalsted (1999), and Khan et al. (2000).

## 2 Elements of Probability

Probability theory is essential to our formulation of inverse theory. This chapter therefore contains a review of important elements of probability theory, with special emphasis on results that are important for the analysis of inverse problems. Of particular importance is our explicit introduction of distance and volume in data and model spaces. This has profound consequences for the notion of conditional probability density which plays an important role in probabilistic inverse theory.

Also, we replace the concept of conditional probability by the more general notion of 'conjunction' of probabilities, this allowing us to address the more general problem where not only the data, but also the physical laws, are uncertain.

### 2.1 Volume

Let us consider an abstract space $\mathcal{S}$, where a point $\mathbf{x}$ is represented by some coordinates $\{x^1, x^2, \ldots\}$, and let $\mathcal{A}$ be some region (subspace) of $\mathcal{S}$. The measure associating a volume $V(\mathcal{A})$ to any region $\mathcal{A}$ of $\mathcal{S}$ will be denoted the volume measure

$$V(\mathcal{A}) = \int_{\mathcal{A}} d\mathbf{x} \, v(\mathbf{x}), \tag{1}$$

where the function $v(\mathbf{x})$ is the volume density, and where we write $d\mathbf{x} = dx^1 dx^2 \ldots$. The volume element is then$^3$

$$dV(\mathbf{x}) = v(\mathbf{x}) \, d\mathbf{x}, \tag{2}$$

and we may write $V(\mathcal{A}) = \int_{\mathcal{A}} dV(\mathbf{x})$. A manifold is called a metric manifold if there is a definition of distance between points, such that the distance $ds$ between the point of coordinates $\{x^i\}$ and the point of coordinates $\{x^i + dx^i\}$ can be expressed as$^4$

$$ds^2 = g_{ij}(\mathbf{x}) \, dx^i \, dx^j, \tag{3}$$

i.e., if the notion of distance is 'of the $L_2$ type'$^5$. The matrix whose entries are $g_{ij}$ is the metric matrix, and an important result of differential geometry and integration theory is that the volume density of the space, $v(\mathbf{x})$, equals the square root of the determinant of the metric:

$$v(\mathbf{x}) = \sqrt{\det \mathbf{g}(\mathbf{x})}. \tag{4}$$

Example 1 In the Euclidean 3D space, using spherical coordinates, the distance element is $ds^2 = dr^2 + r^2 d\theta^2 + r^2 \sin^2 \theta \, d\varphi^2$, from where it follows that the metric matrix is

$$\begin{pmatrix} g_{rr} & g_{r\theta} & g_{r\varphi} \\ g_{\theta r} & g_{\theta\theta} & g_{\theta\varphi} \\ g_{\varphi r} & g_{\varphi\theta} & g_{\varphi\varphi} \end{pmatrix} = \begin{pmatrix} 1 & 0 & 0 \\ 0 & r^2 & 0 \\ 0 & 0 & r^2 \sin^2 \theta \end{pmatrix}. \tag{5}$$

$^3$The capacity element associated to the vector elements $d\mathbf{r}_1, d\mathbf{r}_2 \ldots d\mathbf{r}_n$ is defined as $d\tau = \varepsilon_{ij\ldots k} dr_1^i dr_2^j \ldots dr_n^k$, where $\varepsilon_{ij\ldots k}$ is the Levi-Civita capacity (whose components take the values $\{0, \pm 1\}$). If the metric tensor of the space is $\mathbf{g}(\mathbf{x})$, then $\eta_{ij\ldots k} = \sqrt{\det \mathbf{g}} \, \varepsilon_{ij\ldots k}$ is a true tensor, as it is the product of a density $\sqrt{\det \mathbf{g}}$ by a capacity $\varepsilon_{ij\ldots k}$. Then, the volume element, defined as $dV = \eta_{ij\ldots k} dr_1^i dr_2^j \ldots dr_n^k = \sqrt{\det \mathbf{g}} \, d\tau$, is a (true) scalar.

$^4$This is a property that is valid for any coordinate system that can be chosen over the space.

$^5$As a counterexample, the distance defined as $ds = |dx| + |dy|$ is not of the $L_2$ type (it is $L_1$).

6