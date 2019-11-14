
"""

Description: A k-means clustering algorithm that connects with a user's Spotify acocunt
and loads the saved songs into customized playlists based on six selected features.
The value for k may change depending on the size of your music library, make sure to look
at the elbow curve to find your optimal value and make changes accordingly. 

Requirments: Spotify account and developer dashboard app created



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

# Create your own Spotify developer account to get the ID and secret.
# https://developer.spotify.com/dashboard/applications
CLIENT_ID = 'd6d8730653444858a682bd7cf584f761' # Dreated spotify dashboard account ID
CLIENT_SECRET = 'a55b17fdfacc4705b7135e071511b59f'# Dashboard account secret

# Personal to your Spotify username 
USERNAME = 'carregha2'

REDIRECT_URI = 'http://localhost:8888'
SCOPE = 'user-library-read'

# Create a Spotify client that can access a user's saved song information.
token = spotipy.util.prompt_for_user_token(USERNAME, scope=SCOPE, client_id=CLIENT_ID,
                                           client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)

sp = spotipy.Spotify(auth=token)

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
FEATURE_VECTOR = [None]*3; 
features = 1


while features < 4:
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
 

# Train clusters, k = 5 based on the elbow curve produced above
kModel = KMeans(n_clusters = 5)
kModel.fit(trainSongData)
#trainLabels = kModel.labels_
#predict cluster of test data
assigned = kModel.predict(testSongData)

# Organize the training data into playlists based on predicted clsuters (5 clusters so 5 playlists)
playlist0 = []
playlist1 = []
playlist2 = []
playlist3 = []
playlist4 = []

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
        playlist4.append(addSong)
        
# Can have user input for what playlist or random int chosen
# Currently there is no reasoning for which number is assigned to which playlist
#
# Inp = input("What playlist would you like? (0 - 4) ")  
# select = int(inp)
select =  random.randint(0,4)  
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
