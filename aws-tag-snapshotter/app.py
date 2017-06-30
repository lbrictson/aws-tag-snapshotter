import boto3
import datetime
from datetime import timedelta
import time
import logging


logging.basicConfig(level=logging.WARN)

def get_snapshot_targets():
    """Returns all snapshot tagged volumes in ec2 along with some extra metadata"""
    targets = []
    ec2 = boto3.client('ec2')
    filters = [{'Name':'tag:autosnap', 'Values':['true']}]
    ec2s = ec2.describe_instances(Filters=filters)
    for instance in ec2s['Reservations']:
        try:
            for ins in instance['Instances']:
                owner = 'null'
                name = 'null'
                for tags in ins['Tags']:
                    if tags['Key'] == 'Owner':
                        owner = tags['Value']
                    if tags['Key'] == 'Name':
                        name = tags['Value']
                for vol in ins['BlockDeviceMappings']:
                    targets.append({
                        'volume': vol['Ebs']['VolumeId'],
                        'instance': ins['InstanceId'],
                        'DeviceName': vol['DeviceName'],
                        'owner': owner,
                        'name': name})
        except BaseException as e:
            logging.error('ERROR encountered: ' + str(e) + ' on target: ' + str(instance))
    return targets


def take_snapshot(snapmeta):
    """Takes a snapshot, tagging it with the meta data of the instance the volume is attached to"""
    try:
        logging.warn("Taking snapshot of " + str(snapmeta))
        ec2 = boto3.client('ec2')
        response = ec2.create_snapshot(
            Description='Automated snap of {} at {} from instance {} named {}'.format(snapmeta['volume'], snapmeta['DeviceName'], snapmeta['instance'], snapmeta['name']),
            VolumeId=snapmeta['volume'],
            DryRun=False
        )
        tagger(response['SnapshotId'], snapmeta['owner'], snapmeta['instance'], snapmeta['name'])
    except BaseException as e:
        logging.error('ERROR encountered: ' + str(e) + ' with meta ' + str(snapmeta))

def tagger(vol, own, instance_name, instance_vol):
    """handles tagging of snapshots"""
    try:
        today = datetime.datetime.today()
        expdate = today + timedelta(days=5)
        expdate = expdate.strftime('%m/%d/%Y')
        ec2 = boto3.client('ec2')
        response = ec2.create_tags(
            DryRun=False,
            Resources=[
                vol,
            ],
            Tags=[
                {
                    'Key': 'Owner',
                    'Value': own
                },
                {
                    'Key': 'snapexp',
                    'Value': expdate
                },
                {
                    'Key': 'Name',
                    'Value': instance_name + ' ' + instance_vol
                }
            ]
        )
    except BaseException as e:
        logging.error('ERROR encountered: ' + str(e) + ' with meta ' + str(vol))
    

def cleaner():
    """Removes old snapshots that have expired"""
    try:
        today = datetime.datetime.today()
        today = today.strftime('%m/%d/%Y')
        filters = [{'Name':'tag:snapexp', 'Values':[today]}]
        ec2 = boto3.client('ec2')
        response = ec2.describe_snapshots(
            Filters=filters)
        for snapshots in response['Snapshots']:
            logging.warn('Deleting snapshot: ' + str(snapshots))
            response = ec2.delete_snapshot(
                SnapshotId=snapshots['SnapshotId']
                )
    except BaseException as e:
        logging.error('ERROR encountered: ' + str(e) + ' in cleaner function')

def main():
    """You can use this function to create an endless loop that runs daily"""          
    while True:
        targets = get_snapshot_targets()
        for target in targets:
            take_snapshot(target)
        cleaner()
        time.sleep(86400)


def run():
    """This is for doing a 1 shot run"""
    targets = get_snapshot_targets()
    for target in targets:
        take_snapshot(target)
    cleaner()