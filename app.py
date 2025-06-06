import streamlit as st
import requests
from datetime import datetime
import pandas as pd

st.title('NYC Taxi Fare Predictor')

st.markdown('''
This application predicts the fare amount for a taxi ride in New York City
based on pickup and dropoff locations, date and time, and passenger count.
''')

# Create a form for user inputs
with st.form(key='taxi_fare_form'):
    # Date and time input
    date_input = st.date_input('Pickup date', value=datetime.now().date())
    time_input = st.time_input('Pickup time', value=datetime.now().time())

    # Location inputs
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Pickup Location")
        pickup_longitude = st.number_input('Pickup longitude', value=-73.950655, format="%.6f")
        pickup_latitude = st.number_input('Pickup latitude', value=40.783282, format="%.6f")

    with col2:
        st.subheader("Dropoff Location")
        dropoff_longitude = st.number_input('Dropoff longitude', value=-73.984365, format="%.6f")
        dropoff_latitude = st.number_input('Dropoff latitude', value=40.769802, format="%.6f")

    # Passenger count
    passenger_count = st.slider('Passenger count', min_value=1, max_value=8, value=2)

    # Submit button
    submit_button = st.form_submit_button(label='Predict Fare')

# When form is submitted
if submit_button:
    # Format date and time properly (removing microseconds)
    pickup_datetime = f"{date_input} {time_input.strftime('%H:%M:%S')}"

    # Create parameters dictionary
    params = {
        'pickup_datetime': pickup_datetime,
        'pickup_longitude': pickup_longitude,
        'pickup_latitude': pickup_latitude,
        'dropoff_longitude': dropoff_longitude,
        'dropoff_latitude': dropoff_latitude,
        'passenger_count': passenger_count
    }

    # Debug: Show what's being sent to the API
    st.write("Sending to API:", params)

    # API endpoint
    url = 'https://taxi-399730216663.europe-west1.run.app/predict'

    # Call the API
    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            # Parse the response
            prediction = response.json()

            # Display the raw response for debugging
            st.write("API Response:", prediction)

            # Handle different response formats
            if isinstance(prediction, dict):
                if 'fare_amount' in prediction:
                    fare = prediction['fare_amount']
                elif 'prediction' in prediction:
                    fare = prediction['prediction']
                elif 'fare' in prediction:
                    fare = prediction['fare']
                else:
                    # Show all keys to help debug
                    st.warning(f"Response keys: {list(prediction.keys())}")
                    fare = list(prediction.values())[0]  # Try first value
            elif isinstance(prediction, (int, float)):
                # Direct numeric response
                fare = prediction
            else:
                # Try to convert to float if it's a string
                try:
                    fare = float(prediction)
                except:
                    st.error(f"Couldn't parse response: {prediction}")
                    fare = 0

            # Display the prediction
            st.success(f"The predicted fare amount is: ${fare:.2f}")

            # Display a map with the route
            st.subheader("Ride Route")
            data = pd.DataFrame({
                'lat': [pickup_latitude, dropoff_latitude],
                'lon': [pickup_longitude, dropoff_longitude],
                'location': ['Pickup', 'Dropoff']
            })
            st.map(data)

        else:
            st.error(f"Error from API: {response.status_code} - {response.text}")

    except Exception as e:
        st.error(f"An error occurred: {e}")

# Add some helpful information
st.markdown("""
### About
This app connects to a machine learning model API that predicts NYC taxi fares.
The model was trained on historical taxi ride data from the NYC Taxi & Limousine Commission.

### Tips for accurate predictions:
- Longitude values for NYC are typically between -74.03 and -73.75
- Latitude values for NYC are typically between 40.63 and 40.85
- The date and time can affect predictions due to traffic patterns
""")
