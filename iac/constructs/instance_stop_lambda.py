"""Lambda to auto-stop EC2 instances."""

import aws_cdk as cdk
from aws_cdk import aws_ec2, aws_iam, aws_lambda, aws_events, aws_events_targets
from constructs import Construct


class InstanceStopLambda(Construct):
    """Create lambda to stop instances with tag devbox:auto-schedule and schedule it to run nightly at 03:00 UTC."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stopper = aws_lambda.Function(
            self,
            "DevBoxStopper",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=aws_lambda.Code.from_asset("lambdas/dev_box_stop"),
            timeout=cdk.Duration.minutes(1),
        )

        stopper.add_to_role_policy(
            aws_iam.PolicyStatement(actions=["ec2:DescribeInstances", "ec2:StopInstances"], resources=["*"])
        )

        rule = aws_events.Rule(
            self,
            "DevBoxStopSchedule",
            schedule=aws_events.Schedule.cron(minute="0", hour="3"),
        )
        rule.add_target(aws_events_targets.LambdaFunction(stopper))
