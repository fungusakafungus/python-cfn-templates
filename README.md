This is a DSL for Amazon CloudFormation

See tests and example-node.py for usage

Requirements
------------

 * py.test

TODO
----

 * provide an example of stack inheritance
 * use cfn-validate-template
 * Parameters, Mappings
  * maybe use argparse in an example to circumvent the need of parameters
 * write or generate classes for all cfn template types
  * maybe we could write a json schema for it?..
 * get rid of metaclass madness

Caveats
-------

It only contains a very small part of CloudFormation types

Changelog
---------

 - 0.3.0
  * changed the way how to define custom properties, see `test_custom_property` in `tests/test_core.py`
