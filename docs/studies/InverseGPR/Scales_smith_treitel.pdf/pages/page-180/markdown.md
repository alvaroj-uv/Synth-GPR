11.2 Conjugate Gradient

165

the number of which was known in advance. It soon became apparent that $CG$ could be used as an iterative method. One can show that [Cha78]:

$$\| \mathbf{x} - \mathbf{x}_k \|_A \leq \| \mathbf{x} - \mathbf{x}_0 \|_A \left( \frac{1 - \sqrt{\kappa}}{1 + \sqrt{\kappa}} \right)^{2k} \tag{11.49}$$

where $\kappa \equiv \lambda_{max}/\lambda_{min}$ is the condition number of the matrix and $\| \mathbf{x} \|_A \equiv \sqrt{(\mathbf{x}, A\mathbf{x})}$. If the condition number is very nearly one, then $(1 - \sqrt{\kappa})/(1 + \sqrt{\kappa})$ is very small and the iteration converges rapidly. On the other hand if $\kappa = 10^5$ it may take several hundred iterations to get a single digit's improvement in the solution. But (11.49) is only an upper bound and probably rather pessimistic unless the eigenvalues of the matrix are well separated. For some problems, a comparatively small number of iterations will yield acceptable accuracy. And in any event, the convergence can be accelerated by a technique known as preconditioning.

The idea behind preconditioning is to solve a related problem having a much smaller condition number, and then transform the solution of the related problem into the one you want. If one is solving $A\mathbf{x} = \mathbf{h}$, then write this instead as

$$A\mathbf{x} = \mathbf{h} \tag{11.50}$$

$$AC^{-1}C\mathbf{x} = \mathbf{h}$$

$$A'\mathbf{x}' = \mathbf{h}$$

where $A' \equiv AC^{-1}$ and $C\mathbf{x} \equiv \mathbf{x}'$. To be useful, it is necessary that

\(\bullet \kappa (A^{\prime})\ll \kappa (A)\)
- \(C\mathbf{x} = \mathbf{h}\) should be easily solvable.

In this case, $CG$ will converge much more rapidly to a solution of $A'\mathbf{x}' = \mathbf{h}$ than of $A\mathbf{x} = \mathbf{h}$ and one will be able to recover $\mathbf{x}$ by inverting $C\mathbf{x} = \mathbf{x}'$. Alternatively, one could write the preconditioned equations as

$$A\mathbf{x} = \mathbf{h} \tag{11.51}$$

$$DA\mathbf{x} = Dh$$

$$A'\mathbf{x} = \mathbf{h}'$$

where $DA \equiv A'$ and $Dh \equiv \mathbf{h}'$.

The most effective preconditioner would be the inverse of the original matrix, since then $CG$ would converge in a single step. At the other extreme, the simplest preconditioner from a computational standpoint would be a diagonal matrix; whether any useful preconditioning can be obtained from so simple a matrix is another matter. Between these two extremes lies a vast array of possible methods many of which are based upon an approximate factorization of the matrix. For example one could imagine doing a

1