from diagrams import Diagram, Cluster
from diagrams.aws.compute import ECS
from diagrams.aws.network import CloudFront, ALB, VPC
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import SQS
from diagrams.aws.storage import S3
from diagrams.aws.compute import Lambda
from diagrams.aws.general import Client

with Diagram("Video Transcriber AI - Architecture", show=False, filename="video_transcriber_ai_architecture", direction="LR", 
             graph_attr={"splines": "ortho", "nodesep": "1.2", "ranksep": "2.5", "fontsize": "18"},
             node_attr={"fontsize": "16"},
             edge_attr={"fontsize": "14"}):

    user = Client("User")

    with Cluster("Frontend (Global)"):
        cf = CloudFront("CloudFront\n(React App)")

    with Cluster("VPC"):
        with Cluster("Public Subnet"):
            alb = ALB("Application\nLoad Balancer")
        
        with Cluster("Private Subnet"):
            with Cluster("ECS Cluster"):
                api_service = ECS("api-service")
                video_processor = ECS("video-processor")
                dlq_monitor = ECS("dlq-monitor")
            
            lambda_func = Lambda("Lambda\nTrigger")

    with Cluster("AWS Managed Services (Global)"):
        s3 = S3("S3\n(Video Storage)")
        dynamodb = Dynamodb("DynamoDB\n(Metadata)")
        with Cluster("Messaging"):
            sqs = SQS("SQS Queue")
            dlq = SQS("Dead Letter\nQueue")

    # Main user flow
    user >> cf >> alb >> api_service
    
    # API service connections
    api_service >> s3
    api_service >> dynamodb
    
    # Video processing workflow
    s3 >> lambda_func >> sqs >> video_processor
    video_processor >> dynamodb
    video_processor >> dlq
    
    # DLQ monitoring
    dlq >> dlq_monitor
