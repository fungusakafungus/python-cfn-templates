from cfn import Resource, Attribute, Property

class UserData(Property):

    def to_json(self):
        return {'Fn::Base64': self.value}

class Instance(Resource):
    Metadata = Attribute()
    PrivateDnsName = Attribute()
    PrivateIp = Attribute()

    AvailabilityZone = Property()
    ImageId = Property()
    InstanceType = Property()
    SubnetId = Property()
    KeyName = Property()
    SecurityGroupIds = Property()
    IamInstanceProfile = Property()
    UserData = UserData()
