The $P(\mathbf{x}_i \mid \mathbf{x}_j)$ is called the *transition probability density*. As, at each step, the random walker must go somewhere (including the possibility of staying at the same point), then

$$\int_{\mathcal{X}} P(\mathbf{x}_i \mid \mathbf{x}_j) d\mathbf{x}_i = 1. \tag{352}$$

For convenience we shall assume that $P(\mathbf{x}_i \mid \mathbf{x}_j)$ is nonzero everywhere (but typically negligibly small everywhere, except in a certain neighborhood around $\mathbf{x}_j$). For this reason, staying in an infinitesimal neighborhood of the current point $\mathbf{x}_j$ has nonzero probability, and therefore is considered a "transition" (from the point $\mathbf{x}_j$ to itself). The current point, having been reselected, contributes then with one more sample.

Given a random walk defined by the transition probability density $P(\mathbf{x}_i \mid \mathbf{x}_j)$. Assume that the point, where the random walk is initiated, is only known probabilistically: there is a probability density $q(\mathbf{x})$ that the random walk is initiated at point $\mathbf{x}$. Then, when the number of steps tends to infinity, the probability density that the random walker is at point $\mathbf{x}$ will "equilibrate" at some other probability density $p(\mathbf{x})$. It is said that $p(\mathbf{x})$ is an *equilibrium probability density* of $P(\mathbf{x}_i \mid \mathbf{x}_j)$. Then, $p(\mathbf{x})$ is an eigenfunction with eigenvalue 1 of the linear integral operator with kernel $P(\mathbf{x}_i \mid \mathbf{x}_j)$:

$$\int_{\mathcal{X}} P(\mathbf{x}_i \mid \mathbf{x}_j) p(\mathbf{x}_j) d\mathbf{x}_j = p(\mathbf{x}_i). \tag{353}$$

If for any initial probability density $q(\mathbf{x})$ the random walk equilibrates to the same probability density $p(\mathbf{x})$, then $p(\mathbf{x})$ is called *the* equilibrium probability of $P(\mathbf{x}_i \mid \mathbf{x}_j)$. Then, $p(\mathbf{x})$ is the unique eigenfunction of with eigenvalue 1 of the integral operator.

If it is possible for the random walk to go from any point to any other point in $\mathcal{X}$ it is said that the random walk is *irreducible*. Then, there is only one equilibrium probability density.

Given a probability density $p(\mathbf{x})$, many random walks can be defined that have $p(\mathbf{x})$ as their equilibrium density. Some tend more rapidly to the final probability density than others. Samples $\mathbf{x}^{(1)}, \mathbf{x}^{(2)}, \mathbf{x}^{(3)}, \ldots$ obtained by a random walk where $P(\mathbf{x}_i \mid \mathbf{x}_j)$ is negligibly small everywhere, except in a certain neighborhood around $\mathbf{x}_j$ will, of course, not be independent unless we only consider points separated by a sufficient number of steps.

Instead of considering $p(\mathbf{x})$ to be the probability density of the position of a (single) random walker (in which case $\int_{\mathcal{X}} p(\mathbf{x}) d\mathbf{x} = 1$), we can consider a situation where we have a "density $p(\mathbf{x})$ of random walkers" in point $\mathbf{x}$. Then, $\int_{\mathcal{X}} p(\mathbf{x}) d\mathbf{x}$ represents the total number of random walkers. None of the results presented below will depend on the way $p(\mathbf{x})$ is normed.

If at some moment the density of random walkers at a point $\mathbf{x}_j$ is $p(\mathbf{x}_j)$, and the transitions probability density is $P(\mathbf{x}_i \mid \mathbf{x}_j)$, then

$$F(\mathbf{x}_i, \mathbf{x}_j) = P(\mathbf{x}_i \mid \mathbf{x}_j) p(\mathbf{x}_j) \tag{354}$$

represents the probability density of transitions from $\mathbf{x}_j$ to $\mathbf{x}_i$: while $P(\mathbf{x}_i \mid \mathbf{x}_j)$ is the *conditional* probability density of the next point $\mathbf{x}_i$ visited by the random walker, given that it currently is at $\mathbf{x}_j$, $F(\mathbf{x}_i, \mathbf{x}_j)$ is the *unconditional* probability density that the next step will be a transition from $\mathbf{x}_j$ to $\mathbf{x}_i$, given only the probability density $p(\mathbf{x}_j)$.

When $p(\mathbf{x}_j)$ is interpreted as the density of random walkers at a point $\mathbf{x}_j$, $F(\mathbf{x}_i, \mathbf{x}_j)$ is called the *flow density*, as $F(\mathbf{x}_i, \mathbf{x}_j) d\mathbf{x}_i d\mathbf{x}_j$ can be interpreted as the number of particles going to a neighborhood of volume $d\mathbf{x}_i$ around point $\mathbf{x}_i$ from a neighborhood of volume $d\mathbf{x}_j$ around point $\mathbf{x}_j$ in a given step. The flow corresponding to an equilibrated random walk has the property that the particle density $p(\mathbf{x}_i)$ at point $\mathbf{x}_i$ is constant in time. Thus, that a random walk has equilibrated at a distribution $p(\mathbf{x})$ means that, in each step, the total flow into an infinitesimal neighborhood of a given point is equal to the total flow out of this neighborhood

Since each of the particles in a neighborhood around point $\mathbf{x}_i$ must move in each step (possibly to the neighborhood itself), the flow has the property that the total flow out from the neighborhood, and hence the total flow into the neighborhood, must equal $p(\mathbf{x}_i) d\mathbf{x}_i$:

$$\int_{\mathcal{X}} F(\mathbf{x}_i, \mathbf{x}_j) d\mathbf{x}_j = \int_{\mathcal{X}} F(\mathbf{x}_k, \mathbf{x}_i) d\mathbf{x}_k = p(\mathbf{x}_i) \tag{355}$$

Consider a random walk with transition probability density $P(\mathbf{x}_i \mid \mathbf{x}_j)$ with equilibrium probability density $p(\mathbf{x})$ and equilibrium flow density $F(\mathbf{x}_i, \mathbf{x}_j)$. We can multiply $F(\mathbf{x}_i, \mathbf{x}_j)$ with any symmetric flow density $\psi(\mathbf{x}_i, \mathbf{x}_j)$, where $\psi(\mathbf{x}_i, \mathbf{x}_j) \le q(\mathbf{x}_j)$, for all $\mathbf{x}_i$ and $\mathbf{x}_j$, and the resulting flow density

$$\varphi(\mathbf{x}_i, \mathbf{x}_j) = F(\mathbf{x}_i, \mathbf{x}_j) \psi(\mathbf{x}_i, \mathbf{x}_j) \tag{356}$$

78