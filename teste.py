import requests
import os

def test_face_auth_multiple(register_image_path: str, auth_image_path: str, username: str, base_url: str = "http://localhost:8000"):
    """
    Test registration with one image and authentication with another
    
    Args:
        register_image_path: Path to the image file for registration
        auth_image_path: Path to a different image file of the same person for authentication
        username: Username to register
        base_url: Base URL of the API
    """
    
    print("\n=== Testing Registration ===")
    print(f"Using image: {register_image_path}")
    try:
        with open(register_image_path, 'rb') as img:
            files = {'file': (os.path.basename(register_image_path), img, 'image/jpeg')}
            response = requests.post(
                f"{base_url}/register/{username}",
                files=files
            )
            
        print(f"Status Code: {response.status_code}")
        print("Response:", response.json())
            
    except Exception as e:
        print(f"❌ Error during registration: {str(e)}")
        return

    print("\n=== Testing Authentication with Different Image ===")
    print(f"Using image: {auth_image_path}")
    try:
        with open(auth_image_path, 'rb') as img:
            files = {'file': (os.path.basename(auth_image_path), img, 'image/jpeg')}
            response = requests.post(
                f"{base_url}/authenticate",
                files=files
            )
            
        print(f"Status Code: {response.status_code}")
        print("Response:", response.json())
            
    except Exception as e:
        print(f"❌ Error during authentication: {str(e)}")

if __name__ == "__main__":
    REGISTER_IMAGE_PATH = "teste_image.jpg"
    AUTH_IMAGE_PATH = "teste_image2.jpg"
    USERNAME = "cesar camillo"
    
    test_face_auth_multiple(REGISTER_IMAGE_PATH, AUTH_IMAGE_PATH, USERNAME)