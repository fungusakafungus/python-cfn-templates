from cfn.core import Resource, Property, to_json, ResourceCollection
from cfn.util import Facts

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
