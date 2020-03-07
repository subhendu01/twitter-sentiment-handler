from pymongo import MongoClient

client = MongoClient()
client = MongoClient("mongodb://localhost:27017/")

# Access database
mydatabase = client["Twitter"]

# Access collection of the database
tweet_data = mydatabase["tweet_data"]

