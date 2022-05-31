from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import statistics
import numpy as np
import subprocess
import os
import math
import CryptoLib
import Utils
from sklearn.linear_model import LinearRegression
import zipfile
import UserLib


def shift_liq(exchange1, exchange2, token, shift):
    path = "./Liquidity/"+exchange1+exchange2+".csv"
    df = pd.read_csv(path)
    v = list(df[token].values)
    if shift > 0:
        for i in range(0, shift):
            v = v[:-1]
            v.insert(0, -1.0)
    if shift < 0:
        for i in range(0, -shift):
            v = v[1:]
            v.append(-1.0)
    df[token] = np.array(v)
    df.to_csv(path)


#shift_liq("BNN", "KUC", "LTC", -1)
UserLib.track_liquidity([("BNN", "FTX"), ("BNN", "KUC"), ("BNN", "STM")], "XRP")

