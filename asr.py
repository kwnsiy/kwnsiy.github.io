# coding: utf-8 

import pdb
import os 
import json 

"""
base         = "./splitted_speech/"
setting_1    = "20230325-150000-000"
setting_2    = "20230325-150539-579"
setting_3    = "20230325-154844-077"
setting_4    = "20230325-155017-589"
setting_5    = "20230325-161026-551"

f = open("list.tsv", "w")

### print excel ###
for setting in [setting_1, setting_2, setting_3, setting_4,setting_5]:
  #print (setting)
  labels = json.load(open(base+"pinmic/"+setting+"/"+"label.json"))
  for k in labels.keys(): 
    try: 
      f.write("\t".join([setting, k, labels[k][0], labels[k][1]])+"\n")
    except: 
      print (labels[k])      
    #pass
"""

import pandas as pd

# tsvファイルを読み込む
df = pd.read_csv("experiment.tsv", sep="\t")

# ランダムに500行をサンプリング
sampled_df = df.sample(n=500, replace=False, random_state=42)

# 新しいtsvファイルとして保存
sampled_df.to_csv("dataset.tsv", sep="\t", index=True)


dataset = pd.read_csv('dataset.tsv', sep='\t')
vfd = pd.read_csv('vfd.tsv', sep='\t').dropna()

# 'image' カラムと 'image_path' カラム、および 'original_transcript' カラムと 'utterance' カラムを基に結合
merged = pd.merge(dataset, vfd, left_on=['image', 'original_transcript'], right_on=['image_path', 'utterance'])

# 同じ 'image' と 'original_transcript' を持つ行の 'verbal_response' を結合
merged_grouped = merged.groupby(['image', 'original_transcript'])['verbal_response'].apply('||'.join).reset_index()

# 結合したデータフレームを 'dataset' とマージして、新しい 'response' カラムを作成
final_merged = pd.merge(dataset, merged_grouped, on=['image', 'original_transcript'], how='inner')
final_merged.rename(columns={'verbal_response': 'response'}, inplace=True)


pinmics = []
arrays  = []
pinmics_hash = []
arrays_hash  = []

import hashlib

for x,y,z, v in zip(final_merged["session"], final_merged["image"], final_merged["speaker"], final_merged["filename"]): 
  pinmic = "splitted_speech/pinmic/%s/%s" % (x, v)
  array  = "splitted_speech/%s_original/%s/%s" % (z.lower(), x, v)
  
  pinmic_hash = hashlib.sha256(pinmic.encode("utf-8")).hexdigest()
  array_hash  =  hashlib.sha256(array.encode("utf-8")).hexdigest()

  if not(os.path.isfile(pinmic) and os.path.isfile(array)):
    print (pinmic, array) 
  
  template = open("template.txt").read()
  with open(pinmic.replace(".wav", ".html"), "w") as f: 
    template = template.replace("INPUT_SPEECH_FILE_PATH", v)
    template = template.replace("SAMPLE_SPEECH_DB_ID", "experiments/"+pinmic_hash)
    f.write(template)

  template = open("template.txt").read()
  with open(array.replace(".wav", ".html"), "w") as f: 
    template = template.replace("INPUT_SPEECH_FILE_PATH", v)
    template = template.replace("SAMPLE_SPEECH_DB_ID", "experiments/"+array_hash)
    f.write(template)

  pinmics.append("https://kwnsiy.github.io/" + pinmic.replace(".wav", ".html"))
  arrays.append("https://kwnsiy.github.io/" + array.replace(".wav", ".html"))
  pinmics_hash.append(pinmic_hash)
  arrays_hash.append(array_hash)
  
# 新しいTSVファイルとして保存
final_merged["pinmic"]       = pinmics
final_merged["pinmic_hash"]  = pinmics_hash
final_merged["array"]        = arrays
final_merged["array_hash"]   = arrays_hash


final_merged.to_csv('dataset.tsv', sep='\t', index=False)
