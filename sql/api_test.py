import requests

BASE_URL = "http://localhost:5000"

def test_endpoint(endpoint, method="GET", data=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        else:
            print(f"Unsupported method: {method}")
            return
        print(f"{method} {endpoint} -> {response.status_code}")
    except Exception as e:
        print(f"Error for {endpoint}: {e}")

if __name__ == "__main__":
    # GET endpoints
    test_endpoint("/litige/all")
    test_endpoint("/litige")
    test_endpoint("/pie/1")
    test_endpoint("/line")
    test_endpoint("/test")
    test_endpoint("/litige/1/SomeDescription")
    test_endpoint("/litige/1")
    test_endpoint("/litige/1/all")
    test_endpoint("/line/1")
    test_endpoint("/letiges/join")
    test_endpoint("/letiges/join/group")
    test_endpoint("/column")
    test_endpoint("/column/overdue")
    test_endpoint("/autocomplete/SomeName")
    test_endpoint("/client/join")
    test_endpoint("/client/join/1")

    # POST endpoints
   