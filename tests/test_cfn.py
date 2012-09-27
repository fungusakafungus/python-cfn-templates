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
        actual = json.loads(json.dumps(actual, cls=ResourceEncoder, indent=2))
        expected = json.loads(json.dumps(expected))
        self.assertEqual(expected, actual)

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

    def test_stack_creation(self):
        r1 = ResourceWithProperties(prop1=1)
        stack = Stack(r1)
        self.assert_json(stack, {'Resources': { 'ResourceWithProperties1':{ 'Type':
            'ResourceWithProperties', 'Properties': {'prop1': 1} } } })

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
        r1 = ResourceWithAttributes()
        r2 = ResourceWithProperties()
        r2.prop1 = r1.attr1
        stack = Stack(r1, r2)
        self.assert_json(stack,
            {'Resources': {
                'ResourceWithAttributes1':{
                    'Type': 'ResourceWithAttributes'
                    },
                'ResourceWithProperties2':{
                    'Type': 'ResourceWithProperties',
                    'Properties': {
                        'prop1': {'Fn::GetAttr': ['ResourceWithProperties1', 'attr1']}
                        }
                    },
                }
                })
