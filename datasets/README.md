# Datasets

This directory contains sample datasets and references to external data sources.

> [!NOTE]
> Large files are gitignored. Store datasets in GCS and document links here.

## GCS Buckets

| Bucket | Purpose | Link |
|--------|---------|------|
| `metaadsscrapper` | Meta Ad Library videos | [Console](https://console.cloud.google.com/storage/browser/metaadsscrapper) |
| `adiyogi-knowledge-base-new` | Knowledge Base files | [Console](https://console.cloud.google.com/storage/browser/adiyogi-knowledge-base-new) |

## Local Development

For local testing, download sample data:
```bash
gsutil -m cp -r gs://metaadsscrapper/meta-ads/nike ./
```
