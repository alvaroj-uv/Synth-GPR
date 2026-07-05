6.4 Probability Functions and Densities

81

always positive, 2) it's zero on the null set (the impossible event), 3) it's one on the whole sample space (the certain event), 4) and it satisfies the additivity property for an arbitrary collection of mutually independent events $A_i$:

$$P(A_1 \cup A_2 \cup \dots \cup A_n) = P(A_1) + P(A_2) + \dots P(A_n). \tag{6.21}$$

These defining properties of a probability function are already well known to us in other contexts. For example, consider a function $M$ which measures the length of a subinterval of the unit interval $I = [0, 1]$. If $0 \le x_1 \le x_2 \le 1$, then $A = [x_1, x_2]$ is a subinterval of $I$. Then $M(A) = x_2 - x_1$ is always positive unless the interval is empty, $x_1 = x_2$, in which case it's zero. If $A = I$, then $M(A) = 1$. And if two intervals are disjoint, the measure (length) of the union of the two intervals is the sum of the length of the individual intervals. So it looks like a probability function is just a special kind of measure, a measure normalized to one.

Now let's get fancy and write the length of an interval as the integral of some function over the interval.

$$M(A) = \int_A \mu(x) \, dx \equiv \int_{x_1}^{x_2} \mu(x) \, dx. \tag{6.22}$$

In this simple example using cartesian coordinates, the *density* function $\mu$ is equal to a constant one. But it suggests that more generally we can define a probability density such that the probability of a given set is the integral of the probability density over that set

$$P(A) = \int_A \rho(x) \, dx \tag{6.23}$$

or, more generally,

$$P(A) = \int_A \rho(x_1, x_2, \dots, x_n) \, dx_1 \, dx_2 \dots dx_n. \tag{6.24}$$

Of course there is no reason to restrict ourselves to cartesian coordinates. The set itself is independent of the coordinates used and we can transform from one coordinate system to another via the usual rules for a change of variables in definite integrals.

Yet another representation of the probability law of a numerical valued random phenomenon is in terms of the *distribution function* $F(x)$. $F(x)$ is defined as the probability that the observed value of the random variable will be less than $x$:

$$F(x) = P(X < x) = \int_{-\infty}^x \rho(x') \, dx'. \tag{6.25}$$

Clearly, $F$ must go to zero as $x$ goes to $-\infty$ and it must go to one as $x$ goes to $+\infty$. Further, $F'(x) = \rho(x)$.

### Example

$$\int_{-\infty}^\infty e^{-x^2} \, dx = \sqrt{\pi}. \tag{6.26}$$

0