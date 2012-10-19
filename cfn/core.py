# -*- encoding: utf-8 -*-
import json
import re
from inspect import getmembers


def to_json(o):
    resolved = resolve_references(o)
    return json.dumps(resolved, cls=ResourceEncoder, indent=2)


def resolve_references(o):
    if isinstance(o, (list, tuple)):
        return [resolve_references(i) for i in o]
    if isinstance(o, dict):
        return dict((k, resolve_references(v)) for k, v in o.items())
    if isinstance(o, basestring):
        return _resolve_references_in_string(o)
    if hasattr(o, '_resolve_references'):
        return o._resolve_references()
    return o


_reference_regex = re.compile(r'''
    { # Reference to a Resource or Attribute
        (
            (?:
                # ex.: {Attribute|ResourceName|AttrName}
                Attribute \| [^|]+ \| [^|]+
            )
            |
            (?:
                # ex.: {Resource|ResourceName}}
                Resource \| [^|]+
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
                result.append({'Ref': parts[1]})
            else:
                result.append({"Fn::GetAtt": [parts[1], parts[2]]})
    if len(result) == 1:
        return result[0]
    elif len(result) == 0:
        return a_string
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
        dicts = [d for d in resources if isinstance(d, dict)]
        resources = [r for r in resources if isinstance(r, Resource)]
        for arg in dicts:
            for name, resource in arg.items():
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
        return {'Resources': self.resources}


def camel_case_to_pascal_case(a_case):
    return a_case[0].upper() + a_case[1:]


def cfn_join(sequence, glue=''):
    return {'Fn::Join': [glue, sequence]}


class Property(object):
    def __init__(self, resource=None, value=None):
        self.resource = resource
        self.value = value

    def to_json(self):
        return self.value

    def _resolve_references(self):
        if isresource(self.value):
            return self.value.ref()
        else:
            return self


class Attribute(object):
    def __init__(self, resource=None, name=None, value=None):
        self.resource = resource
        self.name = name
        self.value = value

    def ref(self):
        return {'Fn::GetAtt': [self.resource.name, self.name]}

    def to_json(self):
        return self.ref()

    def __format__(self, format_string):
        return '{{Attribute|{resource}|{attribute}}}'.format(
                resource=self.resource.name,
                attribute=self.name)


def isresource(o):
    return isinstance(o, Resource)


def isproperty(o):
    return isinstance(o, Property)


def isattribute(o):
    return isinstance(o, Attribute)


class Resource(object):
    _initialized = False

    def __init__(self, name=None, **properties_and_attributes):
        self.name = name
        self._attribute_names = []
        self._property_names = []

        # walk through our class' attributes
        for name, value in getmembers(self, isattribute):
            # add the attribute name to the list
            self._attribute_names.append(name)
            # copy the attribute from class to instance, setting the resource
            # to self. Copy is done by instantiating the attributes __class__
            setattr(self, name, value.__class__(resource=self, name=name))

        # walk through our class' properties
        for name, value in getmembers(self, isproperty):
            # add the attribute name to the list
            self._property_names.append(name)
            # copy the property from class to instance, setting the resource
            # to self. Copy is done by instantiating the propertys __class__
            setattr(self, name, value.__class__(resource=self))

        # put values from arguments into properties and attributes
        for k, v in properties_and_attributes.items():
            if k in self._attribute_names or k in self._property_names:
                getattr(self, k).value = v
            else:
                raise AttributeError(k)
        self._initialized = True

    def type(self):
        parts = []
        if self.__module__:
            parts.extend(self.__module__.split('.'))
        parts.append(self.__class__.__name__)
        return '::'.join(parts)

    def to_json(self):
        properties = dict((k, getattr(self, k)) for k in self._property_names)
        properties = dict((k, v) for (k, v) in properties.items() if v.value)
        for k, v in properties.items():
            if isinstance(v.value, Resource):
                properties[k] = v.value.ref()
            elif isinstance(v.value, Attribute):
                properties[k] = v.value.ref()
            else:
                properties[k] = v.to_json()

        attributes = dict((k, getattr(self, k)) for k in self._attribute_names)
        attributes = dict((k, v) for (k, v) in attributes.items() if v.value)
        for k, v in attributes.items():
            attributes[k] = v.value

        result = dict(Type=self.type(), **attributes)
        if properties:
            result.update(Properties=properties)
        return result

    def __setattr__(self, name, value):
        if not self._initialized or name == 'name':
            return object.__setattr__(self, name, value)
        else:
            getattr(self, name).value = value

    def __format__(self, format_string):
        return '{{Resource|{0}}}'.format(self.name)

    def ref(self):
        return {'Ref': self.name}
