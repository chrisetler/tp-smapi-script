# Script for Interfacing with TP - Smapi
This script acts as a front end for viewing the battery information provided by tp-smapi, without
having to `cat` everything.

Use is pretty straight forward, simply `chmod +x ./tp-smapi-script.py` and execute.
On runtime, the script should display some basic statistics, followed by a list of options to view more details, or edit
thresholds, etc.

The following should be installed for this script to work properly:

1. modprobe
2. tp-smapi
3. sudo
4. python

Further, to make any changes, the user, using sudo, must have privileges to edit the battery's configuration.
See the Thinkpad or Archwiki pages on tp-smapi for more information.

This script has been tested only on Ubuntu 14.04 on an X220.
