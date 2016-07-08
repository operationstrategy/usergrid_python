#!/bin/bash -x

set -u
set -e


# get the date and build number for the deb filename
NOW=`date +%F.%H.%M`
DEBFILENAME="usergrid_python_$NOW.$BUILD_NUMBER.deb"
echo DEBFILENAME = $DEBFILENAME
./deb-pkg/create-deb.sh "$DEBFILENAME"

# debian file created

# chown everything back to jenkins:jenkins so the 
# workspace can be destroyed if desired.
sudo chown -R jenkins:jenkins *




