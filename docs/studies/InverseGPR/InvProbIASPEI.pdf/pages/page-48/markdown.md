distributions will not be normalizable at all ( $P(\mathcal{D}) = \infty$ ). We can only then compute the relative probabilities of subdomains.

These axioms apply to probability distributions over discrete or continuous spaces. Below, we will consider probability distributions over spaces of physical parameters, that are continuous spaces. Then, a probability distribution is represented by a probability density.

In the next section, given a space $\mathcal{D}$, we will consider different probability distributions $P, Q \dots$. Each probability distribution will represent a particular state of information over $\mathcal{D}$. In what follows, we will use as synonymous the terms “probability distribution” and “state of information”.

## G.2 Inference Space

We will now give a structure to the space of all the probability distributions over a given space, by introducing two operations, the OR and the AND operation. This contrasts with the basic operations introduced in deductive logic, where the negation (“NOT”), nonexistent here, plays a central role. In what follows, the OR and the AND operation will be denoted, symbolically, by $\vee$ and $\wedge$. They are assumed to satisfy the set of axioms here below.

The first axiom states that if an event $\mathcal{A}$ is possible for $(P \text{ OR } Q)$, then the event is either possible for $P$ or possible for $Q$ (which is consistent with the usual logical sense for the “or”): For any subset $\mathcal{A}$, and for any two probability distributions $P$ and $Q$, the OR operation satisfies

$$(P \vee Q)(\mathcal{A}) \neq 0 \quad \implies \quad P(\mathcal{A}) \neq 0 \quad \text{or} \quad Q(\mathcal{A}) \neq 0,$$

the word “or” having here its ordinary logical sense.

The second axiom states that if an event $\mathcal{A}$ is possible for $(P \text{ AND } Q)$, then the event is possible for both $P$ and $Q$ (which is consistent with the usual logical sense for the “and”): For any subset $\mathcal{A}$, and for any two probability distributions $P$ and $Q$, the AND operation satisfies

$$(P \wedge Q)(\mathcal{A}) \neq 0 \quad \implies \quad P(\mathcal{A}) \neq 0 \quad \text{and} \quad Q(\mathcal{A}) \neq 0,$$

the word “and” having here its ordinary logical sense.

The third axiom ensures the existence of a neutral element, that will be interpreted below as the probability distribution carrying no information at all: There is a neutral element, $M$ for the AND operation, i.e., it exists a $M$ such that for any probability distribution $P$ and for any subset $\mathcal{A}$,

$$(M \wedge P)(\mathcal{A}) = (P \wedge M)(\mathcal{A}) = P(\mathcal{A}).$$

The fourth axiom imposes that the OR and the AND operations are commutative and associative, and, by analogy with the algebra of propositions of ordinary logic, have a distributivity property: the AND operation is distributive with respect to the OR operation.

The structure obtained when furnishing the space of all probability distributions (over a given space $\mathcal{D}$) with two operations OR and AND, satisfying the given axioms constitutes what we propose to call an inference space.

These axioms do not define uniquely the operations. Let $\mu(\mathbf{x})$ be the particular probability density representing $M$, the neutral element for the AND operation, and let $p(\mathbf{x}), q(\mathbf{x}) \dots$ be the probability densities representing the probability distributions $P, Q \dots$. Using the notations $(p \vee q)(\mathbf{x})$ and $(p \wedge q)(\mathbf{x})$ for the probability densities representing the probability distributions $P \vee Q$ and $P \wedge Q$ respectively, one realization of the axioms (the one we will retain) is given by

$$(p \vee q)(\mathbf{x}) = p(\mathbf{x}) + q(\mathbf{x}) \quad ; \quad (p \wedge q)(\mathbf{x}) = \frac{p(\mathbf{x})q(\mathbf{x})}{\mu(\mathbf{x})}, \tag{184}$$

where one should remember that we do not impose to our probability distributions to be normalized.

The structure of an inference space, as defined, contains other useful solutions. For instance, the theory of fuzzy sets (Kandel, 1986) uses positive functions $p(\mathbf{x}), q(\mathbf{x}) \dots$ quite similar to probability densities, but having a different interpretation: the are normed by the condition that their maximum value equals one, and are interpreted as the “grades of membership” of a point $\mathbf{x}$ to the “fuzzy sets” $P, Q \dots$. The operations OR and AND correspond then respectively to the union and intersection of fuzzy sets, and to the following realization of our axioms:

$$(p \vee q)(\mathbf{x}) = \max(p(\mathbf{x}), q(\mathbf{x})) \quad ; \quad (p \wedge q)(\mathbf{x}) = \min(p(\mathbf{x}), q(\mathbf{x})), \tag{185}$$

where the neutral element for the AND operation (intersection of fuzzy sets) is simply the function $\mu(\mathbf{x}) = 1$.

48