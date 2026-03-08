# GramSense AI - AWS Architecture Diagram

```mermaid
graph TB
    subgraph "User Layer"
        U[Users<br/>Farmers & FPOs]
        M[Mobile/Web<br/>Browser]
    end

    subgraph "AWS CloudFront (CDN)"
        CF[CloudFront<br/>Distribution]
    end

    subgraph "AWS Region - us-east-1"
        subgraph "VPC"
            subgraph "Public Subnet"
                IGW[Internet Gateway]
                ALB[Application Load Balancer]
                EC2[EC2 Instance<br/>t3.micro<br/>GramSense API]
            end

            subgraph "Private Subnet"
                Lambda[Lambda Functions<br/>Data Processing]
                RDS[RDS PostgreSQL<br/>Metadata Storage]
            end
        end

        subgraph "AWS Services"
            S3[S3 Bucket<br/>Static Assets<br/>Data Storage]
            DynamoDB[DynamoDB<br/>Price Data<br/>Cache]
            SageMaker[SageMaker<br/>ML Models<br/>Forecasting]
            Bedrock[Bedrock<br/>AI Assistant<br/>Explanations]
            CloudWatch[CloudWatch<br/>Monitoring<br/>Logs]
        end

        subgraph "Security & IAM"
            WAF[WAF<br/>Web Application Firewall]
            IAM[IAM Roles<br/>Least Privilege]
        end
    end

    subgraph "External Data Sources"
        IMD[IMD Weather API<br/>Public Data]
        Agmarknet[Agmarknet<br/>Mandi Prices<br/>Public Data]
        OpenWeather[OpenWeatherMap<br/>Weather Backup]
    end

    %% Connections
    U --> M
    M --> CF
    CF --> ALB
    ALB --> EC2

    EC2 --> Lambda
    Lambda --> S3
    Lambda --> DynamoDB
    Lambda --> SageMaker
    Lambda --> Bedrock

    EC2 --> RDS
    EC2 --> CloudWatch

    ALB -.-> WAF
    EC2 -.-> IAM

    Lambda --> IMD
    Lambda --> Agmarknet
    Lambda --> OpenWeather

    %% Styling
    classDef awsService fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#000
    classDef userLayer fill:#4CAF50,stroke:#2E7D32,stroke-width:2px,color:#FFF
    classDef external fill:#2196F3,stroke:#0D47A1,stroke-width:2px,color:#FFF

    class U,M userLayer
    class CF,ALB,EC2,Lambda,RDS,S3,DynamoDB,SageMaker,Bedrock,CloudWatch,WAF,IAM awsService
    class IMD,Agmarknet,OpenWeather external
```

## Architecture Explanation

### Components

1. **User Layer**
   - Farmers and FPOs access via web/mobile browsers
   - Responsive design optimized for rural connectivity

2. **Edge Layer**
   - CloudFront CDN for global content delivery
   - Reduces latency for users across India

3. **Compute Layer**
   - EC2 instance (t3.micro) for main application
   - Lambda functions for serverless data processing
   - Auto-scaling based on demand

4. **Data Layer**
   - DynamoDB for fast price data access
   - RDS for relational metadata
   - S3 for static assets and bulk data

5. **AI/ML Layer**
   - SageMaker for forecasting models
   - Amazon Bedrock for explainable AI responses

6. **Security Layer**
   - WAF for application protection
   - IAM with least privilege access
   - VPC isolation

### Data Flow

1. User requests → CloudFront → ALB → EC2
2. EC2 processes request, calls Lambda for data processing
3. Lambda fetches data from DynamoDB/S3 or external APIs
4. AI processing via SageMaker/Bedrock
5. Results cached and returned to user

### Cost Optimization

- **Free Tier Utilization**: t3.micro (750 hours/month), Lambda free tier
- **Reserved Instances**: For production scaling
- **S3 Storage Classes**: Intelligent tiering
- **CloudWatch**: Basic monitoring included

### Scalability

- **Horizontal Scaling**: EC2 auto-scaling groups
- **Serverless**: Lambda for variable workloads
- **Global**: CloudFront for worldwide access
- **Data**: DynamoDB on-demand scaling

### Security Measures

- **Network**: VPC with public/private subnets
- **Access**: IAM roles, no direct credentials
- **Data**: Encryption at rest and in transit
- **Monitoring**: CloudWatch alerts for anomalies

### Deployment

- **Infrastructure as Code**: CloudFormation templates
- **CI/CD**: GitHub Actions for automated deployment
- **Monitoring**: CloudWatch dashboards
- **Backup**: S3 versioning and cross-region replication