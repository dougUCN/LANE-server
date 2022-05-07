#!/usr/bin/perl

# Find /dev/ttyUSB* associated with a FTDI-based USB to RS232 converter.
# This program creates a symbolic link based on
# the unique FTDI chip serial number of the physical device.
# The links are named ttyftdi#, where # is the chip serial number.
# Association of each /dev/ttyUSB is based on the output of the
# udevadm utility.
#
# udev rules would probably be a much better way to do this...
#
# directory for the symbolic links to the /dev/ttyUSB*

$sought_serial_number = $ARGV[0];
$port_label = $ARGV[1];

print "Looking for serial number ", $sought_serial_number, "\n";

$devlink_dir = $ENV{PWD} . "/ports";

# unique serial numbers of the FTDI 2232 chips
# %ftdi_serial_nums = ("A7032WB0", 1);

if(! -e $devlink_dir)
{
  # make a devices directory
  system "mkdir $devlink_dir";
}

# $linkname = $devlink_dir."/ttyftdi".$sought_serial_number;
$linkname = $devlink_dir."/". $port_label;
if( -l $linkname)
{
  unlink $linkname;
}

open(LSTTYUSB, "ls -1 /dev/ttyUSB* |");
@lsttyUSB = <LSTTYUSB>;
close LSTTYUSB;

print @lsttyUSB;

foreach $devname (@lsttyUSB)
{
  chomp $devname; $udev_command = "udevadm info -a -p \$(udevadm info -q path -n $devname)";
  print $udev_command . "\n";

  $found_product = 0;
  $found_serial_number = 0;
  $serial_number = "";
  open(UDEVINFO, $udev_command . " |");
  while(<UDEVINFO>)
  {
    if( /^\s*$/ ) {  # blank line
      $found_product = 0;
      $found_serial_number = 0;
      $serial_number = "";
    } elsif( /ATTRS\{product\}/ ) {
      if( m/\"FT232R USB UART\"/ ) {
        $found_product++;
      }
    } elsif( /ATTRS\{serial\}/ ) {
      print; 
#      system "ls -l $devname";
      if( m/\"(.*)\"/ ) {
        $found_serial_number++;
        $serial_number = $1;
      }
    }
    if( $found_product and $found_serial_number and ($serial_number eq $sought_serial_number)) {
      print "Found FT232R port: $serial_number\n";
      # $command = "ln -s $devname $devlink_dir/ttyftdi$serial_number";
      $command = "ln -s $devname $linkname";
      print $command . "\n";
      system $command;
      last;
    }
  } # end while <UDEVINFO>
  close UDEVINFO;


} # end while <LSTTYUSB>

exit 0;

