# ====================== API READER SETUP ====================== #
from googleapiclient.discovery import build #GOOGLE API
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote_plus, unquote
from pandas import json_normalize
import json
import requests #XML DECODING
import xmltodict
# ====================== YAML READER SETUP ====================== #
import yaml
import os
from datetime import datetime
# ====================== LOG SETUP ====================== #
import pandas as pd
import colored

# ====================== RETRIEVING DATA FROM API ====================== #
def api_encodetype(name, environment):
    """
    :param name: main name of YAML configuration
    :param environment: api
    :return:
    """
    starttime = datetime.now()
    print(starttime)
    # ====================== CONFIGURATION.YAML READING ====================== #
    try:
        with open('config/credentials.yaml') as stream:
            credential = yaml.safe_load(stream)
    except yaml.YAMLError as e:
        print("Failed to parse credentials " + e.__str__())
    except Exception as e:
        print("Failed to parse credentials " + e.__str__())
    # ====================== Retrieving API and store in DF  ======================#
    env_cred = credential[name][environment]
    url = env_cred['api_url']
    service_key = env_cred['api_key']
    queryparams = '?' + urlencode({quote_plus('serviceKey'): service_key
                                   })
    try:
        response = urlopen(url + unquote(queryparams))
        json_api = response.read().decode("utf-8")
        json_file = json.loads(json_api)
        print(name.upper() + ' Successfully initiated API Connection')
    except:
        print(name.upper() + ' Failed to initiated API Connection')

    df = json_normalize(json_file['data'])

    # ====================== Export to Pickle  ======================#
    try:
        if not os.path.exists('Pickle/' + name + '.pkl'):
            try:
                os.makedirs('Pickle')
            except FileExistsError:
                pass
            df.to_pickle('Pickle/' + name + '.pkl')
    except Exception as e:
        print('Failed to export(.pkl) ' + name.upper() + e.__str__())
    else:
        print('Successfully export(.pkl) ' + name.upper())

    endtime = datetime.now()
    print(endtime)
    timetaken = endtime - starttime
    print('Time taken : ' + timetaken.__str__())

def api_decodetype(name, environment, startdate):
    """
    :param name: main name of YAML configuration
    :param environment: api
    :return:
    """
    starttime = datetime.now()
    print(starttime)
    # ====================== CONFIGURATION.YAML READING ====================== #
    try:
        with open('config/credentials.yaml') as stream:
            credential = yaml.safe_load(stream)
    except yaml.YAMLError as e:
        print("Failed to parse credentials " + e.__str__())
    except Exception as e:
        print("Failed to parse credentials " + e.__str__())
    # ====================== Retrieving API and store in DF  ======================#
    env_cred = credential[name][environment]
    url = env_cred['api_url']
    service_key = env_cred['api_key']
    queryparams = '?' + urlencode({quote_plus('serviceKey'): service_key,
                                   quote_plus('startCreateDt'): startdate})
    try:
        res = requests.get(url + queryparams)
        result = xmltodict.parse(res.text)
        json_file = json.loads(json.dumps(result))
        print(name.upper() + ' Successfully initiated API Connection')
    except:
        print(name.upper() + ' Failed to initiated API Connection')

    df = json_normalize(json_file['response']['body']['items']['item'])
    # ====================== Export to Pickle  ======================#
    try:
        if not os.path.exists('Pickle/' + name + '.pkl'):
            try:
                os.makedirs('Pickle')
            except FileExistsError:
                pass
            df.to_pickle('Pickle/' + name + '.pkl')
    except Exception as e:
        print('Failed to export(.pkl) ' + name.upper() + e.__str__())
    else:
        print('Successfully export(.pkl) ' + name.upper())

    endtime = datetime.now()
    print(endtime)
    timetaken = endtime - starttime
    print('Time taken : ' + timetaken.__str__())

def api_youtube_populear(name, environment, max_result):
    # ====================== Setup ====================== #
    pd.options.mode.chained_assignment = None  # Off warning messages, default='warn'
    dictionary = {0: 'Wiki_Category_1', 1: 'Wiki_Category_2', 2: 'Wiki_Category_3', 3: 'Wiki_Category_4',
                  4: 'Wiki_Category_5', 5: 'Wiki_Category_6'}
    dictionary_list = list(dictionary.values())
    starttime = datetime.now()
    print(starttime)
    # ====================== CONFIGURATION.YAML Reading ====================== #
    try:
        with open('config/credentials.yaml') as stream:
            credential = yaml.safe_load(stream)
    except yaml.YAMLError as e:
        print("Failed to parse credentials " + e.__str__())
    except Exception as e:
        print("Failed to parse credentials " + e.__str__())
    # ====================== Retrieving API and store in DF  ======================#
    env_cred = credential[name][environment]
    service_key = env_cred['api_key']
    youtube = build('youtube', 'v3', developerKey=service_key)

    try:
        # YOUTUBE_VIDEO_LIST
        res_popular = youtube.videos().list(part=['snippet', 'statistics', 'status', 'topicDetails'],
                                            chart='mostPopular',
                                            maxResults=int(max_result), regionCode='KR').execute()
        df_popular = json_normalize(res_popular['items'])
        print('Videos Successfully initiated API Connection')
        # YOUTUBE_VIDEO_CATEGORY
        res_videocategory = youtube.videoCategories().list(part='snippet', regionCode='KR').execute()
        df_videocategory = json_normalize(res_videocategory['items'])
        df_videocategory = df_videocategory[['id', 'snippet.title']]
        print('VideoCategories Successfully initiated API Connection')
    except:
        print(name.upper() + ' Failed to initiated API Connection')

    # ====================== YOUTUBE_VIDEO_LIST : Data Mapping  ======================#
    # Select Columns
    df_popular = df_popular[
        ['snippet.title', 'id', 'snippet.channelTitle', 'snippet.channelId', 'snippet.publishedAt', 'snippet.tags',
         'snippet.categoryId',  # video().list(part='snippet')
         'statistics.viewCount', 'statistics.likeCount', 'statistics.dislikeCount', 'statistics.favoriteCount',
         'statistics.commentCount',  # video().list(part='statistics')
         'topicDetails.topicCategories',  # video().list(part='topicDetails')
         'status.madeForKids']]
    # Rename Columns
    df_popular.rename(columns={'snippet.title': 'VideoTitle',
                               'id': 'VideoId',
                               'snippet.channelTitle': 'ChannelTitle',
                               'snippet.channelId': 'ChannelId',
                               'snippet.publishedAt': 'PublishedAt',
                               'snippet.tags': 'Tags',
                               'snippet.categoryId': 'CategoryId',
                               'statistics.viewCount': 'ViewCount',
                               'statistics.likeCount': 'LikeCount',
                               'statistics.dislikeCount': 'DislikeCount',
                               'statistics.favoriteCount': 'FavoriteCount',
                               'topicDetails.topicCategories': 'TopicCategories',
                               'status.madeForKids': 'ForKids',
                               }, inplace=True)
    # Split TopicCategories URL
    catrgory_split = df_popular['TopicCategories']
    catrgory_split = pd.DataFrame(catrgory_split)
    catrgory_split = catrgory_split['TopicCategories'].apply(pd.Series).rename(columns=dictionary)
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
    df_popular = df_popular.merge(catrgory_split, left_index=True, right_index=True)
    del df_popular['TopicCategories']
    print('YOUTUBE_VIDEO_LIST Successfully Completed Data Mapping')
    # ====================== YOUTUBE_VIDEO_CATEGORY : Data Mapping  ======================#
    df_videocategory = df_videocategory[['id', 'snippet.title']]
    df_videocategory.rename(columns={'id': 'CategoryId',
                                     'snippet.title': 'Reg_Category'
                                     }, inplace=True)
    print('YOUTUBE_VIDEO_CATEGORY Successfully Completed Data Mapping')
    # ====================== MERGE : df_popular & df_videocategory ====================== #
    df_popular = df_popular.merge(df_videocategory, how='inner', on='CategoryId')

    # ====================== Export to Pickle  ======================#
    try:
        if not os.path.exists('Pickle/' + name + '.pkl'):
            try:
                os.makedirs('Pickle')
            except FileExistsError:
                pass
            df_popular.to_pickle('Pickle/' + name + '.pkl')
    except Exception as e:
        print('Failed to export(.pkl) ' + name.upper() + e.__str__())
    else:
        print('Successfully export(.pkl) ' + name.upper())

    endtime = datetime.now()
    print(endtime)
    timetaken = endtime - starttime
    print('Time taken : ' + timetaken.__str__())

# ====================== API RUNNING ====================== #
def run_api():
    # DATA_GO_KR
    api_encodetype(name='covid_vaccines', environment='data_go_kr')
    api_decodetype(name='covid_age_sex', environment='data_go_kr', startdate='20200210')
    api_decodetype(name='covid_city', environment='data_go_kr', startdate='20200210')
    api_decodetype(name='covid_cases', environment='data_go_kr', startdate='20200210')
    # YOUTUBE_API
    api_youtube_populear(name='youtube_popular', environment='youtube', max_result=50)

