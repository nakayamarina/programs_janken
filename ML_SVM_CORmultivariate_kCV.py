
# coding: utf-8

# # SVMによる相関の高いボクセルを用いた学習と性能評価（多変量解析）
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
# 出力：ACCURACY[loo or k_cv]_CORmultivariate_SVM.csv ボクセルごとの識別性能評価結果一覧
#
# ----
#
# 相関の高いボクセルを用いて多変量解析を行う．
# k分割交差検証法により1グループをテストデータの，k-1グループを教師データとし，SVMを用いて学習，精度評価．
# ベクトル：各ボクセルにおけるある時刻のZ-score（ボクセル数ベクトル）

# In[1]:

print('############ ML_SVM_CORvariate_kCV.py program excution ############')


# In[2]:

import numpy as np
import pandas as pd
import sys
from sklearn import cross_validation
from sklearn import svm
from sklearn.model_selection import train_test_split


# In[43]:

args = sys.argv
PATH = args[1]

# jupyter notebookのときはここで指定
# PATH = '../State-2fe_MaskBrodmann/20181029su/mb/COR200vox_RawData/'

# 検証手法
kCV = 10

# 検証手法
col_name = str(kCV) + 'CV'


# ## SVM_kCV関数
# 引数としてデータをX，ラベルをyで受け取る．
# 交差検証法の一つk分割交差検証法で識別精度評価を行う．

# In[44]:

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

# In[45]:

if __name__ == '__main__':

    # 読み込みたいファイルのパス
    PATH_rock = PATH + 'raw_rock.csv'
    PATH_scissor = PATH + 'raw_scissor.csv'
    PATH_paper = PATH + 'raw_paper.csv'

    # csvファイル読み込み
    # headerは設定せず，転置後にset_index()する（header = 0にすると列名が変えられる）
    rock = pd.read_csv(PATH_rock, header = 0, index_col = 0)
    scissor = pd.read_csv(PATH_scissor, header = 0, index_col = 0)
    paper = pd.read_csv(PATH_paper, header = 0, index_col = 0)


# In[46]:

# 各タスクのデータを結合
all_data = pd.concat([rock, scissor, paper], axis = 0)

# ベクトル化
X = all_data.as_matrix()


# In[47]:

# ラベル作成 rock = 0, scissor = 1
label_rock = np.zeros(len(rock))
label_scissor = np.ones(len(scissor))
label_paper = np.ones(len(paper)) * 2

y = np.r_[label_rock, label_scissor, label_paper]


# In[48]:

# 学習と評価
result = SVM_kCV(X, y)
print(result)


# In[49]:

# データフレーム化する際のインデックス名作成
index_name = str(rock.shape[1]) + 'voxels'

# データフレーム化
result_df = pd.DataFrame({col_name:[result]}, index = [index_name])


# In[50]:

# csv書き出し
PATH_RESULT = PATH + 'ACCURACY[' + str(kCV) + 'CV]_CORmultivariate' + '_SVM.csv'
result_df.to_csv(PATH_RESULT)


# In[ ]:




# In[ ]:
