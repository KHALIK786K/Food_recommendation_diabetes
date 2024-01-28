# -*- coding: utf-8 -*-
"""Untitled2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Qw6dDpy1vdY2RTkoCpdkRs5Gpz8nSGpn
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from minisom import MiniSom
import matplotlib.pyplot as plt

df = pd.read_csv('main_dataset.csv')

df['GI (per 100 glucose)'] = pd.to_numeric(df['GI (per 100 glucose)'], errors='coerce')
df['Carbohydrates (per 100 g)'] = pd.to_numeric(df['Carbohydrates (per 100 g)'], errors='coerce')

df = df.dropna()

conditions = [
    (df['GI (per 100 glucose)'].between(0, 55)) & (df['Carbohydrates (per 100 g)'].between(0, 15)),
    (df['GI (per 100 glucose)'].between(56, 69)) & (df['Carbohydrates (per 100 g)'].between(16, 30)),
    (df['GI (per 100 glucose)'] >= 70) | (df['Carbohydrates (per 100 g)'] >= 31)
]

cluster_labels = ['Normal', 'Limited', 'Avoidable']

df['Cluster'] = np.select(conditions, cluster_labels)

X = df[['GI (per 100 glucose)', 'Carbohydrates (per 100 g)']].values

scaler = StandardScaler()
X_std = scaler.fit_transform(X)

wcss = []
for i in range(1, 11):
    kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
    kmeans.fit(X_std)
    wcss.append(kmeans.inertia_)

plt.plot(range(1, 11), wcss)
plt.title('Elbow Method for Optimal K')
plt.xlabel('Number of clusters (K)')
plt.ylabel('WCSS')
plt.show()

optimal_k = 3
kmeans = KMeans(n_clusters=optimal_k, init='k-means++', max_iter=300, n_init=10, random_state=0)
df['KMeans_Cluster'] = kmeans.fit_predict(X_std)

som = MiniSom(x=10, y=10, input_len=2, sigma=1.0, learning_rate=0.5, random_seed=42)
som.train_random(X_std, 100)

def get_cluster(food_name):
    food_index = df.index[df['Food'] == food_name].tolist()
    if not food_index:
        return "Food not found in the dataset"

    kmeans_cluster = df.iloc[food_index]['KMeans_Cluster'].values[0]
    return df.iloc[food_index]['Cluster'].values[0], kmeans_cluster

def recommend_foods(kmeans_cluster):
    normal_foods = df[df['KMeans_Cluster'] == kmeans_cluster]
    recommendations = normal_foods['Food'].sample(5).tolist()
    return recommendations

food_name = input("Enter the name of the food: ")
cluster, kmeans_cluster = get_cluster(food_name)

if cluster == "Food not found in the dataset":
    print(cluster)
else:
    print(f"The food belongs to Cluster: {cluster}")

    if cluster == 'Avoidable':
        recommendations = recommend_foods(kmeans_cluster)
        print("Hey, instead of this, you might want to try these foods, they are healthier!")
        for food in recommendations:
            print(f"- {food}")