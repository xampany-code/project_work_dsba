from os import listdir
from os.path import isfile, join
import pandas as pd
import numpy as np
from datetime import datetime, date
import statistics
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression


def get_all_files_in_dir(dir_path):
    return [f for f in listdir(dir_path) if isfile(join(dir_path, f))]


def get_all_dirs_in_dir(dir_path):
    return [f for f in listdir(dir_path) if not isfile(join(dir_path, f))]


def merge_frames(files, heads):
    columns = []
    for i in range(0, len(heads)):
        columns.append([])
    for f in files:
        df = pd.read_csv(f)
        start = df['unix'][0]
        end = df['unix'][len(df['unix'])-1]
        if end > start:
            for i in range(0, len(heads)):
                (columns[i]).extend(df[heads[i]].values)
        else:
            for i in range(0, len(heads)):
                (columns[i]).extend(df[heads[i]].values[::-1])
    a = {heads[i]: columns[i] for i in range(0, len(heads))}
    return pd.DataFrame(a)


def slice_by_tyme(df, start_time, end_time):
    print("Slicing by time", start_time, end_time)
    unix = []
    value = []
    for i in range(0, len(df['unix'])):
        if start_time <= df['unix'][i] <= end_time:
            unix.append(df['unix'][i])
            value.append((df['open'][i]+df['close'][i])/2)
    abs_start = unix[0]
    abs_end = unix[len(unix) - 1]
    if abs_start > abs_end:
        unix = unix[::-1]
        value = value[::-1]
    a = {'unix': unix, 'value': value}
    del df
    return pd.DataFrame(a)


def slice_dif_by_time(df, start, end):
    print("Slicing difference by time", start, end)
    unix = []
    dif = []
    first = []
    second = []
    abs_start = df['unix'][0]
    abs_end = df['unix'][len(df['unix'])-1]
    if abs_start >= end or abs_end <= start:
        return pd.DataFrame({'unix': [], 'first': [], 'second': [], 'dif': []})
    for i in range(0, len(df['unix'])):
        if start <= df['unix'][i] <= end:
            unix.append(df['unix'][i])
            dif.append(df['dif'][i])
            first.append(df['first'][i])
            second.append(df['second'][i])
    a = {'unix': unix, 'first': first, 'second': second, 'dif': dif}
    del df
    return pd.DataFrame(a)


def sync_frames_by_time(df1, df2):
    print("Sync by time")
    x1 = df1['unix']
    y1 = df1['value']
    x2 = df2['unix']
    y2 = df2['value']
    index_1 = 0
    index_2 = 0
    x = []
    y_1 = []
    y_2 = []
    dif = []
    time = []
    l1 = len(x1)
    l2 = len(x2)
    while index_1 < l1 and index_2 < l2:
        date_1 = datetime.fromtimestamp(int(x1[index_1] / 1000))
        date_2 = datetime.fromtimestamp(int(x2[index_2] / 1000))
        if date_1 == date_2:
            x.append(x1[index_1])
            y_1.append(y1[index_1])
            y_2.append(y2[index_2])
            dif.append(y1[index_1] - y2[index_2])
            time.append(str(date_1))
            index_1 += 1
            index_2 += 1
        elif date_1 > date_2:
            index_2 += 1
            #print(date_2)
        else:
            index_1 += 1
            #print(date_1)
    print("removed:", max(len(x1), len(x2)) - len(x), "from:", max(len(x1), len(x2)))
    a = {'unix': x, 'time': time, 'first': y_1, 'second': y_2, 'dif': dif}
    del df1
    del df2
    return pd.DataFrame(a)


def prep_dif(df):
    print("Prepare difference")
    unix = []
    dif = []
    #print(df['first'])
    #mean_first = statistics.mean(df['first'])
    #mean_second = statistics.mean(df['second'])
    #s = (mean_second+mean_first)/2
    s = statistics.stdev(df['dif'])
    start = df['unix'][0]
    end = df['unix'][len(df['unix'])-1]
    length = end - start
    for i in range(0, len(df['unix'])):
        unix.append((df['unix'][i] - start))
        dif.append(df['dif'][i]/s)
    a = {'unix': unix, 'dif': dif}
    del df
    return pd.DataFrame(data=a)


def add_zeros(df):
    print("Adding zeros")
    unix = df['unix']
    dif = df['dif']
    length = len(unix)
    last_x = unix[0]
    last_y = dif[0]
    new_unix = [last_x]
    new_dif = [last_y]
    for i in range(1, length):
        cur_x = unix[i]
        cur_y = dif[i]
        if (cur_y < 0 and last_y > 0) or (cur_y > 0 and last_y < 0):
            v = ((last_x - cur_x)/(cur_y - last_y)) * last_y + last_x
            new_dif.append(0.0)
            new_unix.append(v)
        new_unix.append(cur_x)
        new_dif.append(cur_y)
        last_x = cur_x
        last_y = cur_y
    a = {'unix': new_unix, 'dif': new_dif}
    del df
    return pd.DataFrame(data=a)


def pitch_duration(df):
    print("Resolving pitch duration")
    height = []
    dur = []
    start = 0.0
    maxx = 0.0
    for i in range(0, len(df['unix'])):
        cur = df['dif'][i]
        if cur == 0:
            dur.append(df['unix'][i] - start)
            height.append(maxx)
            start = df['unix'][i]
            maxx = 0
        if abs(cur) > maxx:
            maxx = abs(cur)
    del df
    # height = height[:1]
    # dur = dur[:1]
    return zip(dur, height)


def slice_deviation(x, y, a, b):
    s = statistics.stdev(y)
    print("Slice deviation:", s*a, s*b)
    minn = s * a
    maxx = s * b
    x_ = []
    y_ = []
    for i in range(0, len(x)):
        if minn <= y[i] <= maxx:
            y_.append(y[i])
            x_.append(x[i])
    return zip(x_, y_)


def to_timestamp(a):
    day = a[0]
    month = a[1]
    year = a[2]
    return int(datetime(year, month, day).timestamp() * 1000)


def show(dur, height):
    plt.plot(dur, height, 'bo')
    plt.legend(['height', "duration"])
    plt.show()


def bottom_line(dur, height):
    count = 1000
    length = 5
    x = [float(i)/(count/length) for i in range(0, count)]
    v = [100.0] * count
    for i in range(0, len(dur)):
        d = dur[i]/1e7
        h = height[i]
        index = 0
        while index < count and x[index] < d:
            index += 1
        if index == 0 or index == count:
            continue
        if v[index] > h:
            v[index] = h
    a = []
    b = []
    for i in range(0, len(v)):
        if not v[i] >= 100:
            a.append(x[i]*1e7)
            b.append(v[i])
    s = np.array(b).std()
    m = np.array(b).mean()
    c = []
    d = []
    for i in range(0, len(a)):
        if abs(b[i]-m) <= 1.0*s:
            c.append(a[i])
            d.append(b[i])
    return zip(c, d)


def calc_liq(dur, height):
    print("Calculating liquidity")
    x, y = zip(*bottom_line(dur, height))
    x = np.array(x).reshape((-1, 1))
    y = np.array(y).reshape((-1, 1))
    model = LinearRegression()
    model.fit(x, y)
    r_sq = model.score(x, y)
    print("Precision:", r_sq)
    return model.coef_, model.intercept_


def from_timestamp(time):
    return datetime.fromtimestamp(int(time / 1000)).strftime("%d/%m/%Y")


def parse_time(s):
    r = s.split('/')
    return (int(r[0]), int(r[1]), int(r[2]))