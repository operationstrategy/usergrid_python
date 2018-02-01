#!/bin/bash

ELBName=$1
ACTION=$2
instid=`wget -q -O - http://169.254.169.254/latest/meta-data/instance-id`

case $ACTION in

  add)
      echo "Adding to ELB: ${ELBName}"
      aws elb register-instances-with-load-balancer --load-balancer-name ${ELBName} --instances ${instid}
      ;;

  remove)
      echo "Removing from ELB: ${ELBName}"
      aws elb deregister-instances-from-load-balancer --load-balancer-name ${ELBName} --instances ${instid}
      sleep 3
      ;;

  *)
      exit 0
      ;;

esac
