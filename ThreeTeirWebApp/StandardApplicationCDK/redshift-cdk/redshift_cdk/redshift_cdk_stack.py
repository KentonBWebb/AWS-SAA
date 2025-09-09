from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_redshift as redshift,
)
from constructs import Construct

class RedshiftCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a new VPC
        vpc = ec2.Vpc(
            self, "RedshiftVpc",
            max_azs=2,
            nat_gateways=1
        )

        # Security group for Redshift
        sg = ec2.SecurityGroup(
            self, "RedshiftSG",
            vpc=vpc,
            description="Allow Redshift access",
            allow_all_outbound=True
        )

        # 👇 Change to your own IP so you can connect
        sg.add_ingress_rule(
            peer=ec2.Peer.ipv4("10.197.188.240/32"),
            connection=ec2.Port.tcp(5439)
        )

        # Create subnet group
        subnet_group = redshift.CfnClusterSubnetGroup(
            self, "RedshiftSubnetGroup",
            description="Redshift subnet group",
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets],
        )

        # Create Redshift cluster
        cluster = redshift.CfnCluster(
            self, "RedshiftCluster",
            cluster_type="single-node",
            db_name="mydb",
            master_username="admin",
            master_user_password="ChangeThisPassword123!",
            node_type="ra3.xlplus",
            vpc_security_group_ids=[sg.security_group_id],
            cluster_subnet_group_name=subnet_group.ref,  # ✅ Use Ref, not hardcoded string
            publicly_accessible=True
        )

        # Ensure dependency so subnet group is ready before cluster
        cluster.add_dependency(subnet_group)