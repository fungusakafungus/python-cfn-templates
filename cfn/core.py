# -*- encoding: utf-8 -*-
import json
import re
import logging
from functools import wraps
from inspect import getmembers


def to_json(o):
    resolved = resolve_references(o, True)
    return json.dumps(resolved, indent=2, sort_keys=True)


def _log_call(func):
    @wraps(func)
    def log(*args, **kwargs):
        logging.debug('calling %s with %s', func.__name__, (args, kwargs))
        return func(*args, **kwargs)

    return log


@_log_call
def resolve_references(o, embed):
    if isinstance(o, (list, tuple)):
        return [resolve_references(i, embed) for i in o]
    if isinstance(o, dict):
        return dict((k, resolve_references(v, embed)) for k, v in o.items())
    if isinstance(o, basestring):
        return resolve_references_in_string(o)
    if hasattr(o, 'resolve_references'):
        return o.resolve_references(embed)
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


def resolve_references_in_string(a_string):
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
                for i in [''] + range(1,1000):
                    r.name = r.type() + str(i)
                    if r.name not in self.resources:
                        break
            self.resources[r.name] = r

    @_log_call
    def resolve_references(self, embed):
        return {'Resources': resolve_references(self.resources, True)}


def camel_case_to_pascal_case(a_case):
    return a_case[0].upper() + a_case[1:]


def cfn_join(sequence, glue=''):
    return {'Fn::Join': [glue, sequence]}


class Property(object):
    def __init__(self, resource=None, value=None):
        self.resource = resource
        self.value = value

    @_log_call
    def resolve_references(self, embed):
        if isresource(self.value):
            result = self.value.ref()
        else:
            result = self.value

        return resolve_references(result, embed)


class Attribute(object):
    def __init__(self, resource=None, name=None, value=None):
        self.resource = resource
        self.name = name
        self.value = value

    def ref(self):
        return {'Fn::GetAtt': [self.resource.name, self.name]}

    @_log_call
    def resolve_references(self, embed):
        return resolve_references(self.ref(), True)

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


class _ResourceMetaClass(type):
    @_log_call
    def __setattr__(cls, name, value):
        if hasattr(cls, name) and isinstance(getattr(cls, name), Property):
            logging.debug('Setting default property {2} of class {0} to {1}', cls,
                    name, value)
            getattr(cls, name).value = value
        else:
            type.__setattr__(cls, name, value)


class Resource(object):
    __metaclass__ = _ResourceMetaClass
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
            setattr(self, name, value.__class__(resource=self,
                value=value.value))

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

    @_log_call
    def resolve_references(self, embed):
        if not embed:
            return self.ref()
        properties = dict((k, getattr(self, k)) for k in self._property_names)
        properties = dict((k, v) for (k, v) in properties.items() if v.value)

        attributes = dict((k, getattr(self, k)) for k in self._attribute_names)
        attributes = dict((k, v) for (k, v) in attributes.items() if v.value)
        for k, v in attributes.items():
            attributes[k] = v.value

        result = dict(Type=self.type(), **attributes)
        if properties:
            result.update(Properties=properties)
        return resolve_references(result, False)

    @_log_call
    def __setattr__(self, name, value):
        if not self._initialized or name == 'name':
            return object.__setattr__(self, name, value)
        else:
            getattr(self, name).value = value

    def __format__(self, format_string):
        return '{{Resource|{0}}}'.format(self.name)

    def ref(self):
        return {'Ref': self.name}
