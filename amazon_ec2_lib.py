import boto.ec2
import re
import time


def list_all_regions():
    list_reg = boto.ec2.regions()
    list_reg_name = []
    for j in list_reg:
        list_reg_name.append(str(j.name))
    return list_reg_name

def launch_inst(region2, ami, min1, max1, key_nam, zone, type1, sgroup):
    connect_ec2 = boto.ec2.connect_to_region(region2)
    im_node = connect_ec2.get_image(ami)
    reservation_ids = im_node.run(min_count=min1, max_count=max1, key_name=key_nam, placement=zone, security_groups=[sgroup], instance_type=type1)
    print "\nFollowing are the Instance details\n"
    inst=reservation_ids.instances
    for v in inst:
        time.sleep(30)
        v.update()
        if v.state == 'running':
            print "InstanceId:", v.id, "\n\nPublic DNS:", v.public_dns_name
            print "Private DNS:", v.private_dns_name, "\nPrivate IP:", v.private_ip_address
            print "Launch Time:", v.launch_time
            print "VPC Id:", v.vpc_id
            imag_ids = connect_ec2.get_all_images(image_ids = str(v.image_id))
            for im in imag_ids:
                det = im.location
                matches1 = re.match(r'([\w.]+)/([\w.-]+)', det)
                if matches1:
                    image_detail1 = matches1.group(2)
                    print "Image Id:", v.image_id, image_detail1
                    print "====================\n"

def display_instanceInfo(region2, ins_id):
    connect_ec2 = boto.ec2.connect_to_region(region2)
    try:
        reservation_ids = connect_ec2.get_all_instances(instance_ids = ins_id)
    except:
        print "\nThe specified Instance is not found in this region, please recheck\n"
        return
    print "\nFollowing are the Instance details\n"
    for ices in reservation_ids:
        inst=ices.instances
        for v in inst:
            if v.state == 'running':
                print "InstanceId:", v.id, "\n\nPublic DNS:", v.public_dns_name
                print "Private DNS:", v.private_dns_name, "\nPrivate IP:", v.private_ip_address
                print "Launch Time:", v.launch_time
                print "VPC Id:", v.vpc_id
                imag_ids = connect_ec2.get_all_images(image_ids = str(v.image_id))
                for im in imag_ids:
                    det = im.location
                    matches1 = re.match(r'([\w.]+)/([\w.-]+)', det)
                    if matches1:
                        image_detail1 = matches1.group(2)
                    print "Image Id:", v.image_id, image_detail1
                    print "====================\n"

def find_instanceId(region2, ip_addr):
    connect_ec2 = boto.ec2.connect_to_region(region2)
    reservation_ids = connect_ec2.get_all_instances()
    if not reservation_ids:
        print "\nNo running Instances, nothing to list"
        return
    for ices in reservation_ids:
        inst=ices.instances
        for v in inst:
            if v.state == 'running':
                if ip_addr in str(v.private_ip_address):
                    print "InstanceId:", v.id, "\n\nPublic DNS:", v.public_dns_name
                    print "Private DNS:", v.private_dns_name, "\nPrivate IP:", v.private_ip_address
                    print "Launch Time:", v.launch_time
                    print "VPC Id:", v.vpc_id
                    imag_ids = connect_ec2.get_all_images(image_ids = str(v.image_id))
                    for im in imag_ids:
                        det = im.location
                        matches1 = re.match(r'([\w.]+)/([\w.-]+)', det)
                        if matches1:
                            image_detail1 = matches1.group(2)
                        print "Image Id:", v.image_id, image_detail1
                        print "====================\n"
                    return "found"

def delete_ebs_volumes(region2):
    connect_ec2 = boto.ec2.connect_to_region(region2)
    vol_ids = connect_ec2.get_all_volumes()
    if not vol_ids:
        print "\nNo EBS volumes to delete"
        return
    for vol in vol_ids:
        if vol.status == 'available':
            connect_ec2.delete_volume(vol.id)
            print "\nDeleted the EBS volume with id", vol.id, "successfully"
        else:
            print "\nThe below disk has not been deleted as it's current status is : ", vol.status
            print vol.id

def list_all_ec2RHELimages(region2):
    connect_ec2 = boto.ec2.connect_to_region(region2)
    imag_ids = connect_ec2.get_all_images()
    print "\nFollowing are the ec2-RHEL-images\n"
    print "\nRHEL 5 Images\n\n"
    for im in imag_ids:
        det = im.location
        if 'RHEL-5' in str(det):
            det1 = im.location
            if 'Hourly2' or 'Access2' in str(det1):
                print im.id, im.location
    print "\nRHEL 6 Images\n\n"
    for im in imag_ids:
        det = im.location
        if 'RHEL-6' in str(det):
            det1 = im.location
            if 'Hourly2' or 'Access2' in str(det1):
                print im.id, im.location

def list_all_runningInst(region2):
    connect_ec2 = boto.ec2.connect_to_region(region2)
    reservation_ids = connect_ec2.get_all_instances()
    if not reservation_ids:
        print "\nNo running Instances, nothing to list"
        return
    print "\nFollowing are the running Instances and their details\n"
    for ices in reservation_ids:
        inst=ices.instances
        for v in inst:
            if v.state == 'running':
                print "InstanceId:", v.id, "\n\nPublic DNS:", v.public_dns_name
                print "Private DNS:", v.private_dns_name, "\nPrivate IP:", v.private_ip_address
                print "Image Id:", v.image_id
                print "Launch Time:", v.launch_time
                imag_ids = connect_ec2.get_all_images(image_ids = str(v.image_id))
                for im in imag_ids:
                    det = im.location
                    matches1 = re.match(r'([\w.]+)/([\w.-]+)', det)
                    if matches1:
                        image_detail1 = matches1.group(2)
                    print "Image Id:", v.image_id, image_detail1
                print "VPC Id:", v.vpc_id
                print "====================\n"

def terminate_all_instances(region2):
    connect_ec2 = boto.ec2.connect_to_region(region2)
    reservation_ids = connect_ec2.get_all_instances()
    if not reservation_ids:
        print "\nAll instances are in terminated state, nothing to terminate in this region"
        return
    for res1 in reservation_ids:
        inst=res1.instances
        for v in inst:
            print "\nChecking the state of the instance"
            if v.state != 'running' :
                print "This node has already been terminated, SKIPPING now"
                continue
            print "\nTerminating the instance :", v.id
            connect_ec2.terminate_instances(str(v.id))
            print "\nTermination successful"

def terminate_delete_instances(region2):
    print "\nTerminating all the instances in this REGION"
    terminate_all_instances(region2)
    connect_ec2 = boto.ec2.connect_to_region(region2)
    vol_ids = connect_ec2.get_all_volumes()
    if vol_ids:
        print "\nSleeping for 90 secs"
        time.sleep(90)
        print "\nDeleting all EBS volumes in this REGION, which are in the state AVAILABLE only"
        delete_ebs_volumes(region2)
    else:
        print "\nNo EBS Volumes found"


