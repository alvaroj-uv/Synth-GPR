146

Bayesian versus Frequentist Methods of Inference

delta $p_i = \delta_{iq}$, where $q$ is the certain event, and $H(p) = 0$ (no uncertainty). If there are two equally likely outcomes, then $H(p) = -1/2 \log(1/2) - 1/2 \log(1/2) = \log 2$. Whereas if one of the events has a probability $1/10$ and one has probability $9/10$ then the entropy is $H(p) = -1/10 \log(1/10) - 9/10 \log(9/10) = \log 10 - .9 \log 9$, which is about half that in the equally likely case. For $M$ equally likely events $H(p) = \log M$. And in the limit that $M$ goes to infinity, then the uncertainty must too.

The usefulness of the definition 10.3 depends on the definition of the probability $p$. If the $p$ is a 1D distribution associated with the frequency of outcomes of the possible events, then $p$ is not affected by the correlation of the points. E.g., if we sample 10 points pseudo-randomly from a probability distribution with two equally likely outcomes 0 and 1, we might see something like the following

0010110110.

As luck would have it there are 5 0's and 5 1's. Now sort these outcomes in increasing order

0000011111.

There are still 5 0's and 5 1's but we certainly would not regard the latter experiment as representing the same degree of uncertainty as the former. Similarly, if we sample 1000 points independently from a Gaussian we'll see a nice bell-shaped curve. But the frequencies of the binned events are independent of their order. So, once again, sorting them into monotonic order will not change the entropy. of course, the dependence (correlation) among events is not being considered by an unidimensional probability distribution. Once multidimensional probabilities are used in definition (10.3), such correlation can be accounted for in entropy calculations.

Now, in inverse theory we are always comparing one state of information to another—what we know before relative to what we know after. So it is more appropriate to measure the relative information of one probability compared to another. Let us therefore revise the original definition of discrete entropy (Equation (10.3)), and introduce the concept of relative entropy. Thus,

$$H[p_i; q_i] = - \sum_i p_i \log \frac{p_i}{q_i}. \quad (10.4)$$

Here, $q_i$ is a discrete probability characterizing a reference state of information. The extension of Equation (10.4) to the continuous case is clean and straightforward:

$$\begin{aligned} H[p(x); q(x)] &= - \sum_i p(x_i) \Delta x_i \log \frac{p(x_i) \Delta x_i}{q(x_i) \Delta x_i} \\ &= - \sum_i p(x_i) \log \frac{p(x_i)}{q(x_i)} \Delta x_i \\ &= - \int_a^b p(x) \log \frac{p(x)}{q(x)} dx, \\ &\quad \text{as } \Delta x_i \to 0 \text{ (or } n \to \infty) \end{aligned} \quad (10.5)$$

1