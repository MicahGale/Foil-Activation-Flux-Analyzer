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
