import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Define the depot locations and container types
depot_locations = ['Depot 1', 'Depot 2', 'Depot 3']
container_types = ['20ST', '40ST', '40RH', '40HC']

# Let's assume this is your initial container stock
initial_container_stock = {
    'Depot 1': {'20ST': 10, '40ST': 5, '40RH': 7, '40HC': 8},
    'Depot 2': {'20ST': 6, '40ST': 8, '40RH': 2, '40HC': 9},
    'Depot 3': {'20ST': 7, '40ST': 6, '40RH': 5, '40HC': 4},
}

# Initialize the session state
if 'container_stock' not in st.session_state:
    st.session_state.container_stock = initial_container_stock

def check_container_availability(depot, container_type, quantity):
    # Check if the depot has the container type
    if depot in st.session_state.container_stock and container_type in st.session_state.container_stock[depot]:
        # Check if the container stock is more than the requested quantity
        if st.session_state.container_stock[depot][container_type] >= quantity:
            return True
    return False

# Create a title for the app
st.title('Empty Container Release Process')

# Display the current date based on the system date
current_date = datetime.now().date()
st.write(f'Today\'s Date: {current_date.strftime("%Y-%m-%d")}')

# Create a placeholder for the table at the top of the page
table_placeholder = st.empty()

# Display the initial container stock in the table placeholder
table_placeholder.table(pd.DataFrame(st.session_state.container_stock))
# Create a button to reset the container stock
if st.button('Reset Container Stock'):
    st.session_state.container_stock = initial_container_stock
    st.success('Container stock has been reset.')
    # Update the table in the placeholder
    table_placeholder.table(pd.DataFrame(st.session_state.container_stock))


# Create a select box for the depot locations
depot_location = st.selectbox('Select Depot Location', depot_locations)

# Create a select box for the container types
container_type = st.selectbox('Select Container Type', container_types)

# Create a number input for the quantity of containers to release
container_quantity = st.number_input('Enter Quantity of Containers to Release', min_value=1, value=1, step=1)

# Create a date input for the port of loading date
port_of_loading_date = st.date_input('Enter Port of Loading Date (ETD of vessel)', value=datetime.now().date())

# Create a number input for the allowance days
allowance_days = st.number_input(f'Enter Allowance Days for {container_type} (40RH = 5 days allowance; 20ST/40ST/40HC = 8 days allowance)', min_value=1, value=1, step=1)

# If the container type is '40RH', create an additional date input
specific_date_40RH = None
if container_type == '40RH':
    min_date = port_of_loading_date - timedelta(days=5)
    max_date = port_of_loading_date
    specific_date_40RH = st.date_input('Enter Specific Date for 40RH', value=min_date, min_value=min_date, max_value=max_date)

# Calculate the earliest pickup date based on the port of loading date and the allowance days
earliest_pickup_date = port_of_loading_date - timedelta(days=allowance_days)

# Display the earliest pickup date
st.write(f'Earliest Pickup Date: {earliest_pickup_date.strftime("%Y-%m-%d")} (Loading Date - Allowance Days)')

# Check if the current date is within the pickup window
pickup_window_valid = earliest_pickup_date <= current_date <= port_of_loading_date

# Display a validation icon if the current date is within the pickup window
if pickup_window_valid:
    st.success('The current date is within the pickup window.')
else:
    st.error('The current date is not within the pickup window.')

# Create a button to release the container, but only if the pickup window is valid
if st.button('Release Container!'):
    if pickup_window_valid:
        # Check container availability
        if check_container_availability(depot_location, container_type, container_quantity):
            # If the container type is '40RH', check if the current date is the specific date
            if container_type == '40RH' and current_date != specific_date_40RH:
                st.error(f'Unable to release container. {container_type} containers can only be released on {specific_date_40RH.strftime("%Y-%m-%d")}.')
            else:
                # Reduce the container stock
                st.session_state.container_stock[depot_location][container_type] -= container_quantity
                st.success(f'{container_quantity} {container_type} containers have been successfully released at {depot_location} with earliest pickup date on {earliest_pickup_date.strftime("%Y-%m-%d")}!')
                # Update the table in the placeholder
                table_placeholder.table(pd.DataFrame(st.session_state.container_stock))
        else:
            st.error(f'Unable to release container. Not enough {container_type} containers available at {depot_location}.')
    else:
        st.error('Unable to release container. The current date is not within the pickup window.')
