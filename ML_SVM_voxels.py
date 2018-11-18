
# coding: utf-8

# # SVMによるボクセルごとの学習と識別性能評価（時系列解析）

# ---
#
# 引数：div_rock.csv/div_scissor.csv/div_paper.csvがあるディレクトリまでのパス
#
# ---
#
# 入力：div_rock.csv/div_scissor.csv/div_paper.csv
#
# ---
#
# 出力：ACCURACY[loo or k_cv]_voxels_SVM.csv　識別性能評価結果一覧
#
# ---
#
# ボクセルごとに区切られた時系列データをSVMを用いて学習し，交差検証法（k-分割交差検証，leave-one-out交差検証）を用いて識別性能評価を行う．
# ベクトル：各ボクセルの区切られた時系列データ
#

# In[1]:

print('############# ML_SVM_voxels.py program excution ##############')


# In[2]:

import numpy as np
import pandas as pd
import sys

from sklearn import cross_validation
from sklearn import svm
from sklearn.model_selection import train_test_split


# コマンドライン引数でdiv_rock.csv/div_scissor.csv/div_paper.csvがあるディレクトリまでのパスを取得

# In[3]:

args = sys.argv
PATH = args[1]

# jupyter notebookのときはここで指定
# PATH = '../State-2fe_Active/20181029rn/64ch/8divData/'

# 検証手法
col_name = 'leave-one-out'

# ボクセル数
voxels = 7


# ## SVM_LOO関数
# 引数として教師データをX，ラベルをyで受け取る．
# 交差検証法の一つleave-one-out交差検証で識別精度評価を行う．
#
# * (1個をテストデータ，残りを教師データにして学習・評価) * すべてのデータ個
# * 得られたすべてのデータ個の評価結果（識別率）の平均を求めてパーセントに直す
# * 評価結果（識別率）をmain関数に返す

# In[4]:

def SVM_LOO(X, y):

    LOOscore = np.zeros(len(X))

    # 1個をテストデータ，残りを教師データにして学習・評価
    # すべてのデータに対して行う
    for i in range(len(X)):

        print('------ ' + str(i + 1) + ' / ' + str(len(X)) + '回 -----')

        # テストデータ
        X_test = X[i].reshape(1, -1)
        y_test = y[i].reshape(1, -1)

        # テストデータとして使用するデータを除いた教師データを作成
        X_train = np.delete(X, i, 0)
        y_train = np.delete(y, i, 0)

        # 線形SVMのインスタンスを生成
        model = svm.SVC(kernel = 'linear', C = 1)

        # モデルの学習
        model.fit(X_train, y_train)

        # 評価結果（識別率）を格納
        LOOscore[i] = model.score(X_test, y_test)


    # 評価結果（識別率）の平均を求める
    result = LOOscore.mean()

    # パーセントに直す
    result = round(result * 100, 1)

    print(str(LOOscore) + '\n')

    return result


# ## SVM_kCV関数
# 引数とし教師データをX，ラベルをyで受け取る．
# 交差検証法の一つk-分割交差検証で識別精度評価を行う．
#
# * 学習
# * (k分割し，1グループをテストデータ，残りグループを教師データにして評価) * k
# * 得られたk個の評価結果（識別率）の平均を求めてパーセントに直す
# * 評価結果（識別率）をmain関数に返す

# In[5]:

def SVM_kCV(X, y):

    # 線形SVMのインスタンスを生成
    model = svm.SVC(kernel = 'linear', C = 1)

    # k分割し，1グループをテストデータ，残りグループを教師データにして評価
    # すべてのグループに対して行う
    # 評価結果（識別率）を格納
    CVscore = cross_validation.cross_val_score(model, X, y, cv = cv_k)

    # 評価結果（識別率）の平均を求める
    result = CVscore.mean()

    # パーセントに直す
    result = round(result * 100, 1)

    print('k = ' + str(cv_k) + '：' + str(CVscore))

    return result



# ## TrainingData関数
# 引数として読み込みたいタスクごとのデータをrock,scissor,paperで受け取る．
# * 機械学習にかけれるようにデータのベクトル化とラベルを作成
# * ベクトル化したデータとラベルをmain関数に返す

# In[10]:

def TrainingData(rock, scissor, paper):

    # 各タスクのデータを縦結合
    all_data = pd.concat([rock, scissor, paper], axis = 0)

    # ベクトル化
    X = all_data.as_matrix()

    # ラベル作成 rock = 0, scissor = 1, paper = 2
    label_rock = np.zeros(len(rock.index))
    label_scissor = np.ones(len(scissor.index))
    label_paper = np.ones(len(paper.index)) * 2

    y = np.r_[label_rock, label_scissor, label_paper]


    return X, y




# ## main関数

# In[12]:

if __name__ == '__main__':

    # 読み込みたいファイルのパス
    PATH_rock = PATH + 'div_rock.csv'
    PATH_scissor = PATH + 'div_scissor.csv'
    PATH_paper = PATH + 'div_paper.csv'

    # csvファイル読み込み
    # headerは設定せず，転置後にset_index()する（header = 0にすると列名が変えられる）
    rock = pd.read_csv(PATH_rock, header = None).T
    rock = rock.set_index(0)

    scissor = pd.read_csv(PATH_scissor, header = None).T
    scissor = scissor.set_index(0)

    paper = pd.read_csv(PATH_paper, header = None).T
    paper = paper.set_index(0)

    # 分割数を求める：列数 / ボクセル数
    divNum = len(rock.columns) // voxels

    # 全ボクセルの識別率を格納するデータフレーム
    voxAc = pd.DataFrame(index = sorted(list(set(rock.index))), columns = [col_name])

    for i in range(voxels):

        # ボクセル名
        voxName = 'Voxel' + str(i+1)

        print(voxName)

        # 各ボクセルごとにデータを取得
        rockVox = rock.loc[voxName]
        scissorVox = scissor.loc[voxName]
        paperVox = paper.loc[voxName]


        # データとラベルの準備
        data, labels = TrainingData(rockVox, scissorVox, paperVox)


        # 学習と交差検証
        print('leave-one-out cross-validation')

        result_loo = SVM_LOO(data, labels)
        print(result_loo)

        # データフレームに格納
        voxAc.at[voxName, col_name] = result_loo



# In[13]:

# csv書き出し
PATH_RESULT = PATH + 'ACCURACY[loo]_voxels_SVM.csv'
voxAc.to_csv(PATH_RESULT, index = True)


# In[ ]:
