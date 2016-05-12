OneButton Plugins
=================

Runs as separated processes with specific arguments and connected by stdin/stdout durning OneButton running.

Entrance points
---------------
* plugins/{type}/{name}/build - preparing plugin script (used on CI to build sources)
* plugins/{type}/{name}/run - plugin script or plugin itself

Interface
---------
Simple JSON messages, separated by the new line (\n).

Common message types
--------------------
Type - is basic part of any message. List of common types:
* init-done - initialization done
* info - log info
* warn - log warning
* error - log error

NOTICE
------
Make sure, that you disable output buffering in your plugin (ex. for C: `setbuf(stdout, NULL);` )
