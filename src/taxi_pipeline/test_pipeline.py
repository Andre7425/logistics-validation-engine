from datetime import datetime, tzinfo, timezone
from pymongo import MongoClient

# Requires the PyMongo package.
# https://api.mongodb.com/python/current

client = MongoClient('mongodb://admin:secret_pass@localhost:27017/')
result = client['taxi_db']['trips'].aggregate([
    {
        '$match': {
            'tpep_pickup_datetime': {
                '$gte': datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc), 
                '$lt': datetime(2024, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
            }
        }
    }, {
        '$project': {
            'hour': {
                '$hour': '$tpep_pickup_datetime'
            }, 
            'total_amount': 1
        }
    }, {
        '$group': {
            '_id': '$hour', 
            'avg_fare': {
                '$avg': '$total_amount'
            }, 
            'trips_count': {
                '$sum': 1
            }
        }
    }, {
        '$sort': {
            '_id': 1
        }
    }
])