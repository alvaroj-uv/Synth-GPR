6.1 Sets

73

The set with no elements in it is called the *empty set* and is denoted $\emptyset$. Its probability is always 0

$$P(\emptyset) = 0. \tag{6.2}$$

Since, by definition, the sample space contains all possible outcomes, its probability must always be 1

$$P(\Omega) = 1. \tag{6.3}$$

The other thing we need to be able to do is combine probabilities:$^a$

$$P(A \cup B) = P(A) + P(B) - P(AB). \tag{6.4}$$

$P(AB)$ is the probability of the event $A$ intersect $B$, which means the event $A$ and $B$. In particular, if the two events are *exclusive*, i.e., if $AB = 0$ then

$$P(A \cup B) = P(A) + P(B). \tag{6.5}$$

This result extends to an arbitrary number of exclusive events $A_i$

$$P(A_1 \cup A_2 \cup \dots \cup A_n) = \sum_{i=1}^n P(A_i). \tag{6.6}$$

This property is called *additivity*. Events $A$ and $B$ are said to be *independent* if $P(AB) = P(A)P(B)$.

### Example 2

Toss the fair die twice. The sample space for this experiment consists of

$$\{\{1, 1\}, \{1, 2\}, \dots \{6, 5\}, \{6, 6\}\}. \tag{6.7}$$

Let $A$ be the event that the first number is a 1. Let $B$ be the event that the second number is a 2. The probability of both $A$ and $B$ occurring is the probability of the intersection of these two sets. So

$$P(AB) = \frac{N(AB)}{N(\Omega)} = \frac{1}{36} \tag{6.8}$$

### Example 3

A certain roulette wheel has 4 numbers on it: 1, 2, 3, and 4. The even numbers are white and the odd numbers are black. The sample space associated with spinning the wheel twice is

$$\{\{1, 1\}, \{1, 2\}, \{1, 3\}, \{1, 4\}\}$$

$^a$That $P(A \cup B) = P(A) + P(B)$ for exclusive events is a fundamental axiom of probability.

0