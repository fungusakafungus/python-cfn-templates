from cfn.core import Resource, Attribute, Property

class AutoScalingGroup(Resource):
    _type = 'AWS::AutoScaling::AutoScalingGroup'
    AvailabilityZones = Property()
    AvailabilityZones.__doc__ = '''Contains a list of Availability Zones for the group.

Required : Yes

Type : List of Strings'''
    Cooldown = Property()
    Cooldown.__doc__ = '''The number of seconds after a scaling activity completes before any further scaling activities
                  can start.

Required : No

Type : String'''
    DesiredCapacity = Property()
    DesiredCapacity.__doc__ = '''Specifies the desired capacity for the auto scaling group.

If SpotPrice is not set in the AWS::AutoScaling::LaunchConfiguration for this auto
               scaling group, then Auto Scaling will begin to bring up instances based on DesiredCapacity .  CloudFormation will not mark the auto scaling group as
               successful (by setting its status to CREATE_COMPLETE) until the desired capacity is reached.

If SpotPrice is set, then DesiredCapacity will not be used as a criteria for success, since instances will
               only be run when the spot price has been matched. Once the spot price has been matched, however, Auto
               Scaling will use DesiredCapacity as the target capacity for bringing up
               instances.

Required : No

Type : String'''
    HealthCheckGracePeriod = Property()
    HealthCheckGracePeriod.__doc__ = '''The length of time in seconds after a new EC2 instance comes into service that Auto Scaling starts
                  checking its health.

Required : No

Type : Integer'''
    HealthCheckType = Property()
    HealthCheckType.__doc__ = '''The service you want the health status from, Amazon EC2 or Elastic Load Balancer. Valid values
                  are "EC2" or "ELB."

Required : No

Type : String'''
    LaunchConfigurationName = Property()
    LaunchConfigurationName.__doc__ = '''Specifies the name of the associated AWS::AutoScaling::LaunchConfiguration .

Required : Yes

Type : String

Update requires : replacement'''
    LoadBalancerNames = Property()
    LoadBalancerNames.__doc__ = '''A list of load balancers associated with this auto scaling group.

Required : Yes

Type : List of Strings

Update requires : replacement'''
    MaxSize = Property()
    MaxSize.__doc__ = '''The maximum size of the auto scaling group.

Required : Yes

Type : String'''
    MinSize = Property()
    MinSize.__doc__ = '''The minimum size of the auto scaling group.

Required : Yes

Type : String'''
    NotificationConfiguration = Property()
    NotificationConfiguration.__doc__ = '''An embedded property that configures an auto scaling group to send notifications when specified
                  events take place.

Required : No

Type : NotificationConfiguration'''
    Tags = Property()
    Tags.__doc__ = '''The tags you want to attach to this resource.

For more information about tags, go to Tagging
                     Auto Scaling Groups and Amazon EC2 Instances in the Auto Scaling Developer Guide .

Required : Yes

Type : List of Auto Scaling
                     Tags

Update requires : no interruption'''
    VPCZoneIdentifier = Property()
    VPCZoneIdentifier.__doc__ = '''A list of subnet identifiers of Amazon Virtual Private Clouds (Amazon VPCs).

The subnets that you specify for VPCZoneIdentifier must reside in the
               availability zones that you specify with the AvailabilityZones parameter.

For more information, go to Using
               EC2 Dedicated Instances Within Your VPC in the Auto Scaling Developer Guide .

Update requires : replacement

Required : No

Type : List of Strings'''
