152

Iterative Linear Solvers

subject of iterative methods is vast and in no sense will a survey be attempted. The aim of the first section is simply to get the ball rolling and introduce a few classical methods before diving into conjugate gradient. In addition, the classical iterative methods are mostly based on matrix “splitting” which plays a key role in preconditioned conjugate gradient. This brief discussion is patterned on Chapter 8 of [SB80] and Chapter 4 of [You71]. Young is *the* pioneer in computational linear algebra and his book is the standard reference in the field.

Let $A$ be a nonsingular $n \times n$ matrix and $\mathbf{x} = A^{-1}\mathbf{h}$ be the exact solution of the system

$$A\mathbf{x} = \mathbf{h}. \tag{11.1}$$

A general class of iterative methods is of the form

$$\mathbf{x}_{i+1} = \Phi(\mathbf{x}_i), \qquad i = 0, 1, 2, \dots \tag{11.2}$$

where $\Phi$ is called the iteration function. A necessary and sufficient condition for (11.2) to converge is that the spectral radius$^a$ of $\Phi$ be less than one. For example, taking (11.1), introduce an arbitrary nonsingular matrix $B$ via the identity

$$B\mathbf{x} + (A - B)\mathbf{x} = \mathbf{h}. \tag{11.4}$$

Then, by making the *ansatz*

$$B\mathbf{x}_{i+1} + (A - B)\mathbf{x}_i = \mathbf{h} \tag{11.5}$$

one has

$$\mathbf{x}_{i+1} = \mathbf{x}_i - B^{-1}(A\mathbf{x}_i - \mathbf{h}) = (I - B^{-1}A)\mathbf{x}_i + B^{-1}\mathbf{h}. \tag{11.6}$$

In order for this to work one must be able to solve (11.5). Further, the closer $B$ is to $A$, the smaller the moduli of the eigenvalues of $I - B^{-1}A$ will be, and the more rapidly will (11.6) converge. Many of the common iterative methods can be illustrated with the following splitting.

$$A = D - E - F \tag{11.7}$$

where $D = \text{diag}(A)$, $-E$ is the lower triangular part of $A$ and $-F$ is the upper triangular part of $A$. Now, using the abbreviations

$$L \equiv D^{-1}E, \qquad U \equiv D^{-1}F, \qquad J \equiv L + U, \qquad H \equiv (I - L)^{-1}U \tag{11.8}$$

and assuming $a_{i,i} \neq 0 \ \forall i$, one has

$^a$The spectral radius of an operator is the least upper bound of its spectrum $\sigma$:

$$\rho(\Phi) \equiv \sup_{\lambda \in \sigma(\Phi)} |\lambda| \tag{11.3}$$

1