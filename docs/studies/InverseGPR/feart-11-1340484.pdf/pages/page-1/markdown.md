frontiers | Frontiers in Earth Science

TYPE Original Research
PUBLISHED 22 January 2024
DOI 10.3389/feart.2023.1340484

OPEN ACCESS

EDITED BY

Xinyu Liu,
Huazhong University of Science and
Technology, China

REVIEWED BY

Lei Su,
Qingdao University of Technology, China
Xiaoyu Zhang,
Guangzhou University, China
Jiahui Wang,
Nanjing Forestry University, China

*CORRESPONDENCE

Yulong Qin,
✉ 225033067@stu.hit.edu.cn

RECEIVED 18 November 2023

ACCEPTED 22 December 2023

PUBLISHED 22 January 2024

CITATION

Qin Y, Jiang Z, Tian Y, Jiang Y, Zhao G, Yan J,
Li Z, Cui Z, Zhao Z, Huang L, Zhang F, Du J and
Rong Z (2024). Deep learning-based inverse
analysis of GPR data for landslide hazards.
Front. Earth Sci. 11:1340484.
doi: 10.3389/feart.2023.1340484

COPYRIGHT

© 2024 Qin, Jiang, Tian, Jiang, Zhao, Yan, Li,
Cui, Zhao, Huang, Zhang, Du and Rong. This is
an open-access article distributed under the
terms of the Creative Commons Attribution
License (CC BY). The use, distribution or
reproduction in other forums is permitted,
provided the original author(s) and the
copyright owner(s) are credited and that the
original publication in this journal is cited, in
accordance with accepted academic practice.
No use, distribution or reproduction is
permitted which does not comply with these
terms.

# Deep learning-based inverse analysis of GPR data for landslide hazards

Yulong Qin¹*, Ze Jiang¹, Yongqiang Tian¹, Yuan Jiang¹,
Guanyi Zhao¹, Jiang Yan¹, Zhentao Li¹, Ziwang Cui¹, Zihui Zhao¹,
Linke Huang¹, Fuping Zhang¹, Junfeng Du² and Zhongdi Rong²

¹Longnan Power Supply Company of State Grid Gansu Electric Power Company, Longnan, Gansu, China,
²Chongqing Research Institute, Harbin Institute of Technology, Chongqing, China

In mountainous landscapes, the diverse geotechnical conditions amplify landslide susceptibility. Factors such as precipitation and seismic activity can trigger landslides, while inherent hazards such as voids, fissures, and compaction deficits jeopardize long-term slope stability. Detecting and forecasting these susceptibilities accurately is crucial. In this paper, the time-domain finite-difference approach and the gprMax software are used to conduct forward modeling of landslide susceptibility. An electrical model of subsurface aqueous structures is created, including water-filled and air-filled cavities, fracture zones, and fault lines. The distinctive radar signal responses within these environments are examined, and a dataset of B-scan images associated with their electrical models is constructed. By employing deep learning algorithms and the robust nonlinear mapping ability of convolutional neural networks in the Pix2Pix generative adversarial network, we accelerate the intelligent inversion of the geological radar data on landslide susceptibility. This innovative approach effectively reconstructs hazard models, offering a reliable basis for interpretation of radar signals.

KEYWORDS

landslide hazards, deep learning, inverse, forward simulation, neural networks

## 1 Introduction

Mountain landslides, as a typical geological disaster, often pose serious threats to the lives of people and the socio-economic development. Firstly, mountain landslides directly endanger human lives; the rapid descent of large amounts of soil and rocks during a landslide can lead to casualties (Bai et al., 2017; Alcántara-Ayala and Sassa, 2023). Secondly, mountain landslides can also cause damage to infrastructure such as houses, roads, bridges, and dams, resulting in significant economic losses (Zhang et al., 2020; Bao et al., 2022; Jiao et al., 2022). With the intensification of global climate change and the increase in human activities, the frequency and severity of mountain landslides are likely to rise. The internal structure and hidden dangers within landslides are major causes of their occurrence. Therefore, researching and surveying the internal hazardous conditions of landslides is crucial for preventing the impact of landslide disasters.

Geophysical probing has emerged as a crucial strategy for investigating the profound structure and material distribution of landslides. However, in complex mountainous terrain, the geophysical exploration of deep-seated landslide susceptibilities remains beset by inefficiency and limited accuracy. Ground-penetrating radar (GPR), an

Frontiers in Earth Science

01

frontiersin.org