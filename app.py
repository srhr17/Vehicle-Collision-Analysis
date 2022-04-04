import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL=("https://media.githubusercontent.com/media/chairielazizi/streamlit-collision/master/Motor_Vehicle_Collisions_-_Crashes.csv")

st.set_page_config(
        page_title="Vehicle Collision in NYC",
        page_icon="SH logo.png",
        layout="wide",
    )
st.title("Vehicle Collision Analysis")	
st.markdown(' This application is a Streamlit dashboard that can be used to analyze vehicle collision data in NYC')

@st.cache(persist=True)
def loadData(row_limit):
    df = pd.read_csv(DATA_URL,nrows=row_limit,parse_dates=[['CRASH_DATE','CRASH_TIME']])
    df.dropna(subset=['LATITUDE','LONGITUDE'],inplace=True)
    df.rename(lambda x: str(x).lower(),axis='columns',inplace=True)
    return df

data_frame = loadData(10000)

# st.write(data_frame.columns)

st.header("Number of People injured in Collisions")
injured_people = st.slider("Number of People injured in Collisions",0,19)
st.map(data_frame.query("injured_persons >= @injured_people")[["latitude","longitude"]].dropna(how="any"))

st.header("Number of People injured by hour of the day")
hour = st.sidebar.slider("Hour of the day",0,23)
st.map(data_frame[data_frame["crash_date_crash_time"].dt.hour==hour][["latitude","longitude"]].dropna(how="any"))

st.header("Vehicle collision between %i and %i hours" % (hour,hour+1))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
     "latitude":data_frame["latitude"].mean(),
    "longitude":data_frame["longitude"].mean(),
    "zoom":11,
    "pitch":50
    },
      layers=[pdk.Layer("HexagonLayer",
                        data=data_frame[['crash_date_crash_time','latitude','longitude']],
                        get_position=['longitude','latitude'],
                        radius=100,
                        extruded=True,
                        pickable=True,
                        elevation_scale=4,
                        elevation_range=[0,1000]  )]
))

st.subheader("Breakdown by minutes between %i and %i hours" % (hour,hour+1))
filtered=data_frame[(data_frame['crash_date_crash_time'].dt.hour>=hour) & (data_frame['crash_date_crash_time'].dt.hour<hour+1)]
hist=np.histogram(filtered['crash_date_crash_time'].dt.minute,bins=60,range=(0,60))[0]
chart_data = pd.DataFrame({"minute":range(60),"crashes":hist})
fig = px.bar(chart_data,x='minute',y='crashes',hover_data=['minute','crashes'],height=400)
st.write(fig)

    
st.header("Top 5 dangerous streets by affected type")
select = st.selectbox('Affected type of people',['Pedestrians','Cyclists','Motorists'])

if select == 'Pedestrians':
    st.write(data_frame.query("injured_pedestrians >= 1")[["on_street_name","injured_pedestrians"]].sort_values(by=['injured_pedestrians'],ascending=False).dropna(how="any")[:5])	
elif select == 'Cyclists':
    st.write(data_frame.query("injured_cyclists >= 1")[["on_street_name","injured_cyclists"]].sort_values(by=['injured_cyclists'],ascending=False).dropna(how="any")[:5])
elif select == 'Motorists':
    st.write(data_frame.query("injured_motorists >= 1")[["on_street_name","injured_motorists"]].sort_values(by=['injured_motorists'],ascending=False).dropna(how="any")[:5])
    

st.subheader("Check the box to see/play with raw data")    
if st.checkbox('Show Raw Data',False):
    st.write(data_frame)