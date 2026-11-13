# academic-works
This repository is meant to demonstrate the collection of academic software-development and data visualization curated by William Byrne for published work in his career thus far.

The following work is generally structred as follows:
```text
topic_subtopic/
├── abstract/
│   ├── tex_files/
│   └── conferenceYEAR.pdf
├── data/
├── src/
│   ├── paper_figures/
│       ├── figure1.ipynb
│       └── figure2.ipynb
│   ├── core_code.py
│   ├── core_module1.py
│   └── core_module2.py
├── visuals/
│   ├── fig1.pdf
│   └── fig2.pdf
├── paper.pdf
├── conference_presentation_YEAR.pdf
└── conference_poster_YEAR.pdf
```

Where the **abstract**/ folder contains all abstracts related to the highest-impact publication associated with the project (usually some **paper**) and the **data**/ folder holds the structured scientific data created by some .py file in the **src**/. This data is then used to generate the figures (as seen in **visuals**/) by a handful of .ipynb files found in **src**/paper_figures/. The **data**/ folder is typically uniquely structured to the project. 

The examples within this repository include the following works:
## Modeling the Thermal Effects of Surface Regolith on Enceladus's Ice Shell

1. 1D temperature profiles of Enceladus's ice shell generated with varying ice shell depths, regolith depths, and regolith thermal conductivity by **src**/conductive_profile_equations.py/calc_ConductiveTempProfileVarkT.py
   
2. Temperature profiles are saved in *.txt files under **data**/
   
3. Temperature profiles are used as input to calcualtion two-way radar attenuation via **src**/attenuation_calculator.py
   - We are paricularly interested in the depth to 100 dB of attenuation
  
4. Temperature profiles and associated radar calculations are read into a **src**/paper_figures/paper_figure_*.ipynb file and plotted:
   1. Seperaturely (fig1)
   2. Heatmaps showing each simulation's relative penetration depth to 100 dB (fig2) 
   3. Relative penetration depth maps taking global ice shell thickness estimates from Hemingway & Mital et. al. 2019 (fig3 & fig4)

#### Notes
- The **data**/ folder is structred by figure. 
- Under each data/figure*/ sub-folder, there is a unique figure*_README.txt documenting the tablular structure used for both attenuation calculations and temperature profiles. 

## Assessing the Lateral Detectability of Eutectic Interfaces within Europa's Ice Shell


## A Practical Guide to Git for Academic Software Development
