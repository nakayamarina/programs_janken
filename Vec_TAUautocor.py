
# coding: utf-8

# # 各ボクセルごとの時間遅れτを求める
# ### 自己相関関数が最初に極小値をとる時刻
# ---
#
# 引数：raw_rock.csv/raw_scissor.csv/raw_paper.csvがあるディレクトリまでのパス
#
# ---
#
# 入力：raw_rock.csv/raw_scissor.csv/raw_paper.csv
#
# ---
#
# 出力：rock，scissor，paper時の各ボクセルの時間遅れτをまとめたもの
#
# ---
#
# 時系列特性を得るために3次元空間に写像する．
# 時系列データにおいて，ある時刻tの値をx軸，t+τ（時間遅れ）の値をy軸，t+2*τの値をz軸に写像すると，
# 特徴的な軌道を描くとされている（カオス理論）．
# 時間遅れτの求め方はいくつかあるが，このプログラムでは時系列データ（各ボクセルのデータ）の自己相関関数が最初に極小値をとる時刻をτとする．

# In[1]:

print('########## TAUautocor.py program excution ############')


# In[32]:

import numpy as np
from scipy import signal
import sys
import pandas as pd


# コマンドライン引数でraw_tap.csv/raw_rest.csvがあるディレクトリまでのパスを取得

# In[33]:

args = sys.argv
PATH = args[1]

# jupyter notebookのときはここで指定
# PATH = '../State-2fe_Active/20181029rn/mb/RawData/'

# 読み込みたいファイルのパス
PATH_rock = PATH + 'raw_rock.csv'
PATH_scissor = PATH + 'raw_scissor.csv'
PATH_paper = PATH + 'raw_paper.csv'


# ## autocor関数
# 引数としてmain関数で読み込んだデータをdataで受け取る．
# rock，scissor，paperの各ボクセルごとの自己相関関数が最初に極小値をとる時刻を調べる --> csvファイルで書き出し

# In[34]:

def autocor(data):

    # 求めた値を入れる
    TAUs = []

    # ボクセル（列）の数だけ繰り返す
    for i in range(len(data.columns)):

        # i番目のボクセルデータ抽出
        voxel = data.iloc[:, i]

        # 自己相関関数
        x = np.correlate(voxel, voxel, mode = 'full')

        # 極小値のインデックス一覧
        first_min = signal.argrelmin(x)

        # 「最初に極小値をとるときの値」なので最初の値をTAUsに追加
        TAUs.append(first_min[0][0])

    print(TAUs)

    return TAUs


# ## main関数
#
# * tap_raw.csv/rest_raw.csv読み込み
# * autcor関数呼び出し

# In[35]:

if __name__ == '__main__':

    # csvファイル読み込み
    rock = pd.read_csv(PATH_rock, header = 0)
    scissor = pd.read_csv(PATH_scissor, header = 0)
    paper = pd.read_csv(PATH_paper, header = 0)



# In[36]:

tau_rock = autocor(rock)


# In[37]:

tau_scissor = autocor(scissor)


# In[38]:

tau_paper = autocor(paper)


# In[39]:

# RestとTappingの各ボクセルごとの時間遅れTAUを整形
TAUs = pd.DataFrame({'1':tau_rock, '2':tau_scissor, '3':tau_paper})
TAUs.columns = ['rock', 'scissor', 'paper']


# In[40]:

# csv書き出し
PATH_TAU = PATH + 'TAUautocor.csv'
TAUs.to_csv(PATH_TAU, index = False)


# In[ ]:
