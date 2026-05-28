
import os

import aws_cdk as cdk
from iac.stacks.dev_box import DevBox


def main() -> None:
	app = cdk.App()

	env = cdk.Environment(
		account=os.getenv("CDK_DEFAULT_ACCOUNT"),
		region=os.getenv("CDK_DEFAULT_REGION"),
	)

	DevBox(app, "DevBox", env=env)

	app.synth()


if __name__ == "__main__":
	main()
