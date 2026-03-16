# S3 Document Pipeline

Automatically process documents uploaded to an S3 bucket. The pipeline extracts content, identifies entities, classifies the document type, and routes it to the right team.

```bash
pip install connic-composer-sdk
connic init my-project --templates=s3-document-pipeline   # new project
connic init . --templates=s3-document-pipeline            # existing project
```

[Connic CLI docs](https://connic.co/docs/v1/composer/overview#installation)

## How It Works

1. A file lands in your S3 bucket (PDF, image, text, DOCX).
2. The **S3 inbound connector** triggers `document-pipeline`.
3. **document-intake** (LLM) extracts text, metadata, entities, and a summary. Middleware rejects unsupported file types with `StopProcessing` before the LLM runs.
4. **document-classifier** (LLM) classifies the document and decides where it should be routed.

## Connic Features Used

| Feature | Where |
|---------|-------|
| **S3 inbound connector** | Triggers pipeline on file upload |
| Sequential agent | `document-pipeline.yaml` |
| `StopProcessing` middleware | `middleware/document-intake.py` rejects unsupported file types |
| Output schemas | `schemas/intake-result.json`, `schemas/classification-result.json` |
| `retry_options` | Intake retries 3 times on transient failures |
| Multimodal input | Processes images, PDFs, and text files |

## Connector Setup

Add an **S3 inbound** connector from the agent detail page in the [Connic dashboard](https://connic.co):

| Setting | Value |
|---------|-------|
| Bucket name | `your-documents-bucket` |
| Region | `eu-central-1` |
| AWS Access Key ID | Your IAM access key with S3 permissions |
| AWS Secret Access Key | Your IAM secret key |
| Key prefix (optional) | `inbox/` (only trigger for files in this prefix) |
| Key suffix (optional) | `.pdf` (only trigger for PDFs) |
| Event types | `created` |
| Include file content | `true` (downloads and sends file content to the agent) |
| Max file size (MB) | `50` |
| Linked agent | `document-pipeline` |

After creating the connector, open its detail page to copy the auto-generated **Webhook URL**. Configure [S3 Event Notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/NotificationHowTo.html) on your bucket to send events to that URL.

If your S3 bucket is in a private network, enable **Connect via Bridge** and run the [Connic Bridge](https://connic.co/docs/v1/connectors/bridge) in your VPC.

Optionally add an **HTTP Webhook (outbound)** connector to forward classification results to your document management system.

## Structure

```
s3-document-pipeline/
  agents/
    document-intake.yaml       # Extracts content and entities from uploaded files
    document-classifier.yaml   # Classifies and routes documents
    document-pipeline.yaml     # Sequential: intake then classify
  middleware/
    document-intake.py         # File type validation with StopProcessing
  schemas/
    intake-result.json         # Extraction output schema
    classification-result.json # Classification output schema
  requirements.txt
```
