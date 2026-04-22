# AWS Pixelator 🖼️

A serverless image pixelation pipeline built on AWS. Upload any image and receive a pixelated 32×32 version — powered by S3, Lambda, and IAM working together automatically.

🔗 **Live Demo:** ([https://pixelator-jdthebean.pythonanywhere.com/](https://pixelator-jdthebean.pythonanywhere.com/))

---

## How It Works

1. User uploads an image through the web interface
2. Flask uploads the file to the **source S3 bucket** using `boto3`
3. The S3 upload **automatically triggers an AWS Lambda function**
4. Lambda processes the image and writes a pixelated version to the **processed S3 bucket**
5. The app polls the processed bucket until the output file appears
6. **Presigned URLs** for both the original and pixelated images are generated and returned to the user

   Example of a pixilated image...
   
    <img width="1607" height="808" alt="Architect" src="https://github.com/Chi-Jd-Udeh/Image-box/blob/main/pup_pixliate.png?raw=true" />

---

## AWS Architecture

<img width="1607" height="808" alt="Architect" src="https://github.com/Chi-Jd-Udeh/Image-box/blob/main/aws_pixleator_diagram.png?raw=true"/>

---

## AWS Services Used

### S3 — Simple Storage Service

Two buckets are used in this project:

| Bucket | Purpose |
|--------|---------|
| **Source Bucket** | Receives raw image uploads from the Flask app |
| **Processed Bucket** | Stores the pixelated output written by Lambda |

The processed file is named with the prefix `pixelated-32x32-` followed by the original filename, making it easy to look up after processing.

Access to both buckets is handled via **presigned URLs** — time-limited, pre-authenticated links that allow the browser to fetch private S3 objects without exposing credentials. URLs expire after 60 seconds.

### Lambda — Serverless Function

The Lambda function is triggered automatically by an **S3 ObjectCreated event** on the source bucket. It reads the uploaded image, applies pixelation at 32×32 resolution, and writes the result to the processed bucket.

Key Lambda configuration:

| Setting | Value |
|---------|-------|
| **Trigger** | S3 → ObjectCreated (All) |
| **Input** | Reads uploaded image from source bucket using the event key |
| **Output** | Writes to processed bucket with `pixelated-32x32-` prefix |
| **Runtime** | Python (Pillow for image processing) |


---

## AWS Cost Breakdown

This project uses two AWS services that incur costs: **S3** and **Lambda**.

---

### Lambda Costs

Lambda charges on two dimensions: **requests** and **compute duration**.

| Dimension | Price |
|-----------|-------|
| Requests | $0.20 per 1 million |
| Duration (x86) | $0.0000166667 per GB-second |
| Duration (ARM/Graviton2) | ~20% cheaper |

---

### S3 Costs

S3 charges across three dimensions: **storage**, **requests**, and **data transfer**.

**Storage** (S3 Standard):

| Usage | Price |
|-------|-------|
| First 50 TB/month | $0.023 per GB |

**Requests:**

| Request Type | Price |
|-------------|-------|
| PUT, COPY, POST, LIST | $0.005 per 1,000 |
| GET, HEAD | $0.0004 per 1,000 |

**Data Transfer:**

| Transfer | Price |
|----------|-------|
| Inbound (uploads to S3) | Free |
| S3 → Lambda (same region) | Free |
| S3 → Internet (presigned URL downloads) | $0.09/GB after first 100 GB/month free |

---

### Cost Summary

| Scenario | Estimated Monthly Cost |
|----------|----------------------|
| Personal / demo (< 1,000 uploads) | **$0.00** (free tier) |
| Light usage (~10,000 uploads) | **~$0.50–$1.00** |
| Moderate usage (~100,000 uploads) | **~$5–$15** |

---

## Project Structure

```
AWS-Pixelator/
├── app.py               # Flask app — handles upload, polling, presigned URLs
├── requirements.txt     # Python dependencies
├── .env                 # AWS credentials (local only, never commit)
├── .gitignore
└── templates/
    └── index.html       # Upload UI
```

---

## License

MIT
