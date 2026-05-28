from aws_cdk import aws_ec2
from constructs import Construct


class IsolatedEc2(Construct):
	def __init__(self, scope: Construct, construct_id: str, instance_name: str, **kwargs) -> None:
		super().__init__(scope, construct_id, **kwargs)

		security_group = aws_ec2.SecurityGroup(
            self,
            "DevBoxSecurityGroup",
            allow_all_outbound=True,
            security_group_name="DevBoxSecurityGroup",
        )

		role = aws_ec2.Role(
            self,
            "DevBoxRole",
            assumed_by=aws_ec2.ServicePrincipal("ec2.amazonaws.com"),
        )

		user_data = aws_ec2.UserData.for_linux()
		user_data.add_commands(
            "yum update -y",
            "yum install -y git",
            "yum install -y docker",
            "service docker start",
            "usermod -a -G docker ec2-user",
        )

		self.ec2 = aws_ec2.Instance(
            self,
            "DevBoxInstance",
            instance_type=aws_ec2.InstanceType("t3.medium"),
            machine_image=aws_ec2.MachineImage.latest_amazon_linux(),
            associate_public_ip_address=True,
            instance_name=instance_name,
            role=role,
            security_group=security_group,
            ssm_session_permissions=True,
            user_data=user_data,
        )