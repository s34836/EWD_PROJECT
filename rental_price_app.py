# rental_price_app.py
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# Load artifacts
@st.cache_resource
def load_model():
    artifacts = joblib.load('warsaw_rental_model_artifacts.pkl')
    return artifacts

artifacts = load_model()
model = artifacts['model']
feature_names = artifacts['feature_names']
high_premium_districts = artifacts['high_premium_districts']

# Create the app
st.title('Warsaw Rental Price Predictor')
st.write('Enter property details to get an estimated rental price:')

# Create input form
with st.form("prediction_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        area = st.number_input('Area (sqm)', min_value=15.0, max_value=300.0, value=50.0)
        rooms_num = st.number_input('Number of rooms', min_value=1, max_value=10, value=2)
        build_year = st.number_input('Construction year', min_value=1900, max_value=2025, value=2000)
        floor_numeric = st.number_input('Floor', min_value=0, max_value=50, value=2)
        building_floors_num = st.number_input('Building floors', min_value=1, max_value=50, value=5)
    
    with col2:
        distance_to_center = st.number_input('Distance to center (km)', min_value=0.1, max_value=25.0, value=5.0)
        districts = st.selectbox('District', 
                               ['Śródmieście', 'Wola', 'Mokotów', 'Praga-Południe', 'Ursynów', 
                                'Wilanów', 'Ochota', 'Bielany', 'Żoliborz', 'Bemowo', 'Białołęka',
                                'Targówek', 'Włochy', 'Praga-Północ', 'Ursus', 'Other'])
        
        building_type = st.selectbox('Building type', ['Apartment', 'Block', 'Tenement', 'Other'])
        window_type = st.selectbox('Window type', ['Plastic', 'Wooden', 'Other'])
        is_agency = st.checkbox('Listed by agency')
    
    # Amenities section
    st.subheader('Amenities')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        kitchen_furniture_score = st.slider('Kitchen quality', 0, 7, 0)
        security_score = st.slider('Security features', 0, 5, 0)
    
    with col2:
        tech_score = st.slider('Technology features', 0, 3, 0)
        premium_amenities_score = st.slider('Premium amenities', 0, 3, 0)
    
    with col3:
        infrastructure_score = st.slider('Infrastructure', 0, 3, 0)
        interior_score = st.slider('Interior quality', 0, 5, 0)
    
    submitted = st.form_submit_button("Predict Price")

if submitted:
    # Prepare features
    features = {feature: 0 for feature in feature_names}
    
    # Basic features
    features['area'] = area
    features['rooms_num'] = rooms_num
    features['building_floors_num'] = building_floors_num
    features['build_year'] = build_year
    features['distance_to_center'] = distance_to_center
    features['floor_numeric'] = floor_numeric
    
    # District
    district_col = f'district_{districts}'
    if district_col in features:
        features[district_col] = 1
    
    # Building type
    if building_type == 'Apartment':
        features['building_type_apartment'] = 1
    elif building_type == 'Tenement':
        features['building_type_tenement'] = 1
    
    # Window type
    if window_type == 'Plastic':
        features['window_plastic'] = 1
    elif window_type == 'Wooden':
        features['window_wooden'] = 1
    
    # Agency
    features['user_type_agency'] = 1 if is_agency else 0
    
    # Amenity scores
    features['kitchen_furniture_score'] = kitchen_furniture_score
    features['security_score'] = security_score
    features['tech_score'] = tech_score
    features['premium_amenities_score'] = premium_amenities_score
    features['infrastructure_score'] = infrastructure_score
    features['interior_score'] = interior_score
    
    # Calculate relative floor position
    features['relative_floor_position'] = floor_numeric / building_floors_num if building_floors_num > 0 else 0
    
    # Is top floor
    features['is_top_floor'] = 1 if floor_numeric == building_floors_num else 0
    
    # Engineered features
    features['area_per_room'] = area / max(rooms_num, 1)
    features['area_distance_interaction'] = area * distance_to_center
    features['high_premium_district'] = 1 if district_col in high_premium_districts else 0
    features['building_age'] = 2025 - build_year
    features['top_floor_distance'] = building_floors_num - floor_numeric
    
    # Make prediction
    input_df = pd.DataFrame([features])[feature_names]
    log_price_pred = model.predict(input_df)[0]
    price_pred = np.exp(log_price_pred)
    price_per_sqm = price_pred / area
    
    # Display results
    st.success(f"**Estimated Monthly Rent: {price_pred:.2f} PLN**")
    st.info(f"Price per Square Meter: {price_per_sqm:.2f} PLN/sqm")
    
