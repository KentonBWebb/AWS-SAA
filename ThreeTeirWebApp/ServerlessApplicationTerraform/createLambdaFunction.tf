# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "lambda_pokedex_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}
# Additional Permissions for Policy
resource "aws_iam_role_policy" "lambda_dynamodb_policy" {
  name = "LambdaDynamoDBPolicy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["dynamodb:GetItem", "dynamodb:Scan"],
        Resource = "arn:aws:dynamodb:us-east-1:877086053095:table/webkentoPokedex"
      }
    ]
  })
} 

#additional Permissions for Lambda
resource "aws_lambda_permission" "apigw_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.pokedex_lookup.function_name
  principal     = "apigateway.amazonaws.com"

  # The source ARN limits the permission to this API/method/stage
  source_arn = "${aws_api_gateway_rest_api.pokedex_api.execution_arn}/*/*"
}


# Attach basic execution + DynamoDB read permissions
resource "aws_iam_policy" "lambda_policy" {
  name        = "lambda_pokedex_policy"
  description = "Policy for Lambda to read from DynamoDB Pokedex table"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem"
        ]
        Resource = aws_dynamodb_table.webkentoPokedex.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# Zip the lambda function
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_webkentoPokedex.py"
  output_path = "${path.module}/lambda_webkentoPokedex.zip"
}

# Lambda Function
resource "aws_lambda_function" "pokedex" {
  function_name = "pokedex_lookup"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_webkentoPokedex.lambda_handler"
  runtime       = "python3.9"
  filename      = data.archive_file.lambda_zip.output_path

  environment {
    variables = {
      POKEDEX_TABLE = aws_dynamodb_table.webkentoPokedex.name 
    }
  }
}

##aws lambda invoke --function-name pokedex_lookup --payload '{"id":"25"}' response.json