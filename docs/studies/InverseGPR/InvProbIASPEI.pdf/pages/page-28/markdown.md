data that, within experimental uncertainties, are models with high likelihood. In other words, we must accept that data alone cannot have a preferred model.

The posterior movie allows us to perform a proper resolution analysis that helps us to choose between different interpretations of a given data set. Using the movie we can answer complicated questions about the correlations between several model parameters. To answer such questions, we can view the posterior movie and try to discover structure that is well resolved by data. Such structure will appear as “persistent” in the posterior movie.

The ‘movie’ can be used to answer quite complicated questions. For instance, to answer the question ‘which is the probability that the Earth has this special characteristic, but not having this other special characteristic?’ we can just count the number $n$ of models (samples) satisfying the criterion, and the probability is $P = n/m$, where $m$ is the total number of samples.

Once this ‘movie’ is generated, it is, of course, possible to represent the 1D or 2D marginal probability densities for all or for some selected parameters: it is enough to concentrate one’s attention to those selected parameters in each of the samples generated. Those marginal probability densities may have some pathologies (like being multimodal, or having infinite dispersions), but those are the general characteristics of the joint probability density. Our numerical experience shows that these marginals are, quite often, ‘stable’ objects, in the sense that they can be accurately determined with only a small number of samples.

If the marginals are, essentially, beautiful bell-shaped distributions, then, one may proceed to just computing mean values and standard deviations (or median values and mean deviations), using each of the samples and the elementary statistical formulas.

Another, more traditional, way of investigating resolution is to calculate covariances and higher order moments. For this we need to evaluate integrals of the form

$$R _ { f } = \int _ { \mathcal { A } } d \mathbf { m } f ( \mathbf { m } ) \sigma _ { m } ( \mathbf { m } ) \tag { 8 5 }$$

where $f ( \mathbf { m } )$ is a given function of the model parameters and $\mathcal { A }$ is an event in the model space $\mathcal { M }$ containing the models we are interested in. For instance,

$$\mathcal { A } = \{ \mathbf { m } \mid \mathrm { a ~ g i v e n ~ r a n g e ~ o f ~ p a r a m e t e r s ~ i n ~ } \mathbf { m } \mathrm { ~ i s ~ c y c l i c } \} . \tag { 8 6 }$$

In the special case when $\mathcal { A } = \mathcal { M }$ is the entire model space, and $f ( \mathbf { m } ) = m _ { i }$ , the $R _ { f }$ in equation (85) equals the mean $\langle m _ { i } \rangle$ of the $i$ th model parameter $m _ { i }$ . If $f ( \mathbf { m } ) = ( m _ { i } - \langle m _ { i } \rangle ) ( m _ { j } - \langle m _ { j } \rangle )$ , $R _ { f }$ becomes the covariance between the $i$ th and $j$ th model parameters. Typically, in the general inverse problem we cannot evaluate the integral in (85) analytically because we have no analytical expression for $\sigma ( \mathbf { m } )$ . However, from the samples of the posterior movie $\mathbf { m } _ { 1 } , \ldots , \mathbf { m } _ { n }$ we can approximate $R _ { f }$ by the simple average

$$R _ { f } \approx \frac { 1 } { \mathrm { t o t a l ~ n u m b e r ~ o f ~ m o d e l s } } \sum _ { \{ i | \mathbf { m } _ { i } \in \mathcal { A } \} } f ( \mathbf { m } _ { i } ) \quad . \tag { 8 7 }$$

## 7 Solving Inverse Problems (III): Deterministic Methods

As we have seen, the solution of an inverse problem essentially consists of a probability distribution over the space of all possible models of the physical system under study. In general, this ‘model space’ is high-dimensional, and the only general way to explore it is by using the Monte Carlo methods developed in section 3.

If the probability distributions are ‘bell-shaped’ (i.e., if they look like a Gaussian or like a generalized Gaussian), then one may simplify the problem by calculating only the point around which the probability is maximum, with an approximate estimation of the variances and covariances. This is the problem addressed in this section. Among the many methods available to obtain the point at which a scalar function reaches its maximum value (relaxation methods, linear programming techniques, etc.) we limit our scope here to the methods using the gradient of the function, which we assume can be computed analytically or, at least, numerically. For more general methods, the reader may have a look at Fletcher, (1980, 1981), Powell (1981), Scales (1985), Tarantola (1987) or Scales et al. (1992).

28