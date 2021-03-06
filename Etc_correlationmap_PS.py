
# coding: utf-8

# # 相関マップ（Paper と Scissor）
# ---
# 引数：raw_paper.csv/raw_scissor.csvがあるディレクトリまでのパス
#
# ----
#
# 入力：raw_paper.csv/raw_scissor.csv
#
# ----
#
# 出力：correlationmap.csv ボクセルごとに相関を算出したもの一覧
#
# ---
# ボクセルごとに相関を算出する．
# 値のものほど相関が大きいということになるため，昇順に並べ替えておく．

# In[1]:

print('############ Etc_correlationmap.py program excution ############')


# In[2]:

import numpy as np
import pandas as pd
import sys


# In[3]:

args = sys.argv
PATH = args[1]

# jupyter notebookのときはここで指定
# PATH = '../State-2fe_SpmActive/20181029rn/mb/RawData/'


# In[4]:

# 読み込みたいファイルのパス
PATH_paper = PATH + 'raw_paper.csv'
PATH_scissor = PATH + 'raw_scissor.csv'

# csvファイル読み込み
# headerは設定せず，転置後にset_index()する（header = 0にすると列名が変えられる）
paper = pd.read_csv(PATH_paper, header = 0, index_col = None).T

scissor = pd.read_csv(PATH_scissor, header = 0, index_col = None).T


# In[5]:

# データフレームに格納されている値がstr型なのでfloat型にする
paper = paper.astype(float)
scissor = scissor.astype(float)


# In[7]:

# ボクセル数
voxNum = len(paper)

# 何ボクセル目かをカウント
counter = 0

# ボクセル名取得用
voxNames = []

# ボクセルごとの相関格納用
cormap = []

for voxNo in range(voxNum):

    voxName = 'Voxel' + str(voxNo + 1)

    # ボクセルのデータを取得
    paperVox = paper.loc[voxName]
    scissorVox = scissor.loc[voxName]

    # array型に変換，各試行を一つにまとめる
    paperar = np.array(paperVox).reshape(-1)
    scissorar = np.array(scissorVox).reshape(-1)

    # 相関を求める
    cor_matrix = np.corrcoef(paperar, scissorar)

    # 相関行列という形になっているので相関係数を取得
    cor = cor_matrix[0][1]

    # 求めた相関係数の絶対値を格納
    cormap = cormap + [abs(cor)]

    print(voxName + '( ' + str(counter+1) + ' / ' + str(voxNum) + ' ) : ' + str(cor))

    counter = counter + 1
    voxNames = voxNames + [voxName]


# In[8]:

# 相関一覧をデータフレーム化
cormap = pd.DataFrame(cormap)

# カラム名，インデックス名をつける
cormap.index = voxNames
cormap.columns = ['Correlation']


# In[9]:

# 相関の大き順に並べ替え
cormap_sort = cormap.sort_values('Correlation', ascending = False)


# In[10]:

# csv書き出し
PATH_cormap = PATH + 'correlationmap_PS.csv'
cormap_sort.to_csv(PATH_cormap)


# In[11]:

# 相関一覧をデータフレーム化
cormap = pd.DataFrame(cormap)

# カラム名，インデックス名をつける
cormap.index = voxNames
cormap.columns = ['Correlation']
# 相関の大き順に並べ替え
cormap_sort = cormap.sort_values('Correlation', ascending = False)


# In[ ]:
