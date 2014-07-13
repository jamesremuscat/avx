#!/usr/bin/perl -w

# A device path looks something like
# /devices/platform/bcm2708_usb/usb1/1-1/1-1.2/1-1.2:1.0/ttyUSB0/tty/ttyUSB0

@items = split("/", $ARGV[0]);

# Walk backwards along the path until we find a device:configuration.interface
# then print it out and exit

for ($i = @items - 1; $i > 0; $i--) {
    if ($items[$i] =~ m/^[0-9]-([0-9]+\.)+[0-9]+:[0-9]+\.[0-9]+$/) {
        print $items[$i] . "\n";
        last;
    }
}

