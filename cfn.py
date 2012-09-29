# -*- encoding: utf-8 -*-
from itertools import repeat
from json import JSONEncoder
import string

class ResourceEncoder(JSONEncoder):
    def default(self, o):
        return  o.to_json() if getattr(o, 'to_json', None) else JSONEncoder.default(self, o)

class ResourceCollection(object):
    def __init__(self, *resources):
        self.resources = {}
        dicts = [d for d in resources if isinstance(d,dict)]
        resources = [r for r in resources if isinstance(r,Resource)]
        for arg in dicts:
            for name,resource in arg.items():
                if not isinstance(resource, Resource):
                    continue
                if not resource.name:
                    resource.name = name
                resources.append(resource)
        for r in resources:
            if not r.name:
                for i in xrange(1000):
                    r.name = r.type() + str(i + 1)
                    if r.name not in self.resources:
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

    def _has_formatting(self, format_string):
        formatter = string.Formatter()
        field_names = [field_name for (literal_text, field_name, format_spec, conversion) in formatter.parse(format_string)]
        return any(field_names)

    def _format_string_chunks(self, format_string):
        formatter = string.Formatter()
        result = []
        for (literal_text, field_name, format_spec, conversion) in formatter.parse(format_string):
            if literal_text:
                result.append(literal_text)
            if field_name:
                result.append({'Ref': field_name})
        return result


    def to_json(self):
        if isinstance(self.value, basestring) and self._has_formatting(self.value):
                return {'Fn::Join': ['', self._format_string_chunks(self.value)]}
        return self.value

class Attribute(object):
    def __init__(self, resource=None, name=None, value=None):
        self.resource=resource
        self.name=name
        self.value=value

    def to_json(self):
        return self.value

    def ref(self, name):
        return {'Fn::GetAttr': [self.resource.name, self.name]}

class Resource(object):
    _initialized = False
    def __init__(self, name=None, **properties_and_attributes):
        self.name = name
        self._attribute_names = []
        self._property_names = []
        for k,v in self.__class__.__dict__.items():
            if isinstance(getattr(self, k, None), Attribute):
                self._attribute_names.append(k)
                setattr(self, k, Attribute(resource=self, name=k))
        for k,v in self.__class__.__dict__.items():
            if isinstance(getattr(self, k, None), Property):
                self._property_names.append(k)
                setattr(self, k, Property(resource=self))
        for k, v in properties_and_attributes.items():
            if k in self._attribute_names:
                setattr(self, k, Attribute(resource=self, value=v))
            if k in self._property_names:
                setattr(self, k, Property(resource=self, value=v))
        self._initialized=True

    def type(self):
        parts = []
        if self.__module__:
            parts.extend(self.__module__.split('.'))
        parts.append(self.__class__.__name__)
        return '::'.join(parts)

    def to_json(self):
        properties=dict((k,getattr(self,k)) for k in self._property_names)
        properties=dict((k,v) for (k,v) in properties.items() if v.value)
        for k,v in properties.items():
            if isinstance(v.value, Resource):
                properties[k] = v.value.ref()
            if isinstance(v.value, Attribute):
                properties[k] = v.value.ref(k)

        attributes=dict((k,getattr(self,k)) for k in self._attribute_names)
        attributes=dict((k,v) for (k,v) in attributes.items() if v.value)

        result = dict(Type=self.type(), **attributes)
        if properties:
            result.update(Properties=properties)
        return result

    def __setattr__(self, name, value):
        if not self._initialized or name == 'name':
            return object.__setattr__(self, name, value)
        else:
            if isinstance(getattr(self,name), (Attribute, Property)):
                getattr(self,name).value = value
            else:
                return object.__setattr__(self, name, value)

    # hackish, very hackish
    def __format__(self, format_string):
        return '{{{0}}}'.format(self.name)

    def ref(self):
        return {'Ref':self.name}
