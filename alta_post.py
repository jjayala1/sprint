import pandas as pd
from urllib.parse import unquote
import requests

df = pd.read_csv("./posts/links1-16.csv")
print(df)
df = df[df['LINK TO POST'].str.len() > 0]
df = df[df["LINK TO POST"].str.contains("linkedin")]
#df = df[df["SPRINT DAY"].str.contains("DAY 15")]
print(df["SPRINT DAY"].count())

for index, row in df.iterrows():

    day = int(row['SPRINT DAY'].split(' ')[1])
    link = row['LINK TO POST'].strip().split('?')[0]
    owner = row['FULL NAME'].strip()

    data=f"day_number={day}&new_link={link}&fauthor={owner}"
    r = requests.post("http://sprintoct21.pythonanywhere.com/new_post", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
