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


#CryptoLib.show_liq("BNN", "KUC", "BNB", Utils.to_timestamp((1, 11, 2019)), Utils.to_timestamp((1, 1, 2020)))
#CryptoLib.prep_dif_every_exchange()
#CryptoLib.write_liquidity_all()
#CryptoLib.prep_dif_usd("BNN", "ETH", "USDC")
#CryptoLib.show_liq("BNN", "USDC", "ETH", Utils.to_timestamp((1,1,2021)), Utils.to_timestamp((1,9,2021)))
CryptoLib.write_liquidity_all()