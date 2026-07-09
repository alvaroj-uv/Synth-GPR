Qin et al.

10.3389/feart.2023.1340484

convolutional generative adversarial network (DCGAN) for data augmentation, this method was demonstrated to have a decent identification accuracy in field GPR investigation experiments. Liu proposed a deep neural network (DNN) architecture, GPRInvNet, aimed at mapping GPR B-scan data to complex permittivity images (Liu et al., 2021). This method effectively reconstructs subsurface engineering defects with clear boundaries. Li developed a deep learning algorithm, GR-RCNN, which fuses the 2-D and 3-D features of GPR B-scans and C-scans and can reliably detect subsurface defects in airport runways even under noisy conditions (Li et al., 2021). Wang proposed a rebar clutter elimination-generative adversarial network (RCE-GAN) method to improve tunnel lining void recognition in GPR data by eliminating steel bar clutter using generative adversarial networks (Wang et al., 2022). This method has achieved good results for both generated and real-world images. Liu presented a method that uses a deep 3-D convolutional network and multiple mirror encoding to capture 3-D GPR data (Liu et al., 2023). This method improves the accuracy of subsurface object classification by capturing the spatiotemporal features between parallel B-scans, and it outperforms existing B-scan-based methods. Yang proposed a defect segmentation method for non-destructive testing of internal defects in subsurface engineering using GPR data (Yang et al., 2022). This method leverages a CNN called Segnet and a loss function to improve the accuracy, automation, and efficiency of defect recognition. Hou proposed a method for automatically detecting latent lining damage inside tunnels using GPR data. This method employs convolutional neural networks to suppress strong reflections from reinforcement bars and uses a support vector machine to extract multi-dimensional features in the time, frequency, and time-frequency domains (Hou et al., 2022). Liu developed a method for evaluating the overall condition of tunnel linings using GPR images, which was validated through numerical simulations, sandbox experiments, and field tests, and it was found to effectively identify defects and thickness sections from GPR B-scan images (Liu et al., 2022).

In conclusion, through the development of numerous techniques and methodologies, significant advancements have been made in recent years in GPR inversion research for tunnel damage detection. The ongoing integration of novel methods and machine learning technologies promises to foster further progress in this domain, with potential applications spanning various aspects of subsurface and geological engineering monitoring. However, research on landslide hazard damage inversion based on deep learning remains notably scarce.

In this paper, the TDFD method and the gprMax software were used to conduct forward modeling to realize the forward simulation of landslide susceptibility defects. An electrical model for water-filled and air-filled voids, fissures, and uncompacted areas is established, and the characteristic responses and patterns of radar signals within different constructs are researched and analyzed. Using the gprMax software, the forward simulation of numerous irregular lining defects is performed, and a dataset that correlates B-scan images of landslide defects with their corresponding electrical model imagery is established. Leveraging deep learning algorithms and utilizing the Pix2Pix generative adversarial network, we accomplish the intelligent inversion of GPR data. Based on the nonlinear mapping relationship of deep learning, effective landslide

defect models are generated, providing a reference for the interpretation of radar signals.

## 2 Methodology

### 2.1 Establishment of a GPR numerical model

#### 2.1.1 Forward modeling of rock and soil media

The dimensions and distributions of soil–rock bodies differ significantly from traditional single target detection or uniform layered medium detection. In the case of such loose materials, conducting forward simulations with different parameters may lead to substantial disparities. The factors influencing the simulation results include the distance between the transmitting and receiving antennas, the center frequency of the antenna, and the step length of the spatial grid.

Given the characteristics of the gprMax software, its command can only create regular spatial geometric shapes, such as spheres, cuboids, and cylinders. However, irregular shapes such as soil–rock mixtures, cracks, and uncompacted areas are challenging to model directly using gprMax. Forward simulations that substitute regular shapes for complex shapes often result in excessive errors.

In this paper, we generate irregular rocks by writing Python scripts, saving them as HDF5 files, and using gprMax to read the HDF5 files for irregular rock modeling. We can control parameters such as the number of rock particles and the radius of the rocks through the script, thereby controlling the pixel occupancy ratio of the rocks in space. This control allows for the setting of different soil–rock ratios. The effect of the rock generation is shown in Figure 1A.

We import the rocks to create the geoelectric model depicted in Figure 1B to study the typical features of the GPR reflection signal of the soil-rock mixture with randomly distributed rocks. The upper layer of this model is air, the middle layer is a 3-m-thick soil–rock body, and the lower layer is a rock layer. The number and grain size of the rocks are adjusted to control the soil–rock ratio of the soil–rock mixture, and the relative permittivity of the soil is controlled to manage the water content. The model calculation parameters are listed in Table 1. The rock grain size, ranging from 4 to 50 cm, is arranged randomly.

The excitation source is a point source, and a Ricker wavelet is selected. The transmitting antenna and receiving antenna are 0.3 m apart. The computational load of the forward simulation model increases with enhancement of the grid accuracy. Considering the calculation accuracy and time, the grid cell length is set to 0.005. The soil and rocks are nonmagnetic materials, and their magnetic conductivity is typically assumed to be 1 H/m, with a magnetic loss factor of 0.

#### 2.1.2 Solution stability and dispersion

According to the principles of electromagnetism, the phase velocity of electromagnetic waves in a loss medium is a function of the frequency. The phase velocity of the electromagnetic pulse wave changes with the temporal discretization interval and the spatial discretization interval, and numerical dispersion can occur as the number of iterations increases. To ensure the stability of the numerical solution, the temporal discretization interval and spatial

Frontiers in Earth Science

03

frontiersin.org