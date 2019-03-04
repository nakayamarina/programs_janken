
# coding: utf-8

# # SVMによるボクセルごとの学習と性能評価（単変量解析）
# ----
#
# 引数：raw_rock.csv/raw_scissor.csv/raw_paper.csvがあるディレクトリまでのパス
#
# ----
#
# 入力：raw_rock.csv/raw_scissor.csv/raw_paper.csv
#
# ----
#
# 出力：ACCURACY[loo or k_cv]_VOXunivariate_SVM.csv ボクセルごとの識別性能評価結果一覧
#
# ----
#
# ボクセルごとに単変量解析を行う．
# k分割交差検証法により1グループをテストデータの，k-1グループを教師データとし，SVMを用いて学習，精度評価．
# ベクトル：各ボクセルにおけるある時刻のZ-score（1ベクトル）

# In[12]:

print('############ ML_SVM_VOXunivariate_kCV.py program excution ############')


# In[13]:

import numpy as np
import pandas as pd
import sys
from sklearn import cross_validation
from sklearn import svm
from sklearn.model_selection import train_test_split


# In[17]:

args = sys.argv
PATH = args[1]

# jupyter notebookのときはここで指定
# PATH = '../State-2fe_SpmActive/20181029rn/mb/RawData/'

# 検証手法
kCV = 10

# 検証手法
col_name = str(kCV) + 'CV'


# ## SVM_kCV関数
# 引く数としてデータをX，ラベルをyで受け取る．
# 交差検証法の一つk分割交差検証法で識別精度評価を行う．

# In[18]:

def SVM_kCV(X, y):

    # 線形SVMのインスタンスを生成
    model = svm.SVC(kernel = 'linear', C = 1)

    # k分割し，1グループをテストデータ，残りグループを教師データにして評価
    # すべてのグループに対して行う
    # 評価結果（識別率）を格納
    CVscore = cross_validation.cross_val_score(model, X, y, cv = kCV)

    # 評価結果（識別率）の平均を求める
    result = CVscore.mean()

    # パーセントに直す
    result = round(result * 100, 1)

    print('k = ' + str(kCV) + '：' + str(CVscore))

    return result



# # main関数

# In[22]:

if __name__ == '__main__':

    # 読み込みたいファイルのパス
    PATH_rock = PATH + 'raw_rock.csv'
    PATH_scissor = PATH + 'raw_scissor.csv'
    PATH_paper = PATH + 'raw_paper.csv'

    # csvファイル読み込み
    # headerは設定せず，転置後にset_index()する（header = 0にすると列名が変えられる）
    rock = pd.read_csv(PATH_rock, header = 0, index_col = None).T
    scissor = pd.read_csv(PATH_scissor, header = 0, index_col = None).T
    paper = pd.read_csv(PATH_paper, header = 0, index_col = None).T


# In[24]:

# ボクセルの数
voxNum = len(rock)

# 全ボクセルの識別率を格納するデータフレーム
voxAc = pd.DataFrame(index = range(voxNum), columns = [col_name])

counter = 0
csvcounter = 0
voxNames = []

for voxNo in range(voxNum):

    voxName = 'Voxel' + str(voxNo + 1)
    print(voxName + '( ' + str(counter+1) + ' / ' + str(voxNum) + ' )')

    # ボクセルのデータを取得
    rockVox = rock.loc[voxName]
    scissorVox = scissor.loc[voxName]
    paperVox = paper.loc[voxName]

    # データセット作成
    rockVox_vec = np.ravel(rockVox)
    scissorVox_vec = np.ravel(scissorVox)
    paperVox_vec = np.ravel(paperVox)

    data = np.r_[rockVox_vec, scissorVox_vec, paperVox_vec]

    # データ数+1にするためにリシェイプ
    data = data.reshape(-1, 1)

    # ラベルを作成
    rockVox_label = np.zeros(len(rockVox_vec))
    scissorVox_label = np.ones(len(scissorVox_vec))
    paperVox_label = np.ones(len(paperVox_vec)) * 2

    labels = np.r_[rockVox_label, scissorVox_label, paperVox_label]

    # 学習と評価
    result_vox = SVM_kCV(data, labels)
    print(result_vox)

    # データフレームに格納
    voxAc.at[voxNo, :] = result_vox

    # 途中経過見る用
    # 何ボクセルで一度出力するか
    midNum = 1000

    if (counter % midNum == 0) and (counter != 0):

        PATH_test = PATH + 'ACMID' + str(csvcounter) + '[' + str(kCV) + 'cv]_VOXunivariate' + '_SVM.csv'
        print(PATH_test)
        MidVoxAc = voxAc.iloc[(csvcounter * midNum):((csvcounter + 1) * midNum), :]
        MidVoxAc.index = voxNames[(csvcounter * midNum):((csvcounter + 1) * midNum)]
        MidVoxAc.to_csv(PATH_test, index = True)

        csvcounter = csvcounter + 1

    counter = counter + 1
    voxNames = voxNames + [voxName]



# In[25]:

# 行名つける
voxAc.index = voxNames

# csv書き出し
PATH_RESULT = PATH + 'ACCURACY[' + str(kCV) + 'CV]_VOXunivariate' + '_SVM.csv'
voxAc.to_csv(PATH_RESULT, index = True)


# In[ ]:
