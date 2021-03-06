
# coding: utf-8

# # 一次元CNNによる学習と識別性能評価（TDA）

# ---
#
# 引数：TDAvec_autocor_rock_(パラメータ).csv/TDAvec_autocor_scissor_(パラメータ).csv/TDAvec_autocor_paper_(パラメータ).csvがあるディレクトリまでのパス
#
# ---
#
# 入力：TDAvec_autocor_rock_(パラメータ).csv/TDAvec_autocor_scissor_(パラメータ).csv/TDAvec_autocor_paper_(パラメータ).csv
#
# ---
#
# 出力：ACCURACY[loo or k_cv]_TDAautocor(パラメータ)_1dCNN.csv　識別性能評価結果一覧
#
# ---
#
# 1dCNNを用いて学習し，交差検証法（k-分割交差検証，leave-one-out交差検証）を用いて識別性能評価を行う．
# ベクトル：時系列データにTDAを適用したもの

# In[10]:

print('########### ML_1dCNN_TDAautocor.py program excution ############')


# In[11]:

import pandas as pd
import sys

# matplotlib inline部分は.pyの時にはコメントアウトしないとエラー出る！

import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
# get_ipython().magic('matplotlib inline')
import matplotlib.pyplot as plt
from keras.layers.convolutional import Conv1D, UpSampling1D
from keras.layers.pooling import MaxPooling1D
from keras.utils import np_utils

from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split


# コマンドライン引数でraw_rock.csv/raw_scissor.csv/raw_paper.csvファイルがあるディレクトリまでのパスを取得

# In[12]:

args = sys.argv
PATH = args[1]

# jupyter notebookのときはここで指定
# PATH = '../State-2fe_Active/20181029rn/64ch/RawData/'

# 検証手法
col_name = 'leave-one-out'

# 機械学習するデータ（csvファイルのパラメータ名前）
PM_kizami = ['100', '300']
PM_hole = ['01dim', '012dim']


# ## ONEdCNN_LOO関数

# 引数として教師データをX，ラベルをyで受け取る．
# 交差検証法の一つleave-one-out交差検証で識別精度評価を行う．
#
# * (1個をテストデータ，残りを教師データにして学習・評価) * すべてのデータ個
# * 得られたすべてのデータ個の評価結果（識別率）の平均を求めてパーセントに直す
# * 評価結果（識別率）をmain関数に返す

# In[13]:

def ONEdCNN_LOO(X, y):

    # 識別率を格納する配列
    LOOscore = np.zeros(len(X))

    # ベクトルの長さを格納しておく
    bach_size = X.shape[1]


    # 1個をテストデータ，残りを教師データにして学習・評価
    # すべてのデータに対して行う
    for i in range(len(X)):

        print('------ ' + str(i) + ' / ' + str(len(X)) + '回 -----')

        # テストデータ
        X_test = X[i]
        y_test = y[i]

        # テストデータとして使用するデータを除いた教師データを作成
        X_train = np.delete(X, i, 0)
        y_train = np.delete(y, i, 0)


        # （データ数, ベクトルの長さ，1）という形にリシェイプする
        X_train = np.reshape(X_train, (-1, bach_size, 1))
        X_test = np.reshape(X_test, (-1, bach_size, 1))

        # ダミー変数に変換：何分類するかによって数字を書き換える（rock,scissor,paperの３分類なので3）
        y_train = np_utils.to_categorical(y_train, 3)
        y_test = np_utils.to_categorical(y_test, 3)


        # 1次元CNNのインスタンスを作成
        # 参考文献（Time series classification via TDA）に従ってパラメータを設定
        # 1st Conv1d : kernel_number = 7, kernel_size = 6
        # 1st MacPooling : kernel_number = 7
        # 2nd Conv1d : kernel_number = 7, kernel_size = 2
        # 2nd MacPooling : kernel_number = 3
        # Flattenで1次元に
        model = Sequential()
        model.add(Conv1D(7, 6, padding='same', input_shape=(bach_size, 1)))
        model.add(Activation('relu'))
        model.add(MaxPooling1D(7, padding='same'))
        model.add(Conv1D(7, 2, padding='same', activation='relu'))
        model.add(MaxPooling1D(3, padding='same'))

        model.add(Flatten())

        # 何分類するかによってunitsを書き換える（rock,scissor,paperの３分類なのでunits=3）
        model.add(Dense(units=3, activation='softmax'))
        model.compile(loss='mse', optimizer='adam', metrics=["accuracy"])

        # 学習
        history = model.fit(X_train, y_train, epochs=100)

        # 評価結果（識別率）を格納
        score = model.evaluate(X_test, y_test)
        LOOscore[i] = score[1]



    # 評価結果（識別率）の平均を求める
    result = LOOscore.mean()

    # パーセントに直す
    result = round(result * 100, 1)

    print(str(LOOscore) + '\n')

    return result


# ## ONEdCNN_kCV関数

# 引数として教師データをX，ラベルをyで受け取る．
# 交差検証法の一つk-分割交差検証で識別精度評価を行う．
#
# * 学習
# * (k分割し，1グループをテストデータ，残りグループを教師データにして評価) * k
# * 得られたk個の評価結果（識別率）の平均を求めてパーセントに直す
# * 評価結果（識別率）をmain関数に返す

# In[14]:

def ONEdCNN_kCV(X, y):


    # 識別率を格納する配列
    kCVscore = np.zeros(cv_k)

    # ベクトルの長さを格納しておく
    bach_size = X.shape[1]

    # 分割数
    kf = KFold(n_splits=cv_k, shuffle=False)
    # 繰り返し回数
    i = 0

    for train_index, eval_index in kf.split(X):

        print('------ ' + str(i) + ' / ' + str(cv_k) + '回 -----')

        X_train, X_test = X[train_index], X[eval_index]
        y_train, y_test = y[train_index], y[eval_index]

        # （データ数, ベクトルの長さ，1）という形にリシェイプする
        X_train = np.reshape(X_train, (-1, bach_size, 1))
        X_test = np.reshape(X_test, (-1, bach_size, 1))

        # ダミー変数に変換：何分類するかによって数字を書き換える（rock,scissor,paperの３分類なので3）
        y_train = np_utils.to_categorical(y_train, 3)
        y_test = np_utils.to_categorical(y_test, 3)


        # 1次元CNNのインスタンスを作成
        # 参考文献（Time series classification via TDA）に従ってパラメータを設定
        # 1st Conv1d : kernel_number = 7, kernel_size = 6
        # 1st MacPooling : kernel_number = 7
        # 2nd Conv1d : kernel_number = 7, kernel_size = 2
        # 2nd MacPooling : kernel_number = 3
        # Flattenで1次元に
        model = Sequential()
        model.add(Conv1D(7, 6, padding='same', input_shape=(bach_size, 1)))
        model.add(Activation('relu'))
        model.add(MaxPooling1D(7, padding='same'))
        model.add(Conv1D(7, 2, padding='same', activation='relu'))
        model.add(MaxPooling1D(3, padding='same'))

        model.add(Flatten())

        # 何分類するかによってunitsを書き換える（rock,scissor,paperの３分類なのでunits=3）
        model.add(Dense(units=3, activation='softmax'))
        model.compile(loss='mse', optimizer='adam', metrics=["accuracy"])

        # 学習
        history = model.fit(X_train, y_train, epochs=100)

        # 評価結果（識別率）を格納
        score = model.evaluate(X_test, y_test)
        kCVscore[i] = score[1]

        i = i + 1


    # 評価結果（識別率）の平均を求める
    result = kCVscore.mean()

    # パーセントに直す
    result = round(result * 100, 1)

    print('k = ' + str(cv_k) + '：' + str(kCVscore))

    return result


# ## TrainingData関数
# 引数として読み込みたいタスクごとのファイル名をfile_rock/file_scissor/file_paperで受け取る．
# * 機械学習にかけれるようにデータのベクトル化とラベルを作成
# * ベクトル化したデータとラベルをmain関数に返す

# In[18]:

def TrainingData(file_rock, file_scissor, file_paper):

    # 読み込みたいファイルのパス
    PATH_rock = PATH + file_rock
    PATH_scissor = PATH + file_scissor
    PATH_paper = PATH + file_paper

    # csvファイル読み込み（転地することでベクトルを時系列データとする）
    rock = pd.read_csv(PATH_rock, header = 0)
    scissor = pd.read_csv(PATH_scissor, header = 0)
    paper = pd.read_csv(PATH_paper, header = 0)

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

# In[19]:

if __name__ == '__main__':

    for kizami in range(len(PM_kizami)):

        for hole in range(len(PM_hole)):

            PM_dataName = PM_hole[hole] + PM_kizami[kizami]

            # 機械学習するデータ（提案手法でベクトル化したcsvファイル）
            ML_rockData = 'TDAvec_autocor_rock_' + PM_dataName + '.csv'
            ML_scissorData = 'TDAvec_autocor_scissor_' + PM_dataName + '.csv'
            ML_paperData = 'TDAvec_autocor_paper_' + PM_dataName + '.csv'


            # データとラベルの作成
            data, labels = TrainingData(ML_rockData, ML_scissorData, ML_paperData)


            # 学習とleave-one-out交差検証法

            print('leave-one-out Cross-Validation : ' + PM_dataName)

            result_loo = ONEdCNN_LOO(data, labels)

            # データフレーム化
            result_loo = pd.DataFrame({col_name:[result_loo]}, index = ['TDA(' + PM_dataName + ') + 1dCNN'])
            print(result_loo)

            # csv書き出し
            PATH_RESULT = PATH + 'ACCURACY[loo]_TDAautocor' + PM_dataName + '_1dCNN.csv'
            result_loo.to_csv(PATH_RESULT, index = True)



# In[ ]:
