from scipy.stats import pearsonr
def read_file(file_name):
    '''
    read the dataset from a file
    '''
    with open(file_name, 'r') as f:
        header = f.readline()
        lines = f.readlines()

    # the first colum is "blog name", so it should be removed
    col_names = header.strip().split('\t')[1:]

    row_names = []
    data = []
    for line in lines:
        row = line.strip().split('\t')
        # First column in each row is the row name
        row_names.append(row[0])
        # The rest columns are data elements
        data.append([float(v) for v in row[1:]])

    return row_names, col_names, data


def pearson_distance(v1, v2):
    '''
    calculate the Pearson correlation and return ( 1 - Pearson correlation )
    '''
    return 1 - pearsonr(v1, v2)[0]


class Bicluster:
    def __init__(
        self, 
        vec, 
        left=None, 
        right=None, 
        distance=0.0, 
        id=None
        ):

        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance


def hierarchical_clustering(rows, distance=pearson_distance):
    '''
    create hierarchical cluster
    '''
    distances = {}
    current_clust_id = -1

    clust = [Bicluster(row, id=i) for i, row in enumerate(rows)]

    while len(clust) > 1:
        closest_pair = (0, 1)
        closest_distance = distance(clust[0].vec, clust[1].vec)

        # loop through every pair looking for the smallest distance
        for i in range(len(clust)):
            for j in range(i+1, len(clust)):
                # distances is the cache of distance calculation
                if (clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id)] = distance(clust[i].vec, clust[j].vec)

                current_distance = distances[(clust[i].id, clust[j].id)]

                if current_distance < closest_distance:
                    closest_distance = current_distance
                    closest_pair = (i, j)

        # calculate the average of the two clusters to be merged
        merge_vec = [
                (clust[closest_pair[0]].vec[i] + clust[closest_pair[1]].vec[i]) / 2.0
                for i in range(len(clust[0].vec))
            ]
        # create the new cluster 
        new_cluster = Bicluster(merge_vec, left=clust[closest_pair[0]], 
                                right=clust[closest_pair[1]], distance=closest_distance, id=current_clust_id)

        # cluster ids that weren't in the original set are negative
        current_clust_id -= 1
        # should delete closet_pair[1] (>closet_pair[0]) first
        del clust[closest_pair[1]]
        del clust[closest_pair[0]]
        clust.append(new_cluster)
    
    return clust[0]


def print_clust(clust, labels=None, n=0):
    '''
    nicely print hirarchical cluster that is made by hirarchical_clustering
    '''
    # indent to make a hirarchy layout
    for i in range(n):
        print(' ', end='')
    if clust.id < 0:
       # negative id means that this is branch
       print('-')
    else:
        # positive id means that this is an endpoint
        if labels is None:
            print(clust.id)
        else:
            print(labels[clust.id])
    # now print the right and left branches
    if clust.left:
        print_clust(clust.left, labels=labels, n=n+1)
    if clust.right:
        print_clust(clust.right, labels=labels, n=n+1)


if __name__ == '__main__':
    blog_names, words, data = read_file('blogdata.txt')
    clust = hierarchical_clustering(data)
    print_clust(clust, labels=blog_names)
    
