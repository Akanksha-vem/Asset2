# Custom Layer
resource "aws_lambda_layer_version" "custom_layer" {
  layer_name  = "custom_layer"
  compatible_runtimes = ["python3.10"]
  description = "Your custom layer"

  filename = "C:/Users/vemula.akanksha/lambda-layer.zip"
  compatible_architectures = ["x86_64"]
}

# Lambda Function
resource "aws_lambda_function" "file_processor" {
  function_name = "FileProcessorLambda"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.10"
  filename      = "C:/Users/vemula.akanksha/Desktop/lmabda/lambda_function.zip"
  architectures = ["x86_64"]

  # Include AWS-provided layer and custom layer
  layers = [
    "arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python310:19", # Replace this with the correct ARN for your region
    aws_lambda_layer_version.custom_layer.arn,
  ]

  environment {
    variables = {
      DESTINATION_BUCKET = aws_s3_bucket.destinationbucket.bucket
    }
  }
  # Extend the timeout to 5 minutes (300 seconds)
  timeout = 300
}

# Lambda Permission for S3 Trigger
resource "aws_lambda_permission" "s3_trigger_permission" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.file_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.sourcebucket.arn
}

# S3 Bucket Notification for Lambda Trigger
resource "aws_s3_bucket_notification" "sourcebucket_notification" {
  bucket = aws_s3_bucket.sourcebucket.bucket

  lambda_function {
    lambda_function_arn = aws_lambda_function.file_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = ""
    filter_suffix       = ""
  }
}
