import boto3

def handler(event, context):
    ec2 = boto3.client('ec2')
    resp = ec2.describe_instances(Filters=[{'Name':'tag:devbox:auto-schedule','Values':['true']},{'Name':'instance-state-name','Values':['running']}])
    ids = []
    for r in resp.get('Reservations',[]):
        for i in r.get('Instances',[]):
            ids.append(i['InstanceId'])
    if ids:
        ec2.stop_instances(InstanceIds=ids)
    return {'stopped': len(ids)}