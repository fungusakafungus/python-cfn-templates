from itertools import repeat
from json import JSONEncoder

class ResourceEncoder(JSONEncoder):
    def default(self, o):
        return  o.to_json() if getattr(o, 'to_json', None) else JSONEncoder.default(self, o)

class Stack(object):
    resources = {}
    def __init__(self, *resources):
        for r in resources:
            if not r.name:
                for i in xrange(1000):
                    r.name = r.__class__.__name__ + str(i + 1)
                    if r.name not in resources:
                        break
            self.resources[r.name] = r

    def to_json(self):
        return {'Resources':self.resources}

def camel_case_to_pascal_case(a_case):
    return a_case[0].upper() + a_case[1:]

class Property(object):
    def __init__(self, resource=None, value=None):
        self.resource=resource
        self.value=value

    def to_json(self):
        return self.value

class Attribute(object):
    def __init__(self, resource=None, value=None):
        self.resource=resource
        self.value=value

    def to_json(self):
        return self.value

class Resource(object):
    _initialized = False
    def __init__(self, name=None, **properties_and_attributes):
        self.name = name
        for k,v in self.__class__.__dict__.items():
            if isinstance(getattr(self, k, None), Attribute):
                setattr(self, k, Attribute(resource=self))
        for k,v in self.__class__.__dict__.items():
            if isinstance(getattr(self, k, None), Property):
                setattr(self, k, Property(resource=self))
        for k, v in properties_and_attributes.items():
            if isinstance(getattr(self, k, None), Attribute):
                setattr(self, k, Attribute(resource=self, value=v))
            if isinstance(getattr(self, k, None), Property):
                setattr(self, k, Property(resource=self, value=v))
        self._initialized=True

    def to_json(self):
        properties=dict(((k,v) for k,v in self.__dict__.items() if
            isinstance(v, Property)))
        attributes=dict(((k,v) for k,v in self.__dict__.items() if isinstance(v,
            Attribute)))
        properties_and_refs = dict((
                (k, v.value.ref()) if isinstance(v.value, Resource) else (k,
                    v.value)
                for k,v in properties.items() if v.value))
        result = dict(Type=self.__class__.__name__, **attributes)
        if properties_and_refs:
            result.update(Properties=properties_and_refs)
        return result

    def __setattr__(self, name, value):
        if not self._initialized or name == 'name':
            return object.__setattr__(self, name, value)



    def ref(self):
        return {'Ref':self.name}
