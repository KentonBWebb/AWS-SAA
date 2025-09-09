from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_redshift as redshift,
)
from constructs import Construct

class RedshiftStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        vpc = ec2.Vpc(
            self, "RedshiftVPC3Tier",
            max_azs=2,
            nat_gateways=1
        )

        # Security group for Redshift
        sg = ec2.SecurityGroup(
            self, "RedshiftSG3Tier",
            vpc=vpc,
            description="Allow access to Redshift",
            allow_all_outbound=True
        )

        # Allow inbound access (adjust CIDR for your needs!)
        sg.add_ingress_rule(
            peer=ec2.Peer.ipv4("YOUR_PUBLIC_IP/32"),  # Replace with your IP
            connection=ec2.Port.tcp(5439)
        )

        # Redshift Cluster Subnet Group
        subnet_group = redshift.CfnClusterSubnetGroup(
            self, "RedshiftSubnetGroup",
            description="Subnet group for Redshift",
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets],
            cluster_subnet_group_name="redshift-subnet-group"
        )

        # Redshift Cluster
        cluster = redshift.CfnCluster(
            self, "RedshiftCluster3Tier",
            cluster_type="single-node",  # Change to multi-node for prod
            db_name="mydb",
            master_username="admin",
            master_user_password="ChangeThisPassword123",  # store in SecretsManager ideally
            node_type="dc2.large",  # dev: dc2.large / prod: ra3.4xlarge etc.
            vpc_security_group_ids=[sg.security_group_id],
            cluster_subnet_group_name=subnet_group.cluster_subnet_group_name,
            publicly_accessible=False
        )

