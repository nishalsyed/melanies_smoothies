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
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('search_on'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

pd_df = my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 Ingredients", my_dataframe['FRUIT_NAME'].tolist(), max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        search_on=pd_df.loc[pd_df['fruit_name']== fruit_chosen, 'search_on'].iloc[0]
        st.write('The search vluse for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen+ 'Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
        fv_dv = st.dataframe(fruityvice_response.json(), use_container_width=True)

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
