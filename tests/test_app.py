from app import app

#Test the health endpoint is working correctly
def test_health_endpoint():
    # Create a test client for the Flask application
    with app.test_client() as client:
        # Send a GET request to the /health endpoint
        response = client.get("/health")
        
        # Assert that the response status code is 200 (OK)
        assert response.status_code == 200
        
        # Assert that the response JSON contains the expected status
        assert response.get_json() == {"status": "UP"}

def test_version_endpoint():
    # Create a test client for the Flask application
    with app.test_client() as client:
        # Send a GET request to the /version endpoint
        response = client.get("/version")
        
        # Assert that the response status code is 200 (OK)
        assert response.status_code == 200
        
        # Assert that the response JSON contains the expected version
        assert response.get_json() == {"version": "1.0.0"}

def test_echo_endpoint():
    # Create a test client for the Flask application
    with app.test_client() as client:
        # Send a POST request to the /echo endpoint
        response = client.post("/echo", json={"message": "Hello, World!"})
        
        # Assert that the response status code is 200 (OK)
        assert response.status_code == 200
        
        # Assert that the response JSON contains the expected echo
        assert response.get_json() == {"echo": {"message": "Hello, World!"}}

def test_environment_endpoint():
    # Create a test client for the Flask application
    with app.test_client() as client:
        # Send a GET request to the /environment endpoint
        response = client.get("/environment")
        
        # Assert that the response status code is 200 (OK)
        assert response.status_code == 200
        
        # Assert that the response JSON contains the expected environment
        assert response.get_json() == {"environment": "development"}


