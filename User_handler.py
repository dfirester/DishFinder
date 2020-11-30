import functools
import numpy as np
import pandas as pd

class User(object):

    def __init__(self):
        self.features = [0]*20 + [1] + [0]
        self.reviews = dict()
        self.numiterations = 5
        self.featurematrix = []
        self.featurehistory = []

        f = open("Toronto_business_key.txt", "r")
        businesskey = f.read()
        businesskey = businesskey.split('\n')[:-1]
        ResturantMatrix = np.loadtxt('Toronto_matrix_new.txt')
        self.dataframe = pd.DataFrame(ResturantMatrix, index=businesskey)
       
        
    def addreview(self,restid,stars):
        self.reviews[restid] = stars
        self._userfactorization()
        self.numiterations += 5

    def generate_distribution(self, eps = .1, numsamples=10000):
        resturantmatrix = np.array(self.restmatrix).T
        reviews = np.array(self.reviewmatrix)
        uservals = [list(self.features)]
        for _ in range(numsamples):
            uservals.append(self._step(np.array(uservals[-1]), resturantmatrix, reviews, eps))
        self.featurematrix = np.array(uservals)

    def expectedreview(self,restid):
        resturant = np.array(self.dataframe.loc[restid].values)
        return resturant.dot(self.features)

    def _userfactorization(self,learn_rate=0.05,lambda_u=.05): # default lambda_u = .01
        restmatrix = []
        reviewmatrix = []
        for restid in self.reviews:
            restmatrix += [list(self.dataframe.loc[restid].values)]
            reviewmatrix += [self.reviews[restid]]

        for i in range(self.numiterations):
            n = np.random.choice(len(reviewmatrix))
            review, Resturant = reviewmatrix[n], restmatrix[n]
            Resturant = np.array(Resturant)
            features = np.array(self.features)
            self.features = list(features + learn_rate*((review - np.dot(features,Resturant))*Resturant - lambda_u*features))
            self.featurehistory += self.features
        

    def _starprob(self,Star_d, Star_c, std):
        def probdensity(x):
            return 1/(np.sqrt(2*np.pi)*std) * np.exp(-.5*((Star_d - Star_c)/std)**2)
        return sum([probdensity(x)*.1 for x in np.linspace(Star_d-.5,Star_d+.5,11)])

    def _step(self,user,resturants,reviews,eps):
        newuser = user + np.random.uniform(-eps,eps)
        oldreviews = user.dot(resturants)
        newreviews = newuser.dot(resturants)
        oldprob = functools.reduce(lambda x,y : x*y,map(functools.partial(self._starprob,std=.5),reviews,oldreviews))
        newprob = functools.reduce(lambda x,y : x*y,map(functools.partial(self._starprob,std=.5),reviews,newreviews))
        if np.random.uniform(0,1) < newprob/oldprob:
            return list(newuser)
        else:
            return list(user)
