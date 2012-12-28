# -*- encoding: utf-8 -*-
import json
import logging

import pytest

from cfn.core import *

logging.basicConfig(level=logging.INFO)

def assert_json(actual, expected):
    actual = to_json(actual)
    expected = json.dumps(expected, indent=2, sort_keys=True)

    assert expected ==  actual


class Resource1(Resource):
    __module__=''


class ResourceWithProperties(Resource):
    prop1=Property()
    __module__=''


class ResourceWithAttributes(Resource):
    attr1=Attribute()
    __module__=''


class ResourceWithMetadata(Resource):
    Metadata=Attribute()
    __module__=''


def test_resource_creation():
    r = Resource1()

def test_resources_attribute_of_stack():
    r1 = Resource1('r1')
    stack = ResourceCollection(r1)
    assert {'r1': r1} ==  stack.resources

def test_resource_creation_with_attributes():
    r1 = ResourceWithAttributes(attr1='value')
    r2 = ResourceWithAttributes()
    r2.attr1='value'

def test_resource_with_attributes_to_json():
    r1 = ResourceWithAttributes(attr1='value')
    assert_json(r1.to_json(), {'Type':'ResourceWithAttributes', 'attr1':'value'})

def test_resource_creation_with_properties():
    r1 = ResourceWithProperties(prop1=1)
    r2 = ResourceWithProperties()
    r2.prop1=1

def test_resource_with_properties_to_json():
    r1 = ResourceWithProperties(prop1=1)
    assert_json(r1.to_json(), {'Type':'ResourceWithProperties', 'Properties': {'prop1':1}})

def test_setting_properties():
    r1 = ResourceWithProperties()
    r1.prop1 = 1
    assert_json(r1.to_json(), {'Type':'ResourceWithProperties', 'Properties': {'prop1':1}})

def test_stack_creation():
    r1 = ResourceWithProperties(prop1=1)
    stack = ResourceCollection(r1)
    assert_json(stack, {'Resources': { 'ResourceWithProperties':{ 'Type':
        'ResourceWithProperties', 'Properties': {'prop1': 1} } } })

def test_autonaming():
    r1 = Resource1()
    r2 = Resource1()
    r3 = Resource1()
    stack = ResourceCollection(r1, r2, r3)
    assert_json(stack, {'Resources': {
        'Resource1':{ 'Type': 'Resource1'},
        'Resource11':{ 'Type': 'Resource1'},
        'Resource12':{ 'Type': 'Resource1'},
        }})

def test_autonaming_with_non_empty_module():
    class TestResource(Resource): pass

    r1 = TestResource()
    r2 = TestResource()
    stack = ResourceCollection(r1, r2)
    assert_json(stack, {'Resources': {
        'TestResource':{ 'Type': 'tests::test_core::TestResource'},
        'TestResource1':{ 'Type': 'tests::test_core::TestResource'},
        }})

def test_stack_with_dependencies_in_properties():
    r1 = ResourceWithProperties()
    r2 = ResourceWithProperties()
    r1.prop1=r2
    stack = ResourceCollection(r1, r2)
    assert_json(stack,
            {'Resources': {
                'ResourceWithProperties':{
                    'Type': 'ResourceWithProperties',
                    'Properties': {
                        'prop1': {'Ref': 'ResourceWithProperties1'}
                        }
                    },
                'ResourceWithProperties1':{
                    'Type': 'ResourceWithProperties',
                    }
                }
                })

def test_resources_deep_in_properties():
    r1 = ResourceWithProperties()
    r2 = ResourceWithProperties()
    r1.prop1=[r2]
    stack = ResourceCollection(r1, r2)
    assert_json(stack, {
        'Resources': {
            'ResourceWithProperties': {
                'Type': 'ResourceWithProperties',
                'Properties': {
                    'prop1': [{'Ref': 'ResourceWithProperties1'}]
                    }
                },
            'ResourceWithProperties1': {
                'Type': 'ResourceWithProperties',
                }
            }
        })

def test_stack_with_dependencies_in_attributes():
    r1 = ResourceWithAttributes('r1')
    r2 = ResourceWithProperties('r2')
    r2.prop1 = r1.attr1
    stack = ResourceCollection(r1, r2)
    assert_json(stack, {
        'Resources': {
            'r1':{
                'Type': 'ResourceWithAttributes'
                },
            'r2':{
                'Type': 'ResourceWithProperties',
                'Properties': {
                    'prop1': {'Fn::GetAtt': ['r1', 'attr1']}
                    }
                },
            }
        })

def test_resource_format():
    r1 = Resource1('r1')
    assert '{Resource|r1}' == '{0}'.format(r1)

def test_join_in_property():
    r1 = Resource1('r1')
    r2 = ResourceWithProperties('r2')
    r2.prop1 = 'prefix{0}'.format(r1)
    stack = ResourceCollection(r1, r2)
    assert_json(stack, {
        'Resources': {
            'r1':{
                'Type': 'Resource1'
                },
            'r2':{
                'Type': 'ResourceWithProperties',
                'Properties': {
                    'prop1': {'Fn::Join': ['', ['prefix', {'Ref': 'r1'}]]}
                    }
                },
            }
        })
def test_stack_from_locals():
    r1 = Resource1('r1')
    stack = ResourceCollection(**locals())
    assert_json(stack, {
        'Resources': {
            'r1':{ 'Type': 'Resource1'},
            }
        })

def test_stack_from_locals_with_unnamed_resources():
    r1 = Resource1()
    stack = ResourceCollection(**locals())
    assert_json(stack, {
        'Resources': {
            'r1':{ 'Type': 'Resource1'},
            }
        })

def test_stack_from_mixed():
    r1 = Resource1()
    r2 = Resource1('RES2')
    stack = ResourceCollection(r2,RES1=r1)
    assert_json(stack, {
        'Resources': {
            'RES1':{ 'Type': 'Resource1'},
            'RES2':{ 'Type': 'Resource1'},
            }
        })

def test_attribute_format():
    r1 = ResourceWithAttributes('RES1', attr1='value')
    actual = 'prefix{attribute}suffix'.format(attribute=r1.attr1)
    assert 'prefix{Attribute|RES1|attr1}suffix' ==  actual

def test_attribute_format_unnamed_resource():
    r1 = ResourceWithAttributes(attr1='value')
    with pytest.raises(AttributeError):
        'prefix{attribute}suffix'.format(attribute=r1.attr1)

def test_attribute_in_string_to_json1():
    r1 = ResourceWithAttributes('r1', attr1='value')
    a1 = r1.attr1
    str_with_attr = "{0}".format(a1)
    assert_json(str_with_attr, { 'Fn::GetAtt': ['r1', 'attr1']})

def test_attribute_in_string_to_json2():
    r1 = ResourceWithAttributes('r1', attr1='value')
    a1 = r1.attr1
    str_with_attr = "text{0}text".format(a1)
    assert_json(str_with_attr, {
        'Fn::Join': [
            '',
            [
                'text',
                {'Fn::GetAtt': ['r1', 'attr1']},
                'text']
            ]
        })

def test_attributes_in_strings():
    r1 = ResourceWithAttributes('r1', attr1='value')
    r2 = ResourceWithProperties('r2')
    r2.prop1 = 'test{0}'.format(r1.attr1)

    stack = ResourceCollection(r1, r2)
    assert_json(stack, {
        'Resources': {
            'r1':{'Type': 'ResourceWithAttributes', 'attr1': 'value'},
            'r2':{'Type': 'ResourceWithProperties',
                'Properties': {
                    'prop1': {
                        'Fn::Join': [
                            '',
                            [
                                'test',
                                { 'Fn::GetAtt': ['r1', 'attr1']}
                                ]
                            ]
                        }
                    }
                },
            }
        })


def test_attributes_in_metadata():
    r1 = ResourceWithAttributes(attr1='value')
    r2 = ResourceWithMetadata()
    r2.Metadata = {'key':r1.attr1}
    stack = ResourceCollection(**locals())
    assert_json(stack, {
        'Resources': {
            'r1':{ 'Type': 'ResourceWithAttributes', 'attr1':'value'},
            'r2':{ 'Type': 'ResourceWithMetadata', 'Metadata': {'key': {'Fn::GetAtt': ['r1', 'attr1']}}},
            }
        })

def test_attribute_in_a_list():
    r1 = ResourceWithAttributes('r1', attr1='value')
    r2 = ResourceWithProperties('r2')
    r2.prop1 = [r1.attr1]
    stack = ResourceCollection(r1, r2)
    assert_json(stack, {
        'Resources': {
            'r1':{'Type': 'ResourceWithAttributes', 'attr1': 'value'},
            'r2':{'Type': 'ResourceWithProperties',
                'Properties': {
                    'prop1': [
                        {'Fn::GetAtt': ['r1', 'attr1']}
                        ]
                    },
                }
            }
        })

def test_format_with_colons_in_resource_names():
    r1 = Resource1('Namespace::Name')
    r2 = ResourceWithProperties('r2')
    r2.prop1 = '{0}'.format(r1)
    stack = ResourceCollection(r1,r2)
    assert_json(stack, {
        'Resources': {
            'Namespace::Name':{'Type': 'Resource1'},
            'r2': {
                'Type': 'ResourceWithProperties',
                'Properties': {
                    'prop1':  {'Ref': 'Namespace::Name'}
                    }
                }
            }
        })

def test_custom_property():
    class CustomProperty(Property):
        def to_json(self):
            return {'Custom': self.value}

    class ResourceWithCustomProperty(Resource):
        __module__ = ''
        property = CustomProperty()

    r = ResourceWithCustomProperty('r', property='value')
    assert_json(r.to_json(), {
        'Type': 'ResourceWithCustomProperty',
        'Properties': {
            'property': {'Custom': 'value'}
            }
        })

    stack = ResourceCollection(r)
    assert_json(stack, {
        'Resources': {
            'r': {
                'Type': 'ResourceWithCustomProperty',
                'Properties': {
                    'property': {'Custom': 'value'}
                    }
                }
            }
        })

def test_properties_and_resource_inheritance():
    class Resource2(ResourceWithProperties):
        prop2 = Property()
        __module__ = ''

    r = Resource2('r', prop1=1, prop2=2)
    assert_json(r.to_json(), {
        'Type':'Resource2',
        'Properties': {'prop1':1,'prop2':2}
        })

def test_completion():
    r1 = ResourceWithProperties()
    assert 'prop1' in dir(ResourceWithProperties)
    assert 'prop1' in dir(r1)

def test_stack_inheritance():
    class Stack1(ResourceCollection):
        def __init__(self, *args, **kwargs):
            r1 = Resource1('r1')
            super(Stack1, self).__init__(r1, *args, **kwargs)

    class Stack2(Stack1):
        def __init__(self, *args, **kwargs):
            r2 = Resource1('r2')
            super(Stack2, self).__init__(r2, *args, **kwargs)

    s = Stack2()
    assert_json(s, {'Resources': {'r1': {'Type': 'Resource1'}, 'r2': {'Type': 'Resource1'}}})

def test_property_assignment():
    r = ResourceWithProperties(prop1='old value')
    r.prop1 = 'new value'
    assert_json(r.to_json(), {'Type':'ResourceWithProperties', 'Properties':{'prop1': 'new value'}})

def test_defaults_assigning():
    class ResourceWithDefaults(Resource):
        __module__ = ''
        prop1 = Property()

    ResourceWithDefaults.prop1 = 'default'
    r = ResourceWithDefaults()
    assert_json(r.to_json(), {'Type':'ResourceWithDefaults',
        'Properties':{'prop1': 'default'}})
