from cfn.core import Resource, Attribute, Property

class WaitConditionHandle(Resource): pass

class WaitCondition(Resource):
    DependsOn = Attribute()
    Handle = Property()
    Timeout = Property()
