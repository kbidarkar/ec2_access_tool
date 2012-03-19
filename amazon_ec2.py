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
import rhui_lib

region_parser = argparse.ArgumentParser(add_help=False)
region_parser.add_argument('-r','--region', action='store', metavar='REG', required=True, help='Specify the region to connect')
#region_parser.add_argument('-ex','--exclude', action='store', metavar='EXC', help='Excludes specified regions when selecting ALL the regions')

parser = argparse.ArgumentParser(description='Amazon EC2 Cloud Tool')
subparsers = parser.add_subparsers(title="Supported Commands", dest='subparser_name')

parser_regions = subparsers.add_parser("regions", help="Query things related to your amazon ec2 account")
group_regions = parser_regions.add_mutually_exclusive_group(required=True)
group_regions.add_argument('-l','--list', action='store_const', const=True , default=False, help='Displays all the available REGIONS')
group_regions.add_argument('-kp','--key-pairs', action='store_const', const=True , default=False, help='Displays all the available key pairs in all the regions')
group_regions.add_argument('-sg','--security-groups', action='store_const', const=True , default=False, help='Displays all the security group names in all the regions')
group_regions.add_argument('-z','--zones', action='store_const', const=True , default=False, help='Displays all the zones in all the regions')

parser_list = subparsers.add_parser("list", help="Lists info related to ami's and instances at ec2 of a specified region", parents=[region_parser])
group_list = parser_list.add_mutually_exclusive_group(required=True)
group_list.add_argument('-img','--list-allimages', action='store_const', const=True, default=False, help='Lists all the EC2 images in a specified region')
parser_list.add_argument('-t','--img-type', action='store', metavar='TYP', default='Starter-EBS', help='The type of ami. Ex:- OpenShift, default=Starter-EBS, MRG-Grid')
parser_list.add_argument('-rv','--rhel-version', action='store', metavar='RV', default='6.2', help='Specify the rhel version. default=6.2. Ex:- 5.5 to 5.8/ 6.0 to 6.2')
parser_list.add_argument('-hw','--arch', action='store', metavar='ARCH', default='x86_64', help='Specify the architecture i386 or x86_64. default=x86_64')
group_list.add_argument('-ins','--list-allinstances', action='store_const', const=True, default=False, help='Lists only the running instances in a specified region')
group_list.add_argument('-n','--noof-instances', action='store_const', const=True, default=False, help='Specifies the total number of instances running in a region')

parser_nukes = subparsers.add_parser("nukes", help="Nuke a region by terminating all instances and/or deleting all EBS volumes, Caution: Removes everything", parents=[region_parser])
group_nukes = parser_nukes.add_mutually_exclusive_group(required=True)
group_nukes.add_argument('-c','--clear-all', action='store_const', const=True, default=False, help='Terminates all instances & deletes all EBS volumes in a specified region')
group_nukes.add_argument('-t','--terminate-allinstances', action='store_const', const=True, default=False, help='Terminates all the instances in the specified region')
group_nukes.add_argument('-off','--stop-allinstances', action='store_const', const=True, default=False, help='Stop all the instances in the specified region')
group_nukes.add_argument('-rs','--reboot-allinstances', action='store_const', const=True, default=False, help='Restarts all the instances in the specified region')
group_nukes.add_argument('-on','--start-allinstances', action='store_const', const=True, default=False, help='Start all the instances in the specified region')
group_nukes.add_argument('-d','--delete-allebsvols', action='store_const', const=True, default=False, help='Deletes all the EBS volumes in a specified region')


parser_destroy = subparsers.add_parser("destroy", help="Destroy by terminating an instance and/or deleting an EBS volume in a region", parents=[region_parser])
group_destroy = parser_destroy.add_mutually_exclusive_group(required=True)
group2_destroy = parser_destroy.add_mutually_exclusive_group(required=True)
group_destroy.add_argument('-t','--terminate-aninstance', action='store_const', const=True, default=False, help='Terminate an instance in the specified region')
group_destroy.add_argument('-off','--stop-aninstance', action='store_const', const=True, default=False, help='Stop an instance in the specified region')
group_destroy.add_argument('-rs','--reboot-aninstance', action='store_const', const=True, default=False, help='Restart an instance in the specified region')
group_destroy.add_argument('-on','--start-aninstance', action='store_const', const=True, default=False, help='Start an instance in the specified region')
#group_destroy.add_argument('-d','--delete-ebsvol', action='store_const', const=True, default=False, help='Deletes EBS volume in a specified region')
group2_destroy.add_argument('-ip','--ipaddress', action='store', metavar='IPADDR', help='The ip address of the node to switch off')
group2_destroy.add_argument('-id','--instanceid', action='store', metavar='INSID', help='The instanceid of the instance to switch ON')

parser_launch = subparsers.add_parser("launch", help="Launch  instances at ec2", parents=[region_parser])
parser_launch.add_argument('-ami','--ami-id', action='store', metavar='AMIID', required=True, help='The ami-id(x86_64 only) to be used to launch the instances')
parser_launch.add_argument('-min','--min-instances', action='store', metavar='MIN', default='1', help='The minimum number of instances to be launched, By default: -min 1')
parser_launch.add_argument('-max','--max-instances', action='store', metavar='MAX', default='1', help='The maximum number of instances to be launched, By default: -max 1')
parser_launch.add_argument('-key','--key-name', action='store', metavar='KNAM', required=True, help='The key name for the specified region')
parser_launch.add_argument('-zone','--placement-zone', action='store', metavar='ZNAM', choices='abc', default='b', help='The zone in which the instance is to be launched')
parser_launch.add_argument('-type','--instance-type', action='store', metavar='TYPE', default='m1.large', help='Hardware profile of the instance, By default: -type m1.large')
parser_launch.add_argument('-sg','--security-group', action='store', metavar='SGRP', default='default',help='Security group the instance to be placed, By default: -sg default')

parser_transfer = subparsers.add_parser("remote", help="Transfer various files to ec2")
group_transfer = parser_transfer.add_mutually_exclusive_group(required=True)
group_transfer.add_argument('-p','--put-files', action='store_const', const=True, default=False, help='PUT a specified file into an instance')
group_transfer.add_argument('-g','--get-files', action='store_const', const=True, default=False, help='GET a specified file from an instance')
group_transfer.add_argument('-e','--execute', action='store_const', const=True, default=False, help='Executes a specified command on an instance')
parser_transfer.add_argument('-puh','--public-dns', action='store', metavar='PUB', required=True, help='The public dns hostname of an instance to connect')
parser_transfer.add_argument('-key','--key-name', action='store', metavar='KNAM', required=True, help='The key name to connect to the specified instance')
parser_transfer.add_argument('-src','--source-location', action='store', metavar='SRC', help='The src location of the file to be uploaded or downloaded')
parser_transfer.add_argument('-des','--destination-location', action='store', metavar='DES', help='The destination location of the file to be uploaded or downloaded')
parser_transfer.add_argument('-cmd','--command', action='store', metavar='CMMD', help='The command to be run on the instance')

#parser_security = subparsers.add_parser("security", help="Work with security features of  ec2", parents=[region_parser])
#group_security = parser_security.add_mutually_exclusive_group(required=True)
#group_security.add_argument('-c','--clone-sginnewregion', action='store', metavar='NEWREG', default=False, help='Clones the specified  Security Group to a new REGION')
#parser_security.add_argument('-sg','--security-group', action='store', metavar='SGRP', required=True, help='Security group name to be cloned to another region')
#group_security.add_argument('-ins','--list-instances', action='store_const', const=True, default=False, help='Lists the instances which use the specified Security Group')
#group_security.add_argument('-ar','--add-rule', action='store_const', const=True, help='Adds a rule to the security group')
#group_security.add_argument('-dr','--delete-rule', action='store_const', const=True, help='Deletes a rule from the security group')


parser_search = subparsers.add_parser("search", help="Search the amazon ec2 for various information", parents=[region_parser])
group_search = parser_search.add_mutually_exclusive_group(required=True)
group_search.add_argument('-id','--instanceid', action='store', metavar='INSID', help='Displays in detail information of a launched instance')
group_search.add_argument('-ip','--ipaddress', action='store', metavar='IPADDR', help='Displays detailed instance info by providing ip address')


args = parser.parse_args()

list_reg_name = amazon_ec2_lib.list_all_regions()
def print_region_info():
    for regions in list_reg_name:
        print regions

def call_nukes(region):
    if args.clear_all:
        amazon_ec2_lib.terminate_delete_instances(region, 'terminate')
    if args.terminate_allinstances:
        amazon_ec2_lib.tasks_all_instances(region, 'terminate')
    if args.stop_allinstances:
        amazon_ec2_lib.tasks_all_instances(region, 'stop')
    if args.reboot_allinstances:
        amazon_ec2_lib.tasks_all_instances(region, 'reboot')
    if args.start_allinstances:
        amazon_ec2_lib.tasks_all_instances(region, 'start')
    if args.delete_allebsvols:
        amazon_ec2_lib.delete_ebs_volumes(region)

def call_destroy(region, IPADDR, INSID):
    if args.terminate_aninstance:
        amazon_ec2_lib.task_instances(region, 'terminate', IPADDR)
    if args.stop_aninstance:
        amazon_ec2_lib.task_instances(region, 'stop', IPADDR)
    if args.reboot_aninstance:
        amazon_ec2_lib.task_instances(region, 'reboot', IPADDR)
    if args.start_aninstance:
        amazon_ec2_lib.task_instances(region, 'start', INSID)
#    if args.delete_ebsvol:
#        amazon_ec2_lib.delete_ebs_volumes(region, IPADDR)

def call_list(region, RV, TYP, ARCH):
    if args.list_allimages:
        amazon_ec2_lib.list_all_ec2RHELimages(region, RV, TYP, ARCH)
    if args.list_allinstances:
        amazon_ec2_lib.list_all_runningInst(region)
    if args.noof_instances:
        amazon_ec2_lib.noof_instances(region)


def call_remote (PUB, KNAM, SRC, DES, CMD):
    if args.put_files:
        rhui_lib.putfile(PUB, KNAM, SRC, DES)
    if args.get_files:
        rhui_lib.getfile(PUB, KNAM, SRC, DES)
    if args.execute:
        rhui_lib.remote_exe(PUB, KNAM, CMD)

def call_search(region, IPADDR, INSID):
    if args.instanceid:
        stat = amazon_ec2_lib.display_instanceInfo(region, INSID)
        return stat
    if args.ipaddress:
        stat = amazon_ec2_lib.find_instanceId(region, IPADDR)
        return stat

if args.subparser_name == 'regions':
    if args.list:
        print "\nFollowing are the Regions:"
        print_region_info()
    if args.key_pairs:
        amazon_ec2_lib.regions_key_pairs()
    if args.security_groups:
        amazon_ec2_lib.regions_security_groups()
    if args.zones:
        amazon_ec2_lib.regions_get_all_zones()

elif args.subparser_name == 'launch':
    REG = args.region
    AMIID = args.ami_id
    MIN = args.min_instances
    MAX = args.max_instances
    KNAM = args.key_name
    ZNAM = args.placement_zone
    ZONE = REG + ZNAM
    TYPE = args.instance_type
    SGRP = args.security_group
    amazon_ec2_lib.launch_inst(REG, AMIID, MIN, MAX, KNAM, ZONE, TYPE, SGRP)

elif args.subparser_name == 'list':
    RV = args.rhel_version
    TYP = args.img_type
    REG = args.region
    ARCH = args.arch
    if args.region and REG == "all":
        for reg in list_reg_name:
            print "\nWorking with the Region :", reg
            call_list(reg,RV,TYP,ARCH)
    elif args.region and REG in list_reg_name:
        print "\nWorking with the Region :", REG
        call_list(REG,RV,TYP,ARCH)
    elif args.region:
        print "\nPlease select the correct region"
        print_region_info()
        print "all"

elif args.subparser_name == 'nukes':
    REG = args.region
    if args.region and REG == "all":
        for reg in list_reg_name:
            print "\nWorking with the Region :", reg
            call_nukes(reg)
    elif args.region and REG in list_reg_name:
        print "\nWorking with the Region :", REG
        call_nukes(REG)
    elif args.region:
        print "\nPlease select the correct region"
        print_region_info()
        print "all"

elif args.subparser_name == 'destroy':
    IPADDR = args.ipaddress
    REG = args.region
    INSID = args.instanceid
    if args.region and REG == "all":
        for reg in list_reg_name:
            print "\nWorking with the Region :", reg
            call_destroy(reg, IPADDR, INSID)
    elif args.region and REG in list_reg_name:
        print "\nWorking with the Region :", REG
        call_destroy(REG, IPADDR, INSID)
    elif args.region:
        print "\nPlease select the correct region"
        print_region_info()
        print "all"

elif args.subparser_name == 'search':
    REG = args.region
    INSID = args.instanceid
    IPADDR = args.ipaddress
    if args.region and REG == "all":
        for reg in list_reg_name:
            print "\nWorking with the Region :", reg
            stat = call_search(reg, IPADDR, INSID)
            if stat == "found":
                break
    elif args.region and REG in list_reg_name:
        print "\nWorking with the Region :", REG
        call_search(REG, IPADDR, INSID)
    elif args.region:
        print "\nPlease select the correct region"
        print_region_info()
        print "all"

elif args.subparser_name == 'remote':
    PUB = args.public_dns
    KNAM = args.key_name
    SRC = args.source_location
    DES = args.destination_location
    CMMD = args.command
    call_remote(PUB, KNAM, SRC, DES, CMMD)
