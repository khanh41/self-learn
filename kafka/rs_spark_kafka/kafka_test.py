import numpy as np
import pandas as pd
import random
import time
from datetime import datetime
from kafka import KafkaProducer

# pip install kafka-python

KAFKA_TOPIC_NAME_CONS = "songTopic"
KAFKA_BOOTSTRAP_SERVERS_CONS = 'localhost:9092'

if __name__ == "__main__":
    print("Kafka Producer Application Started ... ")

    kafka_producer_obj = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS_CONS,
                                       value_serializer=lambda x: x.encode('utf-8'))

    filepath = "tracks.csv"
    # This is the csv which has Spotify data.

    songs_df = pd.read_csv(filepath)
    # songs_df = songs_df[songs_df['release_date'] > '2020-01-01']
    songs_df = songs_df[songs_df['popularity'] > 50]
    # We use this filter to get popular songs streaming. This can be tuned based on your intrest.

    songs_df['order_id'] = np.arange(len(songs_df))

    songs_df['artists'] = songs_df['artists'].str.replace('[^a-zA-Z]', '')
    songs_df['id_artists'] = songs_df['id_artists'].str.replace('[^a-zA-Z]', '')

    # Some pre-processing performed for clean data.

    song_list = songs_df.to_dict(orient="records")

    message_list = []
    message = None
    for message in song_list:
        message_fields_value_list = [message["order_id"], message["id"], message["name"], message["popularity"],
                                     message["duration_ms"], message["explicit"], message["artists"],
                                     message["id_artists"], message["release_date"], message["danceability"],
                                     message["energy"], message["key"], message["loudness"], message["mode"],
                                     message["speechiness"], message["acousticness"], message["instrumentalness"],
                                     message["liveness"], message["valence"], message["tempo"],
                                     message["time_signature"]]

        message = ','.join(str(v) for v in message_fields_value_list)
        print("Message Type: ", type(message))
        print("Message: ", message)
        kafka_producer_obj.send(KAFKA_TOPIC_NAME_CONS, message)
        time.sleep(1)

    print("Kafka Producer Application Completed. ")
