
# coding: utf-8

# ## fMRI時系列データを区切る前処理
# ----
#
# 引数：raw_rock.csv/raw_scissor.csv/raw_paper.csvがあるディレクトリまでのパス，分割数
#
# ----
#
# 入力：raw_rock.csv/raw_scissor.csv/raw_paper.csv
#
# ----
#
# 出力： /(分割数)divData/div_rock.csv, /(分割数)divData/div_scissor.csv, /(分割数)divData/div_paper.csv
#
# ----
#
# State Designで計測したfMRIデータを数ブロックに区切る．（ボクセルごとに識別率を算出するため）

# In[3]:

print('########### Preprocessing_divided.py program excution ##########')


# In[5]:

import glob
import sys
import pandas as pd
import matplotlib.pyplot as plt
import os


# コマンドライン引数でraw_rock.csv/raw_scissor.csv/raw_paper.csvがあるディレクトリまでのパスと分割数を取得

# In[6]:

args = sys.argv
PATH = args[1]
divNum = int(args[2])

# jupyter notebookのときはここで指定
# PATH = '../State-2fe_Active/20181029rn/64ch/RawData/'
# divNum = 8


# 後で出力するcsvファイルを保存するディレクトリを作成

# In[7]:

# 作成したいディレクトリ名・パス
DIR_div = PATH + '../' + str(divNum) + 'divData'
PATH_div = DIR_div + '/'

# 既に存在する場合は何もせず，存在していない場合はディレクトリ作成
if not os.path.exists(DIR_div):
    os.mkdir(DIR_div)


# # DataDiv関数
# 引数としてボクセルの時系列fMRIデータをvoxで受け取る.
# divNum(分割数)に応じて一つの時系列fMRIデータを分割し，横結合することで新しいデータフレームを生成．

# In[8]:

def DataDiv(vox):

    # ボクセルのfMRIデータをdivNum分割したデータ格納用データフレーム
    voxData = pd.DataFrame(index = [], columns = [])

    # divNum分割した時の1ブロックあたりのscan数
    divScan = len(vox) // divNum

    for i in range(divNum):

        # データを分割
        divVox = vox.iloc[(divScan*i):(divScan*(i+1))]

        # データフレームに結合するためには行名を合わせとく必要があるので連番を行名とする
        divVox.index = range(divScan)

        # 新しいデータフレームに追加
        voxData = pd.concat([voxData, divVox], axis = 1)

    return voxData


# # main関数

# In[15]:

if __name__ == '__main__':

    # 読み込みたいファイルのパス
    PATH_rock = PATH + 'raw_rock.csv'
    PATH_scissor = PATH + 'raw_scissor.csv'
    PATH_paper = PATH + 'raw_paper.csv'

    # csvファイル読み込み
    rock = pd.read_csv(PATH_rock, header = 0)
    scissor = pd.read_csv(PATH_scissor, header = 0)
    paper = pd.read_csv(PATH_paper, header = 0)



# In[16]:

# rock時の全ボクセルをdivNum分割してまとめたデータ格納用データフレーム
rockData = pd.DataFrame(index = [], columns = [])

for i in rock.columns:

    # ボクセルごとにdivNum分割
    rockVox = DataDiv(rock[i])

    # 全ボクセルをまとめていく
    rockData = pd.concat([rockData, rockVox], axis = 1)


# In[17]:

# csv書きだし
PATH_rock = PATH_div + 'div_rock.csv'
rockData.to_csv(PATH_rock, index = False)


# In[18]:

# scissor時の全ボクセルをdivNum分割してまとめたデータ格納用データフレーム
scissorData = pd.DataFrame(index = [], columns = [])

for i in scissor.columns:

    # ボクセルごとにdivNum分割
    scissorVox = DataDiv(scissor[i])

    # 全ボクセルをまとめていく
    scissorData = pd.concat([scissorData, scissorVox], axis = 1)


# In[19]:

# csv書きだし
PATH_scissor = PATH_div + 'div_scissor.csv'
scissorData.to_csv(PATH_scissor, index = False)


# In[20]:

# paper時の全ボクセルをdivNum分割してまとめたデータ格納用データフレーム
paperData = pd.DataFrame(index = [], columns = [])

for i in paper.columns:

    # ボクセルごとにdivNum分割
    paperVox = DataDiv(paper[i])

    # 全ボクセルをまとめていく
    paperData = pd.concat([paperData, paperVox], axis = 1)


# In[21]:

# csv書きだし
PATH_paper = PATH_div + 'div_paper.csv'
paperData.to_csv(PATH_paper, index = False)


# In[ ]:
