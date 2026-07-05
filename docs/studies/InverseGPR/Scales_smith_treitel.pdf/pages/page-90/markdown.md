6.2 Random Variables

75

## 6.2.1 A Definition of Random

It turns out to be difficult to give a precise mathematical definition of randomness, so we won't try. (A brief perusal of randomness in Volume 2 of Knuth's great *The Art of Computer Programming* is edifying and frustrating in equal measures.) In any case it is undoubtedly more satisfying to think in terms of observations of physical experiments. Here is Parzen's (1960) definition, which is as good as any:

A random (or chance) phenomenon is an empirical phenomenon characterized by the property that its observation under a given set of circumstances does not always lead to the same observed outcomes (so that there is no deterministic regularity) but rather to different outcomes in such a way that there is statistical regularity. By this is meant that numbers exist between 0 and 1 that represent the relative frequency with which the different possible outcomes may be observed in a series of observations of independent occurrences of the phenomenon. ... A random event is one whose relative frequency of occurrence, in a very long sequence of observations of randomly selected situations in which the event may occur, approaches a stable limit value as the number of observations is increased to infinity; the limit value of the relative frequency is called the probability of the random event

It is precisely this lack of deterministic reproducibility that allows us to reduce random noise by averaging over many repetitions of the experiment.

## 6.2.2 Generating random numbers on a computer

Typically computers generate 'pseudo-random' numbers according to deterministic recursion relations called Congruential Random Number Generators, of the form

$$X(n + 1) = (aX(n) + c) \bmod m \tag{6.10}$$

where $a$ and $b$ are constants and $m$ is called the modulus. (E.g., $24 = 12 \pmod{12}$.) The value at the step $n$ is determined by the value and step $n - 1$.

The modulus defines the maximum period of the sequence; but the multiplier $a$ and the shift $b$ must be properly chosen in order that the sequence generate all possible integers between 0 and $m - 1$. For badly chosen values of these constants there will be hidden periodicities which show up when plotting groups of $k$ of these numbers as points in $k$-dimensional space.

To implement Equation 6.10 We need four magic numbers:

- $m$, the modulus $m > 0$

0