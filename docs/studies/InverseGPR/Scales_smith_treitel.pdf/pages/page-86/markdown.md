# Chapter 6

## A Summary of Probability and Statistics

Collected here are a few basic definitions and ideas. For more details consult a textbook on probability or mathematical statistics, for instance [Sin91], [Par60], and [Bru65]. We begin with a discussion of discrete probabilities, which involves counting sets. Then we introduce the notion of a numerical valued random variable and random physical phenomena. The main goal of this chapter is to develop the tools we need to characterize the uncertainties in both geophysical data sets and in the description of Earth models—at least when we have our Bayesian hats on. So the chapter culminates with a discussion of various descriptive statistics numerical data (means, variances, etc). Most of the problems that we face in geophysics involves spatially or temporally varying random phenomena, also known as stochastic processes; e.g., velocity as a function of space. For everything we will do in this course, however, it suffices to consider only finite dimensional vector-valued random variables, such as we would measure by sampling a random function at discrete times or spatial locations.

### 6.1 Sets

Probability is fundamentally about measuring sets. The sets can be finite, as in the possible outcomes of a toss of a coin, or infinite, as in the possible values of a measured P-wave impedance. The space of all possible outcomes of a given experiment is called the *sample space*. We will usually denote the sample space by $\Omega$. If the problem is simple enough that we can enumerate all possible outcomes, then assigning probabilities is easy.

0