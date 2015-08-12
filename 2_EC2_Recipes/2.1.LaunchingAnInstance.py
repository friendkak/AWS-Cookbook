__author__ = 'Shravan Papanaidu'
import os
import time
import boto
import boto.ec2
import boto.manage.cmdshell

def launch_instance(ami='ami-d114f295',
                    instance_type='t2.micro',
                    key_name='spapanaidu',
                    key_extension='.pub',
                    key_dir='C:\\Workspace\\ssh\\non_prod\\',
                    group_name='sg',
                    ssh_port=22,
                    cidr='0.0.0.0/0',
                    tag='sg',
                    user_data=None,
                    cmd_shell=True,
                    login_user='ec2-user',
                    ssh_passwd=None):
    cmd = None
# Create a connection to EC2 service.
# You can pass credentials in to the connect_ec2 method explicitly
# or you can use the default credentials in your ~/.boto config file
# as we are doing here.

    ec2 = boto.ec2.connect_to_region("us-west-1")
    # ec2 = boto.connect_ec2(aws_access_key_id='',
    #                        aws_secret_access_key='')
    instances = ec2.get_all_instances()

# Check to see if specified keypair already exists.
# If we get an InvalidKeyPair.NotFound error back from EC2,
# it means that it doesn't exist and we need to create it.
    try:
        key = ec2.get_key_pair('spapanaidu')
    except ec2.ResponseError, e:
        if e.code == 'InvalidKeyPair.NotFound':
            print 'Creating keypair %s' %key_name
            key = ec2.create_key_pair(key_name)
            key.save(key_dir)
        else:
            raise
# Check to see if specified security group already exists.
# If we get an InvalidGroup.NotFound error back from EC2,
# it means that it doesn't exist and we need to create it.
    try:
        group = ec2.get_all_security_groups(groupnames=[group_name])[0]
    except ec2.ResponseError, e:
        if e.code == "InvalidGroup.NotFound":
            print 'Creating Security group: %s' %group_name
            group = ec2.create_security_group(group_name, "Allow SSH")
        else:
            raise
#Add SSH rule to Security group
    try:
        group.authorize('tcp',ssh_port,ssh_port, cidr)
    except ec2.ResponseError, e:
        if e.code == 'InvalidPermission.Duplicate':
            print 'Security group %s already authorized' % group_name
        else:
            raise
# Now start up the instance. The run_instances method
# has many, many parameters but these are all we need
# for now.
    reservation = ec2.run_instances(ami,
                                    key_name=key_name,
                                    security_groups=[group_name],
                                    instance_type=instance_type,
                                    user_data=user_data)
# Find the actual Instance object inside the Reservation object
# returned by EC2.
    instance = reservation.instances[0]

# The instance has been launched but it's not yet up and
# running. Let's wait for its state to change to 'running'.
    print 'Waiting for the instance'
    while instance.state != 'running':
        print '.'
        time.sleep(5)
        instance.update()
    print 'done'

# Let's tag the instance with the specified label so we can
# identify it later.
    instance.add_tag(tag)

# The instance is now running, let's try to programmatically
# SSH to the instance using Paramiko via boto CmdShell.

    # if cmd_shell:
    #     key_path = os.path.join(key_dir,key_name,'.pem')
    #     cmd = boto.manage.cmdshell.sshclient_from_instance(instance,key_path,user_name=login_user)

    return (instance)

print launch_instance()