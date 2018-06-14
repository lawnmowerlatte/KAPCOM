KAPCOM
=============

[![Build Status](https://travis-ci.org/lawnmowerlatte/KAPCOM.svg)](https://travis-ci.org/lawnmowerlatte/KAPCOM)

[![Coverage Status](https://coveralls.io/repos/lawnmowerlatte/KAPCOM/badge.svg)](https://coveralls.io/r/lawnmowerlatte/KAPCOM)

[![Code Issues](http://www.quantifiedcode.com/api/v1/project/00317bdaff814223a6f33d28f1e37479/badge.svg)](http://www.quantifiedcode.com/app/project/00317bdaff814223a6f33d28f1e37479)

About
---------
This set of Python scripts and Arduino sketch can be used to send and receive information via the Telemachus plugin for Kerbal Space Program. The idea is to:

* Create Python modules for interacting with an Arduino as well as handling device specific tasks
* Create a Python library which acts as a middleman between the PyKSP Python module and the Arduino module
* Create a simple Arduino sketch which allows remote execution of commands by Python over serial
* Provide a sample configuration file and schematic for Arduino. The sample will show:
	* Examples of how to connect digital (buttons and switches) input for system states.
	* Examples of how to connect analog (joysticks and faders) input to control the vehicle.
	* Examples of how to display data either as seven segment displays or as analog gauges.

There is NO visible component to the Python script other than logging. It is purely an interface between other points. The idea is that this should be a flexible stepping off point for other DIYers to easily jump into making your own hardware console.

I have tried to keep data and roles strictly segmented and to keep hardware specifics in specific places. In an ideal world, you should only have to customize the configuration file to suit your desires (and current budget!)

Name
---------
The name is a reference to the "[Capsule Communicator](http://en.wikipedia.org/wiki/Flight_controller#Capsule_Communicator_.28CAPCOM.29)" which commiunicated with the crew of NASA's manned flights. Of course, it wouldn't be Kerbal Space Program if there wasn't a "**K**" somewhere.

License
----------
GNU GPL 3.0

Credits
----------
Thanks to [RichardBunt](https://github.com/richardbunt) for the wonderful [Telemachus plugin](http://forum.kerbalspaceprogram.com/threads/24594) for Kerbal Space Program. Many thanks for your hard work on the project.

Thanks to [thearn](https://github.com/thearn) for the [Python-Arduino-Command-API](https://github.com/thearn/Python-Arduino-Command-API) which I based my Arduino sketch and module upon.

Thanks to [Louis Goessling](https://github.com/602p) for the [PyKSP API](https://github.com/602p/pyksp).

Thanks to [KK4TEE](https://github.com/KK4TEE) for the foundation of this script. Although I rewrote enough of it to make forking unrealistic, the idea and core are based on their [Control Panel](https://github.com/KK4TEE/Control-Panel) project.

Finally, thanks to Squad for [Kerbal Space Program](https://kerbalspaceprogram.com)!

