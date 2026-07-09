6.11 Other Common Analytic Distributions

103

## Exercises

1. Show that for any two events $A$ and $B$

$$P(AB^c) = P(A) - P(BA) \tag{6.65}$$

2. Show that for any event $A$, $P(A^c) = 1 - P(A)$.
3. Show that $1/x$ is a measure, but not a probability density.
4. Show that the truth of the following formula for any two sets $A$ and $B$

$$P(A \cup B) = P(A) + P(B) - P(A \cup B) \tag{6.66}$$

follows from the fact that for independent sets $A'$ and $B'$

$$P(A' \cup B') = P(A') + P(B'). \tag{6.67}$$

Hint. The union of any two sets $A$ and $B$ can be written as the sum of three independent sets of elements: the elements in $A$ but not in $B$; the elements in $B$ but not in $A$; and the elements in both $A$ and $B$.

5. Show that all the central moments of the normal distribution beyond the second are either zero or can be written in terms of the mean and variance.
6. You have made $n$ different measurements of the mass of an object. You want to find the mass that best "fits" the data. Show that the mass estimator which minimizes the sum of squared errors is given by the mean of the data, while the mass estimator which minimizes the sum of the absolute values of the errors is given by the median of the data. Feel free to assume that you have an odd number of data.
7. Show that Equation 6.47 is normalized.
8. Take the $n$ data you recorded above and put them in numerical order: $x_1 \le x_2 \le \dots \le x_n$. Compute the sensitivity of the two different estimators, average and median, to perturbations in $x_n$.

What does this say about how least squares and least absolute values treat "outliers" in the data?

9. Find the normalization constant that will make

$$p(x) = e^{-(x^2 - x_0 x + x_0^2)} \tag{6.68}$$

a probability density on the real line. $x_0$ is a constant.

What are the mean and variance?

0