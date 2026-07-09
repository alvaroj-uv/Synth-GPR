2.3 What is an Answer?

15

## 2.3 What is an Answer?

Let's consider how we can use this information to refine the results of our experiment. Since we have an observation (namely 5.2) we'd like to know the probability that the *true* density has a particular value, say 5.4.

This is going to be a little tricky, and it's going to lead us into some unusual topics. We need to proceed with caution, and for that we need to sort out some notation.

### 2.3.1 Conditional Probabilities

Let $\rho_O$ be the value of density we *compute* after measuring the volume and mass of $K$; we will refer to $\rho_O$ as the *observed* density. Let $\rho_T$ be the actual value of $K$'s density; we will refer to $\rho_T$ as the *true* density.$^b$

Let $P_{O|T}(\rho_O, \rho_T)$ denote the *conditional* probability that we would measure $\rho_O$ if the true density was $\rho_T$. The quantity plotted above is $P_{O|T}(\rho_O, 5.2)$, the probability that we would *observe* $\rho_O$ if the true density was 5.2.

#### A few observations

First, keep in mind that in general we don't know what the true value of the density is. But if we nonetheless made repeated measurements we would still be mapping out $P_{O|T}$, only this time it would be $P_{O|T}(\rho_O, \rho_T)$. And secondly, you'll notice in the figure above that the true value of the density does not lie exactly at the peak of our distribution of observations. This must be the result of some kind of systematic error in the experiment. Perhaps the scale is biased; perhaps we've got a bad A/D converter; perhaps there was a steady breeze blowing in the window of the lab that day.

A distinction is usually made between *modeling* or *theoretical* errors and *random* errors. A good example of a modeling error, would be assuming that K were pure kryptonite, when in fact it is an alloy of kryptonite and titanium. So in this case our theory is slightly wrong. In fact, we normally think of random noise as being the small scale fluctuations which occur when a measurement is repeated. Unfortunately this distinction is hard to maintain in practice. Few experiments are truly repeatable. So when we try to repeat it, we're actually introducing small changes into the assumptions; as we repeatedly pick up K and put it back down on the scale, perhaps little bits fleck off, or some perspiration from our hands sticks to the sample, or we disturb the balance of the scale slightly by touching it. An even better example would be the positions of the gravimeters in the buried treasure example. We need to know these to do the modeling.

$^b$We will later consider whether this definition must be made more precise, but for now we will avoid the issue.

1