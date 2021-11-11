# ====================== LIBRARY SETUP ====================== #
# API READER SETUP
from googleapiclient.discovery import build #pip install google-api-python-client
#from urllib.request import Request, urlopen #공공데이터 API
#from urllib.parse import urlencode, quote_plus, unquote #공공데이터 API
from pandas import json_normalize
#import json #공공데이터 API
#import requests #XML DECODING & 공공데이터 API
#import xmltodict ##공공데이터 API
# DIRECTORY SETUP
import os
# PICKLE SETUP
import pickle
# LOG/COLUMN SETUP
import pandas as pd
from datetime import datetime, date
import calendar
#from tabulate import tabulate #Future Markdown
# GOOGLE SETUP
import google.cloud.secretmanager as secretmanager #pip install google-cloud-secret-manager
import mysql.connector #pip install mysql-connector-python #Private IP
import sqlalchemy #pip install cloud-sql-python-connector[pymysql] #SOCKET

# ====================== FUNCTION SETUP ====================== #
def secret_manager_setup():
    # GOOGLE SECRET MANAGER
    project_id = "youtubeapi-314206"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/youtubeapi-314206-bf48e1ce8e42.json"
    client = secretmanager.SecretManagerServiceClient()
    return project_id, client

def get_secrets(secret_request, project_id, client):
    name = f"projects/{project_id}/secrets/{secret_request}/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

def keys():
    # GOOGLE SECRET MANAGER
    project_id, client = secret_manager_setup()
    # GCP CLOUD ENGINE
    connection_name = get_secrets("connection_name", project_id, client)
    query_string = dict({"unix_socket": "/cloudsql/{}".format(connection_name)})
    db_name = get_secrets("db_name", project_id, client)
    db_user = get_secrets("db_user", project_id, client)
    db_password = get_secrets("db_password", project_id, client)
    driver_name = 'mysql+pymysql'
    # GCP CLOUD PUBLIC IP
    public_ip = get_secrets("public_ip", project_id, client)
    # YOUTUBE API SERVICE KEY
    service_key = get_secrets("service_key", project_id, client)
    return query_string, db_name, db_user, db_password, driver_name, public_ip, service_key

# PICKLE SETUP
def picke_replace(name, file):
    # Create pickle directory path if it does not exist
    try:
        if not os.path.exists('Pickle/'):
            try:
                os.makedirs('Pickle')
            except FileExistsError:
                pass
    except Exception as e:
        print('Failed to create directory (Pickle/..) ' + name.upper() + e.__str__())
    else:
        print('Successfully created directory (Pickle/..) ' + name.upper())
    # Create pickle file if the file is not existing (If the file exist, then write it again)
    try:
        if os.path.exists('Pickle/' + name + '.pkl'):
            with open('Pickle/' + name + '.pkl', 'wb') as f:
                pickle.dump(file, f)
        else:
            file.to_pickle('Pickle/' + name + '.pkl')
    except Exception as e:
        print('Failed to export(.pkl) ' + name.upper() + e.__str__())
    else:
        print('Successfully export(.pkl) ' + name.upper())

def read_pickle(file_name: str) -> pd.DataFrame:
    return pd.read_pickle('Pickle/' + file_name)

# ==================== RETRIEVING DATA FROM GOOGLE CLOUD SQL =================== #
def gcp_sql_connection():

    # ======================== GOOGLE SECRET Reading ========================= #
    query_string, db_name, db_user, db_password, driver_name, service_key = keys()
    # ======================================================================== #

    # ============================ GCP Connection ============================ #
    # Create engine
    db = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername=driver_name,
            username=db_user,
            password=db_password,
            database=db_name,
            query=query_string,
        ),
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,
        pool_recycle=1800
    )
    # Query
    query = ("SELECT * FROM youtube_daily_chart")
    # Connect & Execute
    try:
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            df = pd.DataFrame(cursor.fetchall())
            df.columns = [['run_date', 'run_time', 'day', 'video_title', 'video_id', 'channel_title', 'channel_id', 'published_at', 'category_id',
                          'view_count', 'like_count', 'dislike_count', 'favorite_count','comment_count', 'for_kids', 'wiki_category', 'reg_category']]
        cursor.close()
    except Exception as e:
        return 'Error: {}'.format(str(e))
    return df

def gcp_sql_ip_connection():

    # ======================== GOOGLE SECRET Reading ========================= #
    query_string, db_name, db_user, db_password, driver_name, public_ip, service_key = keys()
    # ======================================================================== #

    # ============================ GCP Connection ============================ #
    # Create engine
    cnx = mysql.connector.connect(user=db_user, password=db_password, host=public_ip, database=db_name)
    cursor = cnx.cursor()
    # Query
    query = ("SELECT * FROM youtube_daily_chart")
    # Connect & Execute
    cursor.execute(query)
    df = pd.DataFrame(cursor.fetchall())
    df.columns = [['run_date', 'run_time', 'day', 'video_title', 'video_id', 'channel_title', 'channel_id', 'published_at',
                   'category_id', 'view_count', 'like_count', 'dislike_count', 'favorite_count', 'comment_count', 'for_kids',
                   'wiki_category', 'reg_category']]
    return df
# ====================== RETRIEVING DATA FROM YOUTUBE API ====================== #

def api_youtube_popular(name, max_result):

    # ====================== Setup ====================== #
    pd.options.mode.chained_assignment = None  # Off warning messages, default='warn'
    starttime = datetime.now()
    print(starttime)
    dictionary = {0: 'wiki_category'}
    dictionary_list = list(dictionary.values())
    pickle_name = name


    # ======================== GOOGLE SECRET Reading ========================= #
    query_string, db_name, db_user, db_password, driver_name, service_key = keys()
    youtube = build('youtube', 'v3', developerKey=service_key)
    # ======================================================================== #

    # ====================== Retrieving API and store in DF  ====================== #
    try:
        # YOUTUBE_VIDEO_LIST
        res_popular = youtube.videos().list(part=['snippet', 'statistics', 'status', 'topicDetails'],
                                            chart='mostPopular',
                                            maxResults=int(max_result), regionCode='KR').execute()
        df_popular = json_normalize(res_popular['items'])
        print('Videos API Connection has been successfully completed')

        # YOUTUBE_VIDEO_CATEGORY
        res_videocategory = youtube.videoCategories().list(part='snippet', regionCode='KR').execute()
        df_videocategory = json_normalize(res_videocategory['items'])
        df_videocategory = df_videocategory[['id', 'snippet.title']]
        print('VideoCategories API Connection has been successfully completed')
    except:
        print(name.upper() + ' has failed to open API Connection')

    # ====================== YOUTUBE_VIDEO_LIST : Data Mapping  ====================== #
    # Select Columns
    df_popular = df_popular[
        ['snippet.title', 'id', 'snippet.channelTitle', 'snippet.channelId', 'snippet.publishedAt',
         'snippet.categoryId',  # video().list(part='snippet')
         'statistics.viewCount', 'statistics.likeCount', 'statistics.dislikeCount', 'statistics.favoriteCount',
         'statistics.commentCount',  # video().list(part='statistics')
         'topicDetails.topicCategories',  # video().list(part='topicDetails')
         'status.madeForKids']]

    # Rename Columns
    df_popular.rename(columns={'snippet.title': 'video_title',
                               'id': 'video_id',
                               'snippet.channelTitle': 'channel_title',
                               'snippet.channelId': 'channel_id',
                               'snippet.publishedAt': 'published_at',
                               'snippet.categoryId': 'category_id',
                               'statistics.viewCount': 'view_count',
                               'statistics.likeCount': 'like_count',
                               'statistics.dislikeCount': 'dislike_count',
                               'statistics.favoriteCount': 'favorite_count',
                               'statistics.commentCount': 'comment_count',
                               'topicDetails.topicCategories': 'topic_categories',
                               'status.madeForKids': 'for_kids',
                               }, inplace=True)

    # Reset Index
    df_popular = df_popular.reset_index(drop=True)

    # Split TopicCategories URL
    catrgory_split = df_popular['topic_categories']
    catrgory_split = pd.DataFrame(catrgory_split)
    catrgory_split = catrgory_split['topic_categories'].apply(pd.Series).rename(columns=dictionary)

    # Filter columns based on the length
    dictionary_list = dictionary_list[0:len(catrgory_split.columns)]

    # Split WIKI_URL and pick up the last word (Filtering category)
    for i in range(len(catrgory_split.columns)):
        df = catrgory_split.iloc[:, i].str.split('/').apply(pd.Series).iloc[:, -1]
        df.columns = [i]
        catrgory_split[i] = df

    # Remove & Rename columns
    catrgory_split.drop(dictionary_list, axis=1, inplace=True)
    catrgory_split = catrgory_split.rename(columns=dictionary)
    catrgory_split = catrgory_split['wiki_category']

    # Merge & Rename columns
    df_popular = df_popular.merge(catrgory_split, left_index=True, right_index=True)
    del df_popular['topic_categories']
    print('Youtube Video List : Data mapping has been successfully completed')

    # ====================== YOUTUBE_VIDEO_CATEGORY : Data Mapping  ====================== #
    df_videocategory = df_videocategory[['id', 'snippet.title']]
    df_videocategory.rename(columns={'id': 'category_id',
                                     'snippet.title': 'reg_category'
                                     }, inplace=True)
    print('Youtube Video Category : Data mapping has been successfully completed')

    # ====================== MERGE : df_popular & df_videocategory ====================== #
    youtube_popular = df_popular.merge(df_videocategory, how='inner', on='category_id')

    # MYSQL insert 'run_date' and 'day'
    youtube_popular['run_date'] = date.today()
    youtube_popular['run_time'] = datetime.now().time().strftime('%H:%M:%S')
    youtube_popular['day'] = calendar.day_name[date.today().weekday()]
    # Move last column(run_date) to first sequence
    cols = youtube_popular.columns.tolist()
    cols = cols[-3:] + cols[:-3]
    youtube_popular = youtube_popular[cols]

    # ====================== Export to Pickle & Read  ====================== #
    picke_replace(name=pickle_name, file=youtube_popular)
    youtube_popular = read_pickle('youtube_popular.pkl')
    # ====================================================================== #

    endtime = datetime.now()
    print(endtime)
    timetaken = endtime - starttime
    print('Time taken : ' + timetaken.__str__())

    return youtube_popular

class channel:
    def __init__(self, cha_name):
        self.cha_name = cha_name

    def search(self):
        """
        NAME : channel.search()
        DESCRIPTION : Print channel information from the channel id key in __init__(cha_name)
        USAGE : User can check statistics figures in each relevant channel and finally uses ChanneId.
        """
        pd.options.mode.chained_assignment = None  # Off warning messages, default='warn'
        starttime = datetime.now()
        print(starttime)

        # ======================== GOOGLE SECRET Reading ========================= #
        query_string, db_name, db_user, db_password, driver_name, service_key = keys()
        youtube = build('youtube', 'v3', developerKey=service_key)
        # ======================================================================== #

        try:
            # YOUTUBE_CHANNEL_SEARCH
            res_channel_search = youtube.search().list(part='snippet', type='channel', regionCode='KR', q=self.cha_name,
                                                       order='videoCount', maxResults=20).execute()
            df_channel_search = json_normalize(res_channel_search['items'])
            print('Channel Search API Connection : ' + self.cha_name + '  has been successfully completed')
        except:
            print('Channel Search : ' + self.cha_name + ' has failed to open API connection')

        # ====================== YOUTUBE_CHANNEL_SEARCH : Data Mapping  ====================== #

        # Select Columns
        df_channel_search = df_channel_search[['id.kind', 'id.channelId', 'snippet.publishedAt', 'snippet.title']]

        # Rename Columns
        df_channel_search.rename(columns={'id.kind': 'type',
                                          'id.channelId': 'channel_id',
                                          'snippet.publishedAt': 'published_at',
                                          'snippet.title': 'channel_title',
                                          'snippet.categoryId': 'category_id'
                                          }, inplace=True)

        # ======================  Retrieving API : YOUTUBE_CHANNEL_INFO  ====================== #

        df_channel_info = pd.DataFrame()

        # Running loop to get Channel_ID from 'df_channel_search'
        for id in df_channel_search['channel_id']:
            try:
                # YOUTUBE_CHANNEL_INFORMATION
                res_channel = youtube.channels().list(part=['snippet', 'statistics', 'contentDetails'],
                                                      id=id).execute()
                df = json_normalize(res_channel['items'][0])
                df_channel_info = df_channel_info.append(df)
                print('Channel ID API Connection : ' + id + '  has been successfully completed')
            except:
                print('Channel ID : ' + id + ' has failed to open API connection')

        # ====================== YOUTUBE_CHANNEL_INFO : Data Mapping  ====================== #
        # Select Columns
        df_channel_info = df_channel_info[['id',
                                           'snippet.customUrl',
                                           'statistics.viewCount', 'statistics.subscriberCount',
                                           'statistics.videoCount']]

        # Rename Columns
        df_channel_info.rename(columns={'id': 'channel_id',
                                        'snippet.customUrl': 'custom_url',
                                        'statistics.viewCount': 'view_count',
                                        'statistics.subscriberCount': 'subscriber_count',
                                        'statistics.videoCount': 'video_count'
                                        }, inplace=True)

        # ====================== MERGE : df_channel_search & df_channel_info ====================== #
        # Merge & Rename columns
        df_chanel = df_channel_search.merge(df_channel_info, how='inner', on='channel_id')
        # ========================================================================================= #

        print(df_chanel.to_markdown())  # Choose index=TRUE / index=FALSE
        endtime = datetime.now()
        print(endtime)
        timetaken = endtime - starttime
        print('Time taken : ' + timetaken.__str__())

    def video(self, channel_id):
        """
        NAME : channel.video()
        DESCRIPTION : Create pickle files for all video information from the channel ID key in by users.
        USAGE : User can have a list of video IDs from the channel with some basic statistic figures.
        """
        # ====================== Setup ====================== #
        pd.options.mode.chained_assignment = None  # Off warning messages, default='warn'
        starttime = datetime.now()
        print(starttime)
        dictionary = {0: 'wiki_category'}
        dictionary_list = list(dictionary.values())

        # ======================== GOOGLE SECRET Reading ========================= #
        query_string, db_name, db_user, db_password, driver_name, service_key = keys()
        youtube = build('youtube', 'v3', developerKey=service_key)
        # ======================================================================== #

        # STEP1 : Search VIDEO_ID using Search()
        try:
            videos = []
            next_page_token = None
            while 1:
                res_video_id = youtube.search().list(part='id', type='video', channelId=channel_id, maxResults=50,
                                                     pageToken=next_page_token).execute()
                videos += res_video_id['items']
                next_page_token = res_video_id.get('nextPageToken')
                if next_page_token is None:
                    break
            # Extract VIDEO_IDs only
            video_ids = list(map(lambda x: x['id']['videoId'], videos))
            print('Video Item : video IDs has been successfully completed')
        except:
            print('Video Item : video IDs has failed to pull video IDs')

        # STEP2 : Use VIDEO_ID to extract VIDEO_INFORMATION
        try:
            df_video_info = pd.DataFrame()
            for id in video_ids:
                res_video_info = youtube.videos().list(part=['snippet', 'statistics', 'status', 'topicDetails'],
                                                       id=id,
                                                       regionCode='KR').execute()
                df = json_normalize(res_video_info['items'])
                df_video_info = df_video_info.append(df)
            print('Collecting Video Information has been successfully completed')
        except:
            print('Collecting Video Information has failed to extract')

        # ====================== YOUTUBE_CHANNEL_INFO : Data Mapping  ======================#
        # Select Columns
        df_video_info = df_video_info[[
            'id',
            'snippet.title', 'snippet.publishedAt',
            'statistics.viewCount', 'statistics.likeCount', 'statistics.dislikeCount', 'statistics.favoriteCount',
            'statistics.commentCount',  # video().list(part='statistics')
            'topicDetails.topicCategories',  # video().list(part='topicDetails')
            'status.madeForKids']]

        # Rename Columns
        df_video_info.rename(columns={'id': 'video_id',
                                      'snippet.title': 'video_title',
                                      'snippet.publishedAt': 'published_at',
                                      'statistics.viewCount': 'view_count',
                                      'statistics.likeCount': 'like_count',
                                      'statistics.dislikeCount': 'dislike_count',
                                      'statistics.favoriteCount': 'favorite_count',
                                      'statistics.commentCount': 'comment_count',
                                      'topicDetails.topicCategories': 'topic_categories',
                                      'status.madeForKids': 'for_kids'
                                      }, inplace=True)

        # Reset Index
        df_video_info = df_video_info.reset_index()

        # Split TopicCategories URL
        catrgory_split = df_video_info['topic_categories']
        catrgory_split = pd.DataFrame(catrgory_split)
        catrgory_split = catrgory_split['topic_categories'].apply(pd.Series).rename(columns=dictionary)

        # Filter columns based on the length
        dictionary_list = dictionary_list[0:len(catrgory_split.columns)]

        # Split WIKI_URL and pick up the last word (Filtering category)
        for i in range(len(catrgory_split.columns)):
            df = catrgory_split.iloc[:, i].str.split('/').apply(pd.Series).iloc[:, -1]
            df.columns = [i]
            catrgory_split[i] = df

        # Remove & Rename columns
        catrgory_split.drop(dictionary_list, axis=1, inplace=True)
        catrgory_split = catrgory_split.rename(columns=dictionary)
        catrgory_split = catrgory_split['wiki_category']

        # Merge & Rename columns
        df_video_info = df_video_info.merge(catrgory_split, left_index=True, right_index=True)
        del df_video_info['topic_categories']
        del df_video_info['index']
        print('Youtube Video Information : Data mapping has been successfully completed')

        # ====================== Export to Pickle & Read  ====================== #
        picke_replace(name='video_info', file=df_video_info)
        video_info = read_pickle('video_info.pkl')
        # ====================================================================== #

        endtime = datetime.now()
        print(endtime)
        timetaken = endtime - starttime
        print('Time taken : ' + timetaken.__str__())

        return video_info

    def playlist(self, channel_id):
        """
        ** WARNING : Heavy channel id may runs over your given resources in youtube API
        NAME : channel.playlist()
        DESCRIPTION : Create pickle files for all video information from the playlist ID key in by users.
        USAGE : User can have a list of video IDs from the channel with some basic statistic figures.
        """
        # ====================== Setup ====================== #
        pd.options.mode.chained_assignment = None  # Off warning messages, default='warn'
        starttime = datetime.now()
        print(starttime)
        dictionary = {0: 'wiki_category_1', 1: 'wiki_category_2', 2: 'wiki_category_3', 3: 'wiki_category_4',
                      4: 'wiki_category_5', 5: 'wiki_category_6'}
        dictionary_list = list(dictionary.values())

        # ======================== GOOGLE SECRET Reading ========================= #
        query_string, db_name, db_user, db_password, driver_name, service_key = keys()
        youtube = build('youtube', 'v3', developerKey=service_key)
        # ======================================================================== #

        # STEP1 : Collect PLAYLIST_ID using CHANNELS()
        try:
            res_playlist = youtube.channels().list(part='contentDetails', id=channel_id).execute()
            playlist_id = res_playlist['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            print('Channel PlaylistID API Connection : ' + self.cha_name + ' has been successfully completed')
        except:
            print('Channel PlaylistID API Connection : ' + self.cha_name + ' has failed to initiate')

        # STEP2 : Get VIDEO_ID from PLAYLIST_ID
        try:
            videos = []
            next_page_token = None
            while 1:
                res_video_id = youtube.playlistItems().list(part='snippet', playlistId=playlist_id, maxResults=50,
                                                   pageToken=next_page_token).execute()
                videos += res_video_id['items']
                next_page_token = res_video_id.get('nextPageToken')
                if next_page_token is None:
                    break
            # Extract VIDEO_IDs only
            video_ids = list(map(lambda x: x['snippet']['resourceId']['videoId'], videos))
            print('Playlist Item : video IDs has been successfully completed')
        except:
            print('Playlist Item : video IDs has failed to pull video IDs')

        # STEP3 : Use VIDEO_ID to extract VIDEO_INFORMATION
        try:
            df_video_info = pd.DataFrame()
            for id in video_ids:
                res_video_info = youtube.videos().list(part=['snippet', 'statistics', 'status', 'topicDetails'],
                                                         id=id,
                                                         regionCode='KR').execute()
                df = json_normalize(res_video_info['items'])
                df_video_info = df_video_info.append(df)
            print('Collecting Video Information has been successfully completed')
        except:
            print('Collecting Video Information has failed to extract')

        # ====================== YOUTUBE_CHANNEL_INFO : Data Mapping  ====================== #
        # Select Columns
        df_video_info = df_video_info[[
            'id',
            'snippet.title', 'snippet.publishedAt',
            'statistics.viewCount', 'statistics.likeCount', 'statistics.dislikeCount', 'statistics.favoriteCount','statistics.commentCount',  # video().list(part='statistics')
            'topicDetails.topicCategories',  # video().list(part='topicDetails')
            'status.madeForKids']]

        # Rename Columns
        df_video_info.rename(columns={'id': 'video_id',
                                   'snippet.title': 'video_title',
                                   'snippet.publishedAt': 'published_at',
                                   'statistics.viewCount': 'view_count',
                                   'statistics.likeCount': 'like_count',
                                   'statistics.dislikeCount': 'dislike_count',
                                   'statistics.favoriteCount': 'favorite_count',
                                   'topicDetails.topicCategories': 'topic_categories',
                                   'status.madeForKids': 'for_kids'
                                   }, inplace=True)

        # Reset Index
        df_video_info = df_video_info.reset_index()

        # Split TopicCategories URL
        catrgory_split = df_video_info['topic_categories']
        catrgory_split = pd.DataFrame(catrgory_split)
        catrgory_split = catrgory_split['topic_categories'].apply(pd.Series).rename(columns=dictionary)

        # Filter columns based on the length
        dictionary_list = dictionary_list[0:len(catrgory_split.columns)]

        # Split WIKI_URL and pick up the last word (Filtering category)
        for i in range(len(catrgory_split.columns)):
            df = catrgory_split.iloc[:, i].str.split('/').apply(pd.Series).iloc[:, -1]
            df.columns = [i]
            catrgory_split[i] = df

        # Remove & Rename columns
        catrgory_split.drop(dictionary_list, axis=1, inplace=True)
        catrgory_split = catrgory_split.rename(columns=dictionary)

        # Merge & Rename columns
        df_video_info = df_video_info.merge(catrgory_split, left_index=True, right_index=True)
        del df_video_info['topic_categories']
        del df_video_info['index']
        print('Youtube Video Information : Data mapping has been successfully completed')

        # ====================== Export to Pickle & Read  ====================== #
        picke_replace(name='playlist_info', file=df_video_info)
        playlist_info = read_pickle('playlist_info.pkl')
        # ====================================================================== #

        endtime = datetime.now()
        print(endtime)
        timetaken = endtime - starttime
        print('Time taken : ' + timetaken.__str__())

        return playlist_info

    def video_filter(self, find):
        """
        :param find: Find substrings from the video title.
        NAME : channel.video_filter()
        DESCRIPTION : Find substrings from the channel title to narrow down the search results.
        USAGE : Extraction of the comments takes less number of videos after the tile search.
        """
        # ====================== Setup ====================== #
        pd.options.mode.chained_assignment = None  # Off warning messages, default='warn'
        # =================================================== #

        # ====================== LOAD & FILTER PICKLES ====================== #
        print('Starting to filter video titles in the list of videos from' + self.cha_name)

        # Load video_info
        if os.path.exists('Pickle/video_info.pkl'):
            video_info = read_pickle('video_info.pkl')
            # Find substrings
            video_info_filter = video_info.loc[video_info['video_title'].str.contains(find, case=False)].reset_index(drop=True)
            # Export to Pickle & Read
            picke_replace(name='video_info_filter', file=video_info_filter)
            video_info_filter = read_pickle('video_info_filter.pkl')
            print('Title Searching : filtering titles from video_info has been successfully completed')
        else:
            print('playlist_info.pkl is not exist in the path')

        return video_info_filter

    def playlist_filter(self, find):
        """
        :param find: Find substrings from the playlist title.
        NAME : channel.playlist_filter()
        DESCRIPTION : Find substrings from the channel title to narrow down the search results.
        USAGE : Extraction of the comments takes less number of videos after the tile search.
        """
        # ====================== Setup ====================== #
        pd.options.mode.chained_assignment = None  # Off warning messages, default='warn'
        # =================================================== #

        # ====================== LOAD & FILTER PICKLES ====================== #
        print('Starting to filter video titles in the list of playlist from' + self.cha_name)

        # Load playlist_info
        if os.path.exists('Pickle/playlist_info.pkl'):
            playlist_info = read_pickle('playlist_info.pkl')
            # Find substrings
            playlist_info_filter = playlist_info.loc[playlist_info['VideoTitle'].str.contains(find, case=False)].reset_index(drop=True)
            # Export to Pickle & Read
            picke_replace(name='playlist_info_filter', file=playlist_info_filter)
            playlist_info_filter = read_pickle('playlist_info_filter.pkl')
            print('Title Searching : filtering titles from playlist_info has been successfully completed')
        else:
            print('playlist_info.pkl is not exist in the path')

        return playlist_info_filter

    def video_comment(self):
        """
        NAME : channel.video_comment()
        DESCRIPTION : Extract comments from video_info_subs
        USAGE : The comment will be used to have sentiment analysis
        """
        # ====================== Setup ====================== #
        pd.options.mode.chained_assignment = None  # Off warning messages, default='warn'
        starttime = datetime.now()
        print(starttime)

        # ====================== Read Pickles (VideoIDs) ====================== #
        video_info_filter = read_pickle('video_info_filter.pkl')

        # ======================== GOOGLE SECRET Reading ========================= #
        query_string, db_name, db_user, db_password, driver_name, service_key = keys()
        youtube = build('youtube', 'v3', developerKey=service_key)
        # ======================================================================== #

        # ====================== Retrieving API and store in DF  ====================== #
        print('Starting to extract comments in the list of filtered videos from' + self.cha_name)
        df_comment = pd.DataFrame()
        try:
            for id in video_info_filter.video_id:
                # CommentThread based on relevance filter
                res_rel_comments = youtube.commentThreads().list(part='snippet', videoId=id, order='relevance', maxResults=25).execute()
                df = json_normalize(res_rel_comments['items'])
                df_comment = df_comment.append(df)
                # CommentThread based on order filter
                res_ord_comments = youtube.commentThreads().list(part='snippet', videoId=id, order='time', maxResults=25).execute()
                df = json_normalize(res_ord_comments['items'])
                df_comment = df_comment.append(df, ignore_index=True)
            # Reset_index()
            df_comment = df_comment.reset_index(drop=True)
            print(str(len(df_comment)) + ' Comments has been successfully loaded')
        except:
            print('Comments has failed to load')

        # ====================== YOUTUBE_COMMENT : Data Mapping  ====================== #

        # Select Columns
        df_comment = df_comment[[
            'id',
            'snippet.topLevelComment.snippet.textOriginal',
            'snippet.topLevelComment.snippet.authorDisplayName',
            'snippet.topLevelComment.snippet.likeCount',
            'snippet.topLevelComment.snippet.publishedAt',
            'snippet.totalReplyCount'
        ]]

        # Rename Columns
        df_comment.rename(columns={'id': 'comment_id',
                                   'snippet.topLevelComment.snippet.textOriginal': 'comment',
                                   'snippet.topLevelComment.snippet.authorDisplayName': 'author',
                                   'snippet.topLevelComment.snippet.likeCount': 'like_count',
                                   'snippet.topLevelComment.snippet.publishedAt': 'published_at',
                                   'snippet.totalReplyCount': 'reply_count',
                                   }, inplace=True)

        # ====================== Export to Pickle & Read ====================== #
        picke_replace(name='video_comment', file=df_comment)
        video_comment = read_pickle('video_comment.pkl')
        # ===================================================================== #

        endtime = datetime.now()
        print(endtime)
        timetaken = endtime - starttime
        print('Time taken : ' + timetaken.__str__())

        return video_comment

    def playlist_comment(self):
        """
        NAME : channel.playlist_comment()
        DESCRIPTION : Extract comments from playlist_info_sub
        USAGE : The comment will be used to have sentiment analysis
        """
        # ====================== Setup ====================== #
        pd.options.mode.chained_assignment = None  # Off warning messages, default='warn'
        starttime = datetime.now()
        print(starttime)

        # ====================== Read Pickles (VideoIDs) ====================== #
        playlist_info_filter = read_pickle('playlist_info_filter.pkl')
        # ===================================================================== #

        # ======================== GOOGLE SECRET Reading ========================= #
        query_string, db_name, db_user, db_password, driver_name, service_key = keys()
        youtube = build('youtube', 'v3', developerKey=service_key)
        # ======================================================================== #

        # ====================== Retrieving API and store in DF  ====================== #
        print('Starting to extract comments in the list of filtered playlist from' + self.cha_name)
        df_comment = pd.DataFrame()
        try:
            for id in playlist_info_filter.video_id:
                # CommentThread based on relevance filter
                res_rel_comments = youtube.commentThreads().list(part='snippet', videoId=id, order='relevance', maxResults=25).execute()
                df = json_normalize(res_rel_comments['items'])
                df_comment = df_comment.append(df)
                # CommentThread based on order filter
                res_ord_comments = youtube.commentThreads().list(part='snippet', videoId=id, order='time', maxResults=25).execute()
                df = json_normalize(res_ord_comments['items'])
                df_comment = df_comment.append(df, ignore_index=True)
            # Reset_index()
            df_comment = df_comment.reset_index(drop=True)
            print(str(len(df_comment)) + ' Comments has been successfully loaded')
        except:
            print('Comments has failed to load')

        # ====================== YOUTUBE_COMMENT : Data Mapping  ====================== #

        # Select Columns
        df_comment = df_comment[[
            'id',
            'snippet.topLevelComment.snippet.textOriginal',
            'snippet.topLevelComment.snippet.authorDisplayName',
            'snippet.topLevelComment.snippet.likeCount',
            'snippet.topLevelComment.snippet.publishedAt',
            'snippet.totalReplyCount'
        ]]

        # Rename Columns
        df_comment.rename(columns={'id': 'comment_id',
                                   'snippet.topLevelComment.snippet.textOriginal': 'comment',
                                   'snippet.topLevelComment.snippet.authorDisplayName': 'author',
                                   'snippet.topLevelComment.snippet.likeCount': 'like_count',
                                   'snippet.topLevelComment.snippet.publishedAt': 'published_at',
                                   'snippet.totalReplyCount': 'reply_count',
                                   }, inplace=True)

        # ====================== Export to Pickle & Read ====================== #
        picke_replace(name='playlist_comment', file=df_comment)
        playlist_comment = read_pickle('playlist_comment.pkl')
        # ===================================================================== #

        endtime = datetime.now()
        print(endtime)
        timetaken = endtime - starttime
        print('Time taken : ' + timetaken.__str__())

        return playlist_comment