__author__ = 'Shravan Papanaidu'
import os
import time
import boto
import boto.manage.cmdshell

def launch_instance(
        ami='ami-7341831a',
        instance_type='t1.micro',
        key_name=
)