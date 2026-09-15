import asyncio
import base64
import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client



gateway_url = "https://tyk-master-gateway.docker.local"
oauth2_api_listen_path = "/oauth2/"
test_api_listen_path = "/oauth2-test/"

client_id = "dabdcf0ba8394aefaf68301427f7b4f1"
client_secret = "ZDIxNTBkY2UtNmJiNy00ZjE5LTkwMmItYjdiM2QzM2RmMTdi"

    
def get_token() -> str:
    """
    This function retrieves an access token from the OAuth2 token endpoint
    using the client credentials grant type.

    Returns:
        str: The access token if the request is successful, otherwise None.
    """
    
    print(f"Basic {base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()}")
    
    # Construct the token endpoint URL
    url = f"{gateway_url}{oauth2_api_listen_path}".rstrip("/") + "/oauth/token"

    # Prepare the headers with Basic Authentication
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()}"
    }

    # Prepare the data for the token request
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    # Make the POST request to obtain the access token
    response = httpx.post(url, data=data, headers=headers, verify=False)
    
    # Return the access token, will throw an error if the request was unsuccessful
    return response.json().get("access_token")

async def get_token_lib() -> str:
    """
    This function retrieves an access token from the OAuth2 token endpoint
    using the client credentials grant type with the authlib library.

    Returns:
        str: The access token if the request is successful, otherwise None.
    """
    
    # Construct the token endpoint URL
    url = f"{gateway_url}{oauth2_api_listen_path}".rstrip("/") + "/oauth/token"

    # Create an OAuth2 client
    client = AsyncOAuth2Client(client_id, client_secret, token_endpoint=url, verify=False)

    # Fetch the access token using the client credentials grant type
    token = await client.fetch_token(grant_type="client_credentials")

    return token.get("access_token")

def query_api(access_token) -> bool:
    api_url = f"{gateway_url}{test_api_listen_path}".rstrip("/") + "/"
    
    api_headers = {
        "Authorization": f"{access_token}"
    }
    
    api_response = httpx.get(api_url, headers=api_headers, verify=False)
    
    return api_response.status_code == 200

if __name__ == "__main__":
    
    token = get_token()
    print("Access Token:", token)
    print("API query successful." if query_api(token) else "API query failed.")
    print(asyncio.run(get_token_lib()))
