# ---------------------------------------------
# API Gateway REST API
# ---------------------------------------------
resource "aws_api_gateway_rest_api" "pokedex_api" {
  name        = "PokedexAPI"
  description = "API Gateway for Pokédex Lambda"
}

# ---------------------------------------------
# /pokemon resource
# ---------------------------------------------
resource "aws_api_gateway_resource" "pokemon" {
  rest_api_id = aws_api_gateway_rest_api.pokedex_api.id
  parent_id   = aws_api_gateway_rest_api.pokedex_api.root_resource_id
  path_part   = "pokemon"
}

# ---------------------------------------------
# GET method
# ---------------------------------------------
resource "aws_api_gateway_method" "get_pokemon" {
  rest_api_id   = aws_api_gateway_rest_api.pokedex_api.id
  resource_id   = aws_api_gateway_resource.pokemon.id
  http_method   = "GET"
  authorization = "NONE"  # no auth for testing
}

# ---------------------------------------------
# Lambda integration
# ---------------------------------------------
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.pokedex_api.id
  resource_id             = aws_api_gateway_resource.pokemon.id
  http_method             = aws_api_gateway_method.get_pokemon.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = data.aws_lambda_function.pokedex_lookup.invoke_arn
}

# ---------------------------------------------
# Deployment
# ---------------------------------------------
resource "aws_api_gateway_deployment" "deployment" {
  depends_on  = [aws_api_gateway_integration.lambda_integration]
  rest_api_id = aws_api_gateway_rest_api.pokedex_api.id

  triggers = {
    redeploy = sha1(jsonencode(aws_api_gateway_rest_api.pokedex_api))
  }
}

# ---------------------------------------------
# Stage
# ---------------------------------------------
resource "aws_api_gateway_stage" "dev" {
  stage_name    = "dev"
  rest_api_id   = aws_api_gateway_rest_api.pokedex_api.id
  deployment_id = aws_api_gateway_deployment.deployment.id
}