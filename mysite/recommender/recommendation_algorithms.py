import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import sparse
import pandas as pd

from django.contrib.auth.models import User
from .models import Movie, Rating

class ContentBased():
    def __init__(self, username):

        lam = 0.01
        self.tf_idf = sparse.load_npz('static/tf_idf.npz')
        self.lam_I = sparse.csr_matrix(lam * np.eye(self.tf_idf.shape[1]))
        self.active_user = User.objects.get(username=username)

    def get_rated_movies(self):
        user_ratings = self.active_user.rating_set.all()
        ratings_list = list(user_ratings.values_list('value', flat=True))
        ids_list = list(user_ratings.values_list('movie__id', flat=True))
        # subtract 1 from each element, because numpy arrays' indexing starts at 1
        ids_list = [x - 1 for x in ids_list]
        return ratings_list, ids_list

    def recommend_n_movies(self, n):
        ratings_list, ids_list = self.get_rated_movies()
        print(ratings_list, ids_list)
        Dl = self.tf_idf[ids_list]
        y = sparse.csr_matrix(np.array(ratings_list)).T
        wt_1 = sparse.linalg.inv((np.dot(Dl.T, Dl) + self.lam_I))
        wt_2 = np.dot(Dl.T, y)
        Wt = np.dot(wt_1, wt_2)
        predicted_ratings = np.dot(self.tf_idf, Wt).todense()
        print(predicted_ratings)
        print(predicted_ratings.shape)
        recommended_ids = []
        counter = 0
        for i in np.argsort(predicted_ratings, axis=0)[::-1]:
            if i.item() not in ids_list:
                recommended_ids.append(i.item()+1)  # adding 1 - SQL database's indexing starts at 1
                counter += 1
            if counter == n:
                break
        return Movie.objects.filter(id__in=recommended_ids).values_list('title', flat=True)