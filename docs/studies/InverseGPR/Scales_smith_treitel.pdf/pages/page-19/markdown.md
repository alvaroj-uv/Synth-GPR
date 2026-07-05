4

What Is Inverse Theory

- generate all possible models by trying all combinations of sand and gold densities in our little rectangles, and
- compare the predicted gravity values to the observed gravity values and tell us which models, if any, agreed well with the observations.

**Model space and data space** In the beach example a *model* consists of 45 parameters, namely the content (sand or gold) of each block. We could represent this mathematically as a 45-tuple containing the densities of each block. For example, $(2.2, 2.2, 2.2, 19.3, 2, 2 \dots)$ is an example of a model. Moreover, since we're only allowing those densities to be that of gold and sand, we might as well consider the 45-tuple as consisting of zeros and ones. Therefore all possible models of the subsurface are elements of the set of 45-tuples whose elements are 0 or 1. There are $2^{45}$ such models. We call this the *model space* for our problem. On the other hand, the *data space* consists of all possible data predictions. For this example there are 5 gravity measurements, so the data space consists of all possible 5-tuples whose elements vary continuously between 0 and some upper limit; i.e., a subset of $\mathbf{R}^5$, the 5-dimensional Euclidean space.

## 1.1 Too many models

The first problem is that there are forty-five little rectangles under our model beach and so there are

$$2^{45} \approx 3 \times 10^{13} \tag{1.2}$$

models to inspect. If we can evaluate a thousand models per second, it will still take us about 1100 years to complete the search. It is almost always impossible to examine more than the tiniest fraction of the possible answers (models) in any interesting inverse calculation.

## 1.2 No unique answer

We have forty-five knobs to play with in our model (one for each little rectangle) and only five observations to match. It is very likely that there will be more than one best-fitting model. This likelihood increases to near certainty once we admit the possibility of noise in the observations. There are almost always many possible answers to an inverse problem which cannot be distinguished by the available observations.

1