28

Example: A Vertical Seismic Profile

for now by simply asserting that the rays are straight lines. This would be a reasonable approximation for x-ray, but likely not for sound.

### an example

As a simple synthetic example we constructed a piecewise constant $v(z)$ using 40 unknown layers. We computed 78 synthetic travel times and contaminated them with Gaussian noise. (The numbers 40 and 78 have no significance whatsoever; they're just pulled from a hat.) The level of the noise doesn't matter for the present purposes; the point is that given an unknown level of noise in the data, different assumptions about this noise will lead to different kinds of reconstructions. With the constant velocity layers, the system of forward problems for all 78 rays (Equation 3.2) reduces to

$$\mathbf{t} = J \cdot \mathbf{s} \tag{3.3}$$

where $\mathbf{s}$ is the 40-dimensional vector of layer slownesses and $J$ is a matrix whose $(i, j)$ entry is the distance the $i$-th ray travels in the $j$-th layer. The details are given Bording et al. [BGL$^{+}$87] or later in Chapter 8. For now, the main point is that Equation 3.3 is simply a numerical approximation of the continuous Equation 3.2. The data mapping, the function that maps models into data, is the inner product of the matrix $J$ and the slowness vector $\mathbf{s}$. The vector $\mathbf{s}$, is another example of a model vector. It results from discretizing a function (slowness as a function of space). The first element of $\mathbf{s}$, $s_1$, is the slowness in the first layer, $s_2$ is the slowness in the second layer, and so on.

Let $t_i^o$ be the $i$-th observed travel time (which we get by examining the raw data shown in Figure 3.1. Let $t_i^c(\mathbf{s})$ be the $i$-th travel time calculated through an arbitrary slowness model $\mathbf{s}$ (by computing $J$ for the given geometry and taking the dot product in Equation 3.3. Finally, let $\sigma_i$ is the uncertainty (standard deviation) of the $i$-th datum.

If the true slowness is $\mathbf{s}_t$, then the following model of the observed travel times is assumed to hold:

$$t_i^o = t_i^c(\mathbf{s}_t) + \epsilon_i, \tag{3.4}$$

where $\epsilon_i$ is a noise term (whose standard deviation is $\sigma_i$). For this example, our goal is to estimate $\mathbf{s}_t$. A standard approach to solve this problem is to determine slowness vectors $\mathbf{s}$ that make a misfit function such as

$$\chi^2(\mathbf{s}) = \frac{1}{N} \sum_{i=1}^{N} \left( \frac{t_i^c(\mathbf{s}) - t_i^o}{\sigma_i} \right)^2, \tag{3.5}$$

smaller than some tolerance. Here $N$ is the number of observations. The symbol $\chi^2$ is often used to denote this sum because the sum of uncorrelated Gaussian random variables has a distribution known as $\chi^2$ by statisticians. Any statistics will have the details, for example the informative and highly entertaining [GS94]. We will come back to this idea later in the course.

1