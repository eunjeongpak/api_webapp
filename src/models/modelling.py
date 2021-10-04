from src.utils.api import run_covid_api
from src.utils.api import run_youtube_api
from src.utils.api import api_channel_search
import pandas as pd

# ====================== API RUNNING ====================== #
run_covid_api()
run_youtube_api()
api_channel_search(cha_name='슈카월드')
# ====================== DEFINE FUNCTION ====================== #
def read_pickle(file_name: str) -> pd.DataFrame:
    return pd.read_pickle('Pickle/' + file_name)
# ====================== LOAD PICKES ====================== #
df_age_sex = read_pickle('covid_age_sex.pkl')
df_vaccines = read_pickle('covid_vaccines.pkl')
df_city = read_pickle('covid_city.pkl')
df_cases = read_pickle('covid_cases.pkl')

youtube_popular = read_pickle('youtube_popular.pkl')



