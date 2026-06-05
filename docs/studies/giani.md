ELSEVIER

Available online at www.sciencedirect.com

SCIENCE @DIRECT

Construction and Building Materials 19 (2005) 755-762

Construction and Building MATERIALS

www.elsevier.com/locate/conbuildmat

# Modelling ground penetrating radar by GprMax

A. Giannopoulos

School of Engineering and Electronics, Institute for Infrastructure and Environment, University of Edinburgh, Alexander Graham Bell Building, Kings Buildings, Edinburgh EH9 3JN, UK

Available online 2 August 2005

# Abstract

This paper deals with the fundamentals of ground penetrating radar (GPR) operation and presents a software tool that can be used to model GPR responses from arbitrarily complex targets. This software tool called GprMax is available free of charge for both academic and commercial use and has been successfully employed in situations, where a deeper understanding of the operation and detection mechanism of GPR was required. Examples from both 2D and 3D models are presented which demonstrate the use of GprMax. The tool can be downloaded from www.gprmax.org or by contacting the author. © 2005 Elsevier Ltd. All rights reserved.

Keywords: Ground penetrating radar; Modelling; Non-destructive testing; GprMax; Finite-difference time-domain

# 1. Introduction

Ground penetrating radar is customarily used for the non-destructive testing (NDT) of structures and transport systems [1,2]. The use of GPR for NDT is just one of the many different areas, where radar is being applied as an important tool assisting the engineer or scientist in their efforts to determine the presence or absence as well as the kind of key underground features [3]. The main advantages of GPR are: its fast data acquisition capability, its high resolving ability and the fact that it responds equally well to metallic and nonmetallic targets. Its main drawback is the complex nature of its data and the difficulty that the GPR user faces when trying to interpret them. Interpretation of the data acquired using a GPR is often a complicated and error prone procedure mainly due to the complexity of the GPR signals and the variety of factors that influence and determine them. In order to successfully interpret GPR data a considerable amount of expertise is required by the system's user or the data analyst. This experience

is usually obtained either by expensive experimentation or by referring to prior knowledge often obtained after costly mistakes in the field.

Due to the frequent complexity of GPR data their interpretation is usually limited to defining general "areas of interest" or just locating "anomalies" instead of accurately determining the type and size and exact position of targets. The inability of interpreting GPR data quantitatively lies partly on the lack of understanding of how they have been created (i.e., understanding of the complex interactions between radar's electromagnetic fields and the targets) as well as on the lack of advanced processing tools that can process GPR data beyond the simple filtering procedures employed by most GPR users today. In order to improve our ability to understand and get more out of GPR data more sophisticated data analysis tools as well as better understanding of the radar's detection mechanism are required.

Modelling of GPR responses – either analytically or numerically – plays a central role in advancing our understanding of GPR as well as providing the means for testing new data processing techniques and

0950-0618/$ - see front matter © 2005 Elsevier Ltd. All rights reserved.
doi:10.1016/j.conbuildmat.2005.06.007

A. Giannopoulos / Construction and Building Materials 19 (2005) 755-762

interpretation software. The availability of a free GPR modelling tool gives both researchers and practitioners the opportunity to numerically “experiment” with GPR on their computers without incurring a substantial cost by creating expensive physical models – at least at an initial stage of a project. Simulating what-if scenarios can save money and time as well as provide data to support project proposals that could employ GPR but need some preliminary evidence in order to convince more sceptic project managers of GPR’s suitability to solve a given problem. Most importantly however, a freely available and well documented modelling tool avoids the syndrome of re-inventing the wheel that plagues many new research efforts that need GPR modelling facilities.

Successful modelling attempts of ground penetrating radar have been reported by many authors [4–6]. Most of the proposed approaches are based on the finite-difference time-domain (FDTD) method. The main reasons for such widespread use of the FDTD method are: its ease of implementation in a computer programme – at least at a simple introductory level – and its good scalability when compared with other popular electromagnetic modelling methods such the finite-element and integral techniques [7]. The main drawbacks of the FDTD technique are: the need to discretize the volume of the problem space which could lead to excessive computer memory requirements and the staircase representation of curved interfaces. Details of the development of the FDTD method can be found in [8] which provides an excellent introduction to the technique.

## 2. Numerical modelling of GPR

The analytical solution of the GPR’s forward problem is a difficult – and if realistic problems are to be addressed – an almost impossible task for even experienced scientists and engineers. The analytical difficulties in solving the GPR problem arise from the lack of closed form solutions to general “electromagnetic dipole sources over a half space” category of problems. The formulations of such problems lead to the well known Sommerfield type of integrals [9] which are difficult to be accurately evaluated even numerically. Most importantly though the need to model with as much detail and realism possible complex GPR targets as well as include in our advanced models the GPR transducers precludes the use of purely analytical techniques.

All electromagnetic phenomena, on a macroscopic scale, are described by the well known Maxwell’s equations. These are first order partial differential equations that express mathematically the relations between the fundamental electromagnetic field quantities and their dependence on their sources [10].

$$
\nabla \times E = - \frac {\partial B}{\partial t}, \tag {1}
$$

$$
\nabla \times H = \frac {\partial D}{\partial t} + J _ {\mathrm {c}} + J _ {\mathrm {s}}, \tag {2}
$$

$$
\nabla \cdot B = 0, \tag {3}
$$

$$
\nabla \cdot D = q _ {\mathrm {v}}, \tag {4}
$$

where $t$ is time (seconds) and $q_{\mathrm{v}}$ is the volume electric charge density (coulombs/cubic meter). In Maxwell’s equations, the field vectors are assumed to be single-valued, bounded, continuous functions of position and time. Further, the macroscopic effects of charged particles contained in a given medium on the electromagnetic fields interacting with it are described by the constitutive relations which are [10]:

$$
D = \bar {\bar {\epsilon}} * E, \tag {5}
$$

$$
B = \bar {\bar {\mu}} * H, \tag {6}
$$

$$
J _ {\mathrm {c}} = \bar {\bar {\sigma}} * E, \tag {7}
$$

where * denotes convolution and the tensors $\bar{\bar{\epsilon}}$, $\bar{\bar{\mu}}$ and $\bar{\bar{\sigma}}$ are the permittivity (farads/meter), permeability (henries/meter) and conductivity (siemens/meter) of the medium, respectively, and are usually referred to as the constitutive parameters. They could, in general, be functions of position, direction, the strength of the applied field and time. These relations couple the flux quantities with the electric and magnetic field intensities. In order to simulate the GPR response from a particular target or set of targets the above equations have to be solved subject to the geometry of the problem and its initial conditions.

The nature of the GPR forward problem classifies it as an initial value open boundary problem. That means that in order to obtain a solution one has to define an initial condition (i.e., the excitation of the GPR transmitting antenna) and allow for the resulting fields to propagate through space reaching a zero value at infinity because there is usually no specific boundary limiting the problem’s geometry where the electromagnetic fields can take a predetermined value. The first part (initiation of a source) is relatively easy to accommodate if the exact details of the GPR antenna are not taken into account. However, the second part (i.e., the truncation of the model) can not as easily be tackled by using a finite computational space.

The FDTD approach to the numerical solution of Maxwell’s equations is to discretize both the space and time continua. Thus, the spatial and temporal discretization steps play a very significant role since the smaller they are the closer the FDTD model is to a real representation of the problem. However, the values of the discretization steps always have to be finite, since computers have a limited amount of storage and finite processing speed. Hence, the FDTD model represents a discretized version of the real problem and of limited

A. Giannopoulos / Construction and Building Materials 19 (2005) 755-762

size. The building block of this discretized FDTD grid is the Yee cell named after Kane Yee who pioneered the FDTD method [11]. The 3D Yee cell is illustrated in Fig. 1. The 2D FDTD cell is easily obtained as a simplification of the 3D Yee cell. By assigning appropriate

![img-0.jpeg](img-0.jpeg)
Fig. 1. The Yee cell.

![img-1.jpeg](img-1.jpeg)
Fig. 2. FDTD view of the model's space.

constitutive parameters to the locations of the electromagnetic field components complex shaped targets can be easily included in the models. However, objects with curved boundaries are represented using a staircase approximation.

The numerical solution is obtained directly in the time domain by using a discretized version of Maxwell's curl equations that are applied in each FDTD cell. Since these equations are discretized in both space and time the solution is obtained in an iterative fashion. In each iteration the electromagnetic fields advance (propagate) in the FDTD grid and each iteration corresponds to an elapsed simulated time of one  $\Delta t$ . Hence by specifying the number of iterations one can instruct the FDTD solver to simulate the fields for a given time window.

The price one has to pay for obtaining a solution directly in the time domain using an explicit numerical method like FDTD is that the values of the temporal discretization step  $\Delta t$  and the spatial discretization  $\Delta x$ ,  $\Delta y$  and  $\Delta z$  cannot be assigned independently of each other. FDTD is a conditionally stable numerical process. The stability condition known as the CFL condition after the initials of Courant, Freidrichs and Lewy - [8] is

$$
\Delta t \leqslant \frac {1}{c \sqrt {\frac {1}{\Delta x ^ {2}} + \frac {1}{\Delta y ^ {2}} + \frac {1}{\Delta z ^ {2}}}}, \tag {8}
$$

where  $c$  is the speed of light. Hence  $t$  is bounded by the values of  $\Delta x$ ,  $\Delta y$  and  $\Delta z$ . The stability condition for the 2D case is easily obtained by letting  $\Delta z \to \infty$ .

One of the most challenging issues in modelling open boundary problems like GPR is the truncation of the computational domain at a finite distance from the sources and targets where the values of the electromagnetic fields can not be calculated directly by the numerical method. Therefore, approximate conditions known as absorbing boundary conditions (ABCs) are applied at a sufficient distance from the source to truncate and therefore limit the computational space. The role of these ABCs is to absorb any waves impinging on them, hence simulating an unbounded space. The computational space (i.e., the model) limited by these ABCs

Table 1 Some GprMax2D commands

|  Command | Function  |
| --- | --- |
|  #domain: | Controls the physical size of the model  |
|  #dx_dy: | Defines the discretization steps  |
|  #time_window: | Defines the simulated time window for the GPR trace  |
|  #medium: | Introduces the electrical properties of different media in the model  |
|  #box: | Introduce a rectangle of specific properties into the model's space  |
|  #cylinder: | Like the box: but introduces a cylinder into the model  |
|  #triangle: | Like the box: but introduces a triangular patch.  |
|  #tx: | Specifies the details of a transmitter (Tx)  |
|  #rx: | Specifies the details of a receiver (Rx)  |
|  #scan: | Can be used to automatically generate B-Scans  |

A. Giannopoulos / Construction and Building Materials 19 (2005) 755-762

should contain all important features of the problem's geometry such as all sources and output points and important targets. Fig. 2 illustrates the basic difference between a real problem's space and the actual FDTD modelled space.

In Fig. 2 it has been assumed that the half-space, where the target is situated is of infinite extent. As a result of this assumption the only reflected waves will be the ones originating from the target. In cases, where the host medium cannot be assumed to be of infinite extent (e.g., a finite concrete slab) the assumption can still be made as far as the slab's actual size is large enough

that any reflected waves that will originate at its termination will not affect the solution for the required time window. In general, any objects that span the size of the computational domain (i.e., model) are assumed to extend to infinity. The only reflections that will originate from their termination at the truncation boundaries of the model are due to imperfections of the ABCs and in general are of very small amplitude compared with the reflections from target(s) inside the model. All other boundary conditions which apply at interfaces between different media in the FDTD model are automatically enforced.

![img-2.jpeg](img-2.jpeg)
Fig. 3. Simulated GPR trace from a rebar in concrete.

![img-3.jpeg](img-3.jpeg)
Fig. 4. Geometry of a GprMax2D concrete slab with rebars model.

A. Giannopoulos / Construction and Building Materials 19 (2005) 755-762

# 3. GprMax

GprMax2D and GprMax3D are two computer programmes that implement the FDTD method for GPR modelling in 2D and 3D, respectively. Some of their key features are: an easy to use command interface, the ability to model dispersive materials, the modelling of complex shaped targets as well as the simulation of unbounded space using powerful absorbing boundary conditions. GprMax3D allows the simulation of GPR antennas and even the introduction of their feeding transmission lines into the model. GprMax2D is mainly used for GPR "signature" simulation whereas GprMax3D is used for more detail and realistic simulations especially when comparisons with real GPR data are important. Both GprMax2D and 3D programmes use a simple ASCII (text) file to define the model's parameters. In this file special commands are used which instruct the software to perform specific functions that are required by the type of the model the user wants to create. Some of the commands of GprMax2D are shown in Table 1. The software package includes a comprehensive Users' Manual in which details of the functionality of the programmes can be found.

As an illustration of the simplicity of creating models for GprMax2D the following input file creates a GPR model that can simulate a single GPR trace (A-scan) from a rebar embedded in a concrete half-space:

```txt
domain:0.50.5
#dx_dy:0.0050.005
#time_window:8.0e-9
#medium:6.00.00.00.011.00.0 concrete
#box:0.00.00.50.4 concrete
#cylinder:0.250.30.02 pec
#tx:0.200.421.01500e6 ricker trace.out b
#rx:0.300.42
```

The result of this simulation-a GPR trace over a rebar can be seen in Fig. 3.

# 4. GprMax2D modelling example

The flexibility of GprMax2D allows the modelling of complex what-if scenarios. In the following a simple example of modelling rebars in concrete is presented. The geometry of the problem consists of a  $2\mathrm{m}$  wide

![img-4.jpeg](img-4.jpeg)

![img-5.jpeg](img-5.jpeg)
Fig. 5. Simulated GPR scans from the 2D concrete slab model using different antenna centre frequencies.

A. Giannopoulos / Construction and Building Materials 19 (2005) 755-762

slab, where rebars of 20 mm diameter are located at an average depth of 150 mm from the slab's surface. Although, the horizontal distance between each rebar is fixed at 100 mm their cover depth is randomly varied between ±4 mm from the average cover depth of 150 mm. An illustration of the model's geometry is presented in Fig. 4. The electrical properties of concrete were assumed to be εr = 6 and σ = 0.01 S/m. In Fig. 5 a comparison is made of simulated GPR scans obtained from the model when different centre frequencies for the modelled GPR transducers were used. As it was expected, it evident that the resolution of the 900 MHz antenna is less than the 1.5 GHz one since the 1.5 GHz response resolves the rebars more clearly.

Fig. 6 illustrates three simulated scans from the same model when different values for the relative permittivity

of concrete are used. In all these scans the GPR antenna is simulated using a 1.5 GHz ricker pulse. The values for the relative permittivity of concrete that were used for this comparison are: εr = 6, εr = 12 and εr = 18. As it was expected the resolution of the modelled GPR data improves as the propagating wavelength becomes smaller since the velocity of propagation decreases with increasing values of relative permittivity. Further, it can be seen as well that although the target's positions have not been altered in the model their responses appear to register at a later time in the simulated GPR scans. The above example illustrates in a simple way that the model predicts key features of GPR responses reasonably well especially when one takes into account the fact that GprMax2D provides only a solution based on a 2D approximation of a real 3D problem.

![img-6.jpeg](img-6.jpeg)

![img-7.jpeg](img-7.jpeg)

![img-8.jpeg](img-8.jpeg)

Fig. 6. Simulated GPR scans from the 2D concrete slab model for different values of relative permittivity of concrete.

A. Giannopoulos / Construction and Building Materials 19 (2005) 755-762

# 5. GprMax3D modelling example

Modelling GPR in 3D using GprMax3D requires substantially more computer resources than simple 2D modelling. However, the continuous increase of the amount of computer power that is readily available to the average GPR user – an effect of the rapid advancements in computer technology – makes 3D GPR modelling a clear and better alternative to simple 2D simulations. Currently the main use of GprMax3D is to model as realistically as possible GPR antennas and their field distribution when they are in close proximity with targets. GprMax3D is especially useful in studying numerically computed radiation patterns of GPR antennas which demonstrate significant differences from – customarily used in GPR analysis – theoretical field patterns that are calculated assuming infinitesimal Hertzian dipoles as GPR sources and they are based in far-field approximations.

In this paper, a simple 3D example is presented. This example is from a simulation of a simple bowtie antenna located $10\mathrm{mm}$ above a concrete slab. The antenna is unshielded and has a total length of $150\mathrm{mm}$ and a flare angle of $60^{\circ}$. A twin-pair transmission line with impedance of 200 Ohms is used to feed the bow-tie. The excitation pulse is a Gaussian of $900\mathrm{MHz}$ centre frequency.

![img-9.jpeg](img-9.jpeg)
Fig. 7. Snapshots of three principal planes through a bow-tie antenna (units are in FDTD cells).

![img-10.jpeg](img-10.jpeg)
Fig. 8. Snapshot of the plane containing the antenna structure (units are in FDTD cells).

A. Giannopoulos / Construction and Building Materials 19 (2005) 755-762

In Figs. 7 and 8 snapshot images obtained from the model's space are taken after 3 ns had passed from the initiation of the source pulse in the feeding transmission line. The snapshot images presented here are of the field component which has the same orientation with the long axis of the bow-tie antenna. It is interesting to note how the model can be used to provide information that leads to the visualization of the complex radar fields that exist close to the antenna. Fig. 7 includes all three principal planes of the model in an attempt to demonstrate how this simple GPR antenna radiates in 3D space. Fig. 8 presents the snapshot image from the plane that contains the antenna structure itself.

It should be noted here that construction of 3D models using GprMax3D follows the same simple procedure as for the case of 2D models employing similar commands in a simple ASCII file. The only significant difference is obviously the fact that in GprMax3D objects need to be specified as 3D entities and not as simple 2D shapes.

## 6. Conclusions

Numerical modelling of GPR is very useful in enhancing our understanding of the GPR's detection mechanism. The GprMax suite of programmes allows the simulation of realistic scenarios encountered in everyday use of GPR. As computer power is constantly increasing GPR modelling will become an important tool in training new GPR users as well as improving data interpretation of complex GPR sections. The introduction of more sophisticated features into the modelling programmes is a continuing effort especially for the realistic modelling of actual GPR transducers.

## Acknowledgement

The author will like to acknowledge the support of the Building Research Establishment(BRE), UK for providing financial support for the development of the first version of GrpMax.

## References

[1] Bungey JH, Millard SG, Shaw MR. Radar assessment of post-tensioned concrete. Proceedings of the 7th international conference on structural faults and repair-97, Edinburgh, 8–10 July 1997, vol. 1. Edinburgh: Engineering Technics Press; 1997. p. 331–9.
[2] Forde MC, McCavitt N. Impulse radar testing of structures. Proc Instn Civ Engrs Structs and Bldgs 1993;99:96–9.
[3] Daniels DJ. Subsurface penetrating radar. London: The Institution of Electrical Engineers; 1996.
[4] Bergmann T, Robertsson JO, Holliger K. Finite-difference modelling of electromagnetic wave propagation in dispersive and attenuating media. Geophysics 1998;63:856–67.
[5] Giannopoulos A. The investigation of transmission-line matrix and finite-difference time-domain methods for the forward problem of ground probing radar, DPhil Thesis, University of York, Department of Electronics, York, UK; 1997.
[6] Bourgeois JM, Smith GS. A fully three-dimensional simulation of a ground-penetrating radar: FDTD theory compared with experiment. IEEE T Antenn Propag 1996;34:36–44.
[7] Millard SG, Shaw MR, Giannopoulos A, Soutsos MN. Modelling of subsurface pulsed radar for nondestructive testing of structures. ASCE J Mater Civil Eng 1998;10:188–96.
[8] Taflove A. Computational electrodynamics: the finite-difference time-domain method. Artech House; 1995.
[9] King RWP, Owens M, Wu TT. Lateral electromagnetic waves. Springer-Verlag; 1992.
[10] Balanis CA. Advanced engineering electromagnetics. Wiley; 1989.
[11] Yee KS. Numerical solution of initial boundary value problems involving Maxwell's equations in isotropic media. IEEE T Antenn Propag 1966;14:49–58.