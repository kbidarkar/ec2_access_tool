import boto.ec2
import re
import time


list_reg = boto.ec2.regions()

def list_all_regions():
    list_reg_name = []
    for j in list_reg:
        list_reg_name.append(str(j.name))
    return list_reg_name

def regions_key_pairs():
    for kk in list_reg:
        c = boto.ec2.connection.EC2Connection(region=kk)
        keys = c.get_all_key_pairs()
        print "\nKey Pairs for Region =>", kk.name
        for ks in keys:
            matches1 = re.match(r'([\w.]+):([\w.-]+)', str(ks))
            if matches1:
                ks1 = matches1.group(2)
                print ks1

def regions_security_groups():
    print "\nFollowing are the various Security Groups"
    for kk in list_reg:
        c = boto.ec2.connection.EC2Connection(region=kk)
        sgrp = c.get_all_security_groups()
        print "\nSecurity Group for Region =>", kk.name
        for sg in sgrp:
            matches1 = re.match(r'([\w.]+):([\w.]+\s?.*)', str(sg))
            if matches1:
                sg1 = matches1.group(2)
                print sg1

def regions_get_all_zones():
    print "\nFollowing are the various Zones available"
    for kk in list_reg:
        c = boto.ec2.connection.EC2Connection(region=kk)
        sgrp = c.get_all_zones()
        print "\nSecurity Group for Region =>", kk.name
        for sg in sgrp:
            matches1 = re.match(r'([\w.]+):([\w.-]+)', str(sg))
            if matches1:
                z1 = matches1.group(2)
                print z1

def launch_inst(region2, ami, min1, max1, key_nam, zone, type1, sgroup):
    connect_ec2 = boto.ec2.connect_to_region(region2)
    im_node = connect_ec2.get_image(ami)
    reservation_ids = im_node.run(min_count=min1, max_count=max1, key_name=key_nam, placement=zone, security_groups=[sgroup], instance_type=type1)
    print "\nFollowing are the Instance details\n"
    inst=reservation_ids.instances
    for v in inst:
        time.sleep(50)
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
                    print "Login with : ssh -i ~/"+key_nam+".pem root@"+v.public_dns_name
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
                return "found"
            else:
                print "This ip address doesn't match with this running instance"

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
                else:
                    print "This ip address doesn't match with the running instance"

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

def list_all_ec2RHELimages(region2, RV, TYP, ARCH):
    connect_ec2 = boto.ec2.connect_to_region(region2)
    imag_ids = connect_ec2.get_all_images()
    print "\nFollowing are the ec2-RHEL-images\n"
    print "\nRHEL", RV, "Images\n\n"
    access_images = []
    hourly_images = []
    for im in imag_ids:
        det = im.location
        if 'RHEL-'+RV in str(det):
            det1 = im.location
            if TYP in str(det1):
                det2 = im.location
                if ARCH in str(det2):
                    det3 = im.location
                    if 'Access2' in str(det3):
                        access_img = im.id+" "+im.location
                        access_images.append(access_img)
                    if 'Hourly2' in str(det3):
                        hourly_img = im.id+" "+im.location
                        hourly_images.append(hourly_img)
    print "\nAccess2 Images"
    for acc in access_images:
        print acc
    print "\nHourly2 Images"
    for hou in hourly_images:
        print hou

def noof_instances(region2):
    connect_ec2 = boto.ec2.connect_to_region(region2)
    reservation_ids = connect_ec2.get_all_instances()
    running_inst = []
    for ices in reservation_ids:
        inst=ices.instances
        for v in inst:
            if v.state == 'running':
                running_inst.append(v)
    print "\nThe No.of instances running in this region is", len(running_inst)

def list_all_runningInst(region2):
    connect_ec2 = boto.ec2.connect_to_region(region2)
    reservation_ids = connect_ec2.get_all_instances()
    running_inst = []
    stopped_inst = []
    stopping_inst = []
    pending_inst = []
    if not reservation_ids:
        print "\nNo running Instances, nothing to list"
        return
    print "\nFollowing are the Instances and their details\n"
    for ices in reservation_ids:
        inst=ices.instances
        for v in inst:
            if v.state == 'running':
                running_inst.append(v)
                print "InstanceId:", v.id, "\n\nPublic DNS:", v.public_dns_name
                print "Private DNS:", v.private_dns_name, "\nPrivate IP:", v.private_ip_address
                print "Launch Time:", v.launch_time
                print "Instance Type:", v.instance_type
                print "Instance Arch:", v.architecture
                print "Instance Placement:", v.placement
                print "Instance Key Name:", v.key_name
                imag_ids = connect_ec2.get_all_images(image_ids = str(v.image_id))
                for im in imag_ids:
                    det = im.location
                    matches1 = re.match(r'([\w.]+)/([\w.-]+)', det)
                    if matches1:
                        image_detail1 = matches1.group(2)
                    print "Image Id:", v.image_id, image_detail1
                print "====================\n"
            elif v.state == 'stopped':
                stopped_inst.append(v)
            elif v.state == 'stopping':
                stopping_inst.append(v)
            elif v.state == 'pending':
                pending_inst.append(v)
    if running_inst:
        print "The No.of instances running in this region is", len(running_inst)
        for ins in running_inst:
            print ins.id
    if stopped_inst:
        print "The No.of instances in stopped state in this region is", len(stopped_inst)
        for ins in stopped_inst:
            print ins.id
    if stopping_inst:
        print len(stopping_inst)," instances are shutting down"
        for ins in stopping_inst:
            print ins.id
    if pending_inst:
        print len(pending_inst)," instances are starting up"
        for ins in pending_inst:
            print ins.id

def tasks_all_instances(region2, task):
    connect_ec2 = boto.ec2.connect_to_region(region2)
    reservation_ids = connect_ec2.get_all_instances()
    if not reservation_ids:
        print "\nAll instances are in terminated state, nothing to terminate in this region"
        return
    for res1 in reservation_ids:
        inst=res1.instances
        for v in inst:
            nuked_list = []
            print "\n"+task+" instances :", v.id
            print "\nChecking the state of the instance"
            if task == 'terminate':
                if v.state != 'running' :
                    print "This node has already been "+v.state+", SKIPPING now"
                    continue
                nuked = connect_ec2.terminate_instances(str(v.id))
            elif task == 'stop':
                if v.state != 'running':
                    print "This node has already been "+v.state+" , SKIPPING now"
                    continue
                nuked = connect_ec2.stop_instances(str(v.id))
            elif task == 'reboot':
                if v.state != 'running':
                    print "This node is in "+v.state+" state, SKIPPING now"
                    continue
                nuked = connect_ec2.reboot_instances(str(v.id))
            elif task == 'start':
                if v.state != 'stopped':
                    print "This node is in "+v.state+" state, SKIPPING now"
                    continue
                nuked = connect_ec2.start_instances(str(v.id))

            for nu in nuked:
                nuked_list.append(nu.id)
            if v.id in nuked_list:
                print "\n"+task+" successful"
            else:
                print "\n"+task+" unsuccessful"

def instance_tasksnstatus(connect_ec2, task, v):
    nuked_list = []
    print "\nChecking the state of the instance"
    if task == 'terminate':
        print "\n"+task+" instance :", v.id
        if v.state != 'running' :
            print "This node has already been "+v.state+", SKIPPING now"
            return
        nuked = connect_ec2.terminate_instances(str(v.id))
    elif task == 'stop':
        print "\n"+task+" instance :", v.id
        if v.state != 'running':
            print "This node has already been "+v.state+" , SKIPPING now"
            return
        nuked = connect_ec2.stop_instances(str(v.id))
    elif task == 'reboot':
        print "\n"+task+" instance :", v.id
        if v.state != 'running':
            print "This node is in "+v.state+" state, SKIPPING now"
            return
        nuked = connect_ec2.reboot_instances(str(v.id))
    elif task == 'start':
        print "\n"+task+" instance :", v
        start = connect_ec2.start_instances(v)

    if task != 'start' and nuked:
        for nu in nuked:
            nuked_list.append(nu.id)
        if v.id in nuked_list:
            print "\n"+task+" successful"
        else:
            print "\n"+task+" unsuccessful"

def task_instances(region2, task, ip_insid):
    connect_ec2 = boto.ec2.connect_to_region(region2)
    reservation_ids = connect_ec2.get_all_instances()
    if 'i-' in ip_insid:
        instance_tasksnstatus(connect_ec2, task, ip_insid)
        return
    if not reservation_ids:
        print "\nAll instances are in terminated state, nothing to terminate in this region"
        return
    for res1 in reservation_ids:
        inst=res1.instances
        for v in inst:
            if v.state == 'running':
                if ip_insid in str(v.private_ip_address):
                    instance_tasksnstatus(connect_ec2, task, v)
                    return
    print "\nNo Instance found with the specified IP Address nor InstanceId:", ip_insid

def terminate_delete_instances(region2, tasks):
    print "\nTerminating all the instances in this REGION"
    tasks_all_instances(region2, tasks)
    connect_ec2 = boto.ec2.connect_to_region(region2)
    vol_ids = connect_ec2.get_all_volumes()
    if vol_ids:
        print "\nSleeping for 90 secs"
        time.sleep(90)
        print "\nDeleting all EBS volumes in this REGION, which are in the state AVAILABLE only"
        delete_ebs_volumes(region2)
    else:
        print "\nNo EBS Volumes found"
