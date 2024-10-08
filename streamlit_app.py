# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Establish connection
cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

name_on_smoothie = st.text_input("Name on Smoothie:")
st.write("The Name on your smoothie will be:", name_on_smoothie)

# Fetching data from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('search_on')).to_pandas()
st.dataframe(data=my_dataframe, use_container_width=True)

# Print column names to verify
st.write("Columns in DataFrame:", my_dataframe.columns)

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 Ingredients", my_dataframe['FRUIT_NAME'].tolist(), max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        if 'search_on' in my_dataframe.columns:
            search_on = my_dataframe.loc[my_dataframe['FRUIT_NAME'] == fruit_chosen, 'search_on'].iloc[0]
            st.write(f'The search value for {fruit_chosen} is {search_on}.')

            st.subheader(f'{fruit_chosen} Nutrition Information')
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
            fv_dv = st.dataframe(fruityvice_response.json(), use_container_width=True)
        else:
            st.error(f"Column 'search_on' not found in the DataFrame.")

ingredients_string = ', '.join(ingredients_list)

# Constructing the query string directly
my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders(ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_on_smoothie}')
"""
st.write(my_insert_stmt)

time_to_insert = st.button('Submit Order')

if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered!', icon="✅")
