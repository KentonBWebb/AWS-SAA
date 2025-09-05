provider "aws" {
  region = "us-east-1"
}

data "aws_lambda_function" "pokedex_lookup" {
  function_name = "pokedex_lookup"
}
