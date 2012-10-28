# -*- encoding: utf-8 -*-
import json
import unittest2
import logging

from cfn.core import *

logging.basicConfig(level=logging.INFO)

def assert_json(self, actual, expected):
    actual = to_json(actual)
    expected = json.dumps(expected, indent=2, sort_keys=True)

    # unittest2 makes better diff for unicode
    self.assertEqual(unicode(expected), unicode(actual))


unittest2.TestCase.assert_json = assert_json


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


class TestCore(unittest2.TestCase):
    def setUp(self):
        self.maxDiff=None

    def test_resource_creation(self):
        r = Resource1()

    def test_resources_attribute_of_stack(self):
        r1 = Resource1('r1')
        stack = ResourceCollection(r1)
        self.assertEquals({'r1': r1}, stack.resources)

    def test_resource_creation_with_attributes(self):
        r1 = ResourceWithAttributes(attr1='value')
        r2 = ResourceWithAttributes()
        r2.attr1='value'

    def test_resource_with_attributes_to_json(self):
        r1 = ResourceWithAttributes(attr1='value')
        self.assert_json(r1, {'Type':'ResourceWithAttributes', 'attr1':'value'})

    def test_resource_creation_with_properties(self):
        r1 = ResourceWithProperties(prop1=1)
        r2 = ResourceWithProperties()
        r2.prop1=1

    def test_resource_with_properties_to_json(self):
        r1 = ResourceWithProperties(prop1=1)
        self.assert_json(r1, {'Type':'ResourceWithProperties', 'Properties': {'prop1':1}})

    def test_setting_properties(self):
        r1 = ResourceWithProperties()
        r1.prop1 = 1
        self.assert_json(r1, {'Type':'ResourceWithProperties', 'Properties': {'prop1':1}})

    def test_stack_creation(self):
        r1 = ResourceWithProperties(prop1=1)
        stack = ResourceCollection(r1)
        self.assert_json(stack, {'Resources': { 'ResourceWithProperties':{ 'Type':
            'ResourceWithProperties', 'Properties': {'prop1': 1} } } })

    def test_autonaming(self):
        r1 = Resource1()
        r2 = Resource1()
        r3 = Resource1()
        stack = ResourceCollection(r1, r2, r3)
        self.assert_json(stack, {'Resources': {
            'Resource1':{ 'Type': 'Resource1'},
            'Resource11':{ 'Type': 'Resource1'},
            'Resource12':{ 'Type': 'Resource1'},
            }})

    def test_autonaming_with_non_empty_module(self):
        class TestResource(Resource): pass

        r1 = TestResource()
        r2 = TestResource()
        stack = ResourceCollection(r1, r2)
        self.assert_json(stack, {'Resources': {
            'TestResource':{ 'Type': 'tests::test_core::TestResource'},
            'TestResource1':{ 'Type': 'tests::test_core::TestResource'},
            }})

    def test_stack_with_dependencies_in_properties(self):
        r1 = ResourceWithProperties()
        r2 = ResourceWithProperties()
        r1.prop1=r2
        stack = ResourceCollection(r1, r2)
        self.assert_json(stack,
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

    def test_resources_deep_in_properties(self):
        r1 = ResourceWithProperties()
        r2 = ResourceWithProperties()
        r1.prop1=[r2]
        stack = ResourceCollection(r1, r2)
        self.assert_json(stack, {
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

    def test_stack_with_dependencies_in_attributes(self):
        r1 = ResourceWithAttributes('r1')
        r2 = ResourceWithProperties('r2')
        r2.prop1 = r1.attr1
        stack = ResourceCollection(r1, r2)
        self.assert_json(stack, {
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

    def test_resource_format(self):
        r1 = Resource1('r1')
        self.assertEquals('{Resource|r1}','{0}'.format(r1))

    def test_join_in_property(self):
        r1 = Resource1('r1')
        r2 = ResourceWithProperties('r2')
        r2.prop1 = 'prefix{0}'.format(r1)
        stack = ResourceCollection(r1, r2)
        self.assert_json(stack, {
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
    def test_stack_from_locals(self):
        r1 = Resource1('r1')
        stack = ResourceCollection(locals())
        self.assert_json(stack, {
            'Resources': {
                'r1':{ 'Type': 'Resource1'},
                }
            })

    def test_stack_from_locals_with_unnamed_resources(self):
        r1 = Resource1()
        stack = ResourceCollection(locals())
        self.assert_json(stack, {
            'Resources': {
                'r1':{ 'Type': 'Resource1'},
                }
            })

    def test_stack_from_mixed(self):
        r1 = Resource1()
        r2 = Resource1('RES2')
        stack = ResourceCollection({'RES1':r1},r2)
        self.assert_json(stack, {
            'Resources': {
                'RES1':{ 'Type': 'Resource1'},
                'RES2':{ 'Type': 'Resource1'},
                }
            })

    def test_attribute_format(self):
        r1 = ResourceWithAttributes('RES1', attr1='value')
        actual = 'prefix{attribute}suffix'.format(attribute=r1.attr1)
        self.assertEqual('prefix{Attribute|RES1|attr1}suffix', actual)

    def test_attribute_format_unnamed_resource(self):
        r1 = ResourceWithAttributes(attr1='value')
        with self.assertRaises(AttributeError):
            'prefix{attribute}suffix'.format(attribute=r1.attr1)

    def test_attribute_in_string_to_json1(self):
        r1 = ResourceWithAttributes('r1', attr1='value')
        a1 = r1.attr1
        str_with_attr = "{0}".format(a1)
        self.assert_json(str_with_attr, { 'Fn::GetAtt': ['r1', 'attr1']})

    def test_attribute_in_string_to_json2(self):
        r1 = ResourceWithAttributes('r1', attr1='value')
        a1 = r1.attr1
        str_with_attr = "text{0}text".format(a1)
        self.assert_json(str_with_attr, {
            'Fn::Join': [
                '',
                [
                    'text',
                    {'Fn::GetAtt': ['r1', 'attr1']},
                    'text']
                ]
            })

    def test_attributes_in_strings(self):
        r1 = ResourceWithAttributes('r1', attr1='value')
        r2 = ResourceWithProperties('r2')
        r2.prop1 = 'test{0}'.format(r1.attr1)

        stack = ResourceCollection(r1, r2)
        self.assert_json(stack, {
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


    def test_attributes_in_metadata(self):
        r1 = ResourceWithAttributes(attr1='value')
        r2 = ResourceWithMetadata()
        r2.Metadata = {'key':r1.attr1}
        stack = ResourceCollection(locals())
        self.assert_json(stack, {
            'Resources': {
                'r1':{ 'Type': 'ResourceWithAttributes', 'attr1':'value'},
                'r2':{ 'Type': 'ResourceWithMetadata', 'Metadata': {'key': {'Fn::GetAtt': ['r1', 'attr1']}}},
                }
            })

    def test_attribute_in_a_list(self):
        r1 = ResourceWithAttributes('r1', attr1='value')
        r2 = ResourceWithProperties('r2')
        r2.prop1 = [r1.attr1]
        stack = ResourceCollection(r1, r2)
        self.assert_json(stack, {
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

    def test_format_with_colons_in_resource_names(self):
        r1 = Resource1('Namespace::Name')
        r2 = ResourceWithProperties('r2')
        r2.prop1 = '{0}'.format(r1)
        stack = ResourceCollection(r1,r2)
        self.assert_json(stack, {
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

    def test_custom_property(self):
        class CustomProperty(Property):
            def resolve_references(self, embed):
                return {'Custom': resolve_references(self.value, False)}

        class ResourceWithCustomProperty(Resource):
            __module__ = ''
            property = CustomProperty()

        r = ResourceWithCustomProperty('r', property='value')
        self.assert_json(r, {
            'Type': 'ResourceWithCustomProperty',
            'Properties': {
                'property': {'Custom': 'value'}
                }
            })

        stack = ResourceCollection(r)
        self.assert_json(stack, {
            'Resources': {
                'r': {
                    'Type': 'ResourceWithCustomProperty',
                    'Properties': {
                        'property': {'Custom': 'value'}
                        }
                    }
                }
            })

    def test_properties_and_resource_inheritance(self):
        class Resource2(ResourceWithProperties):
            prop2 = Property()
            __module__ = ''

        r = Resource2('r', prop1=1, prop2=2)
        self.assert_json(r, {
            'Type':'Resource2',
            'Properties': {'prop1':1,'prop2':2}
            })

    def test_completion(self):
        r1 = ResourceWithProperties()
        self.assertTrue('prop1' in dir(ResourceWithProperties))
        self.assertTrue('prop1' in dir(r1))

    def test_stack_inheritance(self):
        class Stack1(ResourceCollection):
            def __init__(self, *args, **kwargs):
                r1 = Resource1('r1')
                super(Stack1, self).__init__(r1, *args, **kwargs)

        class Stack2(Stack1):
            def __init__(self, *args, **kwargs):
                r2 = Resource1('r2')
                super(Stack2, self).__init__(r2, *args, **kwargs)

        s = Stack2()
        self.assert_json(s, {'Resources': {'r1': {'Type': 'Resource1'}, 'r2': {'Type': 'Resource1'}}})

    def test_property_assignment(self):
        r = ResourceWithProperties(prop1='old value')
        r.prop1 = 'new value'
        self.assert_json(r, {'Type':'ResourceWithProperties', 'Properties':{'prop1': 'new value'}})

    def test_defaults_assigning(self):
        class ResourceWithDefaults(Resource):
            __module__ = ''
            prop1 = Property()

        ResourceWithDefaults.prop1 = 'default'
        r = ResourceWithDefaults()
        self.assert_json(r, {'Type':'ResourceWithDefaults',
            'Properties':{'prop1': 'default'}})
