import json as js
import pandas as pd
import ast
import numpy as np
with open("AtomicCards.json") as js_data:
    d = js.load(js_data)
    js_data.close()
df = pd.DataFrame(d)
a = df["data"]
#On a deux lignes NaN#
a = a.dropna() 
a = a.apply(lambda x: x[0])
#Convertion en objet Series#
a = a.apply(pd.Series)
df = pd.concat([
    df.drop(columns = ["data"]),
    a
], axis = 1)
df.to_csv("AtomicCars.csv", index = False)

df = pd.read_csv("AtomicCars.csv")
#Ici on dégage les 2 premiers individus casse couille #
df = df[2:]
import ast #To convert str into a good type#
df["foreignData"] = df["foreignData"].apply(lambda x: ast.literal_eval(x))


json_dict_columns = ["identifiers","legalities","purchaseUrls","leadershipSkills"]
json_list = ["foreignData","rulings"]
df = df[2:]
for j in json_list:
    df[j] = df[j].apply(lambda x: x if not( pd.notna(x) ) else ast.literal_eval(x))
    df[j] = df[j].apply(lambda x: x if isinstance(x, list) else [])
    df[j] = df[j].apply(lambda x: x[0] if len(x) > 0 else x)
    df = pd.concat([
    df.drop(columns = [j]),
    df[j].apply(pd.Series)], axis = 1)


for j in json_dict_columns:
    df[j] = df[j].apply(lambda x: x if not( pd.notna(x) ) else ast.literal_eval(x))
    df = pd.concat([
    df.drop(columns = [j]),
    df[j].apply(pd.Series)], axis = 1)