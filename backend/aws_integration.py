"""
AWS Integration Module for GramSense AI
This module provides integration with AWS services for production deployment.
"""

import os
import boto3
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AWSService:
    """AWS service integration class."""

    def __init__(self):
        self.region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.s3_client = None
        self.dynamodb_client = None
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize AWS clients if credentials are available."""
        try:
            # Check if AWS credentials are configured
            if os.getenv('AWS_ACCESS_KEY_ID'):
                self.s3_client = boto3.client('s3', region_name=self.region)
                self.dynamodb_client = boto3.client('dynamodb', region_name=self.region)
                print("✅ AWS clients initialized")
            else:
                print("⚠️  AWS credentials not found. Running in local mode.")
        except Exception as e:
            print(f"⚠️  AWS initialization failed: {e}. Running in local mode.")

    def upload_to_s3(self, bucket_name: str, key: str, data: bytes) -> bool:
        """Upload data to S3 bucket."""
        if not self.s3_client:
            print("⚠️  S3 client not available")
            return False

        try:
            self.s3_client.put_object(Bucket=bucket_name, Key=key, Body=data)
            print(f"✅ Uploaded to S3: s3://{bucket_name}/{key}")
            return True
        except ClientError as e:
            print(f"❌ S3 upload failed: {e}")
            return False

    def save_to_dynamodb(self, table_name: str, item: Dict[str, Any]) -> bool:
        """Save item to DynamoDB table."""
        if not self.dynamodb_client:
            print("⚠️  DynamoDB client not available")
            return False

        try:
            # Convert Python dict to DynamoDB format
            dynamodb_item = {}
            for key, value in item.items():
                if isinstance(value, str):
                    dynamodb_item[key] = {'S': value}
                elif isinstance(value, int):
                    dynamodb_item[key] = {'N': str(value)}
                elif isinstance(value, float):
                    dynamodb_item[key] = {'N': str(value)}
                # Add more type conversions as needed

            self.dynamodb_client.put_item(TableName=table_name, Item=dynamodb_item)
            print(f"✅ Saved to DynamoDB: {table_name}")
            return True
        except ClientError as e:
            print(f"❌ DynamoDB save failed: {e}")
            return False

# Global AWS service instance
aws_service = AWSService()

def get_aws_service() -> AWSService:
    """Get the global AWS service instance."""
    return aws_service