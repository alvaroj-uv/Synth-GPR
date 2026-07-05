# Chapter 8

## Examples: Absorption and Travel Time Tomography

Before we go any further, it will be useful to motivate all the work we're doing with an example that is sufficiently simple that we can do all the calculations without too much stress. We will consider and example of 'tomography'. The word tomography comes from the Greek *tomos* meaning section or slice. The idea is to use observed values of some quantity which is related via a line integral to the physical parameter we wish to infer. Here we will study seismic travel time tomography, is a widely used method of imaging the earth's interior. Mathematically this problem is identical to other types of tomography such as used in X-ray CAT scans.

### 8.1 The X-ray Absorber

Most of the examples shown here are based on an idealized two-dimensional x-ray absorption experiment. This experiment consists of the measurement of the power loss of x-ray beams passing through a domain filled with an x-ray absorber.

We suppose that the absorber is confined to the unit square,

$$(x, y) \in [0, 1] \otimes [0, 1];$$

we will represent this domain by $\mathcal{D}_X$. We also suppose that the sensing beam follows a perfectly straight path from transmitter to receiver and that the transmitter and receiver are located on the perimeter of the unit square. The geometry of a single x-ray absorption measurement looks like Figure 8.1.

1