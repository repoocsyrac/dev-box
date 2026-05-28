"""Tests for the dev box infrastructure."""

from aws_cdk import App, Stack, Environment
from aws_cdk.assertions import Match, Template

from iac.constructs.isolated_ec2 import IsolatedEc2


def test_isolated_ec2_synthesizes_expected_resources() -> None:
    """The construct should synthesize a private Ubuntu instance with SSM access."""

    app = App()
    stack = Stack(
        app,
        "TestStack",
        env=Environment(account="000000000000", region="eu-west-2"),
    )

    IsolatedEc2(stack, "DevBox", instance_name="dev-box-instance")

    template = Template.from_stack(stack)

    template.resource_count_is("AWS::EC2::VPC", 1)
    template.resource_count_is("AWS::EC2::Subnet", 4)
    template.resource_count_is("AWS::EC2::NatGateway", 1)
    template.resource_count_is("AWS::EC2::Instance", 1)
    template.resource_count_is("AWS::EC2::SecurityGroup", 1)
    template.resource_count_is("AWS::IAM::Role", 1)
    template.has_resource_properties(
        "AWS::IAM::Role",
        {
            "ManagedPolicyArns": Match.array_with(
                [Match.object_like({"Fn::Join": Match.any_value()})]
            ),
        },
    )

    template.has_resource_properties(
        "AWS::EC2::Instance",
        {
            "InstanceType": "t3.medium",
            "BlockDeviceMappings": Match.array_with(
                [
                    Match.object_like(
                        {
                            "DeviceName": "/dev/sda1",
                            "Ebs": Match.object_like({"VolumeSize": 30}),
                        }
                    )
                ]
            ),
            "Tags": Match.array_with(
                [
                    Match.object_like(
                        {
                            "Key": "Name",
                            "Value": "dev-box-instance",
                        }
                    )
                ]
            ),
        },
    )
