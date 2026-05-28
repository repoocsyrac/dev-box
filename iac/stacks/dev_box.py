from aws_cdk import Stack, aws_ec2
from constructs import Construct

from iac.constructs.isolated_ec2 import IsolatedEc2

class DevBox(Stack):
    def __init__(self, scope: Construct, id: str, instance_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        IsolatedEc2(
            self,
            "DevBox",
            instance_name=instance_name,
        )