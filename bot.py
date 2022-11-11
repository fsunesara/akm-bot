import csv
import os
import random
import requests
import shutil
import tempfile
import tweepy
import yaml

def create_tweet(event, context):
  with open('config.yml', 'r') as yml:
    cfg = yaml.safe_load(yml)

  API_KEY = cfg['api_key']
  API_SECRET = cfg['api_secret']
  ACCESS_TOKEN = cfg['access_token']
  ACCESS_TOKEN_SECRET = cfg['access_token_secret']
  BEARER_TOKEN = cfg['bearer_token']

  auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
  auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
  api = tweepy.API(auth)
  client = tweepy.Client(BEARER_TOKEN, API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

  with open('artifacts.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter='|')
    next(reader)
    info = random.choice([l for l in reader])[1:]

  name, date, url, img_urls = info

  text = ', '.join((name, date, url))
  i = 0
  while len(text) > 280:
    i += 1
    name = name[:len(name) - i] + '...'
    text = ', '.join((name, date, url))

  fname = img_urls.split('/')[-1]
  path = '/'.join((tempfile.gettempdir(), fname))
  res = requests.get(img_urls, stream=True)
  res.raise_for_status()
  with open(path, 'wb') as out:
    shutil.copyfileobj(res.raw, out)
  del res

  try:
    media = api.media_upload(filename=path)
    client.create_tweet(text=text, media_ids=[media.media_id])
  except Exception as e:
    print('Error', e)

  os.remove(path)