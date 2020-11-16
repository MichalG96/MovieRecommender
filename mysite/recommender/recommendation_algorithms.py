import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import sparse

from django.contrib.auth.models import User
from .models import Movie

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

    @staticmethod
    def to_percent(value):
        # Inflate the numbers a bit, multiply each predicted rating by 1.05
        if value > 9.25:    #10/10.5
            return 100
        else:
            return round(value * 10.5)

    def recommend_n_movies(self, n):
        ratings_list, ids_list = self.get_rated_movies()
        Dl = self.tf_idf[ids_list]
        y = sparse.csr_matrix(np.array(ratings_list)).T
        wt_1 = sparse.linalg.inv((np.dot(Dl.T, Dl) + self.lam_I))
        wt_2 = np.dot(Dl.T, y)
        Wt = np.dot(wt_1, wt_2)
        predicted_ratings = np.dot(self.tf_idf, Wt).todense()
        recommended_ids = []
        recommended_predicted_ratings = []
        counter = 0
        for i in np.argsort(predicted_ratings, axis=0)[::-1]:
            if i.item() not in ids_list:
                recommended_ids.append(i.item()+1)  # adding 1 - SQL database's indexing starts at 1
                recommended_predicted_ratings.append(predicted_ratings[i].item())
                counter += 1
            if counter == n:
                break

        recommended_predicted_ratings = list(map(self.to_percent, recommended_predicted_ratings))
        return Movie.objects.filter(id__in=recommended_ids), recommended_predicted_ratings