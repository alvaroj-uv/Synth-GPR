## M.5 The Transposed Operator

Let $\mathbf{G}$ a linear operator mapping an space $\mathcal{E}$ into an space $\mathcal{F}$ (we have in mind functional spaces, but the definition is general). We denote, as usual

$$\mathbf{G} : \mathcal{E} \to \mathcal{F} \tag{264}$$

If $\mathbf{e} \in \mathcal{E}$ and $\mathbf{f} \in \mathcal{F}$, then we write

$$\mathbf{f} = \mathbf{G} \mathbf{e} \tag{265}$$

Let $\widehat{\mathcal{E}}$ and $\widehat{\mathcal{F}}$ be the respective duals of $\mathcal{E}$ and $\mathcal{F}$, and denote $\langle \cdot, \cdot \rangle_{\mathcal{E}}$ and $\langle \cdot, \cdot \rangle_{\mathcal{F}}$ the respective duality products. A linear operator $\mathbf{H}$ mapping the dual of $\mathcal{F}$ into the dual of $\mathcal{E}$, is named the transpose of $\mathbf{G}$ if for any $\widehat{\mathbf{f}} \in \widehat{\mathcal{F}}$ and for any $\mathbf{e} \in \mathcal{E}$ we have $\langle \widehat{\mathbf{f}}, \mathbf{G} \mathbf{e} \rangle_{\mathcal{F}} = \langle \mathbf{H} \widehat{\mathbf{f}}, \mathbf{e} \rangle_{\mathcal{E}}$, and, in this case, we use the notation $\mathbf{H} = \mathbf{G}^T$. The whole definition then reads

$$\mathbf{G}^T : \widehat{\mathcal{F}} \to \widehat{\mathcal{E}} \tag{266}$$

$$\forall \mathbf{e} \in \mathcal{E} \quad ; \quad \forall \widehat{\mathbf{f}} \in \widehat{\mathcal{F}} \quad : \quad \langle \widehat{\mathbf{f}}, \mathbf{G} \mathbf{e} \rangle_{\mathcal{F}} = \langle \mathbf{G}^T \widehat{\mathbf{f}}, \mathbf{e} \rangle_{\mathcal{E}} \tag{267}$$

Example 29 The Transposed of a Matrix. Let us consider a discrete situation where

$$\mathbf{f} = \mathbf{G} \mathbf{e} \quad \iff \quad f_i = \sum_{\alpha} G_{i\alpha} e_{\alpha} \tag{268}$$

In this circumstance, the duality products in each space will read

$$\langle \widehat{\mathbf{f}}, \mathbf{f} \rangle_{\mathcal{F}} = \sum_i \widehat{f}_i f_i \quad ; \quad \langle \widehat{\mathbf{e}}, \mathbf{e} \rangle_{\mathcal{E}} = \sum_{\alpha} \widehat{e}_{\alpha} e_{\alpha} \tag{269}$$

The linear operator $\mathbf{H}$ is the transposed of $\mathbf{G}$ if for any $\widehat{\mathbf{f}}$ and for any $\mathbf{e}$ (equation 267),

$$\langle \widehat{\mathbf{f}}, \mathbf{G} \mathbf{e} \rangle_{\mathcal{F}} = \langle \mathbf{H} \widehat{\mathbf{f}}, \mathbf{e} \rangle_{\mathcal{E}} \tag{270}$$

i.e., if

$$\sum_i \widehat{f}_i (\mathbf{G} \mathbf{e})_i = \sum_{\alpha} (\mathbf{H} \widehat{\mathbf{f}})_{\alpha} e_{\alpha} \tag{271}$$

or, explicitly,

$$\sum_i \widehat{f}_i \left( \sum_{\alpha} G_{i\alpha} e_{\alpha} \right) = \sum_{\alpha} \left( \sum_i H_{\alpha i} \widehat{f}_i \right) e_{\alpha} \tag{272}$$

The condition can be written

$$\sum_i \sum_{\alpha} \widehat{f}_i G_{i\alpha} e_{\alpha} = \sum_i \sum_{\alpha} \widehat{f}_i H_{\alpha i} e_{\alpha} \tag{273}$$

and it is clear that this true for any $\widehat{\mathbf{f}}$ and for any $\mathbf{e}$ iff

$$H_{\alpha i} = G_{i\alpha} \tag{274}$$

i.e., if the matrix representing $\mathbf{H}$ is the transposed (in the elementary matricial sense) of the matrix representing $\mathbf{G}$:

$$\mathbf{H} = \mathbf{G}^T \tag{275}$$

This demonstrates that the abstract definition given above of the transpose of a linear operator is consistent with the matricial notion of transpose. [END OF EXAMPLE.]

Example 30 The Transposed of the Derivative Operator. Let us consider a situation where

$$\mathbf{v} = \mathbf{D} \mathbf{x} \quad \iff \quad v(t) = \frac{dx}{dt}(t) \tag{276}$$

i.e., where the linear operator $\mathbf{D}$ is the derivative operator. In this circumstance, the duality products in each space will typically read

$$\langle \widehat{\mathbf{v}}, \mathbf{v} \rangle_{\mathcal{V}} = \int_{t_1}^{t_2} dt \, \widehat{v}(t) \, v(t) \quad ; \quad \langle \widehat{\mathbf{x}}, \mathbf{x} \rangle_{\mathcal{X}} = \int_{t_1}^{t_2} dt \, \widehat{x}(t) \, x(t) \tag{277}$$

69