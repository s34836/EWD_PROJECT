import pandas as pd
import json

# Load the data from the text file
df = pd.read_csv('warsaw_rentals.txt')

# Create an empty list to store the processed data
processed_data = []

# Process each row in the dataframe
for index, row in df.iterrows():
    try:
        # Create a default dictionary with NaN values for all fields
        processed_row = {
            'url': row.get('url', pd.NA),
            'price': pd.NA,
            'street': pd.NA,
            'district': pd.NA,
            'latitude': pd.NA,
            'longitude': pd.NA,
            'area': pd.NA,
            'rooms_num': pd.NA,
            'heating': pd.NA,
            'floor_no': pd.NA,
            'building_floors_num': pd.NA,
            'construction_status': pd.NA,
            'rent': pd.NA,
            'deposit': pd.NA,
            'user_type': pd.NA,
            'extras_types': pd.NA,
            'build_year': pd.NA,
            'building_type': pd.NA,
            'building_material': pd.NA,
            'windows_type': pd.NA,
            'equipment_types': pd.NA,
            'security_types': pd.NA,
            'media_types': pd.NA
        }
        
        # Only try to parse JSON if raw_json exists and is not None
        if pd.notna(row.get('raw_json')):
            json_data = json.loads(row['raw_json'])
            
            # Only try to access fields if json_data is not None
            if json_data is not None:
                # Extract fields safely
                if 'target' in json_data and json_data['target'] is not None:
                    target = json_data['target']
                    processed_row['price'] = target.get('Price', pd.NA)
                    processed_row['area'] = target.get('Area', pd.NA)
                    processed_row['rooms_num'] = target.get('Rooms_num', [''])[0] if target.get('Rooms_num') else pd.NA
                    processed_row['heating'] = target.get('Heating', [''])[0] if target.get('Heating') else pd.NA
                    processed_row['floor_no'] = target.get('Floor_no', [''])[0] if target.get('Floor_no') else pd.NA
                    processed_row['building_floors_num'] = target.get('Building_floors_num', pd.NA)
                    processed_row['construction_status'] = target.get('Construction_status', [''])[0] if target.get('Construction_status') else pd.NA
                    processed_row['rent'] = target.get('Rent', pd.NA)
                    processed_row['deposit'] = target.get('Deposit', pd.NA)
                    processed_row['user_type'] = target.get('user_type', pd.NA)
                    processed_row['extras_types'] = target.get('Extras_types', pd.NA)
                    processed_row['build_year'] = target.get('Build_year', pd.NA)
                    processed_row['building_type'] = target.get('Building_type', [''])[0] if target.get('Building_type') else pd.NA
                    processed_row['building_material'] = target.get('Building_material', [''])[0] if target.get('Building_material') else pd.NA
                    processed_row['windows_type'] = target.get('Windows_type', [''])[0] if target.get('Windows_type') else pd.NA
                    processed_row['equipment_types'] = target.get('Equipment_types', pd.NA)
                    processed_row['security_types'] = target.get('Security_types', pd.NA)
                    processed_row['media_types'] = target.get('Media_types', pd.NA)
                
                # Location data
                if 'location' in json_data and json_data['location'] is not None:
                    location = json_data['location']
                    
                    # Address data
                    if 'address' in location and location['address'] is not None:
                        address = location['address']
                        
                        # Street data
                        if 'street' in address and address['street'] is not None:
                            processed_row['street'] = address['street'].get('name', pd.NA)
                        
                        # District data
                        if 'district' in address and address['district'] is not None:
                            processed_row['district'] = address['district'].get('name', pd.NA)
                    
                    # Coordinates
                    if 'coordinates' in location and location['coordinates'] is not None:
                        coordinates = location['coordinates']
                        processed_row['latitude'] = coordinates.get('latitude', pd.NA)
                        processed_row['longitude'] = coordinates.get('longitude', pd.NA)
        
        processed_data.append(processed_row)
    except Exception as e:
        # Print error but still add a row with NaN values
        print(f"Error processing row {index}: {e}")
        processed_row = {col: pd.NA for col in ['url', 'price', 'street', 'district', 'latitude', 'longitude', 
                                              'area', 'rooms_num', 'heating', 'floor_no', 'building_floors_num', 
                                              'construction_status', 'rent', 'deposit', 'user_type', 'extras_types', 
                                              'build_year', 'building_type', 'building_material', 'windows_type', 
                                              'equipment_types', 'security_types', 'media_types']}
        processed_row['url'] = row.get('url', pd.NA)  # At least preserve the URL if available
        processed_data.append(processed_row)

# Create a new dataframe from the processed data
result_df = pd.DataFrame(processed_data)

# Clean up the dataframe (optional)
# Convert list fields to strings for better CSV output
list_columns = ['extras_types', 'equipment_types', 'security_types', 'media_types']
for col in list_columns:
    result_df[col] = result_df[col].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

# Save the processed data to CSV
result_df.to_csv('output_rentals.csv', index=False)

print(f"Successfully processed {len(result_df)} records and saved to output_rentals.csv")