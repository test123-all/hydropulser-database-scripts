import csv
import pandas as pd
from uuid6 import uuid7

num_ids = {"Datenerfassung": 23,
           "Akustik": 4,
           "Druck": 128,
           "Weg": 18,
           "Kraft": 17,
           "Moment": 20,
           "Temperatur": 21,
           "Volumenstrom": 14,
           "Beschleunigung": 14,
           "Schwingungen": 1,
           "Fuellstand": 7,
           "sonstige": 16}

ids = {key: [str(uuid7()) for _ in range(val)] for key, val in num_ids.items()}

df = pd.DataFrame.from_dict(ids, orient='index')
df = df.transpose()
df.to_csv("output.csv", index=False, sep=";", quoting=csv.QUOTE_ALL)
