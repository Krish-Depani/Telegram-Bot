genre_names = {28: 'action', 12: 'adventure', 16: 'animation', 35: 'comedy', 80: 'crime', 99: 'documentary',
                   18: 'drama', 10751: 'family',
                   14: 'fantasy', 36: 'history', 27: 'horror', 10402: 'music', 9648: 'mystery', 10749: 'romance',
                   878: 'science fiction',
                   10770: 'tv movie', 53: 'thriller', 10752: 'war', 37: 'western', 10759: 'action & adventure',
                   10762: 'kids', 10763: 'news',
                   10764: 'reality', 10765: 'sci-fi & fantasy', 10766: 'soap', 10767: 'talk', 10768: 'war & politics'}

def genre_name(id_genre):
    return genre_names[id_genre]

def genre_id(name_genre):
    for key, value in genre_names.items():
        if name_genre in value:
            return key
    return None
