import re
from math import sqrt
from collections import defaultdict
import numpy as np

# A dictionary of movie critics and their ratings of a small set of movies
critics = {
    'Lisa Rose': {
        'Lady in the Water': 2.5,
        'Snakes on a Plane': 3.5,
        'Just My Luck': 3.0,
        'Superman Returns': 3.5,
        'You, Me and Dupree': 2.5,
        'The Night Listener': 3.0,
    },
    'Gene Seymour': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 3.5,
        'Just My Luck': 1.5,
        'Superman Returns': 5.0,
        'The Night Listener': 3.0,
        'You, Me and Dupree': 3.5,
    },
    'Michael Phillips': {
        'Lady in the Water': 2.5,
        'Snakes on a Plane': 3.0,
        'Superman Returns': 3.5,
        'The Night Listener': 4.0,
    },
    'Claudia Puig': {
        'Snakes on a Plane': 3.5,
        'Just My Luck': 3.0,
        'The Night Listener': 4.5,
        'Superman Returns': 4.0,
        'You, Me and Dupree': 2.5,
    },
    'Mick LaSalle': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 4.0,
        'Just My Luck': 2.0,
        'Superman Returns': 3.0,
        'The Night Listener': 3.0,
        'You, Me and Dupree': 2.0,
    },
    'Jack Matthews': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 4.0,
        'The Night Listener': 3.0,
        'Superman Returns': 5.0,
        'You, Me and Dupree': 3.5,
    },
    'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0,
             'Superman Returns': 4.0},
}


def get_shared_items(prefs, p1, p2):
    '''
    Get the list of items that both person1 and person2 specified
    '''

    p1_rated_items = set(prefs[p1].keys())
    p2_rated_items = set(prefs[p2].keys())
    return p1_rated_items & p2_rated_items

def sim_distance(prefs, p1, p2):
    '''
    Return a distance-based similarity score for persona1, person2
    '''

    # if they do not have common items, return 0
    shared_items = get_shared_items(prefs, p1, p2)
    if not shared_items:
        return 0

    # Add up the squares of all the distances
    sum_of_squares = np.square([prefs[p1][item] - prefs[p2][item] for item in shared_items]).sum()
    return 1 / ( 1 + sqrt(sum_of_squares) )


def calc_similarity_pearson(prefs, p1, p2):
    '''
    Return the Pearson correlation coefficient for person1 and person2
    '''

    # if they do not have common items, return 0
    shared_items = get_shared_items(prefs, p1, p2)
    if not shared_items:
        return 0
    p1_shared_ratings = np.array([prefs[p1][item] for item in shared_items])
    p2_shared_ratings = np.array([prefs[p2][item] for item in shared_items])
    
    # Strictly spaeking, average ratings should be calculated with shared items only, but we calculate average ratings with all of the items each person rated
    p1_ave_rating = np.fromiter(prefs[p1].values(), dtype=np.float32).mean()
    p2_ave_rating = np.fromiter(prefs[p2].values(), dtype=np.float32).mean()


    # calculate each of standard deviation of the ratings 
    p1_std_rate = np.sqrt((( p1_shared_ratings - p1_ave_rating ) ** 2 ).sum())
    p2_std_rate = np.sqrt((( p2_shared_ratings - p2_ave_rating ) ** 2 ).sum())

    corr = ((p1_shared_ratings - p1_ave_rating) * (p2_shared_ratings - p2_ave_rating)).sum()

    return corr / ( p1_std_rate * p2_std_rate )

def top_matches(prefs, person, n=5, calc_similarity=calc_similarity_pearson):
    '''
    Return the best matches for person from the prefs dictionary
    Number of results and similarity function are optional params
    '''
    scores = [(calc_similarity(prefs, person, other), other) for other in prefs.keys() if other != person]

    # sort the list so the highest scors appear at the top
    scores.sort(key = lambda x : x[0], reverse=True)
    return scores[:n]


def get_recommendations(prefs, person, calc_similarity=calc_similarity_pearson):
    '''
    Gets recommendations for a person by using a weighted average of every other users' rankings
    '''
    weighted_rating_list = defaultdict(float)
    total_similarity = defaultdict(float)

    for other in prefs:
        # don't compare me to myself
        if other == person:
            continue

        # ignores zero or negative similarity
        similarity = calc_similarity(prefs, person, other)
        if similarity <= 0:
            continue

        for item in prefs[other]:
            # ignores items that I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
               weighted_rating_list[item] += prefs[other][item] * similarity
               total_similarity[item] += similarity

    rankings = [ (total_score / total_similarity[item], item) for item, total_score in weighted_rating_list.items() ]
    rankings.sort(reverse=True)
    return rankings


def transformPrefs(prefs):
    '''
    transform user-based preference dictionary to item-based preference dictionary
    '''
    results = defaultdict(dict)
    for person in prefs.keys():
        for item in prefs[person]:
            # flip item and person
            results[item][person] = prefs[person][item]

    return results


def create_similar_items_list(prefs, n=10):
    '''
    Create a dictionary of items showing which otehr items they are the most similar to
    '''
    similar_item_dataset = {}

    # invert the preference matrix to be item-centric
    item_prefs = transformPrefs(prefs)
    item_count = 0
    for item in item_prefs.keys():
        item_count += 1
        if ( item_count % 100 == 0 ):
            print(f"Progress: {item_count} / {len(item_prefs)}")

        # find items similar to this one
        list_similar_items = top_matches(item_prefs, item, n=n, calc_similarity=sim_distance)
        similar_item_dataset[item] = list_similar_items
    
    return similar_item_dataset


def get_recommended_items(prefs, list_similar_items, user):
    '''
    get the list of item-Based recommended items
    '''
    user_ratings = prefs[user]
    sum_similarities = defaultdict(float)
    scores = defaultdict(float)

    # Loop over items rated by this user
    for (rated_item, rating) in user_ratings.items():

        # Loop over items similar to this item
        for (similarity, similar_item) in list_similar_items[rated_item]:

            # ignore items the user has already rated
            if similar_item in user_ratings:
                continue

            # rate the similar item weighted by similarity 
            scores[similar_item] += similarity * rating
            
            # sum of all the similarity
            sum_similarities[similar_item] += similarity
    
    rankings = [(score / sum_similarities[item], item) for item, score in scores.items()]
    rankings.sort(reverse=True)
    return rankings


def load_movie_lens(path='./ml-latest-small'):
    '''
    load the movie lens dataset
    '''
    # get movie titles
    movies = {}
    with open(f"{path}/movies.csv", "r") as f:
        # If a movie title includes a comma, it is double-quoted
        # So, in this case, find a movie title using regular expression
        quoted = re.compile('"([^"]*)"')
        for line in f:
            movie_title = quoted.findall(line)
            if movie_title:
                # the returned type from the regular expression is a list, so take the first value
                movie_title = movie_title[0]
                movie_id = line.split(',')[0]
            else:
                (movie_id, movie_title) = line.split(',')[0:2]
            movies[movie_id] = movie_title
    
    # load data
    prefs = defaultdict(dict)
    with open(f"{path}/ratings.csv", "r") as f:
        f.readline()
        for line in f:
            user_id, movie_id, rating, _ = line.split(',')
            prefs[user_id][movies[movie_id]] = float(rating)
    
    return prefs

from pprint import pprint
movie_lens = load_movie_lens()
similar_item_list = create_similar_items_list(movie_lens)
recommended_items = get_recommended_items(movie_lens, similar_item_list, '98')
pprint(recommended_items)
