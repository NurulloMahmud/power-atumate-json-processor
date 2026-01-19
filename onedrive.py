import requests
from auth import get_access_token

GRAPH_API_URL = "https://graph.microsoft.com/v1.0"


def upload_file(file_content: bytes, file_name: str) -> dict:
    """
    Upload a file to OneDrive.
    
    Returns:
        API response with file metadata
    """
    token = get_access_token()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream",
    }
    
    upload_url = f"{GRAPH_API_URL}/me/drive/special/approot:/{file_name}:/content"
    
    response = requests.put(upload_url, headers=headers, data=file_content)
    
    if response.status_code in (200, 201):
        print(f"Successfully uploaded: {file_name}")
        return response.json()
    else:
        raise Exception(f"Upload failed: {response.status_code} - {response.text}")


if __name__ == "__main__":
    test_content = b'{"test": "Hello from Python!"}'
    result = upload_file(test_content, "test.json")
    print(f"File uploaded to: {result.get('webUrl')}")