16

A Simple Inverse Problem that Isn't

But every time we pick up the gravimeter and put it back to repeat the observation, we misposition it slightly. Do we regard these mispositionings as noise or do we regard them as actual model parameters that we wish to infer? Do we regard the wind blowing near the trees during our seismic experiment as noise, or could we actually infer the speed of the wind from the seismic data? In fact, recent work in meteorology has shown how microseismic noise (caused by waves at sea) can be used to make inferences about climate.

As far as we can tell, the distinction between random errors and theoretical errors is somewhat arbitrary and up to us to decide on a case by case. What it boils down to are: what features are we really interested in? Noise consists of those features of the data we have no interest in explaining. For more details see the commentary: *What is Noise?* [SS98].

### 2.3.2 What We're Really (Really) After

What we **want** is $P_{T|O}(\rho_T, \rho_O)$, the probability that $\rho_T$ has a particular value given that we have the observed value $\rho_O$. Because $P_{T|O}$ and $P_{O|T}$ appear to be relations between the same quantities, and because they look symmetric, it's tempting to make the connection

$$P_{T|O}(\rho_T, \rho_O) = P_{O|T}(\rho_O, \rho_T) \ ?$$

but unfortunately it's not true.

What is the correct expression for $P_{T|O}$? More important, how can we think our way through issues like this?

We'll start with the last question. One fruitful way to think about these issues is in terms of a simple, repeated experiment. Consider the quantity we already have: $P_{O|T}$, which we plotted earlier. It's easy to imagine the process of repeatedly weighing a mass and recording the results. If we did this, we could directly construct tables of $P_{O|T}$.

### 2.3.3 A (Short) Tale of Two Experiments

Now consider repeatedly estimating density. There are two ways we might think of this. In one experiment we repeatedly estimate the density of a *particular, given* chunk of kryptonite. In the second experiment we repeatedly draw a chunk of kryptonite from some source and estimate its density.

These experiments appear to be quite different. The first experiment sounds just like the measurements we (or someone) made to estimate errors in the scale, *except* in this case we don't know the object's mass to begin with. The second experiment has an

1