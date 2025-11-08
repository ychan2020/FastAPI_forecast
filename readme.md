# Development Team Project: Coding Output

# Prerequisite

The following should be installed already before setup.
- Python3

Requirements:
```
pip install -r requirements.txt
```
# Program

Running from the downloaded directory:
```
uvicorn main:app --reload
```

API page: http://127.0.0.1:8000/docs

# Program test

GET /geocode
Enter location to search for GEO code
```
London
```

GET /forecast
Enter latitude, longitude, current and hourly to get the weather forecast
```
latitude: 51.509865
longitude: -0.118092
current: temperature_2m
hourly: temperature_2m
```
