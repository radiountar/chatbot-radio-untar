import pandas as pd
import re

def load_sinonim_xlsx(path="logs/sinonim.xlsx"):
    df = pd.read_excel(path)
    sinonim_dict = {}
    for index, row in df.iterrows():
        kata_baku = row["kata_baku"]
        daftar_sinonim = str(row["sinonim"]).split(";")  # str() untuk hindari NaN
        sinonim_dict[kata_baku] = daftar_sinonim
    return sinonim_dict

def substitusi_sinonim_dari_xlsx(teks, sinonim_dict):
    teks = teks.lower()
    for kata_baku, daftar_sinonim in sinonim_dict.items():
        for sinonim in daftar_sinonim:
            if sinonim in teks:
                teks = teks.replace(sinonim, kata_baku)
    return teks

def load_kata_kasar_xlsx(path="logs/kata_kasar.xlsx"):
    df = pd.read_excel(path)
    return list(df["kata_kasar"].dropna().values)

def buat_regex_kata_kasar(kata_kasar_list):
    return re.compile(r'\b(' + '|'.join(map(re.escape, kata_kasar_list)) + r')\b', re.IGNORECASE)

def cek_kata_kasar_dari_xlsx(teks, pattern):
    return bool(pattern.search(teks))
