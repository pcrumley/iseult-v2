# Iseult-v2

Note, this codebase is a work in progress, this website more so. Right now...

## Code Structure
----

While there is only one actual process, it is helpful to think of this GUI as being comprised of a 
backend and a frontend. The frontend is all of the code that handles user interaction and input. 
It is located in `src/main_app.py` and in the pop-ups in `src/popup_windows/`.  
The backend handles all of the logic of accessing the data and drawing the plots. It is located at 
`src/oengus.py`, `src/pic_sim.py` and `src/plots/ (Note: Oengus was father of Iseult in gaelic history).

`picSim` class: 

When oengus opens up a sim, it returns what quantities are available. These are all described in the 
YAML file. Right now there are six types of quantities, Prtls, Vector fields, Scalar Fields, Scalars, params, and Axes. 

