ReadMe for Ohio State University Neutron Imaging Code Package
*******************************************************************************************
Original Author: Matt Bisbee			       
Affiliations: Ohio State University Dept. of Mechanical and Aerospace Engineering, Nuclear Engineering
	      Nuclear Analysis and Radiation Sensor (NARS) Laboratory
	      DOE NEUP Fellowship FY19
Points of Contact: Advisor Dr. Raymond Cao - cao.152@osu.edu
		   Author Matt Bisbee - bisbee.11@osu.edu
******************************************************************************************

Python Script Contents include: TomographyV3, ManualControlV3, ExtendedTomographyV3.py, ExtendedLeftoverTomographyV3.py, LeftoverTomographyV3, *SMC100Final, XYZMotion_Station, NewCameraControl, and FewViewPart2
Image Contents include: OSU_NRL.ico used for the icon on the GUIs in top left and OSU_NRL.png used for the image that exists as a placeholder for experimental images before the camera is used.
Must include  both icon and png image in same folder location as the GUI scripts as it automatically tries to load them
*SMC100Final.py was adapted based on code from pySMC100 under the MIT License, see License/License-SMC100

This package includes a variety of python scripts written for use with the neutron imaging station at the Ohio State University. The two main codes to run are TomographyV3 and ManualControlV3 with the majority of the other scripts feeding into these codes. Both of the main codes house the front end GUI structure and commands for the easy to use Tkinter GUIs. Alternatives to the two typical GUI codes are ExtendedTomography, ExtendedLeftoverTomography, and LeftoverTomography. The two extended codes are to be utilized if an experiment is to run over multiple days. It offers the option to have multiple images taken at each degree location and splitting the list of degrees into multiple text files to be run over several days. The ExtendedLeftoverTomography code would then pick up for running the remaining degrees on later days.

In the documentation folder, there is a document for running the codes for the first time giving instructions on installing Python and the added libraries needed. There are two files that give instructions on how to use both GUI codes in the documentation. Each individual code that is utilized in the package has its own document that explains some of the background for the script. The exceptions to this is the ExtendedTomographies and LeftoverTomographies as they both stem from the base tomography code

Finally, there is a document giving details on the imaging station used at Ohio State University specfically explaining some of the components which is available upon request. 

​
​

​

​

​

​

quinonez6@llnl.gov