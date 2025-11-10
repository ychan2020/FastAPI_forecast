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
Enter the location to search for the GEO code
```
Location: London
```
<img width="993" height="994" alt="Image" src="https://github.com/user-attachments/assets/ee7d93a2-fe24-4fe8-a5df-5545efabb39f" />

GET /forecast
Enter latitude, longitude, current and hourly to get the weather forecast
```
Location: London
current: temperature_2m
hourly: temperature_2m
```

<img width="995" height="1216" alt="Image" src="https://github.com/user-attachments/assets/8a41456f-ad3f-46fc-871f-0b65ef0c9a6e" />
