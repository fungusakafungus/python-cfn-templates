from cfn.core import Stack, to_json
from AWS.EC2 import Instance
from AWS.Route53 import RecordSet

# parameter
region = 'us-east-1'
hostedZone = 'aws.company-server.com'


description = "AWS CloudFormation Sample Template Route53_A: Sample template showing how to create an Amazon Route 53 A record that maps to the public IP address of an EC2 instance. It assumes that you already have a Hosted Zone registered with Amazon Route 53. **WARNING** This template creates an Amazon EC2 instance. You will be billed for the AWS resources used if you create a stack from this template."

regionMap = {
        "us-east-1"      : { "AMI" : "ami-7f418316" },
        "us-west-1"      : { "AMI" : "ami-951945d0" },
        }
# need to explicitly set the resource name, so the attributes can be referenced
# in other resources before forming the stack
ec2Instance = Instance('ec2Instance', ImageId=regionMap[region]['AMI'])
myDNSRecord = RecordSet(
        HostedZoneName='{0}.'.format(hostedZone),
        Comment='DNS name for my instance.',
        ResourceRecords=[ec2Instance.PublicIp],
        Name='{0}.{1}.{2}.'.format(ec2Instance, region, hostedZone),
        Type='A',
        TTL='900',
        )
stack = Stack(locals(), Description=description)
stack.Outputs['DomainName'] = myDNSRecord
print to_json(stack)
