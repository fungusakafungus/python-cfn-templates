# -*- coding: utf-8 -*-
from cfn.core import Resource, Attribute, Property

class {{name}}(Resource):
    _type = '{{title}}'
    ## for property in properties:

    {{property.name}} = Property()
    {{property.name}}.__doc__ = """{{ property.doc|indent(8) }}"""
    ## endfor
