from aws_cdk import (
    Stack,
)
from constructs import Construct
import aws_cdk.aws_ecs_patterns as ecs_patterns
from aws_cdk.aws_ecr_assets import DockerImageAsset
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_iam as iam
import aws_cdk.aws_elasticloadbalancingv2 as elbv2
import aws_cdk.aws_route53 as route53
import aws_cdk.aws_certificatemanager as acm
import aws_cdk.aws_ec2 as ec2
from os import path


class ChatbotApp(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        domain_name = self.node.try_get_context("domain_name")
        subdomain = self.node.try_get_context("subdomain")
        print(f"domain_name: {domain_name}")
        print(f"subdomain: {subdomain}")
        if not domain_name or not subdomain:
            raise ValueError("Please provide context values: domain_name and subdomain")

        hosted_zone = route53.HostedZone.from_lookup(
            self,
            "HostedZone",
            domain_name=domain_name,
        )

        certificate = acm.Certificate(
            self,
            "Certificate",
            domain_name=f"{subdomain}.{domain_name}",
            validation=acm.CertificateValidation.from_dns(hosted_zone),
        )

        asset = DockerImageAsset(
            self,
            "DockerImageAsset",
            directory=path.join(path.dirname(__file__), "docker_app"),
        )

        vpc = ec2.Vpc(self, "Vpc", max_azs=2, nat_gateways=0)



        load_balanced_fargate_service = (
            ecs_patterns.ApplicationLoadBalancedFargateService(
                self,
                "Service",
                task_image_options={
                    "image": ecs.ContainerImage.from_docker_image_asset(asset),
                    "container_port": 8501,
                },
                certificate=certificate,
                domain_name=f"{subdomain}.{domain_name}",
                domain_zone=hosted_zone,
                redirect_http=True,
                assign_public_ip=True,
                vpc=vpc,
            )
        )

        load_balanced_fargate_service.task_definition.task_role.add_to_principal_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=["*"],
            )
        )
        listener = load_balanced_fargate_service.listener

        listener.add_action(
            "DefaultAction",
            action=elbv2.ListenerAction.forward(
                [load_balanced_fargate_service.target_group]
            ),
            conditions=[elbv2.ListenerCondition.path_patterns(["/*"])],
            priority=1,
        )

