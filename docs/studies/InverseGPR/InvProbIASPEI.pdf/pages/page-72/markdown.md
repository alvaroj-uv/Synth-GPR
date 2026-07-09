is

$$f(t) = \int dt \, G(t, x) \, e(t) \, , \tag{297}$$

where $G(t, x)$ is an ordinary function$^{38}$, then, it is said that $\mathbf{G}$ is an integral operator, and that the function $G(t, x)$ is its kernel. [END OF EXAMPLE.]

The transpose of $\mathbf{G}$ will map an element $\widehat{\mathbf{f}}$ into an element $\widehat{\mathbf{e}}$, these two elements belonging to the respective duals of the spaces where the elements $\mathbf{e}$ and $\mathbf{f}$ mentioned in equation 296 belong. An equation like

$$\widehat{\mathbf{e}} = \mathbf{G}^T \widehat{\mathbf{f}} \tag{298}$$

will correspond, explicitly, to

$$\widehat{e}(t) = \int dx \, G^T(x, t) \, \widehat{f}(t) \, . \tag{299}$$

The reader may easily verify that the definition of transpose operator imposes that the kernel of $\mathbf{G}^T$ is related to the kernel of $\mathbf{G}$ by the simple expression

$$G^T(x, t) = G(t, x) \, . \tag{300}$$

We see that the kernels of $\mathbf{G}$ and of $\mathbf{G}^T$ are, in fact, identical, via a simple 'transposition' of the variables.

### M.6 The Adjoint Operator

Let $\mathbf{G}$ be a linear operator mapping an space $\mathcal{E}$ into an space $\mathcal{F}$:

$$\mathbf{G} : \mathcal{E} \to \mathcal{F} \, . \tag{301}$$

If $\mathbf{e} \in \mathcal{E}$ and $\mathbf{f} \in \mathcal{F}$, then we write

$$\mathbf{f} = \mathbf{G} \mathbf{e} \, . \tag{302}$$

Assume that both, $\mathcal{E}$ and $\mathcal{F}$ are furnished with an scalar product each (see section M.4), that we denote, respectively, as $(\mathbf{e}_1, \mathbf{e}_2)_\mathcal{E}$ and $(\mathbf{f}_1, \mathbf{f}_2)_\mathcal{F}$.

A linear operator $\mathbf{H}$ mapping $\mathcal{F}$ into $\mathcal{E}$, is named the adjoint of $\mathbf{G}$ if for any $\mathbf{f} \in \mathcal{F}$ and for any $\mathbf{e} \in \mathcal{E}$ we have $(\mathbf{f}, \mathbf{G} \mathbf{e})_{\mathcal{F}} = (\mathbf{H} \mathbf{f}, \mathbf{e})_{\mathcal{E}}$, and, in this case, we use the notation $\mathbf{H} = \mathbf{G}^*$. The whole definition then reads

$$\mathbf{G}^* : \mathcal{F} \to \mathcal{E} \tag{303}$$

$$\forall \mathbf{e} \in \mathcal{E} \quad ; \quad \forall \mathbf{f} \in \mathcal{F} \quad : \quad (\mathbf{f}, \mathbf{G} \mathbf{e})_{\mathcal{F}} = (\mathbf{G}^* \mathbf{f}, \mathbf{e})_{\mathcal{E}} \, . \tag{304}$$

Let $\widehat{\mathcal{E}}$ and $\widehat{\mathcal{F}}$ be the respective duals of $\mathcal{E}$ and $\mathcal{F}$, and denote $\langle \cdot, \cdot \rangle_\mathcal{E}$ and $\langle \cdot, \cdot \rangle_\mathcal{F}$ the respective duality products. We have seen above that a scalar product is defined through a symmetric, positive operator mapping a space into its dual. Then, as $\mathcal{E}$ and $\mathcal{F}$ are assumed to have a scalar product defined, there are two 'covariance' operators $\mathbf{C}_\mathcal{E}$ and $\mathbf{C}_\mathcal{F}$ such that the respective scalar products are given by

$$(\mathbf{e}_1, \mathbf{e}_2)_\mathcal{E} = \langle \mathbf{C}_\mathcal{E}^{-1} \mathbf{e}_2, \mathbf{e}_1 \rangle_\mathcal{E}$$

$$(\mathbf{f}_1, \mathbf{f}_2)_\mathcal{F} = \langle \mathbf{C}_\mathcal{F}^{-1} \mathbf{f}_2, \mathbf{f}_1 \rangle_\mathcal{F} \, . \tag{305}$$

Then, equation 304 writes $\langle \mathbf{C}_\mathcal{F}^{-1} \mathbf{f}, \mathbf{G} \mathbf{e} \rangle_\mathcal{F} = \langle \mathbf{C}_\mathcal{E}^{-1} \mathbf{G}^* \mathbf{f}, \mathbf{e} \rangle_\mathcal{E}$, or, denoting $\widehat{\mathbf{f}} = \mathbf{C}_\mathcal{F}^{-1} \mathbf{f}$,

$$\langle \widehat{\mathbf{f}}, \mathbf{G} \mathbf{e} \rangle_\mathcal{F} = \langle \mathbf{C}_\mathcal{E}^{-1} \mathbf{G}^* \mathbf{C}_\mathcal{F} \widehat{\mathbf{f}}, \mathbf{e} \rangle_\mathcal{E} \, . \tag{306}$$

The comparison with equation 304 defining the transposed operator gives the relation between adjoint and transpose, $\mathbf{G}^T = \mathbf{C}_\mathcal{E}^{-1} \mathbf{G}^* \mathbf{C}_\mathcal{F}$, that can be written, equivalently, as

$$\mathbf{G}^* = \mathbf{C}_\mathcal{E} \mathbf{G}^T \mathbf{C}_\mathcal{F}^{-1} \, . \tag{307}$$

The transposed operator is an elementary operator. Its definition only requires the existence of the dual of the considered spaces, that is automatic. If, for instance, a linear operator $\mathbf{G}$ has the kernel $G(u, v)$, the transposed operator $\mathbf{G}^T$ will have the kernel $G^T(v, u) = G(u, v)$.

The adjoint operator is not an elementary operator. Its definition requires the existence of scalar products in the working spaces, that are necessarily defoned through symmetric, positive definite operators. This means that (excepted degenerated cases) the adjoint operator is a complex object, depending on three elementary objects: this is how equation 307 is to be interpreted.

$^{38}$If $G(t, x)$ is a distribution (like the derivative of a Dirac's delta) then equation 296 may be a disguised expression for a differential operator.

72