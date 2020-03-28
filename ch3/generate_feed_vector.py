from collections import defaultdict
import feedparser
import re
from urllib.error import URLError


def generate_word_counts(url):
    '''
    returns titles and dictionary of word counts for an RSS feed
    '''
    # parse the feed
    try:
        parse_result = feedparser.parse(url)
    except URLError:
        return '', {}
    words_count = defaultdict(int)
    
    # loop over all entries
    for entry in parse_result.entries:
        if 'summary' in entry:
            summary = entry.summary
        else:
            summary = entry.description

        # extract a list of words
        words = get_words(entry.title + ' ' + summary)
        for word in words:
            words_count[word] += 1
            
    if not hasattr(parse_result.feed, 'title'):
        return '', words_count

    return parse_result.feed.title, words_count


def get_words(html):
    # remove all HTML tags
    txt_no_tags = re.compile(r'<[^>]+>').sub('', html)

    # split words by all non-alphabetical characters
    words = re.compile(r'[^A-Z^a-z]+').split(txt_no_tags)

    return [word.lower() for word in words if word != '']


word_counts = {}
overall_count = defaultdict(int)

# Loop over the list of feed urls and count words that appear in websites
with open('feedlist.txt', 'r') as feed_urls:
    for feed_url in feed_urls:
        title, word_count = generate_word_counts(feed_url)
        if not title:
            continue

        word_counts[title] = word_count

        for word, count in word_count.items():
            # do not add words that appear only once
            if count > 1:
                overall_count[word] += 1
    
# create a list of words without ones that appear too frequently or rarely.
words_list = []
for word, count in overall_count.items():
    frac = count / len(feedlist)
    if frac > 0.1 and frac < 0.5:
        words_list.append(word)

# create the dataset
with open("blogdata.txt", "w") as blog_dataset:
    blog_dataset.write('Blog')
    for word in words_list:
        blog_dataset.write(f"\t{word}")
    blog_dataset.write("\n")

    for blog, word_count in word_counts.items():
        blog_dataset.write(blog)
        for word in words_list:
            if word in word_count:
                blog_dataset.write(f"\t{word_count[word]}")
            else:
                blog_dataset.write("\t0")
        blog_dataset.write("\n")

