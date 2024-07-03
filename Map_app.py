# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 09:19:42 2024

@author: Hrish
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# Function to update the map
def update_map(df):
    map_centr = df['Lat'].mean(), df['Lon'].mean()
    m = folium.Map(location=map_centr, zoom_start=10, tiles='CartoDB positron')

    dot_density_layer = folium.FeatureGroup(name='Dot Density Layer')
    buffer_layer = folium.FeatureGroup(name='Buffer Layer')

    def marker(row):
        popup_text = (
            f'<b>Village:</b> {row["Village Name. "]}<br><br>'
            f'<b>Students:</b> {row["Student Count"]}<br><br>'
            f'<b>Achievements:</b> {row["Achievements"]}'
        )
        folium.CircleMarker(
            location=[row['Lat'], row['Lon']],
            radius=5 + row['Student Count'],
            color='blue',
            fill=True,
            fill_color='blue',
            popup=folium.Popup(popup_text, max_width=650)
        ).add_to(dot_density_layer)

    df.apply(marker, axis=1)

    lat = 17.64923336471533
    lon = 73.31791512422657
    radii = [5000, 4000, 3000, 2000]

    def multiring_buffer(lat, lon, radii, buffer_layer):
        for r in radii:
            popup_text = f'Radius: {r / 1000:.1f} km'
            folium.Circle(
                location=[lat, lon],
                radius=r,
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.1,
                popup=folium.Popup(popup_text, max_width=250)
            ).add_to(buffer_layer)

    multiring_buffer(lat, lon, radii, buffer_layer)

    folium.Marker(
        location=[lat, lon],
        popup='New English School Karanjani',
        icon=folium.Icon(color='green', icon='star')
    ).add_to(m)

    buffer_layer.add_to(m)
    dot_density_layer.add_to(m)

    folium.LayerControl().add_to(m)

    return m

# Streamlit app layout
st.title('NESK EduMap')

option = st.radio("Choose an option", ('View Map', 'Update Information'))

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    if option == 'Update Information':
        village = st.selectbox("Village Name", df['Village Name. '].unique())
        achievement = st.text_input("Achievement (Format: 'student name: Achievement')")

        if st.button('Add Data'):
            if village and achievement:
                # Update the DataFrame
                df.loc[df['Village Name. '] == village, 'Student Count'] += 1
                df.loc[df['Village Name. '] == village, 'Achievements'] += '<br>' + achievement
                st.write(df)  # Debugging: Show the updated DataFrame
                df.to_csv(uploaded_file.name, index=False)
                st.success('Data added successfully')
            else:
                st.warning('Please fill in all fields.')

    if option == 'View Map' or (option == 'Update Information' and st.button('Update Map')):
        map_obj = update_map(df)
        folium_static(map_obj)
