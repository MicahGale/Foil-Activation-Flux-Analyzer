# Using the Excel Template

Included in this repository is a template file: foilActivation.xltx. This file has been formatted so that the python API can
easily parse the data which is in the file. To use open it and make a new workbook out of the template. 

## Worksheets in the Template

The work sheets which are included are:
* **ExperimentInfo** - this is an overview of the experiment which was ran.
* **PositionData** - includes information on where the foils were located in the pile.
* **countData** - Includes the counting data for all of the foils measured.
* **foilData** - Includes data on the properties of the foils. 
* **Isotope Data** - Includes data on the decay of the isotopes used. Currently this sheet isn't used.

### ExperimentInfo
This sheet is mostly for the humans to understand what was going on. The time at which the source was inserted is read though, 
and must be present. To complete this insert the date into the date box, and the time of insertion into the timebox, and these
two cells will be summed for the time.

### PositionData

This sheet documents where the foils are located in the pile. Every foil must have it's own row. The columns are:

* **Foil** The foil identifier. Usually a 1 or 2 letter long identifier. The foil must be in foilData
* **Layer** The layer the foil is on. Currently this is for the east-west stringers counting from the bottom of the lattice.
* **Position** The poisiton of the foil in a stringer starting from 1 in the east most position going up to 14.
* **X [cm]** The X- east-west position measured from center in centimeters. This is calculated given the data in column O.
* **Y [cm]** The Y- north-south position. Usually this is 0.
* **Z [cm]** The Z-vertical position. Similarly calculated from the data in column O.
* **End Activation** The time at which the activation for the foil stopped. Usually this is when the stringer is removed from the pile.

* **Offset from East Face** This is the distance which the stringers jut out from the east face of the pile. Used for more precise X locations.
