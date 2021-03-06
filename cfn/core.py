# -*- encoding: utf-8 -*-
import json
import re
import logging
from functools import wraps
from inspect import getmembers

from cfn.util import Parameter

def to_json(o):
    resolved = resolve_references(o)
    return json.dumps(resolved, indent=2, sort_keys=True)


def _log_call(func):
    @wraps(func)
    def log(*args, **kwargs):
        logging.debug('calling %s with %s', func.__name__, (args, kwargs))
        return func(*args, **kwargs)

    return log


@_log_call
def resolve_references(o):
    if hasattr(o, 'ref'):
        return o.ref()
    if hasattr(o, 'to_json'):
        return resolve_references(o.to_json())
    if isinstance(o, (list, tuple)):
        return [resolve_references(i) for i in o]
    if isinstance(o, dict):
        return dict((k, resolve_references(v)) for k, v in o.items())
    if isinstance(o, basestring):
        return resolve_references_in_string(o)
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
            |
            (?:
                # ex.: {Parameter|param1}}
                Parameter \| [^|]+
            )
        )
    }
    |
    ( [^{]+ ) # not a reference
    ''', re.VERBOSE)


def resolve_references_in_string(a_string):
    matches = _reference_regex.findall(a_string)
    result = []
    for reference, literal in matches:
        if literal:
            result.append(literal)
        if reference:
            parts = reference.split('|')
            if parts[0] in ('Resource', 'Parameter'):
                result.append({'Ref': parts[1]})
            else:
                result.append({"Fn::GetAtt": [parts[1], parts[2]]})
    if len(result) == 1:
        return result[0]
    elif len(result) > 1:
        return cfn_join(result)
    return a_string


class ResourceCollection(object):
    def __init__(self, *resources, **kwargs):
        self.resources = {}
        resources = [r for r in resources if isinstance(r, Resource)]
        for name, resource in kwargs.items():
            if not isinstance(resource, Resource):
                continue
            if not resource.name:
                resource.name = name
            resources.append(resource)
        for r in resources:
            if not r.name:
                for i in [''] + range(1, 1000):
                    simple_type_name = re.split('::', r.type())[-1]
                    r.name = simple_type_name + str(i)
                    if r.name not in self.resources:
                        break
            self.resources[r.name] = r

    @_log_call
    def to_json(self):
        result = {}
        if self.resources:
            result.update({'Resources': dict((k, v.to_json()) for k, v in self.resources.items())})
        return result


class Stack(ResourceCollection):
    def __init__(self, *resources_and_parameters, **kwargs):
        self.AWSTemplateFormatVersion = '2010-09-09'
        self.Description = ''
        self.Outputs = {}
        self.Parameters = {}

        for name, parameter in kwargs.items() + [(p.name, p) for p in resources_and_parameters if isinstance(p, Parameter)]:
            if not isinstance(parameter, Parameter):
                continue
            if not parameter.name:
                parameter.name = name
            self.Parameters[parameter.name] = parameter
        ResourceCollection.__init__(self, *resources_and_parameters, **kwargs)
        if 'Description' in kwargs:
            self.Description = kwargs['Description']

    def to_json(self):
        rc = ResourceCollection.to_json(self)
        rc.update({'AWSTemplateFormatVersion': self.AWSTemplateFormatVersion})
        if self.Description:
            rc.update({'Description': self.Description})
        if self.Parameters:
            rc.update({'Parameters': dict((k, dict(v)) for k, v in self.Parameters.items())})
        if self.Outputs:
            outputs = resolve_references(self.Outputs)
            rc.update({'Outputs': outputs})
        return rc


def cfn_join(sequence, glue=''):
    return {'Fn::Join': [glue, sequence]}


class Property(object):
    def __init__(self, resource=None, value=None):
        self.resource = resource
        self.value = value

    @_log_call
    def to_json(self):
        if isresource(self.value):
            result = self.value.ref()
        else:
            result = self.value

        return resolve_references(result)


class Attribute(object):
    def __init__(self, resource=None, name=None, value=None):
        self.resource = resource
        self.name = name
        self.value = value

    def ref(self):
        return {'Fn::GetAtt': [self.resource.name, self.name]}

    def to_json(self):
            return self.value

    def __format__(self, format_string):
        if not self.resource or not self.resource.name:
            raise AttributeError('Referenced attribute '
                                 'does not belong to a resource with a name')
        if not self.name:
            raise AttributeError(
                'Referenced attribute of resource {0} does not have a '
                'name'.format(self.resource.name))
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
    def to_json(self):
        return self.ref()

    @_log_call
    def to_json(self):
        properties = dict((k, getattr(self, k)) for k in self._property_names)
        properties = dict((k, v) for (k, v) in properties.items() if v.value)

        attributes = dict((k, getattr(self, k)) for k in self._attribute_names)
        attributes = dict((k, v.to_json()) for (k, v) in attributes.items())
        # remove empty attributes
        attributes = dict((k, v) for (k, v) in attributes.items() if v is not None)

        result = dict(Type=self.type(), **attributes)
        if properties:
            result.update(Properties=properties)
        return resolve_references(result)

    @_log_call
    def __setattr__(self, name, value):
        if not self._initialized or name == 'name':
            return object.__setattr__(self, name, value)
        else:
            getattr(self, name).value = value

    def __format__(self, format_string):
        if not self.name:
            raise AttributeError(
                'Referenced resource of type {0} does not have a name'.format(self.type()))
        return '{{Resource|{0}}}'.format(self.name)

    def ref(self):
        if not self.name:
            raise AttributeError(
                'Referenced resource of type {0} does not have a name'.format(self.type()))
        return {'Ref': self.name}
