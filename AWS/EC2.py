from cfn.core import Resource, Attribute, Property

class UserData(Property):

    def to_json(self):
        return {'Fn::Base64': self.value}

class Instance(Resource):
    Metadata = Attribute()
    PrivateDnsName = Attribute()
    PrivateIp = Attribute()
    PublicIp = Attribute()

    AvailabilityZone = Property()
    ImageId = Property()
    InstanceType = Property()
    SubnetId = Property()
    KeyName = Property()
    SecurityGroupIds = Property()
    IamInstanceProfile = Property()
    UserData = UserData()

class Volume(Resource):
    AvailabilityZone = Property()
    Iops = Property()
    Size = Property()
    SnapshotId = Property()
    Tags = Property()
    VolumeType = Property()

class VolumeAttachment(Resource):
    Device = Property()
    InstanceId = Property()
    VolumeId = Property()
