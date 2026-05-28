"""Reusable construct for a private, SSM-managed EC2 dev box."""

from aws_cdk import aws_ec2, aws_iam
from constructs import Construct


class IsolatedEc2(Construct):
    """Provision a private Ubuntu EC2 instance with SSM and developer tools."""

    def __init__(self, scope: Construct, construct_id: str, instance_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = aws_ec2.Vpc(
            self,
            "DevBoxVpc",
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                aws_ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_EGRESS,
                )
            ],
        )

        security_group = aws_ec2.SecurityGroup(
            self,
            "DevBoxSecurityGroup",
            vpc=vpc,
            allow_all_outbound=True,
            security_group_name="DevBoxSecurityGroup",
        )

        role = aws_iam.Role(
            self,
            "DevBoxRole",
            assumed_by=aws_iam.ServicePrincipal("ec2.amazonaws.com"),
        )
        role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
        )

        user_data = aws_ec2.UserData.for_linux()
        user_data.add_commands(
            "apt-get update -y",
            "apt-get install -y git docker.io unzip curl",
            "systemctl enable docker",
            "systemctl start docker",
            "usermod -aG docker ubuntu",
            "snap install amazon-ssm-agent --classic || true",
            "systemctl enable snap.amazon-ssm-agent.amazon-ssm-agent.service || true",
            "systemctl restart snap.amazon-ssm-agent.amazon-ssm-agent.service || true",
            "curl -LsSf https://astral.sh/uv/install.sh | sh",
        )

        self.ec2 = aws_ec2.Instance(
            self,
            "DevBoxInstance",
            vpc=vpc,
            block_devices=[
                aws_ec2.BlockDevice(
                    device_name="/dev/sda1",
                    volume=aws_ec2.BlockDeviceVolume.ebs(30),
                )
            ],
            instance_type=aws_ec2.InstanceType("t3.medium"),
            machine_image=aws_ec2.MachineImage.latest_ubuntu(
                aws_ec2.UbuntuVersion.V22_04_LTS
            ),
            associate_public_ip_address=False,
            instance_name=instance_name,
            role=role,
            security_group=security_group,
            ssm_session_permissions=True,
            user_data=user_data,
        )