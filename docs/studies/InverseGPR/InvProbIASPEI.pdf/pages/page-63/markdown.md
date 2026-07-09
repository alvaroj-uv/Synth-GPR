The velocity model is simply defined, in this toy example, by giving its constant value (5 km/s):

v = 5;

The ‘data’ of the problem are those of example 26. Explicitly:

t10BS = 30.3;
s1 = 0.1;
t20BS = 29.4;
s2 = 0.2;
t30BS = 28.6;
s3 = 0.1;
t40BS = 28.3;
s4 = 0.1;

rho1[t1_] := Exp[ - (1/2) (t1 - t10BS)^2/s1^2 ]
rho2[t2_] := Exp[ - (1/2) (t2 - t20BS)^2/s2^2 ]
rho3[t3_] := Exp[ - (1/2) (t3 - t30BS)^2/s3^2 ]
rho4[t4_] := Exp[ - (1/2) (t4 - t40BS)^2/s4^2 ]

rho[t1_, t2_, t3_, t4_] := rho1[t1] rho2[t2] rho3[t3] rho4[t4]

Although an arbitrarily complex velocity velocity model could be considered here, let us take, for solving the forward problem, the simple model in example 27:

t1CAL[X_, Z_, T_] := T + (1/v) Sqrt[(X - x1)^2 + (Z - z1)^2]
t2CAL[X_, Z_, T_] := T + (1/v) Sqrt[(X - x2)^2 + (Z - z2)^2]
t3CAL[X_, Z_, T_] := T + (1/v) Sqrt[(X - x3)^2 + (Z - z3)^2]
t4CAL[X_, Z_, T_] := T + (1/v) Sqrt[(X - x4)^2 + (Z - z4)^2]

The posterior probability density is just that defined in equation 238:

sigma[X_,Z_,T_] := rho[t1CAL[X,Z,T],t2CAL[X,Z,T],t3CAL[X,Z,T],t4CAL[X,Z,T]]

We should have multiplied by the  \( \rho_{m}(X,Z,T) \)  defined in example 25, but as this just corresponds to a ‘trimming’ of the values of the probability density outside the ‘box’ 0 < X < 60 km, 0 < Z < 50 km, we can do this afterwards.

The defined probability density is 3D, and we could try to represent it. Instead, let us just represent the marginal probability densities. First, we ask the software to evaluate analytically the space marginal:

sigmaXZ[X_,Z_] = Integrate[ sigma[X,Z,T], {T,-Infinity,Infinity} ];

This gives a complicated result, with hypergeometric functions \( ^{33} \) . Representing this probability density is easy, as we just need to type the command

ContourPlot[-sigmaXZ[X,Z],{X,15,35},{Z,0,-25}, PlotRange->All,PlotPoints->51]

The result is represented in figure 28 (while the level lines are those directly produced by the software, there has been some additional editing to add the labels). When using ContourPlot, we change the sign of sigma, because we wish to reverse the software's convention of using light colors for positive values. We have chosen the right region of the space to be plotted (significant values of sigma) by a preliminary plotting of 'all' the space (not represented here).

Should we have some a priori probability density on the location of the earthquake, represented by the probability density  \( f(X,Y,Z) \) , then, the theory says that we should multiply the density just plotted by  \( f(X,Y,Z) \) . For instance, if we have the a priori information that the hypocenter is above the level z = -10 km, we just put to zero everything below this level in the figure just plotted.

Let us now evaluate the marginal probability density for the time, by typing the command

sigmaT[T_] := NIntegrate[ sigma[X,Z,T], {X,0,+60}, {Z,0,+50} ]

\( ^{33} \) Typing sigmaXZ[X,Z] presents the result.

63