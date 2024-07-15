from pymongo import MongoClient

client = MongoClient("localhost", 27017)

db = client["valve_guard"]

model_info_collection = db["model_info"]
predict_result_collection = db["predict_result"]
