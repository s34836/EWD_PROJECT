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
standardization_params = artifacts.get('standardization_params', {})

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
    # Calculate relative floor position
    relative_floor_position = floor_numeric / building_floors_num if building_floors_num > 0 else 0
    
    # Prepare features
    features = {}
    
    # Raw features to standardize
    raw_features = {
        'area': area,
        'distance_to_center': distance_to_center,
        'building_floors_num': building_floors_num,
        'floor_numeric': floor_numeric,
        'build_year': build_year,
        'relative_floor_position': relative_floor_position
    }
    
    # Standardize features
    for feature, value in raw_features.items():
        if feature in standardization_params:
            params = standardization_params[feature]
            std_feature = f"{feature}_std"
            features[std_feature] = (value - params['mean']) / params['std']
    
    
    # Regular features
    features['rooms_num'] = rooms_num
    features['is_top_floor'] = 1 if floor_numeric == building_floors_num else 0
    
    # District
    district_col = f'district_{districts}'
    for col in feature_names:
        if col.startswith('district_'):
            features[col] = 1 if col == district_col else 0
    
    # Building type
    features['building_type_apartment'] = 1 if building_type == 'Apartment' else 0
    features['building_type_tenement'] = 1 if building_type == 'Tenement' else 0
    
    # Window type
    features['window_plastic'] = 1 if window_type == 'Plastic' else 0
    features['window_wooden'] = 1 if window_type == 'Wooden' else 0
    
    # Agency
    features['user_type_agency'] = 1 if is_agency else 0
    
    # Amenity scores
    features['kitchen_furniture_score'] = kitchen_furniture_score
    features['security_score'] = security_score
    features['tech_score'] = tech_score
    features['premium_amenities_score'] = premium_amenities_score
    features['infrastructure_score'] = infrastructure_score
    features['interior_score'] = interior_score
    
    # Engineered features
    if 'area_std' in features:
        features['area_per_room'] = features['area_std'] * max(rooms_num, 1)
        
        if 'distance_to_center_std' in features:
            features['area_distance_interaction'] = features['area_std'] * features['distance_to_center_std']
    
    features['high_premium_district'] = 1 if district_col in high_premium_districts else 0
    
    if 'build_year_std' in features:
        features['building_age'] = features['build_year_std'] * -1
    
    if 'building_floors_num_std' in features and 'floor_numeric_std' in features:
        features['top_floor_distance'] = features['building_floors_num_std'] - features['floor_numeric_std']
    
    # Check for missing features
    for feature in feature_names:
        if feature not in features:
            features[feature] = 0
    
    # Make prediction
    input_df = pd.DataFrame([features])[feature_names]
    log_price_pred = model.predict(input_df)[0]
    price_pred = np.exp(log_price_pred)
    price_per_sqm = price_pred / area
    
    # Display results
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"**Estimated Monthly Rent: {price_pred:.2f} PLN**")
        st.info(f"Price per Square Meter: {price_per_sqm:.2f} PLN/sqm")
    
    with col2:
        # Show some property insights
        property_insights = []
        if features.get('high_premium_district', 0) == 1:
            property_insights.append("Located in a premium district")
        
        if premium_amenities_score > 0:
            property_insights.append("Has premium amenities")
            
        if features.get('area_std', 0) > 0:
            property_insights.append("Above average size")
        elif features.get('area_std', 0) < -0.5:
            property_insights.append("Smaller than average")
            
        if features.get('build_year_std', 0) > 0.5:
            property_insights.append("Newer building")
        elif features.get('build_year_std', 0) < -0.5:
            property_insights.append("Older building")
            
        if property_insights:
            st.write("**Property Insights:**")
            for insight in property_insights:
                st.write(f"- {insight}")