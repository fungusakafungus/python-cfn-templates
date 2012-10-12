# -*- encoding: utf-8 -*-
import json
import re

def to_json(o):
    return json.dumps(o, cls=ResourceEncoder, indent=2)

def resolve_references(o):
    if isinstance(o, (list, tuple)):
        return [resolve_references(i) for i in o]
    if isinstance(o, dict):
        return dict((k,resolve_references(v)) for k,v in o.items())
    if isinstance(o, basestring):
        return _resolve_references_in_string(o)
    return o

_reference_regex = re.compile(r'''
        { # Reference to a Resource or Attribute
            (
                (?:
                    Attribute \| [^|]+ \| [^|]+     # ex.: {Attribute|ResourceName|AttrName}
                )
                |
                (?:
                    Resource \| [^|]+               # ex.: {Resource|ResourceName}}
                )
            )
        }
        |
        ( [^{]+ )
    ''', re.VERBOSE)

def _resolve_references_in_string(a_string):
    matches = _reference_regex.findall(a_string)
    result = []
    for reference, literal in matches:
        if literal:
            result.append(literal)
        if reference:
            parts = reference.split('|')
            if parts[0] == 'Resource':
                result.append({'Ref':parts[1]})
            else:
                result.append({"Fn::GetAtt": [parts[1], parts[2]]})
    if len(result) == 1:
        return result[0]
    else:
        return cfn_join(result)
    return a_string

class ResourceEncoder(json.JSONEncoder):
    def encode(self, o):
        return json.JSONEncoder.encode(self, resolve_references(o))
    def default(self, o):
        if isinstance(o, (Resource, Property, ResourceCollection, Attribute)):
            return resolve_references(o.to_json())

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

def cfn_join(sequence, glue=''):
    return {'Fn::Join': [glue, sequence]}

class Property(object):
    def __init__(self, resource=None, value=None):
        self.resource=resource
        self.value=value


    def to_json(self):
        return self.value

class Attribute(object):
    def __init__(self, resource=None, name=None, value=None):
        self.resource=resource
        self.name=name
        self.value=value

    def ref(self):
        return {'Fn::GetAtt': [self.resource.name, self.name]}

    def to_json(self):
        return self.ref()

    def __format__(self, format_string):
        return '{{Attribute|{resource}|{attribute}}}'.format(resource=self.resource.name, attribute=self.name)

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
            p = getattr(self, k, None)
            if isinstance(p, Property):
                self._property_names.append(k)
                setattr(self, k, p.__class__(resource=self))
        for k, v in properties_and_attributes.items():
            if k in self._attribute_names:
                setattr(self, k, Attribute(resource=self, name=k, value=v))
            if k in self._property_names:
                p = getattr(self, k)
                setattr(self, k, p.__class__(resource=self, value=v))
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
            elif isinstance(v.value, Attribute):
                properties[k] = v.value.ref()
            else:
                properties[k] = v.to_json()

        attributes=dict((k,getattr(self,k)) for k in self._attribute_names)
        attributes=dict((k,v) for (k,v) in attributes.items() if v.value)
        for k,v in attributes.items():
            attributes[k]=v.value

        result = dict(Type=self.type(), **attributes)
        if properties:
            result.update(Properties=properties)
        return result

    def __setattr__(self, name, value):
        if not self._initialized or name == 'name':
            return object.__setattr__(self, name, value)
        else:
            getattr(self,name).value = value

    # hackish, very hackish
    def __format__(self, format_string):
        return '{{Resource|{0}}}'.format(self.name)

    def ref(self):
        return {'Ref':self.name}
