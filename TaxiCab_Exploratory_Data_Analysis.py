# Importing basic Libraries
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import datetime as dt
import altair as alt
# %matplotlib inline
import json
from geopy.distance import great_circle
from geopy.geocoders import Nominatim
#for calculating Disstance 
plt.switch_backend('TkAgg')
import os
#import plost


header = st.container()
dataset = st.container()
side_features = st.container()


with header:
    st.title("Data visualisation of the NEWYORK CITY TAXICAB ANALYSIS")
    st.text('Identifying visibility on how well THE TAXICAB company is doing and finding out')
    st.text('potential opportunities that can help the business scale further.')
    st.sidebar.header('Dashboard `NEWYORK CITY TAXICAB`')
    sel_col, disp_col = st.columns(2)
    time_value = sel_col.slider('select the time of the day to see the values')

with dataset:
    st.header("# NEWYORK CITY TAXICAB ANALYSIS")

    @st.cache_data
    def load_data():

      df =pd.read_csv('C:/Users/sushd/Desktop/data analytics course/da-taxi-tech-challenge-master/da-taxi-tech-challenge-master/raw_data/yellow_tripdata_2021-01_raw_updated.csv', low_memory=False)

      return df


    df = load_data()


# load CSV file into memory

#df = pd.read_csv('C:/Users/sushd/Desktop/data analytics course/da-taxi-tech-challenge-master/da-taxi-tech-challenge-master/raw_data/yellow_tripdata_2021-01_raw_updated.csv')
#load Json file
# Open the JSON file
# Load surcharge data from JSON file
# Open the JSON file
    with open('C:/Users/sushd/Desktop/data analytics course/da-taxi-tech-challenge-master/da-taxi-tech-challenge-master/raw_data/surcharge_data.json', 'r') as f:
     surcharge_df =  pd.DataFrame(json.load(f))

#surcharge_df.head()
    surcharge_df = surcharge_df.transpose()
#surcharge_df.head()
# Reset the index
    surcharge_df = surcharge_df.reset_index()

# Rename the columns
    surcharge_df.columns = ['tripId', 'improvement_surcharge', 'congestion_surcharge']


#surcharge_df.head()

    surcharge_df['tripId'] = surcharge_df['tripId'].astype('Int64')

# replacing all null/missing values witheplace the missing values with the most frequent value in each column

    df['passenger_count'] = df['passenger_count'].fillna(df['passenger_count'].mode()[0]).astype('int')
    df['RatecodeID'] = df['RatecodeID'].fillna(df['RatecodeID'].mode()[0]).astype('int')


# for store _and_fwd_flag
    df['store_and_fwd_flag'] = df['store_and_fwd_flag'].fillna('N').astype('category')

#removing 'km' so we can convert trip_distance to numeric value
    df['trip_distance'] = df['trip_distance'].str.replace('km', '')

# Convert columns to appropriate data types
    df['PULocationID'] = df['PULocationID'].astype('category')
    df['DOLocationID'] = df['DOLocationID'].astype('category')
    df['tripId'] = df['tripId'].astype('category')
    df['VendorID'] = df['VendorID'].astype('int')
    df['passenger_count'] = df['passenger_count'].astype('int') 
    df['RatecodeID'] = df['RatecodeID'].astype('int')
    df['payment_type'] = df['payment_type'].astype('int')
    df['fare_amount'] = df['fare_amount'].astype('float')
    df['extra'] = df['extra'].astype('float')
    df['mta_tax'] = df['mta_tax'].astype('float')
    df['tip_amount'] = df['tip_amount'].astype('float')
    df['tolls_amount'] = df['tolls_amount'].astype('float')
    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
    df['trip_distance'] = pd.to_numeric(df['trip_distance'])
    df['store_and_fwd_flag'] = df['store_and_fwd_flag'].astype('category')

# The tpep_pickup_datetime and tpep_dropoff_datetime need to be changed into datetime format. 
# The store and fwd flag need to be change into Category Format(Yes/no).
# expand the date time into weekday, month, hour, min

    df['tpep_pickup_datetime'] =pd.to_datetime(df['tpep_pickup_datetime'])
    df['tpep_dropoff_datetime'] =pd.to_datetime(df['tpep_dropoff_datetime'])

# extracting day of the week
    df['pickup_day']= df['tpep_pickup_datetime'].dt.day_name()
    df['dropoff_day']= df['tpep_dropoff_datetime'].dt.day_name()
# extracting day of the weekday
    df['pickup_day_num']= df['tpep_pickup_datetime'].dt.weekday
    df['dropoff_day_num']= df['tpep_dropoff_datetime'].dt.weekday
# extracting month of the Year
    df['pickup_month']= df['tpep_pickup_datetime'].dt.month_name()
    df['dropoff_month']= df['tpep_dropoff_datetime'].dt.month_name()
# extracting hour, min
    df['pickup_hour']= df['tpep_pickup_datetime'].dt.hour
    df['dropoff_hour']= df['tpep_dropoff_datetime'].dt.hour
    df['pickup_min']= df['tpep_pickup_datetime'].dt.minute
    df['dropoff_min']= df['tpep_dropoff_datetime'].dt.minute

#create a new column called trip_duration
    df['trip_duration'] = ((df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']).dt.total_seconds() / 60).round().astype(int)

#drop un necessary columns
    len(df[df['fare_amount'] <= 0])
    df = df[df['fare_amount'] > 0]


# grouping by rate code ID
    df.groupby('RatecodeID')['trip_distance'].median()

    tip_by_vendor_day = df.groupby(['VendorID', 'pickup_day']).tip_amount.mean().reset_index()

    busiest_hour = df.tpep_pickup_datetime.dt.hour.value_counts().idxmax()
    df.drop_duplicates(inplace=True)

     #classify trips by payment type
    payment_types = df['payment_type'].unique()
    trip_counts = df.groupby('payment_type').size().reset_index(name='count')
    total_distance = df.groupby('payment_type')['trip_distance'].sum().reset_index(name='total_distance')
    total_fare = df.groupby('payment_type')['fare_amount'].sum().reset_index(name='total_fare')
    average_tip = df.groupby('payment_type')['tip_amount'].mean().reset_index(name='average_tip')

    # create visualizations
    st.subheader('Payment Type Analysis')
    st.write('Total Trips by Payment Type:')
    bar_chart = alt.Chart(trip_counts).mark_bar().encode(
        x='payment_type:N',
        y='count:Q'
    ).properties(width=400, height=300)
    st.altair_chart(bar_chart)

    st.write('Total Distance by Payment Type:')
    bar_chart2 = alt.Chart(total_distance).mark_bar().encode(
        x='payment_type:N',
        y='total_distance:Q'
    ).properties(width=400, height=300)
    st.altair_chart(bar_chart2)

    st.write('Total Fare by Payment Type:')
    bar_chart3 = alt.Chart(total_fare).mark_bar().encode(
        x='payment_type:N',
        y='total_fare:Q'
    ).properties(width=400, height=300)
    st.altair_chart(bar_chart3)

    st.write('Average Tip by Payment Type:')
    bar_chart4 = alt.Chart(average_tip).mark_bar().encode(
        x='payment_type:N',
        y='average_tip:Q'
    ).properties(width=400, height=300)
    st.altair_chart(bar_chart4)



     # busiest day of the week
       # Sample the data to limit the size of the chart to 200MB
    sampled_df = df.sample(frac=0.5)

    # Create a bar chart using Altair
    st.subheader('Busiest Day of the Week')
    chart1 = alt.Chart(sampled_df).mark_bar().encode(
        x=alt.X('pickup_day:N', title='Day of Week'),
        y=alt.Y('count():Q', title='Count'),
    ).properties(
        title='Busiest Day of the Week'
    )

    st.altair_chart(chart1, use_container_width=True)



    # Busiest Hour
    st.subheader('Number of pickups by hour')

    # Sample the data to show only 200 MB
    df_sampled = df.sample(frac=0.5)

    chart2 = alt.Chart(df_sampled).mark_bar().encode(
        x=alt.X('hour(tpep_pickup_datetime):O', title='Hour of Day'),
        y=alt.Y('count()', title='Number of Trips'),
        color=alt.Color('hour(tpep_pickup_datetime):O', title='Hour of Day', timeUnit='hours')
    ).properties(
        title='Number of Taxi Trips by Hour of Day'
    )

    st.altair_chart(chart2, use_container_width=True)



    # Calculate average tip by vendor and day
    average_tip_by_vendor_and_day = df.groupby(['VendorID', 'pickup_day'])['tip_amount'].mean().reset_index()

    # Create a grouped bar chart using Altair
    chart3 = alt.Chart(average_tip_by_vendor_and_day).mark_bar().encode(
        x=alt.X('pickup_day:N', title='Day of Week'),
        y=alt.Y('tip_amount:Q', title='Average Tip Amount'),
        color=alt.Color('VendorID:N', title='Vendor ID'),
    ).properties(
        title='Average Tip Amount by Vendor and Day'
    )

    st.altair_chart(chart3, use_container_width=True)



    # Aggregate data by hour of the day
    trips_by_hour = df.groupby('pickup_hour')['tripId'].count()

    # Plot a bar chart
    chart4, ax = plt.subplots()
    ax.bar(trips_by_hour.index, trips_by_hour.values)

    # Set chart title and labels
    ax.set_title('Number of Trips by Hour of the Day')
    ax.set_xlabel('Hour of the Day')
    ax.set_ylabel('Number of Trips')

    # Display the chart in Streamlit
    st.pyplot(chart4)


    # Rename the column in the JSON DataFrame to match the column in the CSV DataFrame
    surcharge_df = surcharge_df.rename(columns={'tripId': 'tripId'})

    # Merge the JSON DataFrame with the CSV DataFrame using the 'tripId' column as the key
    df_merged = pd.merge(df, surcharge_df, on='tripId', how='left')

    # View the merged DataFrame
    print(df_merged.head())


   
    # Merge the two DataFrames based on 'tripId'
    df = pd.merge(df, surcharge_df, on='tripId', how='left')
    df['total_surcharge'] = df['improvement_surcharge'] + df['congestion_surcharge']


    # Get the data
    #x = df['trip_distance']
    #y = df['congestion_surcharge']
    # Create an scatter plot using Altair
    sampled_df = df.sample(frac=0.5)
    chart5 = alt.Chart(sampled_df).mark_circle().encode(
        x=alt.X('trip_distance:Q', title='Trip Distance', type='quantitative'),
        y=alt.Y('congestion_surcharge:Q', title='Congestion Surcharge', type='quantitative'),
        tooltip=['trip_distance:Q', 'congestion_surcharge:Q']
    ).properties(
        title='Relationship between Congestion Surcharge and Trip Distance'
    )

    # Display the chart in Streamlit
    st.altair_chart(chart5, use_container_width=True)

    #   # Group the charts in 2 columns
    ##with st.container():
    #col1, col2 = st.columns(2)


##Display the charts in the left column
#with col1:
#    st.write('## Data is displayed into ')
   
#    st.pyplot(bar_chart)
#    st.pyplot(bar_chart2)
#    st.pyplot(bar_chart3)
#    st.pyplot(chart3)
#    st.pyplot(chart4)

## Display the charts in the right column
#with col2:
#    st.write('## two columns')
#    #st.pyplot(fig4)
#    st.pyplot(bar_chart4)
#    st.pyplot(bar_chart4)
#    st.pyplot(chart1)
#    st.pyplot(chart2)
#    st.pyplot(chart5)
