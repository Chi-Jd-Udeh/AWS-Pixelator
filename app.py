import os
import time
import uuid
import boto3
from flask import Flask, request, render_template, jsonify
from botocore.exceptions import ClientError

app = Flask(__name__)

SOURCE_BUCKET = 'amzn-pixilate-bucket-source'
PROCESSED_BUCKET = 'amzn-pixalate-bucket-2'
AWS_REGION = 'us-east-1'  

s3_client = boto3.client('s3', region_name=AWS_REGION)


def generate_presigned_url(bucket, key, expiry=60):
    return s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=expiry
    )


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    ext = os.path.splitext(file.filename)[1]
    unique_key = f"{uuid.uuid4()}{ext}"

    try:
        s3_client.upload_fileobj(file, SOURCE_BUCKET, unique_key)
    except ClientError as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

    processed_key = f'pixelated-32x32-{unique_key}'
    url = None
    for _ in range(20):  # try for ~20 seconds
        time.sleep(1)
        try:
            s3_client.head_object(Bucket=PROCESSED_BUCKET, Key=processed_key)
            url = generate_presigned_url(PROCESSED_BUCKET, processed_key)
            break
        except ClientError:
            continue

    if not url:
        return jsonify({'error': 'Processing timed out. Try again.'}), 504

    
    original_url = generate_presigned_url(SOURCE_BUCKET, unique_key)

    return jsonify({'original': original_url, 'pixelated': url})


if __name__ == '__main__':
    app.run()
