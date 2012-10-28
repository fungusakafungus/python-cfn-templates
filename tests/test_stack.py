# -*- encoding: utf-8 -*-
import unittest2

from cfn.core import *

from tests.test_core import assert_json, ResourceWithAttributes

unittest2.TestCase.assert_json = assert_json


class TestStack(unittest2.TestCase):
    def test_version(self):
        s = Stack()
        self.assertEqual("2010-09-09", s.AWSTemplateFormatVersion)

    def test_description(self):
        s = Stack(Description='My stack')
        self.assertEqual("My stack", s.Description)

    def test_description_assignment(self):
        s = Stack()
        s.Description = 'My stack'
        self.assertEqual("My stack", s.Description)

    def test_description_in_json(self):
        s = Stack(Description='My stack')
        self.assert_json(s, {
            'AWSTemplateFormatVersion': '2010-09-09',
            'Description': 'My stack'
            })

    def test_description_and_resources(self):
        class R(Resource):
            __module__ = ''

        r = R()
        s = Stack(r, Description='My stack')
        self.assert_json(s, {
            'AWSTemplateFormatVersion': '2010-09-09',
            'Description': 'My stack',
            'Resources': {
                'R': {
                    'Type': 'R'
                    }
                }
            })

    def test_outputs(self):
        r = ResourceWithAttributes()
        s = Stack(r)
        s.Outputs['output'] = r.attr1
        self.assert_json(s, {
            'AWSTemplateFormatVersion': '2010-09-09',
            'Resources': {
                'ResourceWithAttributes': {
                    'Type': 'ResourceWithAttributes'
                    }
                },
            'Outputs': {
                'output': {'Fn::GetAtt': ['ResourceWithAttributes', 'attr1']
                    }
                }
            })
