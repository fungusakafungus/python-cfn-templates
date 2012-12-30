import pytest

from cfn.core import Resource, Property, to_json, ResourceCollection
from cfn.util import Facts
from cfn.core import Stack
from cfn.util import Parameter
from tests.test_core import ResourceWithAttributes, ResourceWithProperties, assert_json


class ResourceWithFacts(Resource):
    __module__ = ''
    facts = Property()


def test_two_facts():
    r = ResourceWithFacts('AName')
    f = Facts()
    f['fact1'] = 'value1'
    f['fact2'] = 'value2'

    r.facts = {'some_key': f}

    assert to_json(ResourceCollection(r)) == to_json({
        'Resources': {
            'AName': {
                'Type': 'ResourceWithFacts',
                'Properties': {
                    'facts': {
                        'some_key': "---\nfact1: value1\nfact2: value2\n"
                    }
                }
            }
        }
    }
    )


def test_parameters():
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


def test_parameters2():
    from cfn.util import Parameter
    r = ResourceWithAttributes()
    p = Parameter('param1')
    s = Stack(r, p)
    assert_json(s, {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Parameters': {
            'param1': {
            'Type': 'String'
            }
        },
        'Resources': {
            'ResourceWithAttributes': {
                'Type': 'ResourceWithAttributes'
            }
        },
    })


def test_parameters_referencing():
    r = ResourceWithProperties()
    p = Parameter()
    r.prop1 = p
    s = Stack(**locals())
    assert_json(s, {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Parameters': {
            'p': {
            'Type': 'String'
            }
        },
        'Resources': {
            'r': {
                'Type': 'ResourceWithProperties',
                'Properties': {
                    'prop1': {'Ref': 'p'}
                }
            }
        },
    })


def test_parameter_format_without_a_name_throws_an_exception():
    with pytest.raises(AttributeError):
        p = Parameter()
        r.prop1 = 'prefix{0}'.format(p)


def test_parameters_referencing_in_strings():
    r = ResourceWithProperties()
    p = Parameter('param')
    r.prop1 = 'prefix{0}'.format(p)
    s = Stack(**locals())
    assert_json(s, {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Parameters': {
            'param': {
            'Type': 'String'
            }
        },
        'Resources': {
            'r': {
                'Type': 'ResourceWithProperties',
                'Properties': {
                    'prop1': {'Fn::Join': ['', ['prefix', {'Ref': 'param'}]]}
                }
            }
        },
    })
