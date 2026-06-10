Received: 17 March 2023 Accepted: 18 September 2023

Check for updates

DOI: 10.1002/nsg.12272

ORIGINAL ARTICLE

Near Surface Geophysics

EAGE

# Synthetic modelling of railway trackbed for improved understanding of ground penetrating radar responses due to varying conditions

Matthew John Couchman Brian Barrett Asger Eriksen

Zetica Ltd, Witney, OX29 4JB, UK

Correspondence

Matthew John Couchman, Zetica Ltd, Zetica House, Southfield Rd, Eynsham, Witney, OX29 4JB, UK.

Email: matthew.couchman@zetica.com.

# Abstract

Ground penetrating radar (GPR) is a commonly used tool for railway trackbed inspection due to its ability to collect information about subsurface materials at high resolution and high speed. Although GPR recording systems allow for the collection of vast quantities of data (hundreds of kilometres per day), accurate ground truth information is difficult to obtain. Models of trackbed can be used to generate synthetic radargrams to provide a better understanding and predictability of GPR responses to a wide range of trackbed conditions. In this research, we produced models of ballast using randomly shaped 3D particles, with a range of particle size distributions to represent various stages of ballast breakdown. Additionally, void spaces are partially filled with a constant dielectric material to represent ballast contamination. We used gprMax to simulate the GPR response for a 2 GHz horn antenna over the trackbed models. These simulations resulted in radargrams that are visually indistinct from real recorded data in known conditions. These radargrams, along with their formative models, have provided valuable insights into how variations in trackbed conditions can impact GPR data.

# KEYWORDS

engineering geophysics, forward modelling, GPR

# INTRODUCTION

Railways are used for the transport of both passengers and freight. Monitoring trackbed condition is a vital process in assuring the efficiency and safety of these services. The loads exhibited by rail traffic and the impact of natural events, such as flooding or landslips, affect trackbed condition and drive the need for periodic maintenance. Identifying areas in most need of maintenance is of paramount importance for the cost-effective deployment of maintenance resources.

In ballasted trackbeds, particles of rock form a layer that acts as an interface between the formation and the track structure, as shown in Figure 1. The ballast plays a key role in allowing water to drain away from the track, as well as distributing the vertical forces applied by traffic at the sleepers (also known as ties), adding lateral stability to the sleepers, absorbing airborne noise,

facilitating rail realignment and alleviating the formation of frost (Al-Qadi et al., 2008). Clean ballast comprises coarse and angular particles, with large, interconnected air-filled voids between the particles. Over time, ballast becomes increasingly fouled, exhibiting smaller void spaces, and becoming less effective at performing its key roles. One type of fouling occurs through the breakdown of ballast particles by mechanical wear under traffic loading, maintenance work, and through chemical and mechanical weathering from environmental conditions. Ballast breakdown results in smaller void spaces due to the reduced size of larger ballast particles and the filling of the remaining voids with fine particles. These fine particles tend to migrate deeper into the ballast layer over time (Meeker, 1990; Selig, 1985). A second type of fouling is the infiltration of contaminants, such as mud or sediment from the formation layer below, into the void spaces.

© 2023 European Association of Geoscientists &amp; Engineers.

wileyonlinelibrary.com/journal/nsg

Near Surface Geophysics 2024;22:206-219.

Ballast fouling may occur to different extents throughout the ballast layer. This can result in a stratified profile of clean ballast above a more fouled lower ballast layer. In this paper, we have made the simplifying assumption that ballast breakdown is uniform throughout the ballast layer, whereas ballast contamination is highly stratified.

The track structure includes the rails and sleepers. The sleepers are normally seated within ballast, with the top of the sleeper at the same height as the top of the ballast. The surface of the ballast layer may be lower or higher than the top of the sleepers, with the sleepers sometimes being completely covered by ballast. The sleepers are commonly constructed out of wood, concrete, steel or composite materials. Concrete sleepers are constructed with tensioned reinforcing bars (rebar) that may be arranged in various configurations depending on the sleeper size, intended loading and manufacturer's design.

Ground penetrating radar (GPR) is used to measure the condition of the railway trackbed and is sensitive to anomalies in the subsurface structure (Al‐Qadi et al. 2008; Brown & Li, 2017; Ciampoli et al. 2018; Eriksen et al. 2010). It is also an effective method of specifically evaluating ballast condition because it responds differently to ballast with different degrees of fouling due to differences in void size (Barrett et al. 2019).

We consider an impulse GPR system utilising a horn antenna, operating with a central frequency of 2 GHz. GPR systems operating at this frequency respond to the voids of clean ballast with strong Mie scattering (Mie, 1908), making them useful for determining ballast condition while achieving sufficient signal penetration to image reflections at the base of the ballast in most conditions and trackbed environments. Lower frequency systems allow for deeper penetration at the cost of vertical resolution but do not have a strong scattering response to clean ballast (Barrett et al. 2019).

The boundary between clean ballast and either highly fouled ballast (if fouling is stratified), a capping layer, or the formation, can sometimes exhibit a reflection in a radargram, marking a distinct layer boundary due to a change in the effective dielectric constant. However, where there is a small contrast in the effective dielectric constant, or where there is a gradual change from clean to fouled ballast with depth, there may not be a detectable reflection. Instead, this boundary may be recognized in the radargram as a change in the amount of scattering.

This research developed synthetic radargrams that qualitatively resemble the complex radargrams that would be recorded from an actual survey. Synthetic radargrams can be used to understand how various trackbed conditions affect GPR responses. An open-source, finite-difference, time-domain electromagnetic simulation software, gprMax (Warren et al. 2016), was used to produce the radargrams from trackbed models. Basic components of the models were generated with specified electrical properties using gprMax tools. More complex materials, such as ballast, were generated externally and their geometries and electrical properties imported into gprMax using an HDF5 file format. Ballast layers were generated utilizing specified particle size distributions (PSDs) that are representative of real ballast. Furthermore, realistic void space ratios were assigned to the ballast layer depending on the PSD.

There have been previous attempts to generate ballast models, including some intended for mechanical simulations and others intended for electromagnetic simulations. Typically, models used for electromagnetic simulation have been 2D models employing simple 2D particle shapes. Zhang et al. (2011) used irregular polygons that appeared highly angular, with many particles being either triangular or trapezoidal. Their particles were randomly sized within a statistical distribution, but were not related to a specific PSD. In contrast, Benedetto et al. (2020) used a PSD to determine the size of their particles, but adopted the simplification of circular particles.

In an attempt simulate more realistic particle shapes for electromagnetic simulations, Kingsuwannaphong et al. (2020) used Blender, an open-source graphics software, with a rock generator plugin to generate 3D ballast particles. Their model was typical of industry standard clean ballast, having diameters of 31.5--63.0 mm and aspect ratios between 1 and 2, although models of fouled ballast were included using an effective medium within the void space.

Another approach for obtaining realistic 3D particle shapes has been to image real ballast particles, to char

Near Surface Geophysics

EAGE

COUCHMAN ET AL.

acterize their shape, texture and angularity (Rao et al., 2001). Broekman et al. (2020) extended this method to produce complete 3D laser scans of particles for digital analysis. They showed renders of these particles in Blender, but their mechanical simulations were performed in a DEM simulation package using simplified particles designed to have the representative characteristics.

Boler et al. (2014) used the results of Rao et al (2001) and Huang (2010) to define five unique polyhedral shapes. These were used repeatedly, scaled randomly between  $12.5\mathrm{mm}$  and  $63.5\mathrm{mm}$ , to populate a ballast section with a specific PSD. Although these particles have realistic aspect ratios and angularity properties, they lack the randomness of a collection of unique particles. Furthermore, the inclusion of cubes within the particle population makes their shapes uncharacteristic of real ballast.

Boler et al. (2014) and Kingsuwannaphong et al. (2020) used physics-based compaction methods to generate 3D ballast volumes, whilst Benedetto et al. (2020) applied compaction by shifting particles downwards to their lowest possible point in the model space. The process of ballast compaction is intuitively important for mechanical studies, but may not be important for electromagnetic studies, providing the models have a representative void space ratio. Boler et al. (2014) investigated the influence of PSD (with compaction) on porosity, finding that variations in the number of particles smaller than  $19\mathrm{mm}$  did not affect the resulting porosity. This was attributed to the particles (between 12.5 mm and  $19\mathrm{mm}$  in size) being larger than most of the void spaces. Very small particles (e.g.,  $&lt; 10\mathrm{mm}$ ) may be more likely to reduce the porosity of the compacted ballast layer.

We introduce a method for ballast modelling using a random arrangement of randomly shaped 3D particles. Our method produces a 3D volume of particles, but does not use any compaction method. Instead, we target a specific PSD and residual void space ratio. Then, we demonstrate the use of a simulated GPR source wavelet that matches the phase, amplitude and frequency characteristics of a 2 GHz horn antenna. We describe parameterisations for the models, including layer dimensions, electromagnetic properties and the inclusion of a variety of sleeper types, before demonstrating that these models produce radargram simulations that are difficult to distinguish from real data.

# SYNTHETIC BALLAST GENERATION

3D ballast models were generated with random arrangements of 3D particles. The process used random sequential adsorption (Benedetto et al., 2020) to add particles to the model domain until a specific PSD and

![img-0.jpeg](img-0.jpeg)
FIGURE 2 Example 3D ballast model (colours represent differences in dielectric constant).

void space ratio (based on a targeted fouling level) were achieved.

The individual particle shapes were defined by calculating the convex hull surrounding a collection of  $N$  randomly generated point coordinates. Particles formed from a small number of points (e.g.,  $N &lt; 10$ ) are highly angular, simplistic polyhedra, being defined by a small number of faces, whereas particles formed from a large number of points (e.g.,  $N &gt; 50$ ) are typically equidimensional and comparatively smooth polyhedra. We identified a collection size of  $N = 30$  as being well suited to defining particles that appear similar to ballast particles.

The model domain was defined as a voxel with a 1-mm cell size (to match our chosen finite-difference mesh discretisation in gprMax). To populate the voxel, the particles were first scaled to the required size. Their sizes are defined by their secondary axes (representing the dimensions significant to sieve tests).

After scaling, the particles were randomly positioned within the model domain and tested for conflict against previously placed particles. The process started with the largest particle sizes in the targeted PSD and continued by adding particles of the same size until either positional conflicts were encountered on sequential attempts, or the volume fraction required to match the targeted PSD was reached. The particle size was then reduced, and the process continued until the smallest particles of the PSD were placed or the model void space ratio reached the anticipated ratio for the defined fouling level. The smallest particles placed in this way had a size of  $1\mathrm{mm}$  to match the chosen voxel resolution.

Each particle placed in the model domain was adsorbed to the voxel by checking which cell centres were enclosed by the particle's polyhedron. Individual particles in our models were assigned a random dielectric constant between 4.5 and 6.5 and a conductivity of  $5.0~\mathrm{mS / m}$ . The models exhibited the required PSDs and void space ratios expected for real ballast suggesting that compaction is not required for electromagnetic

SYNTHETIC TRACKBED MODELLING

Near Surface Geophysics

EAGE European American Society for the Study of the Earth Sciences

![img-1.jpeg](img-1.jpeg)

![img-2.jpeg](img-2.jpeg)

![img-3.jpeg](img-3.jpeg)
FIGURE 3 Demonstration of a 2D ballast model in different stages of construction (a-d) from 3D ballast particles.

![img-4.jpeg](img-4.jpeg)

investigations. An example of a small model of 3D ballast is shown in Figure 2.

The speed of the ballast generation algorithm depends on both the model domain size and the targeted PSD. Higher fouling levels need a higher number of particles to be placed within a smaller residual void space. A 3D model space of  $0.5\mathrm{m}\times 0.5\mathrm{m}\times 0.6\mathrm{m}$  required multiple days of computation, to be filled with a PSD representing clean ballast. Creating a model space with a PSD representing highly fouled ballast was impractical using our available hardware (Intel Core i9-109000X CPU @ 3.7 GHz and 64 GB RAM). Instead, we used the same process to generate 2D ballast layers by setting the voxel size to 1 cell in the third dimension. The effective 2D model space of size  $0.5\mathrm{m}\times 0.001\mathrm{m}\times 0.6\mathrm{m}$  required 210 s to be generated with a PSD represent

ing clean ballast and 1800 s to be generated with a PSD representing highly fouled ballast. Figure 3 illustrates the progressive placement of the 3D particles for a 2D model.

# Ballast fouling by breakdown

We used PSDs derived from Ionescu (2005) to represent five different levels of ballast breakdown, identified as Models A-E in order of increasing fouling. Model A represents clean ballast with predominantly coarse particles, whilst Model E represents significant ballast breakdown, resulting in a PSD skewed more towards finer particles (Figure 4). We set a target void space ratio of  $40\%$  for Model A. This was reduced for models

Near Surface Geophysics

EAGE European Society for the Study of the Aereotomology

COUCHMAN ET AL.

![img-5.jpeg](img-5.jpeg)
FIGURE 4 Ballast particle size distributions for model types A-E.

TABLE 1 Particle size distribution for ballast models A-E, expressed as a percentage of the model space.

|  Ballast model | A | B | C | D | E  |
| --- | --- | --- | --- | --- | --- |
|  Air voids (%) | 40 | 34 | 28 | 22 | 18  |
|  Particles 50–60 mm diameter (mm) | 9.0 | 6.6 | 6.5 | 5.5 | 1.6  |
|  Particles 40–50 mm diameter (mm) | 21.0 | 9.9 | 10.8 | 11.7 | 13.2  |
|  Particles 30–40 mm diameter (mm) | 21.0 | 26.4 | 27.4 | 14.0 | 9.0  |
|  Particles 20–30 mm diameter (mm) | 7.2 | 19.1 | 20.2 | 23.4 | 13.1  |
|  Particles 10–20 mm diameter (mm) | 1.8 | 4.0 | 5.0 | 19.5 | 27.1  |
|  Particles 5–10 mm diameter (mm) | 0.0 | 0.0 | 1.4 | 2.3 | 9.8  |
|  Particles 1–5 mm diameter (mm) | 0.0 | 0.0 | 0.7 | 1.6 | 8.2  |

representing higher fouling levels, with Model E having a targeted  $18\%$  residual void space ratio. It is assumed that the void space (area) ratio in our 2D models is proportional to the void space (volume) ratio that would be achieved in the equivalent 3D model. Examples of each model type are presented in Figure 5 and a breakdown of particle sizes and percentages is given in Table 1. The colours of the particles represent the randomized dielectric constant applied. The decrease in void space from Model A through Model E is visually apparent, as is the increase in the number of small particles.

The models show some ballast particles that are completely isolated from other particles. This is partially a consequence of using random particle positions, without using a physics engine to apply settling or compaction, and partially a consequence of the 2D model representing a vertical slice through an arrangement of 3D

particles. Particles that appear to be floating may have been supported by interactions outside of the plane of the 2D model if a 3D model had been constructed.

# Ballast fouling by contamination

The outlined process of generating a ballast layer model with different PSDs is sufficient to represent the dominant effects of ballast breakdown. However, very fine particles produced during ballast breakdown or introduced through ballast contamination cannot be represented with a 1 mm model discretisation. Instead, these finer materials are introduced into the model as an effective medium for filling the remaining void space. We used the complex refractive index method (CRIM) as described by Barrett et al. (2019) to derive the dielectric properties of the fill material, based on assumed proportions of air, water and fines and on assumed contaminant materials. The CRIM mixing model is independent of geometry, considering only the relative proportions of each component to give an approximation of the bulk dielectric according to:

$$
\sqrt {\varepsilon_ {b u l k}} = V _ {1} \sqrt {\varepsilon_ {1}} + V _ {2} \sqrt {\varepsilon_ {2}} + \dots + V _ {n} \sqrt {\varepsilon_ {n}} \tag {1}
$$

where  $V_{n}$  corresponds to the proportional volume of component  $n$ ,  $\varepsilon_{n}$  corresponds to the dielectric of the component  $n$  and  $\varepsilon_{bulk}$  is the estimated bulk dielectric of the material. The model is appropriate for particles much smaller than the signal wavelength. Ballast contamination was introduced to the ballast models by setting the void space to have the defined dielectric properties of the effective fill material and a specified conductivity.

# TRACKBED MODELS

Individual 2D ballast 'blocks' were generated with a size of  $0.5\mathrm{m}\times 0.6\mathrm{m}$ , but multiple blocks were generated in sequence, allowing for the creation of continuous ballast sections. We combined 14 ballast blocks to create  $7.0\mathrm{m}\times 0.6\mathrm{m}$  ballast models.

The complete trackbed model space was  $7\mathrm{m}\times 1.7\mathrm{m}$  allowing for a layer of trackbed formation and an airspace, within which the simulated source and receiver were located, above the ballast model. Trackbed structures were added to the model space using inbuilt gprMax commands in the following sequence:

1. The effective medium representing the ballast contamination (included as a background layer so that it fills the voids of the ballast model).
2. The ballast model voxel (added via an HDF5 file).
3. The trackbed formation.

SYNTHETIC TRACKBED MODELLING

Near Surface Geophysics

EAGE European Society for the Study of the Earth and the Environment

![img-6.jpeg](img-6.jpeg)
(a)

![img-7.jpeg](img-7.jpeg)
(b)

![img-8.jpeg](img-8.jpeg)
(c)

![img-9.jpeg](img-9.jpeg)
(d)

![img-10.jpeg](img-10.jpeg)
(e)
FIGURE 5 Examples of ballast models A-E and their respective residual void space ratios (colours represent differences in dielectric constant).

|  Model Type | Void Space Ratio  |
| --- | --- |
|  A | 40  |
|  B | 34  |
|  C | 28  |
|  D | 22  |
|  E | 18  |

4. An air layer above the trackbed overprinting the ballast model voxel so that the height and surface roughness of the ballast layer can be controlled.
5. Sleeper cross sections included in models representing the track centre only.

Layer roughness was simulated at the interfaces between layers using fractal boxes (Giannakis &amp; Giannopoulos, 2014). The thickness of each layer varied stochastically, and the specific sequence of building the trackbed model allowed models of thin or thick ballast to be generated from the same (reusable) ballast layer voxel. The voxel could be further reused by flipping about the vertical and horizontal axes.

A variety of sleeper designs were simulated, including a wooden sleeper with rectangular cross section and three types of concrete sleeper with trapezoidal cross section. Concrete sleepers included points of perfect electrical conductors representing rebar. The concrete sleepers were based on known sleeper designs, including their distinctive rebar configurations. Sleeper dielectric constant and conductivity varied depending on the type of sleeper. In the case of wooden sleepers, the dielectric constant and conductivity were randomized from a broad range of values to reflect various levels of moisture that may occur depending on sleeper condition. Sleeper spacing was ran

domized between 40 and  $85~\mathrm{cm}$  for any individual model and varied randomly within each  $7\mathrm{m}$  model by  $2 - 4\mathrm{cm}$ . Models without sleepers were generated to simulate GPR surveys with the antennas located over the track shoulder (beyond the ends of the sleepers).

The height of the ballast relative to the top of sleeper varied stochastically, resulting in scenarios that varied from excess ballast above the sleepers, to significant ballast deficit.

This method of producing and varying each trackbed component allows for a variety of models, representing a diverse range of trackbed conditions to be simulated. Figure 6 demonstrates each of the individual components of the model domain, whereas Figure 7 presents multiple examples of complete trackbed models, illustrating the following:

- variations in the ballast model, representing different levels of ballast breakdown (see Figure 7a compared to b);
- variations in the thickness of an effective medium layer, representing different levels of ballast contamination (see Figure 7a compared to c);
- variations in the height of the formation layer, representing different ballast thicknesses (see Figure 7a compared to d);

Near Surface Geophysics

EAGE

COUCHMAN ET AL.

![img-11.jpeg](img-11.jpeg)
FIGURE 6 Examples of trackbed models. Model A includes a concrete sleeper and fouling by contamination, whereas model B represents clean ballast at the track shoulder (no sleepers).

![img-12.jpeg](img-12.jpeg)
FIGURE 7 Example trackbed models showing variations in ballast layer thickness, degree of breakdown (model types a-e), height of contamination, layer interface roughness, ballast height (relative to sleepers), sleeper type and sleeper spacing.

- variations in layer roughness (see Figure 7a compared to e);
- examples of shoulder data (Figure 7a-c) and example of track centre models (Figure 7d-f);
- variations in sleeper spacing (see Figure 7e compared to f).

# SIMULATION

The source for our simulations was a 2D,  $y$ -polarized, Hertzian dipole with a customized excitation signal. Efforts were made to create a waveform that matched a real horn antenna, with a 2 GHz centre frequency,

SYNTHETIC TRACKBED MODELLING

Near Surface Geophysics

EAGE European American Society for the Study of the Earth Sciences

![img-13.jpeg](img-13.jpeg)
FIGURE 8 Comparison of observed and simulated traces for a metal plate test with an antenna height of  $400~\mathrm{mm}$

as closely as possible. The excitation signal was tested by simulating plate tests in gprMax for a range of antenna heights and comparing the resulting waveforms to those of real plate tests undertaken with a physical antenna. The excitation signal developed produced matching travel times and similar waveforms for reflections recorded when the antenna was 200, 300, 400 and  $450~\mathrm{mm}$  above the metal plate. The waveforms also showed a good correlation in peak frequency with the real data. An example of this matching at a plate height of  $400~\mathrm{mm}$  is shown in Figure 8. Differences in the waveforms after 7 ns are due to multiple reflections between the metal plate and the antenna in the real plate test.

A simulation domain of  $7.0\mathrm{m}\times 1.7\mathrm{m}$  was used to encompass the full trackbed models, but the antenna start and end coordinates were positioned  $1.0\mathrm{m}$  in from the domain boundaries, resulting in a  $5.0\mathrm{m}$  simulated radargram. The first and last metres of the model domain were important contributions to the simulations, providing off-nadir scattering responses from ballast air voids, and preventing the source and receiver from being too close to the perfectly matched layer (PML) at the domain boundary. Each simulated radargram represents a collection of simulations, each with a different antenna location. We used an antenna step of  $5\mathrm{cm}$  between each simulation, thereby providing 100 scans over the  $5.0\mathrm{m}$  section. The antennas were nominally located  $400\mathrm{mm}$  above the top of the trackbed surface, but the simulations included small random variations in the vertical position, to simulate the vibrations that can occur in a real survey.

The simulations took around 105 min, using an Nvidia Quadro RTX 8000 GPU with gprMax using GPU acceleration (Warren et al., 2018).

# Post-processing

Various data processing steps were carried out to enhance the simulated radargrams. First, a finite impulse response filter was applied to reshape the wavelet, in a process that replicated the processing applied to real data. Second, long diffractions were suppressed by applying a time-varying radon filter. The Radon filter is processed via the python library scikit-image (Van der Walt et al., 2014). We calculate the Radon transform of the data and filter the data by velocity (or angle of dip) for various time windows. The resultant data are then reconstructed via filtered back projection (Kaczmarz, 1937) and the full radargram reconstructed from the radon filtered time windows. These diffractions were similar to the scattering observed in real data but extended over much longer antenna position ranges. It is thought that a more accurate radiation pattern, possibly utilizing a 3D antenna model and a 3D model of the ballast, would more accurately capture off-nadir scattering response, likely obviating the need to apply this filter.

The breakthrough response (direct arrival from transmitter to receiver) at 2 ns was observed to have a higher amplitude than that of real data. This was also considered to be due to not producing an accurate antenna radiation pattern. A tapered amplitude reduction was applied to this breakthrough response.

A disadvantage of using a 2D Hertzian dipole as a source instead of a 3D antenna model was the inability to model ringing, which is common in real data. A ringing signature was simulated by convolving the breakthrough event with a random impulse series. Random noise was then added to the convolved timeseries and, a bandpass filter was applied (0.2–0.4 GHz). The ringing time series was then added to each trace in the radargram.

Electromagnetic interference (EMI) was included by adding white noise. All EMI varied in amplitude and the phase was stochastically altered for each trace, providing a visually accurate representation of EMI. High amplitude, mono‐frequency noise is occasionally present in real data, and this was simulated in some of our synthetic radargrams. Bands of 900 MHz noise were added to groups of between three and seven traces, where the phase was again stochastically altered for each trace. Figure 9 shows examples of two synthetic radargrams passing through the full post‐processing sequence.

### Comparison of synthetic radargrams and real data

We compared synthetic radargrams to real data to determine if we had been able to create radargrams that could be mistaken for real data samples. In Figure 10 (without sleepers, representing track shoulder data) and Figure 11 (with sleepers, representing track centre data), synthetic radargrams (left) are presented next to examples of real data (right). The synthetic radargrams were produced from the trackbed models shown in Figures 12 and 13, respectively. The real data were collected by Zetica on a railway using a 2 GHz impulse GPR system with a scan interval of 5 cm. The synthetic radargrams are visually indistinct from real data, giving confidence in the usefulness of the synthetic radargrams. On a blind test with experienced interpreters, many synthetic radargrams were identified incorrectly as real data.

## DISCUSSION

The synthetic radargrams that we can generate using the trackbed modelling approach shown here provide information allowing for further understanding of the GPR response to varying trackbed conditions. The models are a tool that can be updated with alternative geoelectrical parameters and track structures to align with specific trackbed environments. For example, alternative sleeper types could be simulated, including steel or composite sleepers. This can be a useful tool when planning surveys in new environments for locating new and specific targets.

The work shown here can also be used as a training tool, by providing models that demonstrate different trackbed conditions and their associated synthetic radargrams. This can improve an interpreter's understanding and ability to detect and interpret layer boundaries or qualitatively estimate the fouling level of a section of trackbed.

Although the synthetic radargrams look like real data, there are still some discrepancies that will be addressed by further research. The presence of long diffractions (prior to radon filtering) suggests that a 3D approach may be necessary to correctly simulate the scattering characteristics of the ballast layer. Unsuccessful attempts to mitigate the issue prior to adopting the cosmetic fix of a radon filter included reducing the size of the model domain and increasing the thickness of the PML. We expect the most complete solution will require simulations with a more accurate radiation pattern, resulting from the use of a 3D antenna model and model domain, which will require further developments in software and hardware.

Although most post‐processing steps presented either follow standard processing techniques or introduce noise that would depend on external factors (e.g. EMI), the requirement for artificial ringing demonstrates the simplicity of our source. A 3D antenna model would more accurately simulate the wavelet and hence provide the associated ringing without the need to artificially create this effect. We recognize that there may also be a requirement to simulate the structure of a survey platform.

## CONCLUSION

We describe a methodology for the generation of synthetic radargrams representing a range of trackbed conditions. A series of 2D trackbed models have been generated with ballast particle sizes determined by specific PSDs and targeted void space ratios. This method allows for the generation of ballast with varying amounts of ballast breakdown, where the cleanest ballast is composed of large particles with large air voids and the most fouled ballast has smaller particles with smaller air voids. The random sequential adsorption process described here can produce densely populated arrangements of particles using polyhedra that are a first‐order approximation of realistic ballast particles. Ballast fouling by contamination was simulated using an effective medium defined using the CRIM mixing model. The transmitter used in the simulation was a y‐polarized Hertzian dipole with a custom excitation signal designed to match the transmitted wavelet to examples of real data obtained from a 2 GHz antenna.

As well as a range of ballast conditions, the models included variations in the dielectric properties, depths (or thicknesses) and layer interface, roughness of the formation layer, a contamination layer and the surface profile of the ballast, some models included sleeper cross sections, in order to simulate a GPR survey in the centre of the track, whereas others were simulated without sleepers, in order to represent a GPR survey over the shoulder of the track.

Synthetic radargrams of 5.0 m length were produced using gprMax. Post‐processing routines were

SYNTHETIC TRACKBED MODELLING

Near Surface Geophysics

EAGE European American Society for Geophysics

![img-14.jpeg](img-14.jpeg)
Simulation Radargram

![img-15.jpeg](img-15.jpeg)

![img-16.jpeg](img-16.jpeg)
FIR Filter + Radon Filter

![img-17.jpeg](img-17.jpeg)

![img-18.jpeg](img-18.jpeg)
Breakthrough Suppression + Artificial Ringing

![img-19.jpeg](img-19.jpeg)

![img-20.jpeg](img-20.jpeg)
Electromagnetic Interference

![img-21.jpeg](img-21.jpeg)
FIGURE 9 Two examples (left and right) of a synthetic radargram after gprMax simulation and after various stages of the post-processing.

Near Surface Geophysics

EAGE

COUCHMAN ET AL.

![img-22.jpeg](img-22.jpeg)

![img-23.jpeg](img-23.jpeg)

![img-24.jpeg](img-24.jpeg)

![img-25.jpeg](img-25.jpeg)

![img-26.jpeg](img-26.jpeg)

![img-27.jpeg](img-27.jpeg)

![img-28.jpeg](img-28.jpeg)
FIGURE 10 Radargrams without the influence of sleepers, representing surveys of the track shoulder, showing synthetic examples (a-d) from Figure 11, and real data examples (e-h).

![img-29.jpeg](img-29.jpeg)

SYNTHETIC TRACKBED MODELLING

Near Surface Geophysics

EAGE European American Society for Geophysics

![img-30.jpeg](img-30.jpeg)

![img-31.jpeg](img-31.jpeg)

![img-32.jpeg](img-32.jpeg)

![img-33.jpeg](img-33.jpeg)

![img-34.jpeg](img-34.jpeg)

![img-35.jpeg](img-35.jpeg)

![img-36.jpeg](img-36.jpeg)
FIGURE 11 Radargrams with the influence of sleepers, representing surveys of the track centre, showing synthetic examples (a-d) from Figure 13, and real data examples (e-h).

![img-37.jpeg](img-37.jpeg)

Near Surface Geophysics

EAGE

COUCHMAN ET AL.

![img-38.jpeg](img-38.jpeg)

![img-39.jpeg](img-39.jpeg)

![img-40.jpeg](img-40.jpeg)

![img-41.jpeg](img-41.jpeg)
FIGURE 12 Trackbed models with the influence of sleepers, representing surveys of the track centre, used to generate synthetic radargrams shown in Figure 12.

![img-42.jpeg](img-42.jpeg)

![img-43.jpeg](img-43.jpeg)

![img-44.jpeg](img-44.jpeg)

![img-45.jpeg](img-45.jpeg)
FIGURE 13 Trackbed models without influence of sleepers, representing surveys of the track shoulder, used to generate synthetic radargrams shown in Figure 10.

used to produce synthetic radargrams that are difficult to distinguish from real data.

This method provides scope for gaining a further understanding of existing data and will be useful for survey planning in unfamiliar environments. Furthermore, the work shown is an invaluable training tool to help users understand the effect of different foul

ing levels on ballast, thus improving their interpretation capabilities.

Although the ballast modelling was inherently 3D, it was used to build 2D simulations due to computational limitations. An extension of the work to a fully 3D simulation and using a 3D antenna model of our antenna would improve the research outcomes.

SYNTHETIC TRACKBED MODELLING

Near Surface Geophysics

EAGE European Association for the Advancement of Science and Technology

# CONFLICT OF INTEREST STATEMENT

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

# DATA AVAILABILITY STATEMENT

Research data are not shared.

# REFERENCES

Al-Qadi, I.L., Xie, W. &amp; Roberts, R. (2008) Scattering analysis of ground-penetrating radar data to quantify railroad ballast contamination. NDT&amp;E International, 41, 441-447.
Barrett, B., Day, H., Gascoyne, J. &amp; Eriksen, A. (2019) Understanding the capabilities of GPR for the measurement of ballast fouling conditions. Journal of Applied Geophysics, 169, 183-198.
Benedetto, A., Ciampoli, L.B., Brancadoro, M.G., Alani, A.M. &amp; Tosti, A. (2018) A computer-aided model for the simulation of railway ballast by random sequential adsorption process. Computer-Aided Civil and Infrastructure Engineering, 33(5), 243-357. https://doi.org/10.1111/mice.12342
Boler, H., Qian, Y. &amp; Tutumleur, E. (2014) Influence of size and shape properties of railroad ballast on aggregate packing. Transportation Research Record Journal of the Transportation Research Board, 2448, 94-104.
Broekman, A., Van Niekerk, J.O. &amp; Grabe, P.J. (2020) HRSBallast: a high-resolution dataset featuring scanned angular, semi-angular and rounder railway ballast. Data in Brief, 33, 106471.
Brown, M. &amp; Li, D. (2017) Ground penetrating radar technology evaluation and implementation. Phase 2. Washington, DC: Federal Railroad Administration, Office of Research, Development and Technology.
Ciampoli, L.B., Artagan, S.S., Tosti, F., Gagliardi, V., Alani, A.M. &amp; Benedetto, A. (2018) A comparative investigation of the effects of concrete sleepers on the GPR signal for the assessment of railway ballast. In: 17th International Conference on ground penetrating radar (GPR), 18-21 Jun 2018, Rapperswil, Switzerland. London, University of West London. pp. 1-6.
Eriksen, A., Gascoyne, J., Mangan, C. &amp; Fraser, R. (2010) Practical applications of GPR surveys for trackbed characterisation in the UK, Ireland, USA, and Australia. In: Rejuvenation and renaissance: CORE 2010: conference on railway engineering, 12-15 September 2010, Wellington, New Zealand.
Giannakis, I. &amp; Giannopoulos, A. (2014) A novel piecewise linear recursive convolution approach for dispersive media using the finite-difference time-domain method. IEEE Transactions on Antennas and Propagation, 62, 2669-2678. 10.1109/TAP.2014.2308549
Ionescu, D. (2005) Ballast degradation and measurement of ballast fouling. In: Proceedings of 7th International Railway Engineering Conference. Engineering Technical Press, London, pp. 12-18.

Hawari, H.M. (2007) Minimising track degradation through managing vehicle/track interaction (PhD thesis). Brisbane: Queensland University of Technology.
Huang, H. (2010) Discrete element modelling of railroad ballast using imaging based aggregate morphology characterization (PhD dissertation). Urbana: University of Illinois.
Meeker, L.E. (1990) Engineering and economic factors affecting the cost of railroad ballast (MSc thesis). Reno: University of Nevada.
Mie, G. (1908) Beiträge zur optik truer medien, speziell kolloidaler metallösungen. Annals of Physics, 330(3), 377-445.
Kaczmarz, S. (1937) Angenaeherte aufloesung von systemen linearer gleichungen. Bulletin International de l'Académie Polonaise des ciences et des Lettres, 35, 355-357.
Kingsuwannaphong, T., Brau, C. &amp; Heberling, D. (2020) Fouled railway ballast modeling using rigid body simulation. In: 18th International Conference on ground penetrating radar, Golden, CO. Houston, TX, Society of Exploration Geophysicists. pp. 63-66.
Rao, C., Tutumleur, E. &amp; Sefankski, J.A. (2001) Coarse aggregate shape and size properties using a new image analyzer. Journal of Testing and Evaluation, 29(5), 461-471.
Selig, E.T. (1985) Ballast for heavy haul track. In: Track Technology Conference: Thomas Telford Ltd. pp. 245-252.
Van Der Walt, S., Schonberger, J.L., Nunez-Iglesias, J., Boulogne, F., Warner, J.D., Yager, N. et al. (2014) Scikit-image: image processing in python. PeerJ, 2, e453.
Warren, C., Giannopoulos, A. &amp; Giannakis, I. (2016) gprMax: open-source software to simulate electromagnetic wave propagation for ground penetrating radar. Computer Physics Communications, 209, 163-170. 10.1016/j.cpc.2016.08.020
Warren, C., Giannopoulos, A., Gray, A., Giannakis, I., Patterson, A., Wetter, L. et al. (2018) A CUDA-based GPU engine for gprMax. Open source FDTD electromagnetic simulation software. Computer Physics Communications, 237, 208-218. 10.1016/j.cpc.2018.11.007
Zhang, Q., Gascoyne, J. &amp; Eriksen, A. (2011) Characterisation of ballast materials in trackbed using ground penetrating radar: part 1. In: The 5th IET Conference on railway monitoring and no-destructive testing, 4A1-4A1, 29-30 November 2011, Derby, UK, London, Institution of Engineering and Technology (IET)

How to cite this article: Couchman, M.J., Barrett, B. &amp; Eriksen, A. (2024) Synthetic modelling of railway trackbed for improved understanding of ground penetrating radar responses due to varying conditions. Near Surface Geophysics, 22, 206-219. https://doi.org/10.1002/nsg.12272