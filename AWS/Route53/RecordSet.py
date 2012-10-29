# -*- coding: utf-8 -*-
from cfn.core import Resource, Attribute, Property

class RecordSet(Resource):
    _type = 'AWS::Route53::RecordSet'
    HostedZoneId = Property()
    HostedZoneId.__doc__ = """The ID of the hosted zone.
        
        Required : Conditional. You must specify either the HostedZoneName or HostedZoneId , but you cannot
                          specify both.
        
        Type : String"""
    HostedZoneName = Property()
    HostedZoneName.__doc__ = """The name of the domain for the hosted zone where you want to add the record set.
        
        When you create a stack using an AWS::Route53::RecordSet that specifies HostedZoneName , AWS CloudFormation attempts to find a hosted zone whose name matches the HostedZoneName . If AWS CloudFormation cannot find a hosted zone with a matching domain
                          name, or if there is more than one hosted zone with the specified domain name, AWS CloudFormation will not create
                          the stack.
        
        If you have multiple hosted zones with the same domain name, you must explicitly specify the
                          hosted zone using HostedZoneId .
        
        Required : Conditional. You must specify either the HostedZoneName or HostedZoneId , but you cannot
                          specify both.
        
        Type : String"""
    Name = Property()
    Name.__doc__ = """The name of the domain. This must be a fully-specified domain, ending with a period as the last
                          label indication. If you omit the final period, Amazon Route 53 assumes the domain is relative to the
                          root.
        
        Required : Yes
        
        Type : String"""
    Type = Property()
    Type.__doc__ = """The type of records to add.
        
        Required : Yes
        
        Type : String
        
        Valid Values : A | AAAA | CNAME | MX | NS | PTR | SOA | SPF | SRV |
                          TXT"""
    TTL = Property()
    TTL.__doc__ = """The resource record cache time to live (TTL), in seconds.
        
        If TTL is specified, ResourceRecords is also
                          required.
        
        Required : No
        
        Type : String"""
    ResourceRecords = Property()
    ResourceRecords.__doc__ = """List of resource records to add. Each record should be in the format appropriate for the record
                          type specified by the Type property. For information about different record
                          types and their record formats, see Appendix: Domain Name Format in the Route 53 Developer
                                Guide .
        
        Required : Conditional. Required if TTL is specified.
        
        Type : list of Strings"""
    Weight = Property()
    Weight.__doc__ = """Weighted resource record sets only: Among resource record sets that have
                          the same combination of DNS name and type, a value that determines what portion of traffic for the
                          current resource record set is routed to the associated location.
        
        For more information about weighted resource record sets, see Setting Up Weighted Resource Record Sets in the Route 53 Developer
                             Guide .
        
        Required : Conditional. Required if you are creating a weighted resource
                          record set.
        
        Type : Integer"""
    SetIdentifier = Property()
    SetIdentifier.__doc__ = """A unique identifier that differentiates among multiple resource record sets that have the same
                          combination of DNS name and type.
        
        Required : Conditional. Required if you are creating a weighted resource
                          record set.
        
        For more information about weighted resource record sets, see Setting Up Weighted Resource Record Sets in the Route 53 Developer
                             Guide .
        
        Type : String"""
    AliasTarget = Property()
    AliasTarget.__doc__ = """Alias resource record sets only: Information about the domain to which you
                          are redirecting traffic.
        
        For more information about alias resource record sets, see Creating Alias Resource Record Sets in the Route 53 Developer
                          Guide .
        
        Note
        
        Currently, Amazon Route 53 supports aliases only for Elastic Load
                             Balancing.
        
        Required : Conditional. Required if you are creating an alias resource
                          record set.
        
        Type : AliasTarget"""
    Comment = Property()
    Comment.__doc__ = """Any comments you want to include about the hosted zone.
        
        Required : No
        
        Type : String"""
