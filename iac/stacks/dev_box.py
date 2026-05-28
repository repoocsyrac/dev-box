"""Stack definition for the dev box infrastructure."""

from aws_cdk import Stack
from constructs import Construct

from iac.constructs.isolated_ec2 import IsolatedEc2


class DevBox(Stack):
    """Top-level stack that provisions the dev box construct."""

    def __init__(self, scope: Construct, stack_id: str, instance_name: str, **kwargs) -> None:
        super().__init__(scope, stack_id, **kwargs)

        IsolatedEc2(
            self,
            "DevBox",
            instance_name=instance_name,
        )