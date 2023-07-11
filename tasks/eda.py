from wordcloud import WordCloud
import matplotlib.pyplot as plt
import streamlit as st

def graph(df, column):
    tokens = [str(text) for text in column]
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(tokens))
    
    # Plot the word cloud for phish labels
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.title('Word Cloud of TLD - Phish Sites')
    plt.axis('off')
    plt.show()
