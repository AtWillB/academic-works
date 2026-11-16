# academic-works
This repository is meant to demonstrate the collection of academic software-development and data visualization curated by William Byrne (as of 2026) for published work in his career thus far.

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
This work is contained within [enceladus_regolith/](https://github.com/AtWillB/academic-works/tree/master/enceladus_regolith)

The data pipeline for this project was as follows:
1. 1D temperature profiles of Enceladus's ice shell generated with varying ice shell depths, regolith depths, and regolith thermal conductivity by **src**/conductive_profile_equations.py/calc_ConductiveTempProfileVarkT.py
   
2. Temperature profiles are saved in *.txt files under **data**/
   
3. Temperature profiles are used as input to calcualtion two-way radar attenuation via **src**/attenuation_calculator.py
   - We are paricularly interested in the depth to 100 dB of attenuation
  
4. Temperature profiles and associated radar calculations are read into a **src**/paper_figures/paper_figure_*.ipynb file and plotted:
   1. Seperaturely (fig1)
   2. Heatmaps showing each simulation's relative penetration depth to 100 dB (fig2) 
   3. Relative penetration depth maps taking global ice shell thickness estimates from Hemingway & Mital et. al. 2019 (fig3 & fig4)


#### Notes
- Original repository is owned by DLR, and therefore repository commit history is not viewable
- The **data**/ folder is structred by figure. 
- Under each data/figure*/ sub-folder, there is a unique figure*_README.txt documenting the tablular structure used for both attenuation calculations and temperature profiles. 

## Assessing the Lateral Detectability of Eutectic Interfaces within Europa's Ice Shell
This work is contained within europa_eutectic/


The data pipeline for this project was as follows:
1. Simulations with a 2D spherical annulus geometry are run until they reach a true or quasi steady-state, determined by RMS Velocity
   
2. Simulations are read into the **src**/gaia_sim.py class, which performs 
   1. time-averaging of relevant fields (mostly temp field) over last 10% of time steps
   2. Using the time-averaged T field, calculate relevant isothermal depths to 237.15 K and 252.05 K
   3. calculates the depths that you reach 100 dB of attenuation (using either low or high loss model)
   4. Eutectic interface detection (lateral detectability %) is then calcualted for each pair of eutectic interface and attenuation model 
   
3. Calculated fields and assocaited metadata is saved into a **data**/shell_visc*/*.json object

4. Calculations relevant to figure generation are stored in tabular format (**data**/*full_study.csv)

5. .csv data is read in by figure[1-5]*.ipynb notebooks to generate figure components

6. Individual componets are compiled in Inkscape (free photoshop) and then saved as .pdf


#### Notes
- Repository commit history is viewable at https://github.com/AtWillB/gaia_eutectic_constrain
- Data organizational preference per-simulation rather than per figure
- README.md file for simualtion metadata and for tabular .csv content

## A Practical Guide to Git for Academic Software Development
This was the very first work I took to a conference that was not officially supervised, and was entirely my own idea. Source control is not widely adopted in planetary science software development. So I created a poster explaining the value of git at three scales of development

- As an individual academic software developer
- As a small group (2-5) of developers working on the same repository
- Multiple teams of developers operating simulaneously on the same project. 

This work was displayed at the 2026 Europlanet Science Conference (EPSC2026) in poster form
