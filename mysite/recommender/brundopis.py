import pandas as pd
# from django.contrib.auth.models import User

users = pd.read_csv('static/recommender/users.csv')
print(users.head())

for i, row in users.iterrows():
    username = row['username'],
    first_name = row['first_name'],
    last_name = row['last_name'],
    password = row['password'],
    email = row['email'],
    date_joined = row['date_joined'],

