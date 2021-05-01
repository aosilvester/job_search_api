import pandas as pd


# open('json_files\\indeed_scraped_postings.json', 'r', encoding="utf-8") 

df = pd.read_json (r'validated_postings.json')
df.to_csv (r'validated_postings_v2.csv', index = None)