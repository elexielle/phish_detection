import streamlit as st
import joblib
import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


# Custom modules
from tasks.preprocessing import extract_features

# #pipeline
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin

class Converter(BaseEstimator, TransformerMixin):
    def fit(self, x, y=None):
        return self

    def transform(self, data_frame):
        return data_frame.values.ravel()


#---
st.set_page_config(
    page_title='Phish App',
    page_icon=':space_invader:',
    layout = 'centered'
)

st.title('Phishing Detector')

#---
with st.sidebar:
    st.header('About')
    #st.button('About')
    st.write('''
             This phishing detector uses machine learning to distinguish phishing sites 
             from legit sites. It was trained with over 22K links, gathered from PhishTank. 
             This model utilizes support vector machine algorithm, and it gives the probability 
             that the prediction belongs to a certain class.
             ''')

#---
# Section 1: Introduction
st.header('')
st.write('''Welcome to Phish App! This web application is used to **detect phishing sites**. 
         It uses a machine learning algorithm to predict if a link is a phishing or a legitimate link.''')


st.write('To get started, please enter a link below.')
link = st.text_input(" ", placeholder="Enter a link:")

#to center the button
st.markdown("----", unsafe_allow_html=True)
columns = st.columns((2, 1, 2))
button_pressed = columns[1].button('Predict')
st.markdown("----", unsafe_allow_html=True)


# Add the Predict button
if button_pressed:
    dict_label = {
        0: 'Legitimate',
        1: 'Phishing'
    }
    # Call the extract_features function
    features_df = extract_features(link)


    #load model
    model_path = r'C:\Users\exusille\Documents\school\thesis\vsc thesis workspace\NEW_WORKSPACE\DEPLOYMENT\phish_detection\svm_model.joblib'
    svm_model, threshold = joblib.load(model_path)
    #prediction = svm_model.predict(features_df)
    #altered_prediction = (prediction>=(1-threshold)).astype(int)
    proba = svm_model.predict_proba(features_df)[:,1]
    phish_percent = round(proba[0]*100, 2)
        

    #idk i just want a big doughnut for estetik. thanks gpt ;)
    # Calculate the remaining percentage for the doughnut shape
    remaining_percent = 100 - phish_percent

    # Create a figure and axis with transparent background
    fig, ax = plt.subplots(facecolor='none')

    # Define the colors for the doughnut segments
    colors = ['#f63366', '#B9CC95']

    # Create the doughnut plot
    wedges, _ = ax.pie([phish_percent, remaining_percent], colors=colors, startangle=90, counterclock=False, wedgeprops=dict(width=0.3))

    # Set transparent background for the wedges
    for wedge in wedges:
        wedge.set_edgecolor('none')

    # Add a white circle at the center to create the doughnut shape
    center_circle = plt.Circle((0, 3), 0.55, color='white')
    ax.add_artist(center_circle)

    # Set aspect ratio to be equal so the doughnut appears circular
    ax.set_aspect('equal')

    # Remove x and y axis labels
    ax.axis('off')

    # Set the text for the percentage value
    if proba >= threshold:
        text = ax.text(0, 0, f'{phish_percent}%', ha='center', va='center', fontsize=24)
    else:
        text = ax.text(0, 0, f'{remaining_percent}%', ha='center', va='center', fontsize=24)

    # Update the text color based on the percentage value
    if phish_percent >= 50:
        text.set_color('white')
    else:
        text.set_color('white')

    # Display the doughnut gauge with transparent background
    st.pyplot(fig, transparent=True)
    
    
    #using the threshold
    if proba >= threshold:
        final_prediction = 1  # Positive class (Phishing)
        st.header("Phishing Detected!")
        st.write("The model flagged the link as a phish, with a probability of ", phish_percent, "% that it is a phishing link.")
    else:
        final_prediction = 0  # Negative class (Legitimate)
        st.header("Legitimate Link")
        st.write("The model is ", remaining_percent, "% sure that the link leads to a legitimate website.")
        
    st.write(features_df)