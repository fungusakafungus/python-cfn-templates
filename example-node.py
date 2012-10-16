from cfn.core import ResourceCollection, to_json
import AWS
import AWS.IAM
import AWS.EC2
import AWS.CloudFormation
import AWS.Route53

# Parameters
PuppetEnvironment = "production" # "Puppet envioronment (e.g. git branch remote name)"
ImageId = "ami-"
AvailabilityZone = "eu-west-1c" # "Zone where to launch stack"
InstanceType = "m1.small" # "Type of EC2 instance to launch"
Subnet = None # "Subnet in which to launch stack"
KeyName = None # "Keypair to launch stack with"
Environment = "prod" # "Environment to launch stack in"
HostedZone = "aws.jimdo-server.com" # "DNS-Zone to launch stack in"
ServiceName = "example1" # "DNS Service entry for this service"
DataVolumeSnapshot = "snap-" # "Preformatted snapshot to use for data with 80GB XFS formatted"
DataVolumeDevice = "d" # "/dev/xvd<device> to bind DataVolume to"
SecurityGroupId = "sg-" # "Id of security group to put the stacks instances into."
VpcId = "vpc-" # "Id of the vpc to launch stack in"
DefaultSecurityGroupId = "sg-" # "Id of default security group id"

# Resources
policy = AWS.IAM.Policy('CFNInitUserPolicy')
policy.PolicyName = "AccessForCFNInit"
policy.PolicyDocument = {
        "Statement": [{
            "Effect"   : "Allow",
            "Action"   : "cloudformation:DescribeStackResource",
            "Resource" : "*"
            }]
        }
CFNInitUser = AWS.IAM.User('CFNInitUser')
CFNInitUser.policies = [policy]
CFNKeys = AWS.IAM.AccessKey('CFNKeys')
CFNKeys.UserName = 'CFNInitUser'
instance = AWS.EC2.Instance('EC2Instance')
facts = """
---
role_basicnode: true
server_role: basicnode
ec2_provisioned_zone: {AvailabilityZone}
ec2_provisioned_region: {AWS.Region}
jimdo_environment: {Environment}
puppet_environment: {PuppetEnvironment}
device_data_volume: /dev/xvd{DataVolumeDevice}
skip_monitoring: false
service_name: {ServiceName}
service_region_dns_name: {ServiceName}.{Environment}.{AWS.Region}.{HostedZone}.
service_global_dns_name: {ServiceName}.{Environment}.{HostedZone}

""".format(
        AvailabilityZone=AvailabilityZone,
        AWS=AWS,
        Environment=Environment,
        PuppetEnvironment=PuppetEnvironment,
        DataVolumeDevice=DataVolumeDevice,
        ServiceName=ServiceName,
        HostedZone=HostedZone)
instance.Metadata = {
        "AWS::CloudFormation::Init" : {
            "config" : {
                "files" : {
                    "/etc/facter/facts.d/cfn.yaml" : {
                        "content" : facts,
                        "mode" : "000644",
                        "owner" : "root",
                        "group" : "root"
                        }
                    }
                }
            }
        }
instance.AvailabilityZone = AvailabilityZone
instance.ImageId = ImageId
instance.InstanceType = InstanceType
instance.SubnetId = Subnet
instance.KeyName = KeyName
instance.SecurityGroupIds = [DefaultSecurityGroupId]

WaitHandle = AWS.CloudFormation.WaitConditionHandle('WaitHandle')
WaitCondition = AWS.CloudFormation.WaitCondition(
        DependsOn=instance.name,
        Handle=WaitHandle,
        Timeout=600)

user_data_script = """#!/bin/bash
/usr/bin/cfn-init --region '{AWS.Region}' -s '{AWS.StackName}' -r 'Ec2Instance' --access-key '{CFNKeys}' --secret-key '{CFNKeys.SecretAccessKey}' -v
/usr/bin/cfn-signal -e $? '{WaitHandle}'
while [ ! -e '/dev/xvd{DataVolumeDevice}' ]; do echo Waiting for EBS volume to attach; sleep 5; done
while [ ! "$(hostname -f)" ]; do echo Waiting for FQDN to be set; sleep 5; done;
puppetd --test --waitforcert=120 --color=no --pluginsync --environment={PuppetEnvironment}
""".format(
        AWS=AWS,
        CFNKeys=CFNKeys,
        WaitHandle=WaitHandle,
        DataVolumeDevice=DataVolumeDevice,
        PuppetEnvironment=PuppetEnvironment
        )
instance.UserData = user_data_script

Ec2InstanceDNS = AWS.Route53.RecordSet(
        HostedZoneName=HostedZone + '.',
        Name='{0}.'.format(instance.PrivateDnsName),
        Type='A',
        ResourceRecords=instance.PrivateIp,
        TTL=60)

DNS = AWS.Route53.RecordSet(
        HostedZoneName=HostedZone + '.',
        Name='{0}.{1}.{2}.{3}.'.format(ServiceName, Environment, AWS.Region, HostedZone),
        Type='CNAME',
        ResourceRecords=Ec2InstanceDNS)

stack = ResourceCollection(locals())
print to_json(stack)
