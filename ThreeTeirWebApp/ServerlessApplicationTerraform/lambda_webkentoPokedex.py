import json
import boto3
import os

# Initialize DynamoDB client
dynamodb = boto3.client("dynamodb")
TABLE_NAME = os.environ["POKEDEX_TABLE"]

def lambda_handler(event, context):
    """
    Look up a Pokémon by either ID or name via API Gateway query parameters.
    - If 'id' is provided (number), returns the poke_name.
    - If 'name' is provided, returns the ID.
    """
    query = event.get("queryStringParameters") or {}
    pokemon_id = query.get("id")
    pokemon_name = query.get("name")

    # --- Lookup by ID ---
    if pokemon_id:
        try:
            pokemon_id = int(pokemon_id)
        except ValueError:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "ID must be a number"})
            }

        key = {"id": {"N": str(pokemon_id)}}

        try:
            response = dynamodb.get_item(
                TableName=TABLE_NAME,
                Key=key
            )

            if "Item" not in response:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": f"Pokémon with id {pokemon_id} not found"})
                }

            item = response["Item"]
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "id": int(item["id"]["N"]),
                    "poke_name": item["poke_name"]["S"]
                })
            }

        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)})
            }

    # --- Lookup by Name ---
    elif pokemon_name:
        try:
            response = dynamodb.scan(
                TableName=TABLE_NAME,
                FilterExpression="poke_name = :n",
                ExpressionAttributeValues={":n": {"S": pokemon_name}}
            )

            items = response.get("Items", [])
            if not items:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": f"Pokémon with name '{pokemon_name}' not found"})
                }

            item = items[0]  # assume unique names
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "id": int(item["id"]["N"]),
                    "poke_name": item["poke_name"]["S"]
                })
            }

        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)})
            }

    # --- Neither ID nor Name Provided ---
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Please provide either 'id' or 'name' as a query parameter"})
        }
