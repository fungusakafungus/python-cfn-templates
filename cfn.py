from itertools import repeat

class Stack(object):
    resources = {}
    def __init__(self, *resources):
        for r in resources:
            self.resources[r.name] = r

    def to_json(self):
        return {'Resources':self.resources, 'Parameters':{}}

def camel_case_to_pascal_case(a_case):
    return a_case[0].upper() + a_case[1:]

class Attribute(object):
    def __init__(self, value):
        self.value = value

class Resource(object):
    attributes = ['dependsOn']
    # use @property?
    def __init__(self, name=None, **properties):
        self.name = name
        self.properties = properties
        self.attributes = zip(self.__class__.attributes, repeat(None))

    def to_json(self):
        properties_and_refs = dict((
                (k,v.ref()) if isinstance(v, Resource) else (k,v)
                for (k,v) in self.properties.items()))
        attributes = {}
        for k,v in self.attributes.items():
            if not v:
                continue
            if k == 'dependsOn' and isinstance(v, Resource):
                v = v.name
            attributes[camel_case_to_pascal_case(k)] = v
        return dict(Type=self.__class__.__name__,
                Properties=properties_and_refs,
                **attributes)

    def ref(self):
        return {'Ref':self.name}

    def __getattribute__(self, name):

    def __setattr__(self, name, value):
        if name in self.attributes:
            self.attributes[name] = Attribute(value)
        elif name in ('name', 'properties', 'attributes'):
            object.__setattr__(self, name, value)
        else:
            raise AttributeError(name)


class Resource1(Resource): pass
class Resource2(Resource):
    attributes = Resource.attributes + ['attr1']
