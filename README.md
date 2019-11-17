# People-Behavioral-Analysis

In this repository is presented an AI based people behavior tracking algorithm. The algorithm accepts data from bluetooth tracking stations around the city and assigns behavioral tags to people like a late owl, an early bird, a student or, e.g., a tourist. It is planned to use people dynamic behavioral tagging for personalized advertisements on city billboards. 

Data is retrieved from MyHelsinki Open API (https://hri.fi/data/en_GB/dataset/myhelsinki-open-api-paikat-tapahtumat-ja-aktiviteetit)

<b>Components:</b>

+ Open Data Analysis.ipynb - generic available data analysis and feature engineering
+ Stations Tags Assignment & Speed & Social Features Engineering.ipynb - assignment of tags like is_road_nearby, is_recreation_zone and other to tracking stations (it is planned to assign this tags using Maps API in future). Also, people moving speed and transport are devised as well as their social circle.
+ Behvioral analysis pipeline.ipynb & BehavioralAnalysis folder - contain Azure Machine Learning service based pipeline implementation which:
  1) daily accepts raw data (retrieved from Azure Blob Storage) from bluetooth trackers
  2) Based on today's day and historical person's behavior devises tags
  3) Stores tags with users
