resource "aws_dynamodb_table" "fileprocessinglogs" {
  name         = "fileprocessinglogs"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "Timestamp"
    type = "S"
  }

  attribute {
    name = "filename"
    type = "S"
  }

  hash_key  = "Timestamp"
  range_key = "filename"
}

