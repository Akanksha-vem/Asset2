import json
import boto3
import pandas as pd
from io import BytesIO
import pyarrow.parquet as pq
import pyarrow as pa
import avro.schema
import avro.io
import avro.datafile
from datetime import datetime

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('fileprocessinglogs')

def lambda_handler(event, context):
    messages = []
    status_code = 200

    for record in event['Records']:
        try:
            # Extract bucket and object key from the event
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']

            # Process the file based on extension
            if key.endswith('.parquet'):
                process_parquet(bucket, key)
                messages.append(f"Successfully processed Parquet file: {key}")
            elif key.endswith('.avro'):
                process_avro(bucket, key)
                messages.append(f"Successfully processed Avro file: {key}")
            else:
                messages.append(f"Unsupported file type for key: {key}")

        except Exception as e:
            error_message = f"Error processing {record}: {e}"
            print(error_message)
            messages.append(error_message)
            status_code = 500  # Set status code to 500 if an error occurs

    return {
        'statusCode': status_code,
        'body': json.dumps(messages)
    }

def process_parquet(bucket, key):
    start_time = datetime.utcnow()
    
    response = s3_client.get_object(Bucket=bucket, Key=key)
    parquet_data = response['Body'].read()

    parquet_buffer = BytesIO(parquet_data)
    df = pd.read_parquet(parquet_buffer, engine='pyarrow')

    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    destination_bucket = 'csvconvertfilesss'
    csv_key = key.replace('.parquet', '.csv')

    s3_client.put_object(
        Bucket=destination_bucket,
        Key=csv_key,
        Body=csv_buffer.getvalue(),
        ContentType='text/csv'
    )

    end_time = datetime.utcnow()

    # Log to DynamoDB
    log_to_dynamodb(key, bucket, destination_bucket, len(df), 'parquet', start_time, end_time)

def process_avro(bucket, key):
    start_time = datetime.utcnow()
    
    response = s3_client.get_object(Bucket=bucket, Key=key)
    avro_data = response['Body'].read()

    avro_buffer = BytesIO(avro_data)
    reader = avro.datafile.DataFileReader(avro_buffer, avro.io.DatumReader())
    
    df = pd.DataFrame.from_records([record for record in reader])

    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    destination_bucket = 'csvconvertfilesss'
    csv_key = key.replace('.avro', '.csv')

    s3_client.put_object(
        Bucket=destination_bucket,
        Key=csv_key,
        Body=csv_buffer.getvalue(),
        ContentType='text/csv'
    )

    end_time = datetime.utcnow()

    # Log to DynamoDB
    log_to_dynamodb(key, bucket, destination_bucket, len(df), 'avro', start_time, end_time)

import decimal
from datetime import datetime

# Other imports...

def log_to_dynamodb(key, source_bucket, destination_bucket, record_count, file_type, start_time, end_time):
    start_time_iso = start_time.isoformat()
    end_time_iso = end_time.isoformat()
    
    # Convert the duration and record_count to Decimal using strings to avoid inexact conversions
    duration = decimal.Decimal(str((end_time - start_time).total_seconds()))
    record_count_decimal = decimal.Decimal(str(record_count))

    table.put_item(
        Item={
            'Timestamp': start_time_iso,    # Ensure this key matches your table's partition key
            'filename': key,
            'SourceBucket': source_bucket,
            'DestinationBucket': destination_bucket,
            'FileType': file_type,
            'ExecutionTimeSeconds': duration,
            'RecordCount': record_count_decimal,
        }
    )
