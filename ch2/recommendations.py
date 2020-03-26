from math import sqrt
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
    if len(shared_items) == 0:
        return 0

    # Add up the squares of all the distances
    sum_of_squares = np.square([prefs[p1][item] - prefs[p2][item] for item in shared_items]).sum()
    return 1 / ( 1 + sqrt(sum_of_squares) )

import ipdb; ipdb.set_trace()
print(sim_distance(critics, 'Lisa Rose', 'Gene Seymour'))
