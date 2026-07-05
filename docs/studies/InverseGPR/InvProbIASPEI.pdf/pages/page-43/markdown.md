Assume that a measurement of the coordinates  \( (t,x) \)  of an event (like a blinking of the particle), produces the probability density  \( h(t,x) \) . If we are told that the particle is necessarily on the trajectory given by equation 150, and we are not given any other information, we can modify  \( h(t,x) \)  by the condition  \( x=x(t) \) , i.e., we can define the conditional probability density  \( h(t|x=x(t)) \) . To do this consistently, we have to use some distance over our working space (here, the space-time), in order to define the conditional probability density, from the more general notion of conditional probability, using a notion of uniform convergence.

This is what we have done above. Adapting to this special case equation 17 gives

\[
h _ {t} (t) = h (t | x = x (t)) = k h (t, x (t)) \left. \frac {\sqrt {g _ {t t} + g _ {x x} \dot {x} ^ {2}}}{\sqrt {g _ {t t}}} \right| _ {x = x (t)}, \tag {151}
\]

i.e. (redefining the constant),

\[
h _ {t} (t) = k h (t, x (t)) \sqrt {g _ {t t} + g _ {x x} v (t) ^ {2}}. \tag {152}
\]

Using the results above this gives

\[
h _ {t} (t) = k h (t, x (t)) \left(1 - \frac {a ^ {2} t ^ {2}}{a ^ {2} t ^ {2} + c ^ {2}}\right), \tag {153}
\]

and this solves our problem. While for small t this gives

\[
h _ {t} (t) = k h (t, x (t)) \quad , \tag {154}
\]

for large \(t\) we obtain, instead,

\[
h _ {t} (t) = k \frac {1}{t ^ {2}} h (t, x (t)) \quad . \tag {155}
\]

Reversing the use we have made of the variables \( t \) and \( x \), we could have calculated \( h_x(x) \), rather than \( h_t(t) \). But the invariance property mentioned in section 2.4 warrants us that these two probability densities are related through the Jacobian rule, i.e., we shall have

\[
h _ {t} (t) = \frac {d x}{d t} h _ {x} (x) = \dot {x} (t) h _ {x} (x). \tag {156}
\]

### C.3 Uncertain Analytical Theory (Conjunction of Probabilities)

We prepare particles that have to follow a free fall. It is assumed that the trajectory of the particles is, approximately,

\[
x (t) \approx x _ {0} + v _ {0} t + \frac {1}{2} g t ^ {2}, \tag {157}
\]

with some uncertainties, principally due to uncertainties in the values  \( x_{0} \)  and  \( v_{0} \) . These uncertainties are assumed to dominate all other sources of uncertainty (air friction, variations in the gravity field, etc.). The value of g is assumed to be known with high accuracy.

Of course, equation 157 can, equivalently, be written

\[
t (x) \approx \pm \frac {1}{g} \sqrt {v _ {0} ^ {2} + 2 g (x - x _ {0})} - \frac {v _ {0}}{g}, \tag {158}
\]

The probability density for  \( x_{0} \)  is  \( Q(x_{0}) \) , and that of  \( v_{0} \)  is  \( R(v_{0}) \) .

Case \(x = x(t)\)

The particles are prepared so that they desintegrate (or that they blink) at some time instant \( t \) chosen homogeneously at random inside some (large) time interval.

Using equation 157 it is possible to compute \( f(x|t) \), the conditional probability density for the particle to be at \( x \) when it desintegrates at \( t \). For instance, if the probability density for \( v(t_0) \) is a Gaussian centered at \( v_0 \) with standard deviation \( \sigma_v \) and if the probability density for \( x(t_0) \) is another Gaussian centered at \( x_0 \) with standard deviation \( \sigma_x \), we get

\[
f (x \mid t) = k \frac {1}{\sqrt {\sigma_ {x} ^ {2} + \sigma_ {v} ^ {2} t ^ {2}}} \exp \left(- \frac {1}{2} \frac {\left(x - \left(x _ {0} + v _ {0} t + \frac {1}{2} g t ^ {2}\right)\right) ^ {2}}{\sigma_ {x} ^ {2} + \sigma_ {v} ^ {2} t ^ {2}}\right) \tag {159}
\]

43