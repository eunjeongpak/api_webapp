# Web Application using Google API
This project is licensed under the terms of the GNU General Public License v3.0

### Contributor
* Jinmun Park : pjm9827@gmail.com <br/>
* Eunjeong Park : pej111797@gmail.com

### API Resources
| Source | URL | Description |
| --- | --- | --- |
| GoogleAPI | https://developers.google.com/youtube/v3 | Youtube Comments |
| 공공데이터(future) | https://www.data.go.kr/index.do | Covid 19 |

### FIRST STAGE (15'SEPT'2021 ~ 20'OCT'2021) :

| PLAN &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;| DATE &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;| STATUS &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;| DESCRIPTION &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; |
| --- | --- | --- | --- |
| API SETUP | 01'OCT'2021 | COMPLETED | API Connection |
| DATA MAPPING | 6'OCT'2021 | COMPLETED | Mapping API |
| POSTGRESSQL | 8'OCT'2021 | COMPLETED | Postgresql DB |
| HEROKU   | OCT | COMPLETED | Autopush |

### SECOND STAGE (20'OCT'2021 ~ 11'NOV'2021) :
* Replace Heroku with GCP (MySQL, Cloud Function, Cloud Engine)
* Replace Kobert with <bert-base-multilingual-cased> due to library dependencies issue

| PLAN &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;| DATE &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;| STATUS &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;| DESCRIPTION &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; |
| --- | --- | --- | --- |
| KOBERT | 25'OCT'2021 | COMPLETED | Sentiment Analysis |
| G SQL | 5'NOV'2021 | COMPLETED | Replace Heroku |
| BERT | 25'OCT'2021 | COMPLETED | Replace KOBERT |
| G FUNCTION | 9'NOV'2021 | COMPLETED | Replace Heroku |

### THIRD STAGE (11'NOV'2021 ~ 11'DEC'2021) :

| PLAN &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;| DATE &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;| STATUS &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;| DESCRIPTION &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; |
| --- | --- | --- | --- |
| G ENGINE | 16'NOV'2021 | COMPLETED | Deployment |
| FLASK | 11'DEC'2021 | COMPLETED | App Design |

### SUPPORT
| Source | URL | Description |
| --- | --- | --- |
| Google | https://developers.google.com/youtube/v3 | API Documentation |
| Google | https://support.google.com/youtube/contact/yt_api_form | API Extension |
| Kobert | https://github.com/SKTBrain/KoBERT | Korean Bert |

## WEB IMAGES
  http://ourdatapark.com/
    
    Main page
  <img src = "https://user-images.githubusercontent.com/76864400/145665028-824b9274-2012-4d17-93aa-abca3695d077.png" width="80%" height="80%">
  
    Chart page: Provide Youtube Video Popular Chart Table
  <img src = "https://user-images.githubusercontent.com/76864400/145665180-01b4e46f-3b36-4d4c-a978-1f413e681f45.png" width="80%" height="80%">
 
    Dashboard page: Provide Video Comments Keyword Analysis & Sentiment Analysis
  <img src = "https://user-images.githubusercontent.com/76864400/145665279-638788cb-4aa9-413a-aee7-e8d4946dce04.png" width="80%" height="80%">

    Trend page: Provide latest, 15days, 30days Trend Chart
  <img src = "https://user-images.githubusercontent.com/76864400/145665597-5eda761c-f256-4562-8a96-432cff593787.png" width="80%" height="80%">
  <img src = "https://user-images.githubusercontent.com/76864400/145665657-a5c59641-38c2-41f3-b530-a27570f064d5.png" width="80%" height="80%">

## PROJECT NOTE
### Requirements.txt
pip freeze > requirements.txt <br/>
pip install -r requirements.txt 
  
 
