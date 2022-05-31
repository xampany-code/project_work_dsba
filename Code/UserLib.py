import pandas as pd
from matplotlib import pyplot as plt
import CryptoLib
import Utils


def show_rates(exchanges, token, start_time, end_time):
    start_time = Utils.to_timestamp(start_time)
    end_time = Utils.to_timestamp(end_time)
    for e in exchanges:
        df = CryptoLib.gather_spot_crypto(e, token)
        df = Utils.slice_by_tyme(df, start_time, end_time)
        plt.plot(df['unix'], df['value'])
    plt.legend(exchanges)
    plt.title(Utils.from_timestamp(start_time) + "_" + Utils.from_timestamp(end_time)+" "+token)
    plt.show()


def show_dif(exchange1, exchange2, token, start_time, end_time):
    start_time = Utils.to_timestamp(start_time)
    end_time = Utils.to_timestamp(end_time)
    if exchange1 > exchange2:
        e = exchange1
        exchange1 = exchange2
        exchange2 = e
    df = pd.read_csv("./DifTwo/"+exchange1+exchange2+"_"+token+".csv")
    df = Utils.slice_dif_by_time(df, start_time, end_time)
    plt.plot(df['unix'], df['dif'])
    plt.title(Utils.from_timestamp(start_time) + "_" + Utils.from_timestamp(end_time) + " "
                                 + exchange1 + "/" + exchange2 + " " + token)
    plt.show()


def show_liquidity(exchange1, exchange2, token, start_time, end_time):
    start_time = Utils.to_timestamp(start_time)
    end_time = Utils.to_timestamp(end_time)
    CryptoLib.show_liq(exchange1, exchange2, token, start_time, end_time)


def track_liquidity(pairs, token):
    heads = []
    for pair in pairs:
        exchange1 = pair[0]
        exchange2 = pair[1]
        if exchange1 > exchange2:
            e = exchange1
            exchange1 = exchange2
            exchange2 = e
        df = pd.read_csv("./Liquidity/"+exchange1+exchange2+".csv")
        heads.append(exchange1 + exchange2)
        x = []
        y = []
        for i in range(0, len(df['start'])):
            if df[token][i] != -1:
                start = Utils.to_timestamp(Utils.parse_time(df['start'][i]))
                end = Utils.to_timestamp(Utils.parse_time(df['end'][i]))
                x.append((start+end)/2)
                y.append(df[token][i])
        plt.plot(x, y)
    plt.legend(heads)
    plt.title(token)
    plt.show()