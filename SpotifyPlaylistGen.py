
"""
Created on Mon Dec 10 14:47:06 2018

Description: A k-means clustering algorithm that connects with a user's Spotify acocunt
and loads the saved songs into customized playlists based on four selected features.

Requirments: Spotify library installed on device, Spotify account and dashboard app created

@author: Diego Carregha

"""

import itertools
import random
import numpy as np
import matplotlib.pyplot as plt
import spotipy
import spotipy.util
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split


## CODE PROVIDED BY SPOTIFY TO GO THROUGH AUTHORIZATION FLOW ##

# Create your own Spotify app to get the ID and secret.
# https://developer.spotify.com/dashboard/applications
CLIENT_ID = '-----' #created spotify dashboard account ID
CLIENT_SECRET = '-----'#dashboard account secret

# Personal to your Spotify username 
USERNAME = '<USERNAME>'

REDIRECT_URI = 'http://localhost:8888'
SCOPE = 'user-library-read'

# Create a Spotify client that can access a user's saved song information.
token = spotipy.util.prompt_for_user_token(USERNAME, scope=SCOPE, client_id=CLIENT_ID,
                                           client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)

sp = spotipy.Spotify(auth=token)

# END OF SPOTIFY CODE

print("Importing your songs...")
# Get the Spotify URIs of each of my saved songs.
uris = set([])
def add_uris(fetched):
    for item in fetched['items']:
        uris.add(item['track']['uri'])

results = sp.current_user_saved_tracks()
add_uris(results)
while results['next']:
    results = sp.next(results)
    add_uris(results)

# Function that returns the next n elements from the iterator. Used because
# Spotify limits how many items you can group into each of its API calls.
def grouper(n, iterable):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk

# Get the audio features of each of the URIs fetched above.
uris_to_features = {}
for group in grouper(50, uris):
    res = sp.audio_features(tracks=group)
    for item in res:
        uris_to_features[item['uri']] = item
FEATURE_VECTOR = [None]*7; 
features = 1


while features < 5:
	FEATURE_VECTOR[features-1] = input("Enter desired feature vectors (energy, valence, liveness, etc): ")
	features+=1

# Turn dict of features into vector of vlaues
def features_to_vector(item):
    return np.array([item[key] for key in FEATURE_VECTOR])

vectors = [(x[0], features_to_vector(x[1])) for x in uris_to_features.items()]

# Split into training and testing data, 20/80 split
training, testing = train_test_split(vectors, test_size = 0.20, random_state = 0)

# Arrays of test/train data vs IDs
testSongIDs = np.array([x[0] for x in testing]) 
trainSongIDs = np.array([x[0] for x in training]) 
testSongData = np.array([x[1] for x in testing]) 
trainSongData = np.array([x[1] for x in training])    
songCount = len(uris_to_features)


sum_of_squared_distances = []
K = range(1,15)
for k in K:
    km = KMeans(n_clusters=k)
    km = km.fit(trainSongData)
    sum_of_squared_distances.append(km.inertia_)
    
plt.plot(K, sum_of_squared_distances, 'bx-')
plt.xlabel('k')
plt.ylabel('Sum_of_squared_distances')
plt.title('Elbow Method for Optimal k')
plt.show()
 

# Train clusters, k = 12 based on the elbow curve produced above
kModel = KMeans(n_clusters = 12)
kModel.fit(trainSongData)

# Predict cluster of test data
assigned = kModel.predict(testSongData)

# Organize the training data into playlists based on predicted clsuters
playlist0 = []
playlist1 = []
playlist2 = []
playlist3 = []
playlist4 = []
playlist5 = []
playlist6 = []
playlist7 = []
playlist8 = []
playlist9 = []
playlist10 = []
playlist11 = []

itr = -1
for x in assigned:
    itr += 1
    addSong = trainSongIDs[itr]
    if x == 0:
        playlist0.append(addSong)
    elif x == 1:
        playlist1.append(addSong)
    elif x == 2:
        playlist2.append(addSong)
    elif x == 3:
        playlist3.append(addSong)
    elif x == 4:
        playlist3.append(addSong)
    elif x == 5:
        playlist5.append(addSong)
    elif x == 6:
        playlist6.append(addSong)
    elif x == 7:
        playlist7.append(addSong)
    elif x == 8:
        playlist8.append(addSong)
    elif x == 9:
        playlist9.append(addSong)
    elif x == 10:
        playlist10.append(addSong)
    else:
        playlist11.append(addSong)
        
# Can have user input for what playlist or random int chosen. 
# inp = input("What playlist would you like? (0 - 11) ")  
# select = int(inp)
# 
select =  random.randint(0,11)  # Randomly selects playlist
playSelect = []

if select == 0:
    playSelect = playlist0
elif select == 1:
    playSelect = playlist1
elif select == 2:
    playSelect = playlist2
elif select == 3:
    playSelect = playlist3
elif select == 4:
    playSelect = playlist4
elif select == 5:
    playSelect = playlist5
elif select == 6:
    playSelect = playlist6
elif select == 7:
    playSelect = playlist7
elif select == 8:
    playSelect = playlist8
elif select == 9:
    playSelect = playlist9
elif select == 10:
    playSelect = playlist10
elif select == 11:
    playSelect = playlist11
else:
    print("Error. Number not in range")
    
playlistName = input("Playlist successfully generated. Give it a name: ")

SCOPE2 = 'playlist-modify-public'
token = spotipy.util.prompt_for_user_token(USERNAME, scope = SCOPE2, client_id =CLIENT_ID,
                                           client_secret=CLIENT_SECRET, redirect_uri =REDIRECT_URI)
if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    playlistConfirm = sp.user_playlist_create(USERNAME, playlistName, public = True)
    results = sp.user_playlist_add_tracks(USERNAME, playlistConfirm['id'], playSelect)
    print("Your playlist has been uploaded to your Spotify account.")
else:
    print("Error. Unable to get token for", USERNAME)
