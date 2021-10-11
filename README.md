# Robust Pointing with NAO Robot
=====================================================

This project provides a pointing service for NAO robot (SoftBank Robotics Europe, France) to point (and look) at objects with Chilitags (in physical world or on tablet) or to a world or tablet coordinate. The robot uses its closest hand, i.e., choosing left if the object is to the left of the robot and right, if otherwise. Chilitags are 2D fiducial markers to detect objects and determine their positions. The pointing service was tested with NAOqi 2.1 and 2.4 on a NAO robot. While Pepper robot (SoftBank Robotics Europe, France) also has a NAOqi operating system, this project was not tested on it.
 
For installing Chilitags (Bonnard et al., 2013) on NAO robot, see B. Irfan and S. Lemaignan (2016), "Chilitags for NAO Robot", `https://github.com/birfan/chilitags`, which uses ChilitagsModule.

## Installation

This project contains multiple files that need to be uploaded to your NAO robot via Choreographe (v2.1 or later).

The *pointing-webpage.pml* is the main project file that you open through Choregraphe. This contains all of the required files, but the Choregraphe window will stay grey. You can see the files in the 'Project content' tab. To install on the robot, upload the files to your local NAO robot using the 'Package and install current project to the robot' option in the 'Robot Applications' tab. You do not need to run it - it will automatically start, although you may need to restart NAOqi if it does not work straight away. After installing, you can use this library as a default NAOqi library with the functions described below.

You can access the demo webpage by typing the following address into your browser:
http://ROBOT_IP/apps/pointing-webpage/  (change the IP address that corresponds to your NAO)

The robot needs to be 'awake' (not sleeping) before you can execute pointing commands.

## Usage

* If you are using vision to **detect chilitags or localize using chilitags**, use `subscribeCamera(camIndex)` (camIndex: 0 for top camera of NAO robot, 1 for bottom) before. Unsubscribe from camera using `unsubscribeCamera()`, especially if you need to subscribe again.

* If you are **pointing at a world coordinate**, use `pointAtWorld(coorX, coorY, coorZ, speed, sleepTime, frame)`, specifying 3D coordinates (X, Y, Z) with a given arm speed (default 0.2), duration of pointing (default 2 seconds) and frame for the robot. Frame is "0" for using the torso as the frame, 1 for world frame, 2 is robot frame. See [NAOqi documentation](http://doc.aldebaran.com/2-1/naoqi/motion/control-cartesian.html) for further information about frames.

* If you are **pointing at a chilitag**, use `pointAtTag(tagName, speed, sleepTime)`, specifying tag number (e.g., 8) with a given arm speed (default 0.2) and duration of pointing (default 2 seconds). The default tag size is 30 mm. If you use a different size tag, call `setDefaultTagSize(tagSize)`. For reading the configuration of Chilitags from a YAML file, use `readTagConfiguration(configFile)`. See *tag_configuration_sample.yml* in *scripts* folder for an example.

* If you are **pointing at a tablet coordinate**, use `pointAtTablet(tabletPixelX, tabletPixelY, speed, sleepTime)`, specifying tablet pixels (X and Y) with a given arm speed (default 0.2) and duration of pointing (default 2 seconds). Use this function twice if you haven't localized before or use `localize(tabletPixelX, tabletPixelY)` prior to this function to localize using a chilitag (default is tag number 8). You can change localization tag using `setLocalizationTag(localizationTag)`. The tablet resolution should be set prior to using this function `setTabletResolutionSize(resX, resY, tabletWidth, tabletLength)` with number of pixels in X (width), number of pixels in Y (length), tablet width (in metre), tablet length (in metre).

## License

This work is released under GNU Lesser General Public License v3.0 (LGPL3) in accordance with Chilitags (Bonnard et al., 2013). Cite the following if using this work:

 * Robust Pointing with NAO Robot. B. Irfan. University of Plymouth, UK. `https://github.com/birfan/NAOpointing`. 2016.

 * Chilitags for NAO Robot. B. Irfan and S. Lemaignan. University of Plymouth, UK. `https://github.com/birfan/chilitags`. 2016.

 * Chilitags 2: Robust Fiducial Markers for Augmented Reality. Q. Bonnard, S. Lemaignan, G.  Zufferey, A. Mazzei, S. Cuendet, N. Li, P. Dillenbourg. CHILI, EPFL, Switzerland. `http://chili.epfl.ch/software`. 2013.

```
	@misc{NAOpointing,
		title = {Robust Pointing with NAO Robot},
		author={Irfan, Bahar},
		publisher={University of Plymouth, UK},
		url={https://github.com/birfan/NAOpointing},
		year={2016}
	}

	@misc{chilitagsModule,
		title = {Chilitags for NAO Robot},
		author={Irfan, Bahar and Lemaignan, S\'{e}verin},
		publisher={University of Plymouth, UK},
		url={https://github.com/birfan/chilitags},
		year={2016}
	}

	@misc{chilitags,
		title = {Chilitags 2: Robust Fiducial Markers for Augmented Reality and Robotics.},
		author={Bonnard, Quentin and Lemaignan, S\'{e}verin and Zufferey, Guillaume and Mazzei, Andrea and Cuendet, S\'{e}bastien and Li, Nan and \"{O}zg\"{u}r, Ayberk and Dillenbourg, Pierre},
		publisher={CHILI, EPFL, Switzerland},
		url={http://chili.epfl.ch/software},
		year={2013}
	}
```

This work was used during the [L2TOR](http://www.l2tor.eu/) project.

## Contact

If you need further information about using Chilitags with the NAO robot, contact Bahar Irfan: bahar.irfan (at) plymouth (dot) ac (dot) uk (the most recent contact information is available at [personal website](https://www.baharirfan.com)).
