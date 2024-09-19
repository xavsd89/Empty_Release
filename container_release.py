import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Define the depot locations and container types
depot_locations = ['Depot 1', 'Depot 2', 'Depot 3']
container_types = ['20ST', '40ST', '40RH', '40HC']

# Initial container stock
initial_container_stock = {
    'Depot 1': {'20ST': 10, '40ST': 5, '40RH': 7, '40HC': 8},
    'Depot 2': {'20ST': 6, '40ST': 8, '40RH': 2, '40HC': 9},
    'Depot 3': {'20ST': 7, '40ST': 6, '40RH': 5, '40HC': 4},
}

# Initialize the session state
if 'container_stock' not in st.session_state:
    st.session_state.container_stock = initial_container_stock

def check_container_availability(depot, container_type, quantity):
    if depot in st.session_state.container_stock and container_type in st.session_state.container_stock[depot]:
        if st.session_state.container_stock[depot][container_type] >= quantity:
            return True
    return False

# Create a title for the app
st.title('Empty Container Release Process')

# Display the current date
current_date = datetime.now().date()
st.write(f'Today\'s Date: {current_date.strftime("%Y-%m-%d")}')

# Create a placeholder for the table
table_placeholder = st.empty()
table_placeholder.table(pd.DataFrame(st.session_state.container_stock))

# Button to reset the container stock
if st.button('Reset Container Stock'):
    st.session_state.container_stock = initial_container_stock
    st.success('Container stock has been reset.')
    table_placeholder.table(pd.DataFrame(st.session_state.container_stock))

# Create a select box for the depot locations
depot_location = st.selectbox('Select Depot Location', depot_locations)

# Layout for container type and quantity
col1, col2 = st.columns(2)

with col1:
    container_type = st.selectbox('Select Container Type', container_types)

with col2:
    container_quantity = st.number_input('Enter Quantity of Containers to Release', min_value=1, value=1, step=1)

# Layout for default pickup window, shortage pickup window, start date, and end date
col3, col4, col5, col6 = st.columns(4)

with col3:
    default_pickup_window = st.number_input('Default Pickup Window (days)', min_value=1, value=8, step=1)

with col4:
    shortage_pickup_window = st.number_input('Shortage Pickup Window (days)', min_value=1, value=5, step=1)

with col5:
    start_date = st.date_input('Shortage Start Date', value=current_date)

with col6:
    end_date = st.date_input('Shortage End Date', value=current_date + timedelta(days=7))

# Create a date input for the port of loading date
port_of_loading_date = st.date_input('Enter Port of Loading Date (ETD of vessel)', value=datetime.now().date())

# Create a date input for the required date specifically for 40RH containers
req_date = st.date_input('Enter Required Date for 40RH Containers', value=current_date)

# Calculate the earliest pickup date for 20ST and 40ST
if start_date <= current_date <= end_date:
    earliest_pickup_date = port_of_loading_date - timedelta(days=shortage_pickup_window)
else:
    earliest_pickup_date = port_of_loading_date - timedelta(days=default_pickup_window)

# Display the earliest pickup date for 20ST and 40ST
st.write(f'Earliest Pickup Date for 20ST and 40ST: {earliest_pickup_date.strftime("%Y-%m-%d")}')

# Check if the current date allows for container release for 20ST and 40ST
pickup_window_valid = earliest_pickup_date <= current_date

# Display validation status for 20ST and 40ST
if pickup_window_valid:
    st.success('The current date is within the valid pickup window for 20ST and 40ST container release.')
else:
    st.error('The current date is not within the valid pickup window for 20ST and 40ST container release.')

# Create a button to release the container
if st.button('Release Container!'):
    if container_type == '40RH':
        # For 40RH, check against the required date
        if req_date == current_date:
            if check_container_availability(depot_location, container_type, container_quantity):
                st.session_state.container_stock[depot_location][container_type] -= container_quantity
                st.success(f'{container_quantity} {container_type} containers have been successfully released from {depot_location}.')
                table_placeholder.table(pd.DataFrame(st.session_state.container_stock))
            else:
                st.error(f'Not enough {container_type} containers available at {depot_location}.')
        else:
            st.error('Unable to release 40RH containers. Today date must be at the Required Date which is collection date for Reefer.')
    else:
        # For 20ST and 40ST
        if pickup_window_valid:
            if check_container_availability(depot_location, container_type, container_quantity):
                st.session_state.container_stock[depot_location][container_type] -= container_quantity
                st.success(f'{container_quantity} {container_type} containers have been successfully released from {depot_location}.')
                table_placeholder.table(pd.DataFrame(st.session_state.container_stock))
            else:
                st.error(f'Not enough {container_type} containers available at {depot_location}.')
        else:
            st.error('Unable to release container. The current date is not within the valid pickup window.')
