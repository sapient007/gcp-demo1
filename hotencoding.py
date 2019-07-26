import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/benjamindiaz/Desktop/google/ML-sandbox-1-64eb1ed297b7.json"
PROJECT_ID = 'ml-sandbox-1-191918'
from google.cloud import bigquery
client = bigquery.Client(project=PROJECT_ID, location="US")


from numpy import array
from numpy import argmax
from keras.utils import to_categorical
# from sklearn.preprocessing import LabelEncoder, OneHotEncoder


# define example
community_area = [num for num in range(78)]

# data = array(data)
print(community_area)

# one hot encode
encoded = to_categorical(community_area)
print(encoded)
# invert encoding
inverted = argmax(encoded[0])
print(inverted)

