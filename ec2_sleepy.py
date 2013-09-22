#!/bin/env python

import boto
import boto.ec2.cloudwatch
from boto.ec2.cloudwatch import MetricAlarm

access_key_id='YOUR_ACCESS_KEY_ID'
secret_access_key='YOUR_SECRET_ACCESS_KEY'


# make this instance able to sleep, i.e. able to shutdown if not utilised
def make_sleepy(cw_conn, region, instance_id):
    print "Making instance", instance_id, "sleepy..."

    # we build the 'stop' action ARN with region
    shutdown_arn = 'arn:aws:automate:{0}:ec2:stop'.format(region)
    alarm_name = 'ec2_shutdown_sleepy_{0}'.format(instance_id)

    # define our alarm to shutdown the instance if it gets sleepy
    # i.e. if CPU utilisation is less than 2% for 24 x 1 hr intervals
    sleepy_alarm = MetricAlarm(
        name=alarm_name, namespace='AWS/EC2',
        metric='CPUUtilization', statistic='Average',
        comparison='<', threshold='2',
        period='3600', evaluation_periods=24,
        alarm_actions=[shutdown_arn],
        dimensions={'InstanceId':instance_id})

    # create the alarm.. Zzzz!
    cw_conn.create_alarm(sleepy_alarm)


def main():
    # connect to all regions and find all instances we own
    for region in boto.ec2.regions():

        print "Connecting to", region.endpoint, "..."
        ec2_conn = region.connect(aws_access_key_id=access_key_id,
                                  aws_secret_access_key=secret_access_key)

        cw_conn  = boto.ec2.cloudwatch.connect_to_region(region.name)

        # make each instance in the region sleepy (or capable of sleep anyway)
        for reservation in ec2_conn.get_all_instances():
            for instance in reservation.instances:
                make_sleepy(cw_conn, region.name, instance.id)


if __name__ == '__main__':
    main()
