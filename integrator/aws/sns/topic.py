from pulumi_aws import sns

from diagrams.eraser import cloud_architecture as diagram


class Topic(sns.Topic):
    def __init__(self, resource_name: str, **kwargs) -> None:
        """Create a new SNS Topic.

        Args:
            resource_name (str): The name of the SNS Topic.
            **kwargs: [additional arguments](https://www.pulumi.com/registry/packages/aws/api-docs/sns/topic/#inputs)
        """

        super().__init__(resource_name, **kwargs)

        self.diagram = diagram.Node(
            resource_name, icon="aws-simple-notification-service"
        )
