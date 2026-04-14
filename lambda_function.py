import os
import json
import uuid
from urllib.parse import unquote_plus
import boto3
from botocore.exceptions import ClientError
from PIL import Image  # Import Image from PIL

processed_bucket = os.environ['processed_bucket']
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    print(event)
    
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    key = unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    # Generate a temp name, and set location for our original image
    object_key = str(uuid.uuid4()) + '-' + key
    img_download_path = '/tmp/{}'.format(object_key)
    
    # Check if the object exists in the source bucket
    try:
        s3_client.head_object(Bucket=source_bucket, Key=key)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"Error code: {error_code}")  # Will show 403 or 404
        print(f"Error: Object {key} not found in bucket {source_bucket}.")
        return {
            'statusCode': 404,
            'body': json.dumps(f"Object {key} not found in bucket {source_bucket}.")
        }

    # Download the source image from S3 to temp location within execution environment
    try:
        with open(img_download_path, 'wb') as img_file:
            s3_client.download_fileobj(source_bucket, key, img_file)
    except ClientError as e:
        print(f"Error downloading file {key} from bucket {source_bucket}: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error downloading file: {str(e)}")
        }

    try:
        pixelate((32, 32), img_download_path, f'/tmp/pixelated-32x32-{object_key}')
    except Exception as e:
        print(f"Error pixelating image: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error pixelating image: {str(e)}")
        }

    try:
        s3_client.upload_file(f'/tmp/pixelated-32x32-{object_key}', processed_bucket, f'pixelated-32x32-{key}')
    except ClientError as e:
        print(f"Error uploading pixelated images: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error uploading pixelated images: {str(e)}")
        }

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully processed and uploaded pixelated images.')
    }

def pixelate(pixelsize, image_path, pixelated_img_path):
    # Ensure Image module is used here
    img = Image.open(image_path)
    temp_img = img.resize(pixelsize, Image.BILINEAR)
    new_img = temp_img.resize(img.size, Image.NEAREST)
    new_img.save(pixelated_img_path)
