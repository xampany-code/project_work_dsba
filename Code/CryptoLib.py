import Utils
import pandas as pd
from datetime import datetime
import statistics
import matplotlib.pyplot as plt
from os.path import exists
import numpy as np


def prep_time():
    print("Standardizing timestamp time")
    exchanges = Utils.get_all_dirs_in_dir("./RawCrypto")
    for e in exchanges:
        tokens = Utils.get_all_dirs_in_dir("./RawCrypto"+"/"+e)
        for token in tokens:
            files = Utils.get_all_files_in_dir("./RawCrypto"+"/"+e+"/"+token)
            for file in files:
                df = pd.read_csv("./RawCrypto"+"/"+e+"/"+token+"/"+file)
                if df['unix'][0] < 1000000000000:
                    print(e, token, file)
                    for i in range(0, len(df)):
                        df.loc[i, 'unix'] = df['unix'][i] * 1000
                    df.to_csv("./RawCrypto"+"/"+e+"/"+token+"/"+file)
                del df


def gather_spot_crypto(exchange, token):
    print("Gathering spot", exchange, token)
    have_tokens = Utils.get_all_dirs_in_dir("./RawCrypto/"+exchange+"/")
    if not token in have_tokens:
        raise Exception('have not this toke: ' + token)
    path = "./RawCrypto/"+exchange+"/" + token + "/"
    sub_files = Utils.get_all_files_in_dir(path)
    for i in range(0, len(sub_files)):
        sub_files[i] = path+sub_files[i]
    return Utils.merge_frames(sub_files, ['unix', 'open', 'close'])


def prep_dif_usd(exchange, token1, token2):
    df_1 = gather_spot_crypto(exchange, token1)
    df_2 = gather_spot_crypto(exchange, token2)
    start_1 = df_1['unix'][0]
    start_2 = df_2['unix'][0]
    end_1 = df_1['unix'][len(df_1['unix']) - 1]
    end_2 = df_2['unix'][len(df_2['unix']) - 1]
    if start_1 > end_1:
        e = start_1
        start_1 = end_1
        end_1 = e
    if start_2 > end_2:
        e = start_2
        start_2 = end_2
        end_2 = e
    start = max(start_1, start_2)
    end = min(end_1, end_2)
    if start >= end:
        print("No intersaticon by time", start_1, end_1, start_2, end_2)
        return
    df_1 = Utils.slice_by_tyme(df_1, start, end)
    df_2 = Utils.slice_by_tyme(df_2, start, end)
    df = Utils.sync_frames_by_time(df_1, df_2)
    path = "./DifTwo/" + exchange + token2 + "_" + token1 + ".csv"
    df.to_csv(path)


def prep_dif_two_every_token(exchange1, exchange2):
    tokens_1 = Utils.get_all_dirs_in_dir("./RawCrypto/" + exchange1)
    tokens_2 = Utils.get_all_dirs_in_dir("./RawCrypto/" + exchange2)
    tokens = []
    for token in tokens_1:
        if token in tokens_2:
            tokens.append(token)
    print("Fetching:", len(tokens), "tokens")
    for token in tokens:
        path = "./DifTwo/" + exchange1 + exchange2 + "_" + token + ".csv"
        if not exists(path):
            print("Preparing:", token)
            df_1 = gather_spot_crypto(exchange1, token)
            df_2 = gather_spot_crypto(exchange2, token)
            start_1 = df_1['unix'][0]
            start_2 = df_2['unix'][0]
            end_1 = df_1['unix'][len(df_1['unix']) - 1]
            end_2 = df_2['unix'][len(df_2['unix']) - 1]
            if start_1 > end_1:
                e = start_1
                start_1 = end_1
                end_1 = e
            if start_2 > end_2:
                e = start_2
                start_2 = end_2
                end_2 = e
            start = max(start_1, start_2)
            end = min(end_1, end_2)
            if start >= end:
                print("No intersaticon by time", start_1, end_1, start_2, end_2)
                continue
            df_1 = Utils.slice_by_tyme(df_1, start, end)
            df_2 = Utils.slice_by_tyme(df_2, start, end)
            df = Utils.sync_frames_by_time(df_1, df_2)
            if exchange1 > exchange2:
                e = exchange1
                exchange1 = exchange2
                exchange2 = e
            df.to_csv(path)
        else:
            print("Already prepared:", token)


def prep_dif_every_exchange():
    exchanges = Utils.get_all_dirs_in_dir("./RawCrypto/")
    print("Fetching", len(exchanges), "exchanges")
    for e1 in exchanges:
        for e2 in exchanges:
            if e1 == e2 or e1 > e2:
                continue
            print("Preparing dif", e1, e2)
            prep_dif_two_every_token(e1, e2)


def compare_two(exchange1, exchange2, token, start, end):
    print("Comparing:", exchange1, exchange2, token, start, end)
    if exchange1 > exchange2:
        e = exchange1
        exchange1 = exchange2
        exchange2 = e
    path = "./Transit/CompareTwo/"+exchange1+exchange2+"_"+token+"_"+str(start)+"_"+str(end)+".csv"
    if not exists(path):
        df = pd.read_csv("./DifTwo/" + exchange1 + exchange2 + "_" + token + ".csv")
        df = Utils.slice_dif_by_time(df, start, end)
        if len(df['unix']) == 0:
            print("No data for such time")
            return zip([0], [0])
        df = Utils.prep_dif(df)
        df = Utils.add_zeros(df)
        dur, height = zip(*Utils.pitch_duration(df))
        dur, height = zip(*Utils.slice_deviation(dur, height, 0.0, 100.0))
        a = {'dur': dur, 'height': height}
        del df
        df = pd.DataFrame(data=a)
        df.to_csv(path)
        return zip(dur, height)
    else:
        print("Already have csv")
        df = pd.read_csv(path)
        return zip(df['dur'].values, df['height'].values)


def show_liq(exchange1, exchange2, Token, start, end):
    if exchange1 > exchange2:
        e = exchange1
        exchange1 = exchange2
        exchange2 = e
    dur, height = zip(*compare_two(exchange1, exchange2, Token, start, end))
    if len(dur) == 1:
        return
    x, y = zip(*Utils.bottom_line(dur, height))
    a, b = Utils.calc_liq(dur, height)
    xx = [0.0, 10.0 * 1e7]
    yy = [b, 10.0 * 1e7 * a]
    plt.plot(dur, height, 'bo')
    plt.plot(x, y, color="red")
    date_start = datetime.fromtimestamp(int(start / 1000)).strftime("%m/%d/%Y")
    date_end = datetime.fromtimestamp(int(end/ 1000)).strftime("%m/%d/%Y")
    plt.title(str(date_start)+"_"+str(date_end)+" "
                                 +exchange1 + "/" + exchange2 + " " + Token + ": " + str(a[0][0]*1e7))
    plt.plot(xx, yy, color="green")
    plt.show()


def write_liq(exchange1, exchange2, tokens):
    if exchange1 > exchange2:
        e = exchange1
        exchange1 = exchange2
        exchange2 = e
    liq = []
    for i in range(0, len(tokens)):
        liq.append([])
    time = []
    for year in range(2016, 2023):
        time.extend([Utils.to_timestamp((1, i, year)) for i in range(1, 13, 3)])

    for k in range(0, len(tokens)):
        for i in range(0, len(time) - 1):
            dur, height = zip(*compare_two(exchange1, exchange2, tokens[k], time[i], time[i + 1]))
            if len(dur) == 1:
                liq[k].append(-1.0)
            else:
                a, b = Utils.calc_liq(dur, height)
                liq[k].append((a[0][0]*1e7))
    tokens.insert(0, 'end')
    tokens.insert(0, 'start')
    for i in range(0, len(time)):
        time[i] = datetime.fromtimestamp(int(time[i] / 1000)).strftime("%d/%m/%Y")
    time_start = time[1:]
    time_end = time[:-1]
    liq.insert(0, time_end)
    liq.insert(0, time_start)
    a = {tokens[i]: liq[i] for i in range(0, len(tokens))}
    return pd.DataFrame(a)


def write_liquidity_all():
    exchanges = Utils.get_all_dirs_in_dir("./RawCrypto/")
    print("Writing", len(exchanges), "exchanges")
    for e1 in exchanges:
        for e2 in exchanges:
            if e1 == e2 or e1 > e2:
                continue
            if not exists("./Liquidity/" + e1 + e2 + ".csv"):
                tokens_1 = set(Utils.get_all_dirs_in_dir("./RawCrypto/" + e1))
                tokens_2 = set(Utils.get_all_dirs_in_dir("./RawCrypto/" + e2))
                shared_tokens = tokens_1.intersection(tokens_2)
                df = write_liq(e1, e2, list(shared_tokens))
                df.to_csv("./Liquidity/" + e1 + e2 + ".csv")
            else:
                print("Already wrote:", e1, e2)



























