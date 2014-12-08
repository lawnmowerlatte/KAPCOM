KAPCOM
=============
About
---------
This set of Python scripts and Arduino sketch can be used to send and receive information via the Telemachus plugin for Kerbal Space Program. The idea is to:

* Create a Python library which acts as a middleman between the PyKSP Python library and the serial interface for interacting with the Arduino
* Provide a sample sketch and schematic for Arduino which uses the serial interface for sending and retrieving data. The sample will show:
	*  Examples of how to connect digital (buttons and switches) input for system states.
	* Examples of how to connect analog (joysticks and faders) input to control the vehicle.
	* Examples of how to display data either as seven segment displays or as analog gauges.

There is NO visible component to this script other than logging. It is purely an interface between other points. The idea is that this should be a flexible stepping off point for other DIYers to easily jump into making your own hardware console.

I have tried to keep data and roles strictly segmented and to keep hardware specifics in specific places. In an ideal world, you should only have to customize the Arduino sketch to suit your desires (and current budget!)

Name
---------
The name is a reference to the "[Capsule Communicator](http://en.wikipedia.org/wiki/Flight_controller#Capsule_Communicator_.28CAPCOM.29)" which commiunicated with the crew of NASA's manned flights. Of course, it wouldn't be Kerbal Space Program if there wasn't a "**K**" somewhere.

License
----------
GNU GPL 3.0

Credits
----------
Thanks to [RichardBunt](https://github.com/richardbunt) for the wonderful Telemachus plugin. Many thanks for your hard work on the project.

Thanks to [KK4TEE](https://github.com/KK4TEE) for the foundation of this script. Although I rewrote enough of it to make forking unrealistic, the idea and core are based on their [Control Panel](https://github.com/KK4TEE/Control-Panel) project.