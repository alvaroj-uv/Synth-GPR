34

A Little Linear Algebra

Now, the physical vectors have a life independent of the particular 3-tuple we use to represent them. We will get a different 3-tuple depending on whether we use cartesian or spherical coordinates, for example; but the force vector itself is independent of these considerations. On the other hand, our use of vector spaces is purely abstract. There is no physical seismogram vector; all we have is the n-tuple sampled from the recorded seismic trace.

Further, the mathematical definition of a vector space is sufficiently general to incorporate objects that you might not consider as vectors at first glance—such as functions and matrices. The definition of such a space actually requires two sets of objects: a set of vectors $V$ and a one of scalars $F$. For our purposes the scalars will always be either the real numbers $\mathbf{R}$ or the complex numbers $\mathcal{C}$. For this definition we need the idea of a Cartesian product of two sets.

**Definition 1 Cartesian product** *The Cartesian product $A \times B$ of two sets $A$ and $B$ is the set of all ordered pairs $(a, b)$ where $a \in A$ and $b \in B$.*

**Definition 2 Linear Vector Space** *A linear vector space over a set $F$ of scalars is a set of elements $V$ together with a function called addition from $V \times V$ into $V$ and a function called scalar multiplication from $F \times V$ into $V$ satisfying the following conditions for all $x, y, z \in V$ and all $\alpha, \beta \in F$:*

$$V1: (x + y) + z = x + (y + z)$$

$$V2: x + y = y + x$$

$V3$: *There is an element $0$ in $V$ such that $x + 0 = x$ for all $x \in V$.*

$V4$: *For each $x \in V$ there is an element $-x \in V$ such that $x + (-x) = 0$.*

$$V5: \alpha(x + y) = \alpha x + \alpha y$$

$$V6: (\alpha + \beta)x = \alpha x + \beta x$$

$$V7: \alpha(\beta x) = (\alpha\beta)x$$

$$V8: 1 \cdot x = x$$

The simplest example of a vector space is $\mathbf{R}^n$, whose vectors are n-tuples of real numbers. Addition and scalar multiplication are defined component-wise:

$$(x_1, x_2, \cdots, x_n) + (y_1, y_2, \cdots, y_n) = (x_1 + y_1, x_2 + y_2, \cdots, x_n + y_n) \tag{4.3}$$

and

$$\alpha(x_1, x_2, \cdots, x_n) = (\alpha x_1, \alpha x_2, \cdots, \alpha x_n). \tag{4.4}$$

0