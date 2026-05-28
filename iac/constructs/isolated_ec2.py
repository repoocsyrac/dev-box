"""Reusable construct for a private, SSM-managed EC2 dev box."""

import aws_cdk as cdk
from aws_cdk import aws_ec2, aws_iam, aws_lambda, aws_events, aws_events_targets
from constructs import Construct


class IsolatedEc2(Construct):
    """Provision a private Ubuntu EC2 instance with SSM and developer tools."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        instance_name: str,
        *,
        instance_type: str = "t3.medium",
        root_volume_size: int = 30,
        root_volume_type: str = "gp3",
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = aws_ec2.Vpc(
            self,
            "DevBoxVpc",
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                aws_ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=aws_ec2.SubnetType.PUBLIC,
                ),
                aws_ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_EGRESS,
                ),
            ],
        )

        # Add SSM Interface VPC endpoints so instance can reach SSM without NAT
        vpc.add_interface_endpoint(
            "SSMEndpoint", service=aws_ec2.InterfaceVpcEndpointAwsService.SSM
        )
        vpc.add_interface_endpoint(
            "SSMMessagesEndpoint",
            service=aws_ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES,
        )
        vpc.add_interface_endpoint(
            "EC2MessagesEndpoint",
            service=aws_ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES,
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
            aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"
            )
        )

        # Prefer AMI-provided SSM agent; only install Docker and essentials
        user_data = aws_ec2.UserData.for_linux()
        user_data.add_commands(
            "apt-get update -y",
            "apt-get install -y git docker.io unzip curl",
            "systemctl enable docker",
            "systemctl start docker",
            "usermod -aG docker ubuntu",
            "curl -LsSf https://astral.sh/uv/install.sh | sh",
        )

        self.ec2 = aws_ec2.Instance(
            self,
            "DevBoxInstance",
            vpc=vpc,
            block_devices=[
                aws_ec2.BlockDevice(
                    device_name="/dev/sda1",
                    volume=aws_ec2.BlockDeviceVolume.ebs(
                        root_volume_size, volume_type=root_volume_type
                    ),
                )
            ],
            instance_type=aws_ec2.InstanceType(instance_type),
            machine_image=aws_ec2.MachineImage.lookup(
                name="ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*",
                owners=["099720109477"],
            ),
            associate_public_ip_address=False,
            instance_name=instance_name,
            role=role,
            security_group=security_group,
            ssm_session_permissions=True,
            user_data=user_data,
        )

        # Tag instance for autoschedule
        cdk.Tags.of(self.ec2).add("devbox:auto-schedule", "true")
