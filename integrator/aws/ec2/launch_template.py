from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pulumi
from pulumi_aws import ec2

from diagrams.eraser import cloud_architecture as diagram

from .instance import Instance

if TYPE_CHECKING:
    from ..iam import InstanceRole
    from .key_pair import KeyPair
    from .security_group import SecurityGroup
    from .subnet import Subnet
    from .user_data import UserData


class LaunchTemplate(ec2.LaunchTemplate):
    def __init__(
        self,
        resource_name: str,
        role: InstanceRole,
        image: ec2.AwaitableGetAmiResult,
        user_data: UserData,
        key_pair: KeyPair,
        instance_type: str = "t3.micro",
        cpu_credits: str = "standard",
        block_device_mappings: Optional[list[dict[str, str | dict]]] = None,
        **kwargs,
    ) -> None:
        """Create a new EC2 Launch Template.

        Args:
            resource_name (str): The name of the EC2 Launch Template.
            **kwargs: [additional arguments](https://www.pulumi.com/registry/packages/aws/api-docs/ec2/launchtemplate/#inputs)
        """
        profile = role.create_instance_profile(resource_name)
        if block_device_mappings is None:
            block_device_mappings = [
                {
                    "device_name": "/dev/sda1",
                    "ebs": {
                        "delete_on_termination": True,
                        "volume_size": 10,
                        "volume_type": "gp3",
                    },
                }
            ]

        super().__init__(
            resource_name,
            iam_instance_profile={"arn": profile.arn},
            image_id=image.id,
            user_data=user_data.b64encode(),
            key_name=key_pair.id,
            instance_type=instance_type,
            credit_specification={"cpu_credits": cpu_credits},
            block_device_mappings=block_device_mappings,
            update_default_version=True,
            tag_specifications=[
                {"resource_type": "instance", "tags": {"Name": resource_name}},
                {"resource_type": "volume", "tags": {"Name": resource_name}},
            ],
            **kwargs,
        )

        self.diagram = diagram.Node(resource_name, icon="aws-ec2")

    def create_instance(
        self,
        resource_name: str,
        subnet: Subnet,
        security_group: SecurityGroup,
        **kwargs,
    ) -> ec2.Instance:
        """Create a new EC2 Instance using this Launch Template.

        Args:
            resource_name (str): The name of the EC2 Instance.
            subnet (Subnet): The subnet to launch the instance in.
            security_group (SecurityGroup): The security group to attach to the instance.
            **kwargs: [additional arguments](https://www.pulumi.com/registry/packages/aws/api-docs/ec2/instance/#inputs)

        Returns:
            ec2.Instance: The new EC2 Instance.
        """
        kwargs.setdefault(
            "opts",
            pulumi.ResourceOptions(
                parent=self, ignore_changes=["tags", "default_tags"]
            ),
        )
        instance = Instance(
            resource_name,
            launch_template=self,
            subnet=subnet,
            security_group=security_group,
            **kwargs,
        )
        self.diagram.edges.connect(instance.diagram)
        return instance
