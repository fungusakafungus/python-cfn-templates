from cfn.core import Resource, Attribute, Property

class LaunchConfiguration(Resource):
    _type = 'AWS::AutoScaling::LaunchConfiguration'
    BlockDeviceMappings = Property()
    BlockDeviceMappings.__doc__ = '''Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS
                  volumes.

Required : No

Type : List of BlockDeviceMappings .'''
    IamInstanceProfile = Property()
    IamInstanceProfile.__doc__ = '''Provides the name or the Amazon Resource Name (ARN) of the instance profile associated with the IAM
                  role for the instance. The instance profile contains the IAM role.

Required : No

Type : String (1–1600 chars)'''
    ImageId = Property()
    ImageId.__doc__ = '''Provides the unique ID of the Amazon Machine Image (AMI) that was assigned during
                  registration.

Required : Yes

Type : String'''
    InstanceMonitoring = Property()
    InstanceMonitoring.__doc__ = '''Indicates whether or not instance monitoring should be enabled for this autoscaling group. This is
                  enabled by default. To turn it off, set InstanceMonitoring to "false".

Required : No. Default value is "true".

Type : Boolean'''
    InstanceType = Property()
    InstanceType.__doc__ = '''Specifies the instance type of the EC2 instance.

Required : Yes

Type : String'''
    KernelId = Property()
    KernelId.__doc__ = '''Provides the ID of the kernel associated with the EC2 AMI.

Required : No

Type : String'''
    KeyName = Property()
    KeyName.__doc__ = '''Provides the name of the EC2 key pair.

Required : No

Type : String'''
    RamDiskId = Property()
    RamDiskId.__doc__ = '''The ID of the RAM disk to select. Some kernels require additional drivers at launch. Check the
                  kernel requirements for information about whether you need to specify a RAM disk. To find kernel
                  requirements, refer to the AWS Resource Center and search for the kernel ID.

Required : No

Type : String'''
    SecurityGroups = Property()
    SecurityGroups.__doc__ = '''A list containing the EC2 security groups to assign to the Amazon EC2 instances in the Auto Scaling
                  group. The list can contain the name of existing EC2 security groups, references to AWS::EC2::SecurityGroup resources created in the template, or both.

Required : No

Type : List of EC2 security groups'''
    SpotPrice = Property()
    SpotPrice.__doc__ = '''The spot price for this autoscaling group. If a spot price is set, then the autoscaling group will
                  launch when the current spot price is less than the amount specified in the template.

When you have specified a spot price for an auto scaling group, the group will only launch when the
               spot price has been met, regardless of the setting in the autoscaling group's DesiredCapacity .

For more information about configuring a spot price for an autoscaling group, see Using Auto Scaling to Launch Spot Instances in the AutoScaling Developer
                     Guide .

Required : No

Type : String

Update requires : replacement

Note

When you change your bid price by creating a new launch configuration, running instances will
                     continue to run as long as the bid price for those running instances is higher than the current
                     Spot price.'''
    UserData = Property()
    UserData.__doc__ = '''The user data available to the launched EC2 instances.

Required : No

Type : String'''
