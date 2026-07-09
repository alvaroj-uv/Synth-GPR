22

A Simple Inverse Problem that Isn't

$$f ( \mathbf { d } , m ) = \exp \left[ - { \frac { 1 } { 2 \sigma ^ { 2 } } } \sum _ { i = 1 } ^ { n } ( d _ { i } - m ) ^ { 2 } \right] \exp \left[ - { \frac { 1 } { 2 \beta ^ { 2 } } } ( m - \mu ) ^ { 2 } \right] ,$$

As we saw above, the first term on the right is the probability $f ( \mathbf { d } | m )$

Now the following result, known as Bayes theorem, is treated in detail later in book, but it is easy to derive from the definition of conditional probability, so we'll give it here too. In a joint probability distribution (i.e., a probability involving more than one random variable), the order of the random variables doesn't matter, so $f ( \mathbf { d } , m )$ is the same as $f ( m , \mathbf { d } )$. Using the definition of conditional probability twice we have

$$f ( \mathbf { d } , m ) = f ( \mathbf { d } | m ) f ( m )$$

and

$$f ( m , \mathbf { d } ) = f ( m | \mathbf { d } ) f ( d ) .$$

So, since $f ( \mathbf { d } , m ) = f ( m , \mathbf { d } )$, it is clear that

$$f ( \mathbf { d } | m ) f ( m ) = f ( m | \mathbf { d } ) f ( d )$$

from which it follows that

$$f ( m | \mathbf { d } ) = { \frac { f ( \mathbf { d } | m ) f ( m ) } { f ( \mathbf { d } ) } } . \quad { \mathrm { B a y e s ~ T h e o r e m } }$$

The term $f ( m | \mathbf { d } )$ is traditionally called the posterior (or a posteriori) probability since it is conditioned on the data. Later we will see another interpretation of Bayesian inversion in which $f ( m | \mathbf { d } )$ is not the posterior. But for now we'll assume that's what we're after, as in the kryptonite study where we called it $P _ { T | O }$.

We have everything we need to evaluate $f ( m | \mathbf { d } )$ except the marginal $f ( \mathbf { d } )$. So here are the steps in the calculation:

- compute $f ( \mathbf { d } )$ by integrating the joint distribution $f ( \mathbf { d } , m )$ with respect to $m$.
- form $f ( m | \mathbf { d } ) = { \frac { f ( \mathbf { d } | m ) f ( m ) } { f ( \mathbf { d } ) } }$.
- from $f ( m | \mathbf { d } )$ compute a "best" estimated value of $m$ by computing the mean of $f ( m | \mathbf { d } )$. We will discuss later why the posterior mean is what you want to have.

If you do this correctly you should get the following for the posterior mean:

$$\frac { n \bar { \mathbf { d } } / \sigma ^ { 2 } + \mu / \beta ^ { 2 } } { n / \sigma ^ { 2 } + 1 / \beta ^ { 2 } } ,$$

where $\bar { \mathbf { d } }$ is the mean of the data. By a similar calculation the posterior variance is

$$\frac { 1 } { n / \sigma ^ { 2 } + 1 / \beta ^ { 2 } } .$$

1