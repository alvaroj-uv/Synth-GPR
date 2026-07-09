74

A Summary of Probability and Statistics

$$\{\{2, 1\}, \{2, 2\}, \{2, 3\}, \{2, 4\}\}$$

$$\{\{3, 1\}, \{3, 2\}, \{3, 3\}, \{3, 4\}\}$$

$$\{\{4, 1\}, \{4, 2\}, \{4, 3\}, \{4, 4\}\}$$

Now, in terms of black and white, the different outcomes are

$$\{\{\text{black, black}\}, \{\text{black, white}\}, \{\text{black, black}\}, \{\text{black, white}\}\}$$

$$\{\{\text{white, black}\}, \{\text{white, white}\}, \{\text{white, black}\}, \{\text{white, white}\}\}$$

$$\{\{\text{black, black}\}, \{\text{black, white}\}, \{\text{black, black}\}, \{\text{black, white}\}\}$$

$$\{\{\text{white, black}\}, \{\text{white, white}\}, \{\text{white, black}\}, \{\text{white, white}\}\}$$

Let $A$ be the event that the first number is white, and $B$ the event that the second number is white. Then $N(A) = 8$ and $N(B) = 8$. So $P(A) = 8/16$ and $P(B) = 8/16$. The event that both numbers are white is the intersection of $A$ and $B$ and $P(AB) = 4/16$.

Suppose we want to know the probability of the second number being white given that the first number is white. We denote this *conditional probability* by $P(B|A)$. The only way for this conditional event to be true if both $B$ and $A$ are true. Therefore, $P(B|A)$ is going to have to be equal to $N(AB)$ divided by something. That something cannot be $N(\Omega)$ since only half of these have a white number in the first slot, so we must divide by $N(A)$ since these are the only events for which the event $B$ given $A$ could possibly be true. Therefore we have

$$P(B|A) = \frac{N(AB)}{N(A)} = \frac{P(AB)}{P(A)} \tag{6.9}$$

assuming $P(A)$ is not zero, of course. The latter equality holds because we can divide the top and the bottom of $\frac{N(AB)}{N(A)}$ by $N(\Omega)$.

As we saw above, for independent events $P(AB) = P(A)P(B)$. Therefore it follows that for independent events $P(B|A) = P(B)$.

## 6.2 Random Variables

If we use a variable to denote the outcome of a random trial, then we call this a *random variable*. For example, let $d$ denote the outcome of a flip of a fair coin. Then $d$ is a random variable with two possible values, heads and tails. A given outcome of a random trial is called a *realization*. Thus if we flip the coin 100 times, the result is 100 realizations of the random variable $d$. Later in this book we will find it necessary to invent a new notation so as to distinguish a realization of a random process from the random process itself, the later being usually unknown.

0