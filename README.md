# AVX - Audio-Visual Control Extensions

[![Build Status](https://travis-ci.org/jamesremuscat/avx.svg?branch=master)](https://travis-ci.org/jamesremuscat/avx)
[![Coverage Status](https://coveralls.io/repos/jamesremuscat/avx/badge.svg?branch=master&service=github)](https://coveralls.io/github/jamesremuscat/avx?branch=master)

## Introduction

AVX is a library designed to allow control of A/V devices such as video
switchers and PTZ cameras.

It's designed to allow control of devices locally or over a network via Pyro4
RPC. A "Controller" process acts as an interface to the devices, and
controlling them is as straightforward as calling a method on the Controller
object.

Rich client applications can be built with Qt or your windowing toolkit of
choice, using Python and Pyro4 for communications.


## Installation & configuration

The easiest method of installing is via `pip`, which will take care of all
dependencies for you:

```sudo pip install avx```

You can also install from source with the usual `python setup.py install` routine.

AVX requires:

* Python 2.7
* enum34
* Pyro4
* pyserial
* pyusb
* setuptools
* semantic_version

Mapping of physical hardware devices through serial ports to virtual devices is
done in the `config.json` file. A typical definition of a single-device system
may look like:

```
{
  "devices" : [
    {
      "deviceID" : "Main",
      "class" : "avx.devices.serial.KramerVP88.KramerVP88",
      "options" : {
        "serialDevice" : "/dev/usb-ports/1-1.3.3:1.0",
        "machineNumber" : 1
      }
    }
  ]
}
```

Elements under "options" are passed directly as named parameters to the
constructor of the class. Most, but not all, current devices require
a `serialDevice` option.


Be sure to map devices based on their USB device path - `/dev/ttyUSBx`'es
might get swapped round after a reboot, which would break your configuration.
Scripts included under `scripts/etc/udev/rules.d` will create symlinks based on
device path, which relates to the physical port a device is plugged in to, in a
`/dev/usb-ports/` directory. This will not change unless you physically swap
the port a device is plugged in to.

Everything client-side will refer to the `deviceID` string you assign
to each device, so balance these between descriptive and concise.


## Running

You will need a Pyro4 nameserver running somewhere on your network. The
`runNameserver.sh` script will take care of this for you, or use the
`scripts/etc/systemd/pyro4-nsd.service` systemd script to install as a system
service. Systems still running initd can use `scripts/etc/init.d/pyro-nsd`.

The `runController.py` script will start a Controller instance and register it
with the Pyro4 nameserver, making it available to all machines on your network.
By default it will load a `config.json` configuration file, or whatever you
specify with -c on the commandline. Installing via pip/easy_install will
generate an `avx-controller` script which is run in the same way.

The controller machine can also use the `scripts/etc/systemd/avx-controller.service`
systemd script or `scripts/etc/init.d/avx-controller` init script to run the
controller as a daemon.


### Configuring IP address

By default avx will use the first IP address printed by `hostname -I` to
register with the nameserver. If you would like to use a different IP address
(e.g. for a different network adapter) you can set the `PYRO_IP` environment
variable, and that value will be used instead.

On systems without `hostname`, or where `hostname -I` does not produce the
required output, you should use the `PYRO_IP` environment variable.

## Using the HTTP interface

There's a basic HTTP interface built in. To enable it, ensure you have the
following in your config file ('options' should be a sibling of 'devices'):

```
  "options" : {
    "http" : true
  }
```

In addition, each device must have an `httpAccessible` option set to true for
it to be accessible via the HTTP interface.

By default the HTTP server will listen on port 8080 (currently hardcoded).

The URL scheme to call methods is:

```
http://server:8080/deviceID/method/option,option...
```

For example,

```
http://server:8080/Main/sendInputToOutput/2,1
```

will tell the video switcher with ID "Main" to send input 2 to output 1.

The controller will respond with an appropriate HTTP response code:
 * 200 - OK (followed by whatever data is returned by that method)
 * 400 - no such method
 * 403 - not permitted to call methods on that device over HTTP
 * 404 - no such device

## Logging

Starting the controller with a commandline flag of `-d` or `--debug` will
enable debugging messages.

A custom Python logging configuration may be provided in the controller config
file. If the key `logging` is present in the config, then its contents will be
passed directly to `logging.config.dictConfig`.

Using the `-d` flag when such a configuration is specified will overwrite the
default logger's level to `DEBUG` but leave other loggers unchanged.

## Supported Devices

Currently the devices best supported include:

* Blackmagic Design ATEM video switchers
* Blackmagic Design HyperDeck Studio recorders
* Kramer video switchers supporting Protocol 2000 over serial
  * e.g. VP-88
* Kramer 602 (non-Protocol 2000)
* Inline 3080 video switcher
* Kramer VP70x scan converters
* Coriogen Eclipse scan converter
* Sony VISCA PTZ cameras
* Datavideo PTC-150 PTZ camera
* ETC Unison lighting controller
* Several models of USB relay cards
* Philips amBx ambient lighting system
* MiLight / easybulb wireless bulbs
* Tivo (experimental)

In many cases support is partial but straightforward to improve - patches
welcome!

## Cross-client communication

`avx` includes a mechanism for cross-client, and controller-to-client, communication.
Clients should override the `handleMessage(msgType, source, data)` method to handle
messages, which are sent via the controller's `broadcast` method. All messages are
broadcast to all currently-connected clients. The arguments to `broadcast`, which are
the same as those to `handleMessage`, are:

 * `msgType`: string representing the type of message. Built-in message types are defined
   in `avx.Client.MessageTypes` or device-specific classes but client implementations are
   free to specify their own strings as required.
 * `source`: the origin of this message. When called from devices, this will be the device
   ID of the device that calls `broadcast`. Client implementations may use this field as
   required.
 * `data`: the message payload. May be any Python object, or `None`.

Clients may broadcast messages by calling `Controller.broadcast()` or by scheduling a
`BroadcastEvent`, for example as part of a macro sequence.

Built-in message types currently include:

 * `avx.Client.MessageTypes.OUTPUT_MAPPING`: sent by video switcher devices to describe their
   current output state. `source` will be the device ID of the switcher. `data` will be a
   `dict` whose keys are the numbered outputs of the switcher, and whose values are the
   numbered inputs. For example, a switcher currently displaying input 1 on output 4 may send
   the data

   ```{ 4: 1 }```

   Note that the complete state of the switcher may not be represented (a single message may
   only describe a single output state). Nor is it guaranteed that such a message will
   automatically be sent when a switcher changes state (the Inline IN3808, for example, only
   sends its state when asked for).

## Changelog

### v1.4.0 (tbd)

* List of connected clients is no longer written to the config file, but instead
  to its own state file under `/var/lib/avx/`.
* Added ATEM functions for upstream keyers and Super Source
* Added "synthetic" tally for ATEM switcher giving sources per M/E bus

### v1.3.1 (2018-12-02)

* Fixed Hyperdeck functionality.

### v1.3 (2018-11-21)

* Added support for Datavideo PTC-150 network DVIP control (VISCA-over-ethernet).

### v1.2.0 (2017-12-28)

* Controller will now try to reconnect and reproxy to connected clients if it
  is restarted.
* VISCA pan/tilt speeds adjusted for PTC-150
* Fixes and improvements to Hyperdeck functionality

### v1.1.0 (2017-11-29)

* Added support for Blackmagic Design ATEM video switchers. Functionality is partial
  and will be expanded in future releases.
* Added support for Blackmagic Design Hyperdeck Studio recorders. Transport functionality
  is complete (play, record, skip etc) but configuration is not yet supported.
* Added support for multiple VISCA cameras via one serial port. Define a VISCAPort in your
  configuration file and specify a "viscaPort" option against each of your camera devices.
* Added specific VISCA implementation for Datavideo PTC-150 cameras.
* Broadcasts are now logged at the `DEBUG` level rather than the `INFO` level.
* `broadcast()` may now be called without `data`, which defaults to `None`.
