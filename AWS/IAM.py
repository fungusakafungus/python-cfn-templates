from cfn.core import Resource, Property, Attribute

class User(Resource):
    policies = Property()

class Policy(Resource):
    PolicyName = Property()
    PolicyDocument = Property()

class AccessKey(Resource):
    UserName = Property()
    SecretAccessKey = Attribute()

class InstanceProfile(Resource):
    Path = Property()
    Roles = Property()

