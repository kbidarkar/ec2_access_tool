#!/usr/bin/python -tt
################################################################################
# Authors: Kedar Bidarkar <kbidarka@redhat.com>
# ################################################################################
#Please refer the accounts page (http://aws.amazon.com/account/ under security credentials)
#of amazon site for your access details (Access Keys :- access_key_id and secret_access_key).
#Please configure boto.cfg under /etc/  as below
#[Credentials]
#aws_access_key_id = xxxx
#aws_secret_access_key = xxxx

import argparse
import sys
import amazon_ec2_lib

usage = "amazon_ec2.py [-h] -l\
\n\t\t\t  -r REG (-c | -t | -d | -img | -ins | -f IPADDR | -di INSID)\n\
\t\t\t\t  -li [-ami AMIID*] [-min MIN] [-max MAX] [-key KNAM*] [-zone ZONE*] [-type TYPE] [-sg SGRP]"
parser = argparse.ArgumentParser(description='Amazon EC2 Cloud Tool ', usage=usage)
group = parser.add_mutually_exclusive_group(required=True)
group1 = parser.add_mutually_exclusive_group(required=False)

group.add_argument('-l','--list-regions', action='store_const', const=True, default=False, help='displays all the available REGIONS')
group.add_argument('-r','--region', action='store', metavar='REG', help='specify the region to connect.')
group1.add_argument('-c','--clear-all', action='store_const', const=True, default=False, help='terminates all instances and deletes all EBS volumes in the specified region')
group1.add_argument('-t','--terminate-allinstances', action='store_const', const=True, default=False, help='terminates all the instances in the specified region')
group1.add_argument('-d','--delete-allebsvols', action='store_const', const=True, default=False, help='deletes all the EBS volumes in a specified region')
group1.add_argument('-img','--list-allimages', action='store_const', const=True, default=False, help='lists all the EC2 images in a specified region')
group1.add_argument('-ins','--list-allinstances', action='store_const', const=True, default=False, help='lists only the running instances in a specified region')
group1.add_argument('-f','--find-instanceid', action='store', metavar='IPADDR', help='find the InstanceId using the private_ipaddress in a specified region')
group1.add_argument('-di','--display-instanceinfo', action='store', metavar='INSID', help='displays an instance info using the instanceId in a specified region')
group1.add_argument('-li','--launch-instances', action='store_const', const=True, default=False, 
help='launch an instance in a specified region, Requires -ami and -type for launching')
parser.add_argument('-ami','--ami-id', action='store', metavar='AMIID',
help='The ami-id to be used to launch the instances, * signifies mandatory')
parser.add_argument('-min','--min-instances', action='store', metavar='MIN', default='1', help='the minimum number of instances to be launched, By default: -min 1')
parser.add_argument('-max','--max-instances', action='store', metavar='MAX', default='1', help='the maximum number of instances to be launched, By default: -max 1')
parser.add_argument('-key','--key-name', action='store', metavar='KNAM',
help='the key name for the specified region, * signifies mandatory')
parser.add_argument('-type','--instance-type', action='store', metavar='TYPE', default='m1.large', help='the hardware profile of the instance, By default: -type m1.large')
parser.add_argument('-sg','--security-group', action='store', metavar='SGRP', default='default',help='the security group in which the instance is to be placed, By default: -sg default')
args = parser.parse_args()

if args.region:
    if not (args.clear_all or
            args.terminate_allinstances or args.delete_allebsvols or
            args.list_allimages or args.list_allinstances or
            args.find_instanceid or args.display_instanceinfo or
            args.launch_instances):
        parser.print_help()
        parser.error('Please select atleast one action to be performed with \
the specified region')

if args.launch_instances:
    if not (args.ami_id and args.min_instances and args.max_instances and
        args.key_name and args.placement_zone and args.instance_type and
        args.security_group):
        parser.print_help()
        parser.error('Please provide all the necessary information for \
launching an instance')

REG = args.region
INSID = args.display_instanceinfo
IPADDR = args.find_instanceid
AMIID = args.ami_id
MIN = args.min_instances
MAX = args.max_instances
KNAM = args.key_name
ZONE = REG+'b'
TYPE = args.instance_type
SGRP = args.security_group

if args.list_regions or args.region:
    list_reg_name = amazon_ec2_lib.list_all_regions()
    if args.list_regions:
        print "\nFollowing are the Regions:"
        for regions in list_reg_name:
            print regions


if args.region and REG == "all":
    for reg in list_reg_name:
        print "\nWorking with the Region :", reg
        if args.clear_all:
            amazon_ec2_lib.terminate_delete_instances(reg)
        if args.terminate_allinstances:
            amazon_ec2_lib.terminate_all_instances(reg)
        if args.delete_allebsvols:
            amazon_ec2_lib.delete_ebs_volumes(reg)
        if args.list_allimages:
            amazon_ec2_lib.list_all_ec2RHELimages(reg)
        if args.list_allinstances:
            amazon_ec2_lib.list_all_runningInst(reg)
        if args.find_instanceid:
            stat = amazon_ec2_lib.find_instanceId(reg, IPADDR)
            if stat == "found":
                break
        if args.display_instanceinfo:
            amazon_ec2_lib.display_instanceInfo(reg, INSID)
elif args.region and REG in list_reg_name:
    print "\nWorking with the Region :", REG
    if args.clear_all:
        amazon_ec2_lib.terminate_delete_instances(REG)
    if args.terminate_allinstances:
        amazon_ec2_lib.terminate_all_instances(REG)
    if args.delete_allebsvols:
        amazon_ec2_lib.delete_ebs_volumes(REG)
    if args.list_allimages:
        amazon_ec2_lib.list_all_ec2RHELimages(REG)
    if args.list_allinstances:
        amazon_ec2_lib.list_all_runningInst(REG)
    if args.display_instanceinfo:
        amazon_ec2_lib.display_instanceInfo(REG, INSID)
    if args.find_instanceid:
        amazon_ec2_lib.find_instanceId(REG, IPADDR)
    if args.launch_instances:
        amazon_ec2_lib.launch_inst(REG, AMIID, MIN, MAX, KNAM, ZONE, TYPE, SGRP)
elif args.region:
    print "\nPlease select the correct region"
    for regions in list_reg_name:
        print regions
    print "all"
