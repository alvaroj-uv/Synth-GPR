# Chapter 12

# More on the Resolution-Variance Tradeoff

## 12.1 A Surfer's Guide to Backus-Gilbert Theory

The basic reference is [BG67]. The standard discrete inverse problem is

$$\mathbf{d} = A\mathbf{m} + \mathbf{e} \tag{12.1}$$

where $A$ is the derivative of the forward problem (an $n$ by $m$ matrix), $\mathbf{m}$ is a vector of unknown model parameters, and $\mathbf{d}$ contains the observed data. $\mathbf{m}$ is a vector in $R^m$. However, it represents a discretization of the model slowness $s(\mathbf{r})$, which is a scalar function defined on a closed subset $\Omega$ of $R^D$, $D \in (1, 2, 3 \dots)$. It will be assumed that the set of all possible models lies in some linear function space $\mathcal{M}$.

It is useful to introduce an **orthonormal basis of functions** (we will use our old friends the pixel functions) which span the model space $\mathcal{M}$. Suppose that $\Omega$ is completely covered by $m$ closed, convex, mutually disjoint sets (cells) $\sigma \in R^D : \Omega = \cup \sigma_i$ such that $\sigma_i \cap \sigma_j = \emptyset$ if $i \neq j$. The basis functions are then defined to be

$$h_i(\mathbf{r}) = \begin{cases} \nu_i^{-1/2} & \text{if } \mathbf{r} \in \sigma_i \\ 0 & \text{otherwise} \end{cases}$$

where $\nu_i$ is the volume of the $i$th cell. The choice of the normalization $\nu_i^{-1/2}$ is made to remove bias introduced by cell size. If a constant cell size is adopted, $\nu_i^{-1/2}$ can be replaced with 1. Given the definition of $h_i$, it is clear that

$$\int_{\Omega} h_i(\mathbf{r}) h_j(\mathbf{r}) d^D\mathbf{r} = \delta_{ij}.$$

Thus an arbitrary function can be written as an expansion in $h_i$

$$m(\mathbf{r}) = \sum_{i=1}^{\infty} m_i h_i(\mathbf{r}) \equiv \mathbf{m} \cdot \mathbf{h}(\mathbf{r}). \tag{12.2}$$

1