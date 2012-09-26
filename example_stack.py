from cfn import Stack, Resource1, Resource2
from json import JSONEncoder, dumps

class ResourceEncoder(JSONEncoder):
    def default(self, o):
        return o.to_json and o.to_json() or JSONEncoder.default(self, o)

r2 = Resource2('Resource2ID', property1="a string", property2={'a':'dictionary'})
r1 = Resource1('Resource1ID', property1=r2, property2=r2.attr1)
r1.dependsOn = r2
stack = Stack(r1,r2)
print dumps(stack, cls=ResourceEncoder, indent=2)
