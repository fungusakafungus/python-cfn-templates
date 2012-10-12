from cfn import Resource, Attribute, Property

class RecordSet(Resource):
    HostedZoneName = Property()
    Name = Property()
    Type = Property()
    ResourceRecords = Property()
    TTL = Property()
