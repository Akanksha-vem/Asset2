output "source_bucket_name" {
  value = aws_s3_bucket.sourcebucket.bucket
}

output "destination_bucket_name" {
  value = aws_s3_bucket.destinationbucket.bucket
}

output "lambda_function_arn" {
  value = aws_lambda_function.file_processor.arn
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.fileprocessinglogs.name
}
