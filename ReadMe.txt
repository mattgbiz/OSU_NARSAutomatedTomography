ReadMe for Ohio State University Neutron Imaging Code Package
***********************************************************************
Original Author: Matt Bisbee			       
Affiliations: Ohio State University Dept. of Mechanical and Aerospace Engineering, Nuclear Engineering
	      Nuclear Analysis and Radiation Sensor (NARS) Laboratory
	      DOE NEUP Fellowship FY19
Points of Contact: Advisor Dr. Raymond Cao - cao.152@osu.edu
		   Author Matt Bisbee - bisbee.11@osu.edu
*********************************************************************** 

Python Script Contents include: ExtendedLeftoverTomographyV11.28.23, ManualControlV11.28.23, ExtendedLeftoverTomographyV11.28.23, SMC100Final, XYZMotion_Station, NewCameraControl, and FewViewPart2
Image Contents include: OSU_NRL.ico used for the icon on the GUIs in top left and OSU_NRL.png used for the image that exists as a placeholder for experimental images before the camera is used.
Must include  both icon and png image in same folder location as the GUI scripts as it automatically tries to load them

This package includes a variety of python scripts written for use with the neutron imaging station  

***********************************************************************
Troubleshooting:
1:

The Python module pycromanager connects to the code Micro-Manager to control the Camera. Both of these codes are being continuously updated, if someone updates Micro-Manager with a new nightly build. The pycromanager module code may need to be updated itself. If there is a mismatch, in the Python terminal it will say something about "Java ZMQ: #.#.# and Python Client: #.#.#" and whatever numbers those are should match. 

The easiest way to get them to match is to go to https://micro-manager.org/Micro-Manager_Nightly_Builds and download the most recent Version 2.0 build. Then in the Python terminal (I suggest using VS code to make sure it is the same Python environment) type "py -m pip install --upgrade pycromanager" (quotes not included in the command). Once these match, that issue should not persist. If any troubles come about for upgrading Pycromanager, you may need to intentionally install an older version of both pycromanager and micro-manager.

2:
Very often the Micro-Manager connection to the EMCCD camera has an issue when it is first launched. For whatever reason, you need to often go into device manager, uninstall the Andor control, re-install it, restart the computer, and then it will work. There is a whole document taking you through the steps to do this, but you will need Admin rights on this computer.

3: 
SMC controller connection issue. The SMC controller sometimes loses connection to the rotation stage. An easy fix is to just unplug the controller from power then plug it back in.  

4:
XYZ stage connection. make sure the XYZ stages are turned on and have a solid LED light after they have been turned on before connecting via computer. You must turn on the controller on the right hand side before turning on the left hand side. Then once the computer has connected there should be two solid LED lights indicating on and on-line connection.

5:
XYZ stage limit checks. Due to the rotation stage standoff proximity to the light tight box, there are movement limitations to ensure the sample does not hit the box. If the XYZ stage zero positions have been messed with, this may cause issues with movements. Turn off the XYZ stage controllers then turn them on and manually press and hold the jog buttons on the stages to find the zero positions (see documentation for where they should be) and then turn off the controllers. This will reset the zero position. If the limits need to be manually changed, this can be done in the XYZMotion_Station code. The positions are currently based on the step position not mm or in position.

