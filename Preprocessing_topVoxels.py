
# coding: utf-8

# # 全ボクセルファイルから指定ボクセルのみのZ-scoreを抽出
# ----
#
# 引数：raw_rock.csv/raw_scissor.csv/raw_paper.csvがあるディレクトリまでのパス
#
# ----
#
# 入力：raw_rock.csv/raw_scissor.csv/raw_paper.csv/ボクセルをランク順位にしたcsvファイル/指定するボクセル数(k)
#
# ----
#
# 出力：
# * (指定するボクセル数(k))vox_RawData/raw_rock.csv：指定したボクセルにおけるグーの時のZ-score
# * (指定するボクセル数(k))vox_RawData/raw_scissor.csv：指定したボクセルにおけるチョキの時のZ-score
# * (指定するボクセル数(k))vox_RawData/raw_paper.csv：指定したボクセルにおけるパーの時のZ-score
# ----
#
# ボクセルをランク順にしたファイル(correlationmap.csvやACCURACY_BA...csv)をから上位k個のボクセル名を取得する．
# 取得したボクセル名と一致するものをrawファイルから探し，Z-scoreを抽出する．この時のデータは新しく作ったディレクトリに保存する．
#

# In[1]:

print('########## Preprocessing_topVoxels.py program excution ############')


# In[2]:

import glob
import sys
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np


# In[3]:

args = sys.argv
PATH_pre = args[1]

# jupyter notebookのときはここで指定
# PATH_pre = '../State-2fe_SpmActive/20181029rn/mb/RawData/'

# 何ボクセル取得するか
k_list = [10, 15, 30, 45, 200]


# In[4]:

# ボクセルをランク順にしたファイル名
rankFile = 'correlationmap.csv'

# なんのランクか
rankName = 'COR'


# # extraction_vox関数
# もとのrawファイルに記録されているZ-scoreをdata，上位k個のボクセル名をインデックスとしたデータフレームをrank_k，タスク名をtask，新しいRawDataのディレクトリのパスをpathで取得．
# 上位k個に含まれるボクセルのZ-scoreを抽出，csvファイル書き出し

# In[5]:

def extraction_vox(data, rank_k, task, path):


    # インデックスでmergeすることで，dataとrank_kの共通インデックスのみを抽出
    data_k = pd.merge(data, rank_k, left_index = True, right_index = True)

    # もとのrawファイルと同様の形にするため転地
    data_k = data_k.T

    # csv書き出し
    PATH_file = path + task
    print(PATH_file)

    data_k.to_csv(PATH_file)


# # main関数

# In[8]:

if __name__ == '__main__':

    # 読み込みたいファイルのパス
    rock_name = 'raw_rock.csv'
    PATH_rock = PATH_pre + rock_name

    scissor_name = 'raw_scissor.csv'
    PATH_scissor = PATH_pre + scissor_name

    paper_name = 'raw_paper.csv'
    PATH_paper = PATH_pre + paper_name

    # csvファイル読み込み
    # headerは設定せず，転置後にset_index()する（header = 0にすると列名が変えられる）
    rock = pd.read_csv(PATH_rock, header = 0, index_col = 0).T
    scissor = pd.read_csv(PATH_scissor, header = 0, index_col = 0).T
    paper = pd.read_csv(PATH_paper, header = 0, index_col = 0).T

    # ボクセルをランク順にしたファイル
    PATH_rank = PATH_pre + rankFile
    rank = pd.read_csv(PATH_rank, index_col = 0)


# In[11]:

for k in (k_list):

    print('k = ' + str(k))

    # 新しいRawDataのディレクトリ名・パス
    DIR = PATH_pre + '../' + rankName + str(k) + 'vox_RawData'
    PATH = DIR + '/'

    # すでに存在する場合は何もせず，存在していない場合はディレクトリ作成
    if not os.path.exists(DIR):
        os.mkdir(DIR)


    # 上位k個のボクセル名をデータフレームのインデックスとして取得
    # ボクセル名のみが欲しい，データフレームの要素は不要
    rank_k = rank.iloc[0:k, :]
    rank_k = pd.DataFrame(index = list(rank_k.index), columns = [])

    # extraction_vox関数
    extraction_vox(rock, rank_k, rock_name, PATH)
    extraction_vox(scissor, rank_k, scissor_name, PATH)
    extraction_vox(paper, rank_k, paper_name, PATH)


# In[ ]:




# In[ ]:
