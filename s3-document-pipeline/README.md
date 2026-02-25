# S3 Document Pipeline

Automatically process documents uploaded to an S3 bucket. The pipeline extracts content, identifies entities, classifies the document type, and routes it to the right team.

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
| `max_concurrent_runs: 5` | Handles burst uploads in parallel |
| Multimodal input | Processes images, PDFs, and text files |

## Connector Setup

Configure an **S3 inbound** connector in the Connic dashboard:

| Setting | Value |
|---------|-------|
| Bucket | `your-documents-bucket` |
| Region | `eu-central-1` |
| Prefix | `inbox/` (optional: only trigger for files in this prefix) |
| Suffix | `.pdf` (optional: only trigger for PDFs) |
| Event types | `created` |
| Include content | `true` (sends file bytes to the agent) |
| Max file size | `50` MB |

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
