
import os
from platform import node

import aws_cdk as cdk
from iac.stacks.dev_box import DevBox


def main() -> None:
	app = cdk.App()

	env = cdk.Environment(
		account=os.getenv("CDK_DEFAULT_ACCOUNT"),
		region=os.getenv("CDK_DEFAULT_REGION"),
	)

	INSTANCE_NAME = node.try_get_context("INSTANCE_NAME") or "dev-box-instance"

	DevBox(
		app,
		"DevBox",
		instance_name=INSTANCE_NAME,
		env=env
	)

	app.synth()


if __name__ == "__main__":
	main()
