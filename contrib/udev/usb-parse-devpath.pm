#!/usr/bin/perl -w

@items = split("/", $ARGV[0]);
for ($i = 0; $i < @items; $i++) {
    if ($items[$i] =~ m/^usb[0-9]+$/) {
        print $items[$i + 4] . "\n";
        last;
    }
}
