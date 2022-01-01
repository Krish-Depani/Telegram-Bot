# Including all the necessary libraries.
import requests.exceptions
import telebot
import os
from pexels_api import API
from dotenv import load_dotenv
from tmdbv3api import TMDb, Movie, TV, Discover
import genre

# Getting API keys for the respective APIs.
load_dotenv()
telegram_API_KEY = os.getenv("telegram_api_key")
pexel_API_KEY = os.getenv("pexel_api_key")
moviedb_API_KEY = os.getenv("moviedb_api_key")
# Creating objects with the help of API keys.
bot = telebot.TeleBot(telegram_API_KEY)
pexel = API(pexel_API_KEY)
tmdb = TMDb()
tmdb.api_key = moviedb_API_KEY
movies = Movie()
tvseries = TV()
discover = Discover()


@bot.message_handler(commands=["start"])
# This function is invoked when start command is entered and displays the welcome message.
def greet(message):
    msg = """Welcome!!\nClick /help for info"""
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['help'])
# This function is invoked with help command and lists all the available commands/orders.
def help(message):
    msg = """Commands :\n\nwallpapers -> for hd wallpapers\n\nmovie info -> To get info of movies\n\ntvseries info -> To get info of tvseries\n
movie recommendations -> to get recommendations of a particular movie\n\ntvseries recommendations -> to get recommendations of a particular tvseries\n
popular movies -> to get popular movies of a particular genre\n\npopular tvseries -> to get popular tvseries of a particular genre\n
get trailer -> to get trailer as youtube link\n\n/getgenres -> to get all available genre names"""
    bot.send_message(message.chat.id, msg)


@bot.message_handler(regexp=r'Wallpapers')
@bot.message_handler(regexp=r'wallpapers')
@bot.message_handler(regexp=r'Wallpaper')
@bot.message_handler(regexp=r'wallpaper')
# This function handles the wallpaper command and identifies type of wallpaper.
def handle_text(message):
    cid = message.chat.id
    type_of_image = bot.send_message(cid, "Wallpaper for Phone or Desktop?")
    # type is send to type_of_wallpaper ().
    bot.register_next_step_handler(type_of_image, type_of_wallpaper)


# This function calls the respective function according to type.
def type_of_wallpaper(message):
    cid = message.chat.id
    usertxt = message.text
    if usertxt in ['Phone', 'phone', 'PHONE']:
        usr_wallpaper = bot.send_message(cid, 'Enter the name and number of images(seprated by comma)')
        # if type is phone then calling the phone_wallpaper_sender ().
        bot.register_next_step_handler(usr_wallpaper, phone_wallpaper_sender)
    elif usertxt in ['Desktop', 'desktop', 'DESKTOP']:
        usr_wallpaper = bot.send_message(cid, 'Enter the name and number of images(seprated by comma)')
        # if type is desktop then calling the desktop_wallpaper_sender ().
        bot.register_next_step_handler(usr_wallpaper, desktop_wallpaper_sender)
    else:
        bot.send_message(cid, "Enter the choice properly")
        handle_text(message)
        return


# This function sends desktop type wallpapers.
def desktop_wallpaper_sender(message):
    cid = message.chat.id
    usertxt = message.text
    usertxt = usertxt.split(",")
    try:
        img_name = usertxt[0]
        img_no = int(usertxt[1])
    except (IndexError, ValueError):
        bot.send_message(cid, "Enter the name and number of images properly(seprated by comma)\nExample : waterfall, 3")
        message.text = 'Desktop'
        type_of_wallpaper(message)
        return
    x = pexel.search(img_name, page=1, results_per_page=img_no)
    if x['total_results'] == 0:
        bot.send_message(cid, "No wallpapers found\nTry with another wallpaper name")
        message.text = 'Desktop'
        type_of_wallpaper(message)
        return
    photos = pexel.get_entries()
    for photo in photos:
        bot.send_photo(cid, photo.landscape)


# This function sends phone type wallpapers.
def phone_wallpaper_sender(message):
    cid = message.chat.id
    usertxt = message.text
    usertxt = usertxt.split(",")
    try:
        img_name = usertxt[0]
        img_no = int(usertxt[1])
    except (IndexError, ValueError):
        bot.send_message(cid, "Enter the name and number of images properly(seprated by comma)\nExample : waterfall, 3")
        message.text = 'Phone'
        type_of_wallpaper(message)
        return
    x = pexel.search(img_name, page=1, results_per_page=img_no)
    if x['total_results'] == 0:
        bot.send_message(cid, "No wallpapers found\nTry with another wallpaper name")
        message.text = 'Phone'
        type_of_wallpaper(message)
        return
    photos = pexel.get_entries()
    for photo in photos:
        bot.send_photo(cid, photo.portrait)


@bot.message_handler(regexp=r'Movie info')
@bot.message_handler(regexp=r'movie info')
# This function handles movie info command and gets the info of the movie.
def movies_info(message):
    cid = message.chat.id
    movie = bot.send_message(cid, "Enter the movie name")
    # passing movie name to movie_sender ().
    bot.register_next_step_handler(movie, movie_sender)


# This function sends the movie info with the help of name it got.
def movie_sender(message):
    cid = message.chat.id
    try:
        movie_info = movies.search(message.text)
    except requests.exceptions.ConnectionError:
        bot.send_message(cid, "Connection interrupted")
        movies_info(message)
        return
    if not movie_info:
        bot.send_message(cid, "No such Movie\nEnter the name properly")
        movies_info(message)
        return
    cast = movies.credits(movie_info[0]['id'])
    video = movies.videos(movie_info[0]['id'])
    video_key = None
    actors = []
    genres = []
    for i in movie_info[0]['genre_ids']:
        genres.append(genre.genre_name(i))
    j = 0
    while j < 5:
        try:
            actors.append(cast['cast'][j]['name'])
        except IndexError:
            break
        j += 1
    for k in video:
        try:
            if k['type'] in ['Trailer']:
                video_key = k['key']
                break
            elif k['type'] in ['Teaser']:
                video_key = k['key']
                continue
        except IndexError:
            break
    if movie_info[0]["poster_path"] is None:
        bot.send_message(cid, "Poster not available")
    else:
        bot.send_photo(cid, f'https://image.tmdb.org/t/p/w500{movie_info[0]["poster_path"]}')
    if video_key is None:
        bot.send_message(cid, "Trailer not available")
    else:
        bot.send_message(cid, f'Trailer\nhttps://www.youtube.com/watch?v={video_key}')
    bot.send_message(cid, f'Title : {movie_info[0]["title"]}\n\nRelease date : {movie_info[0]["release_date"]}\n\nCast : {", ".join(actors)}\n\nGenre : {", ".join(genres)}\n\nRatings : {movie_info[0]["vote_average"]}\n\nOverview : {movie_info[0]["overview"]}')


@bot.message_handler(regexp=r'Tv series info')
@bot.message_handler(regexp=r'TV series info')
@bot.message_handler(regexp=r'Tvseries info')
@bot.message_handler(regexp=r'tvseries info')
# This function handles tvseries info command and gets the info of the tvseries.
def tv_series_info(message):
    cid = message.chat.id
    tv = bot.send_message(cid, "Enter the TV series name")
    # passing tvseries name to tvseries_sender ().
    bot.register_next_step_handler(tv, tvseries_sender)


# This function sends the tvseries info with the help of name it got.
def tvseries_sender(message):
    cid = message.chat.id
    try:
        tvseries_info = tvseries.search(message.text)
    except requests.exceptions.ConnectionError:
        bot.send_message(cid, "Connection interrupted")
        tv_series_info(message)
        return
    if not tvseries_info:
        bot.send_message(cid, "No such TV series\nEnter the name properly")
        tv_series_info(message)
        return
    details = tvseries.details(tvseries_info[0]['id'])
    video = tvseries.videos(tvseries_info[0]['id'])
    video_key = None
    actors = []
    genres = []
    for i in tvseries_info[0]['genre_ids']:
        genres.append(genre.genre_name(i))
    j = 0
    while j < 5:
        try:
            actors.append(details['credits']['cast'][j]['name'])
        except IndexError:
            break
        j += 1
    for k in video:
        try:
            if k['type'] in ['Trailer']:
                video_key = k['key']
                break
            elif k['type'] in ['Teaser']:
                video_key = k['key']
                continue
        except IndexError:
            break
    if tvseries_info[0]["poster_path"] is None:
        bot.send_message(cid, "Poster not available")
    else:
        bot.send_photo(cid, f'https://image.tmdb.org/t/p/w500{tvseries_info[0]["poster_path"]}')
    if video_key is None:
        bot.send_message(cid, "Trailer not available")
    else:
        bot.send_message(cid, f'Trailer\nhttps://www.youtube.com/watch?v={video_key}')
    bot.send_message(cid, f'Title : {tvseries_info[0]["name"]}\n\nRelease date : {tvseries_info[0]["first_air_date"]}\n\nCast : {", ".join(actors)}\n\nGenre : {", ".join(genres)}\n\nRatings : {tvseries_info[0]["vote_average"]}\n\nNumber of seasons : {details["number_of_seasons"]}\n\nNumber of episodes : {details["number_of_episodes"]}\n\nOverview : {tvseries_info[0]["overview"]}')


@bot.message_handler(regexp=r'movie recommendations')
@bot.message_handler(regexp=r'Movie recommendations')
# This function handles movie recommendations command and takes input from user.
def movies_recommendation(message):
    cid = message.chat.id
    movie = bot.send_message(cid, "Enter the name of movie and number of recommendations(Seprated by comma)")
    # Passing name of movie and number of recommendations to movies_recommendation_sender ().
    bot.register_next_step_handler(movie, movies_recommendation_sender)


# This function sends the specified recommendations in previous function.
def movies_recommendation_sender(message):
    cid = message.chat.id
    usertxt = message.text
    usertxt = usertxt.split(",")
    try:
        no_of_movie = int(usertxt[1])
        movie_name = usertxt[0]
    except (IndexError, ValueError):
        bot.send_message(cid, "Enter the name and number of movies properly\n\nExample : Avengers, 4")
        movies_recommendation(message)
        return
    try:
        movie = movies.search(movie_name)
    except requests.exceptions.ConnectionError:
        bot.send_message(cid, "Connection interrupted")
        movies_recommendation(message)
        return
    if not movie:
        bot.send_message(cid, "No such Movie\nEnter the name properly")
        return
    recommendations = movies.recommendations(movie[0]['id'])
    if not recommendations:
        bot.send_message(cid, "No recommendations available for this movie")
        return
    j = 0
    while j < no_of_movie:
        try:
            if recommendations[j]["poster_path"] is None:
                bot.send_message(cid, "Poster not available")
            else:
                bot.send_photo(cid, f'https://image.tmdb.org/t/p/w500{recommendations[j]["poster_path"]}')
            bot.send_message(cid, f'Title : {recommendations[j]["title"]}\n\nRatings : {recommendations[j]["vote_average"]}\n\nOverview : {recommendations[j]["overview"]}')
        except IndexError:
            break
        j += 1


@bot.message_handler(regexp=r'Tvseries recommendations')
@bot.message_handler(regexp=r'tvseries recommendations')
# This function handles tvseries recommendations command and takes input from user.
def tvseries_recommendation(message):
    cid = message.chat.id
    tv = bot.send_message(cid, "Enter the name of Tvseries and number of recommendations(Seprated by comma)")
    # Passing name of tvseries and number of recommendations to tv_series_recommendation_sender ().
    bot.register_next_step_handler(tv, tv_series_recommendation_sender)


# This function sends the specified recommendations in previous function.
def tv_series_recommendation_sender(message):
    cid = message.chat.id
    usertxt = message.text
    usertxt = usertxt.split(",")
    try:
        tv_name = usertxt[0]
        tv_no = int(usertxt[1])
    except (IndexError, ValueError):
        bot.send_message(cid, "Enter the name and number of tvseries properly\n\nExample : Breaking bad, 4")
        tvseries_recommendation(message)
        return
    try:
        tv = tvseries.search(tv_name)
    except requests.exceptions.ConnectionError:
        bot.send_message(cid, "Connection interrupted")
        tvseries_recommendation(message)
        return
    if not tv:
        bot.send_message(cid, "No such TV series\nEnter the name properly")
        return
    recommendations = tvseries.recommendations(tv[0]['id'])
    if not recommendations:
        bot.send_message(cid, "No recommendations available for this tvseries")
        return
    j = 0
    while j < tv_no:
        try:
            details = tvseries.details(recommendations[j]['id'])
            if recommendations[j]["poster_path"] is None:
                bot.send_message(cid, "Poster not available")
            else:
                bot.send_photo(cid, f'https://image.tmdb.org/t/p/w500{recommendations[j]["poster_path"]}')
            bot.send_message(cid,
                             f'Title : {recommendations[j]["name"]}\n\nRatings : {recommendations[j]["vote_average"]}\n\nNumber of Seasons : {details["number_of_seasons"]}\n\nNumber of Episodes : {details["number_of_episodes"]}\n\nOverview : {recommendations[j]["overview"]}')
        except IndexError:
            break
        j += 1


@bot.message_handler(regexp=r'popular movies')
@bot.message_handler(regexp=r'Popular movies')
# This function handles popular movies command and accepts the genre as input.
def popular_movies(message):
    cid = message.chat.id
    movie = bot.send_message(cid, "Enter the genre")
    # Genre is passed to popular_movie_sender ().
    bot.register_next_step_handler(movie, popular_movie_sender)


# This function sends all the popular movies based on genre passed.
def popular_movie_sender(message):
    cid = message.chat.id
    usertxt = message.text
    genre_id = genre.genre_id(usertxt.lower())
    if genre_id is None:
        bot.send_message(cid, "Invalid genre name")
        popular_movies(message)
        return
    try:
        pop_movies = discover.discover_movies({'with_genres': genre_id, 'sort_by': 'popularity.desc'})
    except requests.exceptions.ConnectionError:
        bot.send_message(cid, "Connection interrupted")
        popular_movies(message)
        return
    if not pop_movies:
        bot.send_message(cid, "No popular movies available for this genre")
        return
    for j in pop_movies:
        if j["poster_path"] is None:
            bot.send_message(cid, "Poster not available")
        else:
            bot.send_photo(cid, f'https://image.tmdb.org/t/p/w500{j["poster_path"]}')
        bot.send_message(cid, f'Title : {j["title"]}\n\nRatings : {j["vote_average"]}\n\nOverview : {j["overview"]}')


@bot.message_handler(regexp=r'popular tvseries')
@bot.message_handler(regexp=r'Popular Tvseries')
# This function handles popular tvseries command and accepts the genre as input.
def popular_tvseries(message):
    cid = message.chat.id
    tv = bot.send_message(cid, "Enter the genre")
    # Genre is passed to popular_tvseries_sender ().
    bot.register_next_step_handler(tv, popular_tvseries_sender)


# This function sends all the popular tvseries based on genre passed.
def popular_tvseries_sender(message):
    cid = message.chat.id
    usertxt = message.text
    genre_id = genre.genre_id(usertxt.lower())
    if genre_id is None:
        bot.send_message(cid, "Invalid genre name")
        popular_tvseries(message)
        return
    try:
        pop_tv = discover.discover_tv_shows({'with_genres': genre_id, 'sort_by': 'popularity.desc'})
    except requests.exceptions.ConnectionError:
        bot.send_message(cid, "Connection interrupted")
        popular_tvseries(message)
        return
    if not pop_tv:
        bot.send_message(cid, "No popular tv series available for this genre")
    for j in pop_tv:
        details = tvseries.details(j['id'])
        if j["poster_path"] is None:
            bot.send_message(cid, "Poster not available")
        else:
            bot.send_photo(cid, f'https://image.tmdb.org/t/p/w500{j["poster_path"]}')
        bot.send_message(cid, f'Title : {j["name"]}\n\nRatings : {j["vote_average"]}\n\nNumber of Seasons : {details["number_of_seasons"]}\n\nNumber of Episodes : {details["number_of_episodes"]}\n\nOverview : {j["overview"]}')


@bot.message_handler(commands='getgenres')
# This function is invoked on getgenres command and displays all the available genres.
def genre_sender(message):
    cid = message.chat.id
    genre_names = [list(genre.genre_names.values())]
    genre_names = genre_names[0]
    bot.send_message(cid, f'Genres\n\n{", ".join(genre_names)}')


@bot.message_handler(regexp=r'get trailer')
@bot.message_handler(regexp=r'Get trailer')
# This function handles the get trailer command and identifies type of trailer.
def get_trailer(message):
    cid = message.chat.id
    m_or_t = bot.send_message(cid, "Trailer for movie or tvseries?")
    # Passes the type to trailer_identifier ().
    bot.register_next_step_handler(m_or_t, trailer_identifier)


# This function calls the respective function according to the type of trailer.
def trailer_identifier(message):
    cid = message.chat.id
    usertxt = message.text
    if usertxt in ['tvseries', 'Tvseries', 'Tv series', 'tv series']:
        tv_show = bot.send_message(cid, 'Enter the name of tvseries')
        bot.register_next_step_handler(tv_show, tv_trailer_sender)
    elif usertxt in ['movie', 'Movie']:
        movie = bot.send_message(cid, 'Enter the name of movie')
        bot.register_next_step_handler(movie, movie_trailer_sender)
    else:
        bot.send_message(cid, "Enter the choice properly")
        get_trailer(message)
        return


# This function sends trailer of specified tvseries.
def tv_trailer_sender(message):
    cid = message.chat.id
    usertxt = message.text
    try:
        tv_show = tvseries.search(usertxt)
    except requests.exceptions.ConnectionError:
        bot.send_message(cid, "Connection interrupted")
        message.text = 'tvseries'
        trailer_identifier(message)
        return
    if not tv_show:
        bot.send_message(cid, "No such tvseries\nEnter the name properly")
        message.text = 'tvseries'
        trailer_identifier(message)
        return
    trailer = tvseries.videos(tv_show[0]['id'])
    trailer_key = None
    for k in trailer:
        try:
            if k['type'] in ['Trailer']:
                trailer_key = k['key']
                break
            elif k['type'] in ['Teaser']:
                trailer_key = k['key']
                continue
        except IndexError:
            break
    if trailer_key is None:
        bot.send_message(cid, "Trailer not available")
    else:
        bot.send_message(cid, f'Trailer\nhttps://www.youtube.com/watch?v={trailer_key}')


# This function sends trailer of specified movie.
def movie_trailer_sender(message):
    cid = message.chat.id
    usertxt = message.text
    try:
        movie = movies.search(usertxt)
    except requests.exceptions.ConnectionError:
        bot.send_message(cid, "Connection interrupted")
        message.text = 'movie'
        trailer_identifier(message)
        return
    if not movie:
        bot.send_message(cid, "No such movie\nEnter the name properly")
        message.text = 'movie'
        trailer_identifier(message)
        return
    trailer = movies.videos(movie[0]['id'])
    trailer_key = None
    for k in trailer:
        try:
            if k['type'] in ['Trailer']:
                trailer_key = k['key']
                break
            elif k['type'] in ['Teaser']:
                trailer_key = k['key']
                continue
        except IndexError:
            break
    if trailer_key is None:
        bot.send_message(cid, "Trailer not available")
    else:
        bot.send_message(cid, f'Trailer\nhttps://www.youtube.com/watch?v={trailer_key}')


bot.polling(none_stop=True)