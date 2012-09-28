from cfn import *
import json
#from nose.tools import *
import unittest2
class Resource1(Resource): pass

class ResourceWithProperties(Resource):
    prop1=Property()

class ResourceWithAttributes(Resource):
    attr1=Attribute()

class TestCFN(unittest2.TestCase):
    def setUp(self):
        self.maxDiff=None

    def assert_json(self, actual, expected):
        actual = json.dumps(actual, cls=ResourceEncoder, indent=2)
        expected = json.dumps(expected, indent=2)
        self.assertEqual(unicode(expected), unicode(actual))

    def test_resource_creation(self):
        r = Resource1()

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
        stack = Stack(r1)
        self.assert_json(stack, {'Resources': { 'ResourceWithProperties1':{ 'Type':
            'ResourceWithProperties', 'Properties': {'prop1': 1} } } })

    def test_autonaming(self):
        r1 = Resource1()
        r2 = Resource1()
        r3 = Resource1()
        stack = Stack(r1, r2, r3)
        self.assert_json(stack, {'Resources': {
            'Resource11':{ 'Type': 'Resource1'},
            'Resource12':{ 'Type': 'Resource1'},
            'Resource13':{ 'Type': 'Resource1'},
            }})

    def test_stack_with_dependencies_in_properties(self):
        r1 = ResourceWithProperties()
        r2 = ResourceWithProperties()
        r1.prop1=r2
        stack = Stack(r1, r2)
        self.assert_json(stack,
                {'Resources': {
                    'ResourceWithProperties1':{
                        'Type': 'ResourceWithProperties',
                        'Properties': {
                            'prop1': {'Ref': 'ResourceWithProperties2'}
                            }
                        },
                    'ResourceWithProperties2':{
                        'Type': 'ResourceWithProperties',
                        }
                    }
                    })

    def test_stack_with_dependencies_in_attributes(self):
        r1 = ResourceWithAttributes('r1')
        r2 = ResourceWithProperties('r2')
        r2.prop1 = r1.attr1
        stack = Stack(r1, r2)
        self.assert_json(stack,
            {'Resources': {
                'r1':{
                    'Type': 'ResourceWithAttributes'
                    },
                'r2':{
                    'Type': 'ResourceWithProperties',
                    'Properties': {
                        'prop1': {'Fn::GetAttr': ['r1', 'attr1']}
                        }
                    },
                }
                })

    def test_resource_format(self):
        r1 = Resource1('r1')
        self.assertEquals('{r1}','{0}'.format(r1))

    def test_join_in_property(self):
        r1 = Resource1('r1')
        r2 = ResourceWithProperties('r2')
        r2.prop1 = 'prefix{0}'.format(r1)
        stack = Stack(r1, r2)
        self.assert_json(stack,
            {'Resources': {
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
