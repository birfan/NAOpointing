This project contains multiple files that need to be uploaded to your NAO robot via Choreographe (v2.1 or later).

The service-webpage.pml is the main project file that you open through Choregraphe. This contains all of the required files, but the Choregraphe window will stay grey. You can see the files in the 'Project content' tab.
To install on the robot, upload the files to your local NAO robot using the 'Package and install current project to the robot' option in the 'Robot Applications' tab. You do not need to run it - it will automatically start, although you may need to restart NaoQi if it does not work straight away.

You can access the demo webpage by typing the following address into your browser:
http://192.168.1.114/apps/service-webpage/  (change the IP address that corresponds to your NAO)

This simple webpage shows you how to communicate with NAO.

The communication is handled from the main.js JavaScript file that you can alter to fit your task.

Button no 4 sends a speech request via the myservice python script on NAO.