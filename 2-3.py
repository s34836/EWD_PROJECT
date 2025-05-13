import pandas as pd
import json
from pprint import pprint

# Load the data from the text file
df = pd.read_csv('warsaw_rentals.txt')

# Get the first row
first_row = df.iloc[1]

# Convert the raw_json string to a Python dictionary
json_data = json.loads(first_row['raw_json'])

print(f"Url: {first_row['url']}")

print(f"Price: {json_data.get('target', {}).get('Price', {})}")
print(f"Street: {json_data.get('location', {}).get('address', {}).get('street', {}).get('name', {})}") #todo: add address
print(f"District: {json_data.get('location', {}).get('address', {}).get('district', {}).get('name', {})}")
print(f"Latitude: {json_data.get('location', {}).get('coordinates', {}).get('latitude')}")
print(f"Longitude: {json_data.get('location', {}).get('coordinates', {}).get('longitude')}")
print(f"Area: {json_data.get('target', {}).get('Area', {})}")
#print(f"Liczba pokoi: {json_data.get('target', {}).get('Rooms_num', {})}")
print(f"Rooms_num: {json_data.get('target', {}).get('Rooms_num', [''])[0] if json_data.get('target', {}).get('Rooms_num') else ''}")

print(f"Heating: {json_data.get('target', {}).get('Heating', [''])[0] if json_data.get('target', {}).get('Heating') else ''}")
print(f"PFloor_no: {json_data.get('target', {}).get('Floor_no', [''])[0] if json_data.get('target', {}).get('Floor_no') else ''}")
print(f"Building_floors_num: {json_data.get('target', {}).get('Building_floors_num', {})}")
print(f"Construction_status: {json_data.get('target', {}).get('Construction_status', [''])[0] if json_data.get('target', {}).get('Construction_status') else ''}")
print(f"Rent: {json_data.get('target', {}).get('Rent', {})}")


print(f"Deposit: {json_data.get('target', {}).get('Deposit', {})}")
print(f"User_type: {json_data.get('target', {}).get('user_type', {})}")
print(f"Extras_types:{json_data.get('target', {}).get('Extras_types', {})}")


print(f"Build_year: {json_data.get('target', {}).get('Build_year', {})}")
print(f"Building_type: {json_data.get('target', {}).get('Building_type', [''])[0] if json_data.get('target', {}).get('Building_type') else ''}")
print(f"Building_material: {json_data.get('target', {}).get('Building_material', [''])[0] if json_data.get('target', {}).get('Building_material') else ''}")

print(f"Windows_type: {json_data.get('target', {}).get('Windows_type', [''])[0] if json_data.get('target', {}).get('Windows_type') else ''}")
print(f"Equipment_types:{json_data.get('target', {}).get('Equipment_types', {})}")
print(f"Security_types: {json_data.get('target', {}).get('Security_types', {})}")
print(f"Media_types: {json_data.get('target', {}).get('Media_types', {})}")


