class Facts(dict):

    def to_json(self):
        return '\n'.join(['---'] + list('{0}: {1}'.format(k, v) for k, v in sorted(self.items()))) + '\n'


class Parameter(dict):

    def __init__(self, name=None, **kwargs):
        """
        Type                    Yes     String, Number, or CommaDelimitedList.
                                        A parameter of type String is simply a literal string.
                                        A parameter of type Number can be an integer or float. Note that AWS CloudFormation validates the parameter as a number but uses the parameter value within the template as a string.
                                        A parameter of type CommaDelimitedList is an array of literal strings separated by commas. The member strings are space trimmed and there is one more string than there are commas in the specified value.
        Default                 No      A value of the appropriate type for the template to use if no value is specified at stack creation. If the parameter has constraints defined, this value must adhere to those constraints.
        NoEcho                  No      If TRUE, the value of the parameter is masked with asterisks (*****) with cfn-describe-stacks.
        AllowedValues           No      An array containing the list of values allowed for the parameter.
        AllowedPattern          No      String constraint. A regular expression that represents the patterns allowed in the parameter's string value.
        MaxLength               No      String constraint. A integer value that determines the maximum number of characters in the parameter's string value.
        MinLength               No      String constraint. A integer value that determines the minimum number of characters in the parameter's string value.
        MaxValue                No      Number constraint. A numeric value that determines the largest numeric value allowed for the parameter.
        MinValue                No      Number constraint. A numeric value that determines the smallest numeric value allowed for the parameter.
        Description             No      A String type up to 4000 characters describing the parameter.
        ConstraintDescription   No      A String type that describes the constraint requirements when the user specifies a parameter value that does not match the constraints defined for the parameter. For example, a parameter that has an AllowedPattern of "[A-Za-z0-9]+" would display this error message when the user specified an invalid value:

                                        cfn-create-stack:  Malformed input-Parameter MyParameter must match pattern [A-Za-z0-9]+
                                        By adding a ConstraintDescription with a value "must only contain upper- and lowercase letters, and numbers", you can display a customized error message:

                                        cfn-create-stack:  Malformed input-Parameter MyParameter must only contain upper and lower case letters and numbers

        """
        self.name = name

        known_args = ('Type', 'Default', 'NoEcho', 'AllowedValues',
                      'AllowedPattern', 'MaxLength', 'MinLength', 'MaxValue',
                      'MinValue', 'Description', 'ConstraintDescription',)
        unknown_args = set(kwargs) - set(known_args)
        if unknown_args:
            raise ValueError('Parameter properties %s are invalid' % (list(unknown_args),))

        if 'Type' not in kwargs:
            kwargs['Type'] = 'String'

        dict.__init__(self, **kwargs)
