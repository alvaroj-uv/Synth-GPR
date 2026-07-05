# 1 Introduction

## 1.1 General Comments

Given a physical system, the 'forward' or 'direct' problem consists, by definition, in using a physical theory to predict the outcome of possible experiments. In classical physics this problem has a unique solution. For instance, given a seismic model of the whole Earth (elastic constants, attenuation, etc. at every point inside the Earth) and given a model of a seismic source, we can use current seismological theories to predict which seismograms should be observed at given locations at the Earth's surface.

The 'inverse problem' arises when we do not have a good model of the Earth, or a good model of the seismic source, but we have a set of seismograms, and we wish to use these observations to infer the internal Earth structure or a model of the source (typically we try to infer both).

There are many reasons that make the inverse problem underdetermined (non-unique). In the seismic example, two different Earth models may predict the same seismograms$^{1}$, the finite bandwidth of our data will never allow us to resolve very small features of the Earth model, and there are always experimental uncertainties that allow different models to be 'acceptable'.

The name 'inverse problem' is widely used. The authors of this text only like this name moderately, as we see the problem more as a problem of 'conjunction of states of information' (theoretical, experimental and prior information). In fact, the equations used below have a range of applicability well beyond 'inverse problems': they can be used, for instance, to predict the values of observations in a realistic situation where the parameters describing the Earth model are not 'given', but only known approximately.

We take here a probabilistic point of view. The axioms of probability theory apply to different situations. One is the traditional statistical analysis of random phenomena, another one is the description of (more or less) subjective states of information on a system. For instance, estimation of the uncertainties attached to any measurement usually involves both uses of probability theory: some uncertainties contributing to the total uncertainty are estimated using statistics, while some other uncertainties are estimated using informed scientific judgement about the quality of an instrument, about effects not explicitly taken into account, etc. The International Organization for Standardization (ISO) in *Guide to the Expression of Uncertainty in Measurement* (1993), recommends that the uncertainties evaluated by statistical methods are named 'type A' uncertainties, and those evaluated by other means (for instance, using Bayesian arguments) are named 'type B' uncertainties. It also recommends that former classifications, for instance into 'random' and 'systematic uncertainties', should be avoided. In the present text, we accept ISO's basic point of view, and extend it by downplaying the role assigned by ISO to the particular Gaussian model for uncertainties (see section 4.3) and by not assuming that the uncertainties are 'small'.

In fact, we like to think of an 'inverse' problem as merely a 'measurement'. A measurement that can be quite complex, but the basic principles and the basic equations to be used are the same for a relatively complex 'inverse problem' as for a relatively simple 'measurement'.

We do not normally use, in this text, the term 'random variable', as we assume that we have probability distributions over 'physical quantities'. This a small shift in terminology that we hope will not disorient the reader.

An important theme of this paper is *invariant formulation* of inverse problems, in the sense that solutions obtained using different, equivalent, sets of parameters should be consistent, i.e., probability densities obtained as the solution of an inverse problem, using two different set of parameters, should be related through the well known rule of multiplication by the Jacobian of the transformation.

This paper is organized as follows. After a brief historical review of inverse problem theory, with special emphasis on seismology, we give a small introduction to probability theory. In addition to being a tutorial, this introduction also aims at fixing a serious problem of classical probability, namely the non-invariant definition of conditional probability. This problem, which materializes in the so-called Borel paradox, has profound consequences for inverse problem theory.

A probabilistic formulation of inverse theory for general inverse problems (usually called 'nonlinear inverse problems') is not complete without the use of Monte Carlo methods. Section 3 is an introduction to the most versatile of these methods, the Metropolis sampler. Apart from being versatile, it also turns out to be the most natural method for implementing our probabilistic approach.

In sections 4, 5 and 6 time has come for applying probability theory and Monte Carlo methods to inverse problems. All the steps of a careful probabilistic formulations are described, including parameterization, prior information over the parameters, and experimental uncertainties. The hitherto overlooked problem of uncertain

$^{1}$For instance, we could fit our observations with a heterogeneous but isotropic Earth model or, alternatively, with an homogeneous but anisotropic Earth.

4