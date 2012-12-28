# -*- encoding: utf-8 -*-

from cfn.core import *

from tests.test_core import assert_json, ResourceWithAttributes


def test_version():
    s = Stack()
    assert "2010-09-09" == s.AWSTemplateFormatVersion


def test_description():
    s = Stack(Description='My stack')
    assert "My stack" == s.Description


def test_description_assignment():
    s = Stack()
    s.Description = 'My stack'
    assert "My stack" == s.Description


def test_description_in_json():
    s = Stack(Description='My stack')
    assert_json(s, {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Description': 'My stack'
    })


def test_description_and_resources():
    class R(Resource):
        __module__ = ''

    r = R()
    s = Stack(r, Description='My stack')
    assert_json(s, {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Description': 'My stack',
        'Resources': {
            'R': {
                'Type': 'R'
                }
        }
    })


def test_outputs():
    r = ResourceWithAttributes()
    s = Stack(r)
    s.Outputs['output'] = r.attr1
    assert_json(s, {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Resources': {
            'ResourceWithAttributes': {
                'Type': 'ResourceWithAttributes'
                }
        },
        'Outputs': {
            'output': {'Fn::GetAtt': ['ResourceWithAttributes', 'attr1']}
        }
    })


def test_parameters():
    from cfn.util import Parameter
    r = ResourceWithAttributes()
    s = Stack(r, p=Parameter())
    assert_json(s, {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Parameters': {
            'p': {
            'Type': 'String'
            }
        },
        'Resources': {
            'ResourceWithAttributes': {
                'Type': 'ResourceWithAttributes'
            }
        },
    })
