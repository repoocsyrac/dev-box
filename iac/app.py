"""CDK application entry point for the dev box stack."""

import os

import aws_cdk as cdk
from iac.stacks.dev_box import DevBox


def main() -> None:
	"""Synthesize the CDK app."""

	app = cdk.App()

	env = cdk.Environment(
		account=os.getenv("CDK_DEFAULT_ACCOUNT"),
		region=os.getenv("CDK_DEFAULT_REGION"),
	)

	instance_name = app.node.try_get_context("INSTANCE_NAME") or "dev-box-instance"

	DevBox(
		app,
		"DevBox",
		instance_name=instance_name,
		env=env,
	)

	app.synth()


if __name__ == "__main__":
	main()
