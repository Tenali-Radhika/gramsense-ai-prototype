"""
CDN Configuration for Static Assets
Provides configuration for CloudFront or other CDN services.
"""

# CloudFront CDN Configuration Template
CLOUDFRONT_CONFIG = {
    "comment": "GramSense AI Static Assets CDN",
    "enabled": True,
    "price_class": "PriceClass_100",  # Use only North America and Europe
    "origins": [
        {
            "id": "S3-gramsense-static",
            "domain_name": "gramsense-static.s3.amazonaws.com",
            "s3_origin_config": {
                "origin_access_identity": ""
            }
        }
    ],
    "default_cache_behavior": {
        "target_origin_id": "S3-gramsense-static",
        "viewer_protocol_policy": "redirect-to-https",
        "allowed_methods": ["GET", "HEAD", "OPTIONS"],
        "cached_methods": ["GET", "HEAD"],
        "compress": True,
        "min_ttl": 0,
        "default_ttl": 86400,  # 24 hours
        "max_ttl": 31536000,  # 1 year
        "forwarded_values": {
            "query_string": False,
            "cookies": {"forward": "none"}
        }
    },
    "cache_behaviors": [
        {
            "path_pattern": "*.html",
            "target_origin_id": "S3-gramsense-static",
            "viewer_protocol_policy": "redirect-to-https",
            "min_ttl": 0,
            "default_ttl": 3600,  # 1 hour for HTML
            "max_ttl": 86400
        },
        {
            "path_pattern": "*.js",
            "target_origin_id": "S3-gramsense-static",
            "viewer_protocol_policy": "redirect-to-https",
            "min_ttl": 0,
            "default_ttl": 604800,  # 1 week for JS
            "max_ttl": 31536000
        },
        {
            "path_pattern": "*.css",
            "target_origin_id": "S3-gramsense-static",
            "viewer_protocol_policy": "redirect-to-https",
            "min_ttl": 0,
            "default_ttl": 604800,  # 1 week for CSS
            "max_ttl": 31536000
        }
    ]
}

# Cache-Control headers for different file types
CACHE_HEADERS = {
    "html": "public, max-age=3600",  # 1 hour
    "css": "public, max-age=604800",  # 1 week
    "js": "public, max-age=604800",  # 1 week
    "images": "public, max-age=2592000",  # 30 days
    "fonts": "public, max-age=31536000",  # 1 year
}


def get_cache_header(file_extension: str) -> str:
    """Get appropriate Cache-Control header for file type."""
    extension_map = {
        ".html": "html",
        ".css": "css",
        ".js": "js",
        ".png": "images",
        ".jpg": "images",
        ".jpeg": "images",
        ".gif": "images",
        ".svg": "images",
        ".woff": "fonts",
        ".woff2": "fonts",
        ".ttf": "fonts",
    }
    
    file_type = extension_map.get(file_extension.lower(), "html")
    return CACHE_HEADERS.get(file_type, "public, max-age=3600")


# AWS CLI command to create CloudFront distribution
CDN_SETUP_COMMAND = """
# Create S3 bucket for static assets
aws s3 mb s3://gramsense-static --region us-east-1

# Upload frontend files
aws s3 sync frontend/ s3://gramsense-static/ --acl public-read

# Create CloudFront distribution
aws cloudfront create-distribution --distribution-config file://cloudfront-config.json

# Get distribution domain name
aws cloudfront list-distributions --query 'DistributionList.Items[0].DomainName'
"""

# Instructions for CDN setup
CDN_SETUP_INSTRUCTIONS = """
CDN Setup Instructions for GramSense AI
========================================

1. Create S3 Bucket for Static Assets:
   aws s3 mb s3://gramsense-static --region us-east-1

2. Configure bucket for static website hosting:
   aws s3 website s3://gramsense-static --index-document index.html

3. Upload frontend files:
   aws s3 sync frontend/ s3://gramsense-static/ --acl public-read

4. Create CloudFront distribution:
   - Use the CLOUDFRONT_CONFIG template above
   - Point to S3 bucket as origin
   - Enable compression
   - Set appropriate cache behaviors

5. Update frontend to use CDN URL:
   - Replace local asset paths with CloudFront URL
   - Example: https://d1234567890.cloudfront.net/

6. Benefits:
   - Faster load times globally
   - Reduced server load
   - Better user experience
   - Lower bandwidth costs

7. Cost Optimization:
   - Use PriceClass_100 (cheapest)
   - Set appropriate TTLs
   - Enable compression
   - Monitor usage in CloudWatch

Estimated Cost: $1-5/month for low traffic
"""
