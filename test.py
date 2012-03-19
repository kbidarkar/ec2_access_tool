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

region_parser = argparse.ArgumentParser(add_help=False)
region_parser.add_argument('-r','--region', action='store', metavar='REG', required=True, help='specify the region to connect')

parser = argparse.ArgumentParser(description='Amazon EC2 Cloud Tool')
subparsers = parser.add_subparsers(title="Supported Commands", dest='subparser_name')

parser_regions = subparsers.add_parser("regions", help="query things related to amazon ec2")
group_regions = parser_regions.add_mutually_exclusive_group(required=True)
group_regions.add_argument('-l','--list', action='store_const', const=True , default=False, help='displays all the available REGIONS')
group_regions.add_argument('-kp','--key-pairs', action='store_const', const=True , default=False, help='displays all the available key pairs')

parser_list = subparsers.add_parser("list", help="lists various stuff related to ami's and instances", parents=[region_parser])
group_list = parser_list.add_mutually_exclusive_group(required=True)
group_list.add_argument('-img','--list-allimages', action='store_const', const=True, default=False, help='lists all the EC2 images in a specified region')
group_list.add_argument('-ins','--list-allinstances', action='store_const', const=True, default=False, help='lists only the running instances in a specified region')

parser_destroy = subparsers.add_parser("destroy", help="destroy by terminating instances or deleting EBS volumes", parents=[region_parser])
group_destroy = parser_destroy.add_mutually_exclusive_group(required=True)
group_destroy.add_argument('-c','--clear-all', action='store_const', const=True, default=False, help='terminates all instances & deletes all EBS volumes in a specified region')
group_destroy.add_argument('-t','--terminate-allinstances', action='store_const', const=True, default=False, help='terminates all the instances in the specified region')
group_destroy.add_argument('-d','--delete-allebsvols', action='store_const', const=True, default=False, help='deletes all the EBS volumes in a specified region')

parser_launch = subparsers.add_parser("launch", help="launch  instances", parents=[region_parser])
parser_launch.add_argument('-ami','--ami-id', action='store', metavar='AMIID', required=True, help='The ami-id to be used to launch the instances')
parser_launch.add_argument('-min','--min-instances', action='store', metavar='MIN', default='1', help='the minimum number of instances to be launched, By default: -min 1')
parser_launch.add_argument('-max','--max-instances', action='store', metavar='MAX', default='1', help='the maximum number of instances to be launched, By default: -max 1')
parser_launch.add_argument('-key','--key-name', action='store', metavar='KNAM', help='the key name for the specified region')
parser_launch.add_argument('-zone','--placement-zone', action='store', metavar='ZONE', help='the zone in which the instance is to be launched')
parser_launch.add_argument('-type','--instance-type', action='store', metavar='TYPE', default='m1.large', help='hardware profile of the instance, By default: -type m1.large')
parser_launch.add_argument('-sg','--security-group', action='store', metavar='SGRP', default='default',help='security group the instance to be placed, By default: -sg default')

parser_transfer = subparsers.add_parser("transfer", help="trabsfer various files to ec2", parents=[region_parser])

args = parser.parse_args()

#INSID = args.display_instanceinfo
#IPADDR = args.find_instanceid

list_reg_name = amazon_ec2_lib.list_all_regions()
def print_region_info():
    for regions in list_reg_name:
        print regions

def call_destroy(region):
    if args.clear_all:
        amazon_ec2_lib.terminate_delete_instances(region)
    if args.terminate_allinstances:
        amazon_ec2_lib.terminate_all_instances(region)
    if args.delete_allebsvols:
        amazon_ec2_lib.delete_ebs_volumes(region)

def call_list(region):
    if args.list_allimages:
        amazon_ec2_lib.list_all_ec2RHELimages(region)
    if args.list_allinstances:
        amazon_ec2_lib.list_all_runningInst(region)

if args.subparser_name == 'regions':
    if args.list:
        print "\nFollowing are the Regions:"
        print_region_info()
    if args.key_pairs:
        amazon_ec2_lib.regions_key_pairs()
elif args.subparser_name == 'launch':
    REG = args.region
    AMIID = args.ami_id
    MIN = args.min_instances
    MAX = args.max_instances
    KNAM = args.key_name
    ZONE = REG + 'b'
    TYPE = args.instance_type
    SGRP = args.security_group
    if args.launch_instances:
        amazon_ec2_lib.launch_inst(REG, AMIID, MIN, MAX, KNAM, ZONE, TYPE, SGRP)
elif args.subparser_name == 'list':
    REG = args.region
    if args.region and REG == "all":
        for reg in list_reg_name:
            print "\nWorking with the Region :", reg
            call_list(reg)
    elif args.region and REG in list_reg_name:
        print "\nWorking with the Region :", REG
        call_list(REG)
    elif args.region:
        print "\nPlease select the correct region"
        print_region_info()
        print "all"
elif args.subparser_name == 'destroy':
    REG = args.region
    if args.region and REG == "all":
        for reg in list_reg_name:
            print "\nWorking with the Region :", reg
            call_destroy(reg)
    elif args.region and REG in list_reg_name:
        print "\nWorking with the Region :", REG
        call_destroy(REG)
    elif args.region:
        print "\nPlease select the correct region"
        print_region_info()
        print "all"
#elif args.subparser_name == 'search':

#        if args.find_instanceid:
#            stat = amazon_ec2_lib.find_instanceId(reg, IPADDR)
#            if stat == "found":
#                break
#        if args.display_instanceinfo:
#            amazon_ec2_lib.display_instanceInfo(reg, INSID)
#    if args.display_instanceinfo:
#        amazon_ec2_lib.display_instanceInfo(REG, INSID)
#    if args.find_instanceid:
#        amazon_ec2_lib.find_instanceId(REG, IPADDR)
