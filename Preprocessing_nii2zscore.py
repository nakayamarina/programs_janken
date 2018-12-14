
# coding: utf-8

# # NiftiファイルからZ-scoreを自動抽出
# ---
#
# 引数：4D化した.niiファイルがあるフォルダまでのパス / 書き出すcsvの保存先 / mask名
#
# ---
#
# 入力：4D化した.niiファイルがあるフォルダまでのパス / 書き出すcsvの保存先 / mask名（chunks_list.csv, targets_list.csv）
#
# ---
#
# 出力：all_raw.csv / raw_rock.csv / raw_scissor.csv / raw_paper.csv（chunks_list.csv, targets_list.csv）
#
# ---
#
# 注意：このプログラムはUbuntuでやったほうがいいかも（抽出する部位が多いほどデータが重くなってメモリがたりなくなる！）
#
#
# 注意：このプログラムを実行する前に以下の作業をすること
#
# 3D脳画像データ（前処理済みの.niiファイル）を4Dに変換
#
# 1. SPM起動
# 2. Batchを開く
# 3. 画面左上SPM → Util → 3D to 4D File Conversion
# 3. 3D Volumesから4Dに変換したいファイル('swr'のついたniftiファイル全て)を選択
# 4. Output Filenameでファイル名を指定
# 5. 再生ボタンを押す
#
# Motor mask（Z-score化したいボクセルの位置）の作成
# ※ wfu_pickatlasはmatlabサーバーで実行（Macだと.nii形式で保存できなかった）
# ※ 中山メモ：ubuntuでshareで作業するにはmatlabまで移動してshareを開く，基本的にsudoを使って作業（matlabもsudoで起動）
#
# 1. wfu_pickatlasフォルダをダウンロード（ネットから or Shareかnakayamaフォルダのどっかにある）
# 2. MATLABでwfu_pickatlasフォルダのパスを通す
# 3. MATLABコマンドライン上で > wfu_pickatlas で起動
# 4. 画面左からマスクしたい部分を選択（全脳の場合は TD Hemispheres を全選択）
# 5. SAVE MASKからマスク画像をmaskとして保存（名前に'-'とか入れない）
# 6. SPM → fMRI起動
# 7. MenuからNormalize(Est & Wri)を選択
# 8. Bath Editorが立ち上がったらDataをダブルクリック
# 9. Image to Alignには'swr'がファイル名についているniftiファイルを適当に1つ選択
# 10. Image to Writeには先ほど作成したmaskファイルを選択
# 11. 再生ボタンを押す → wmask.niiができる
# 12. Batch Editorに戻りRealign(Reslice)を選択
# 13. Imagesをダブルクリック
# 14. 'swr'がファイル名についているniftiファイルを適当に一つ，先ほどできたwmask.niiファイルの順で選択
# 15. 再生ボタンを押す → rwmask.niiができる
#
#
# ※作成したrwmask.niiはどの部位のマスクかわかるように名前を変えている
# ・rwBA.nii：ブロードマンエリア全て
# ・rwmask12346.nii：ブロードマンエリア1,2,3,4,6

# In[2]:

from mvpa2.suite import *
from mvpa2.datasets.mri import fmri_dataset
import os
import os.path
from os.path import join as pathjoin
from pprint import pprint
# from nifti import NiftiImage
import glob
import numpy as np
import pandas as pd
import sys
import pickle
# import dill
import csv

import nibabel as nib

# !!!!!!!!!! scan_numらへん，dataset，zscoreのパラメータ書き換え


# コマンドライン引数で.niiファイルがあるディレクトリまでのパスを取得．

# In[7]:

args = sys.argv
PATH = args[1]
PATH_save = args[2]
MASK_name = args[3]

# jupyter notebookのときはここで指定
# PATH = '../../Data_mri/junkenState-2fe/20181029rn/64ch/'
# PATH_save = '../State-2fe_MaskMotor/20181029rn/64ch/'
# MASK_name = 'rwmask12346.nii'

PATH_mask = PATH + MASK_name

# 前処理済みならswrがついた.niiファイルを選択
PATH_nii = PATH + '4D.nii'



# In[8]:

# RawDataのディレクトリ名・パス
DIR_RAW = PATH_save + 'RawData'
PATH_RAW = DIR_RAW + '/'

# すでに存在する場合は何もせず，存在していない場合はディレクトリ作成
if not os.path.exists(DIR_RAW):
    os.mkdir(DIR_RAW)


# In[9]:

headcoil = PATH.split('/')[5]

if headcoil == 'mb':

    # 総スキャン数
    scan_num = 940

    # TR = 1の時のrestのスキャン数
    restNum = 26

    # 1タスクのスキャン数
    taskNum = 296

elif headcoil == '64ch':

    # 総スキャン数
    scan_num = 300

    # TR = 3の時のrestのスキャン数
    restNum = 6

    # 1タスクのスキャン数
    taskNum = 96


# ## splitTaks関数
#
# 全てのZ-scoreをまとめたものdataで受け取り，Rock時とscissor時とpaper時のデータを分けてcsvファイルで書き出し

# In[33]:

def splitTask(brain):

    # 各タスクごとのマスク作成
    maskRock = ([False] * restNum) + ([True] * taskNum) + ([False] * taskNum) + ([False] * taskNum) + ([False] * restNum)
    maskScissor = ([False] * restNum) + ([False] * taskNum) + ([True] * taskNum) + ([False] * taskNum) + ([False] * restNum)
    maskPaper = ([False] * restNum) + ([False] * taskNum) + ([False] * taskNum) + ([True] * taskNum) + ([False] * restNum)

    # mask適用
    dataRock = brain[maskRock]
    dataScissor = brain[maskScissor]
    dataPaper = brain[maskPaper]

    # csv書き出し
    PATH_rock = PATH_RAW + 'raw_rock.csv'
    dataRock.to_csv(PATH_rock, index = False)
    print(PATH_rock)

    PATH_scissor = PATH_RAW + 'raw_scissor.csv'
    dataScissor.to_csv(PATH_scissor, index = False)
    print(PATH_scissor)

    PATH_paper = PATH_RAW + 'raw_paper.csv'
    dataPaper.to_csv(PATH_paper, index = False)
    print(PATH_paper)


# # main関数

# * fMRIデータ（niftiファイル）読み込み
# * 全ボクセルデータZ-score化，抽出，書きだし

# In[29]:

if __name__ == '__main__':

    # 4D化した.niiファイル名リストを作成

    nifti = [PATH_nii]


    # In[30]:

    # 教師データの作成（この作業なしにやる方法がわからないので，必要のない作業ではあるがやる）

    task = ['-1'] * restNum
    task0 = ['0'] * taskNum
    task1 = ['1'] * taskNum
    task2 = ['2'] * taskNum
    task3 = ['-1'] * restNum

    task.extend(task0)
    task.extend(task1)
    task.extend(task2)
    task.extend(task3)

    target = pd.DataFrame(task)

    PATH_target = PATH + 'targets_list.csv'
    target.to_csv(PATH_target, index = False, header = None)
    print('target')

    targets_list = []

    targets_file = open(PATH_target, 'rU')
    dataReader = csv.reader(targets_file)

    for row in dataReader:
        targets_list.append(row[0])


    # In[31]:

    # チャンク（試行数リスト？）の作成（この作業なしにやる方法がわからないので，必要のない作業ではあるがやる）

    chunk = ['1'] * scan_num

    chunks = pd.DataFrame(chunk)

    PATH_chunk = PATH + 'chunks_list.csv'
    chunks.to_csv(PATH_chunk, index = False, header = None)
    print('chunks')

    chunks_list = []

    chunks = open(PATH_chunk, 'rU')

    for x in chunks:
        chunks_list.append(x.rstrip('\r\n'))

    chunks.close()


    # In[21]:

    # データセットの整形

    dataset = fmri_dataset(nifti, targets=targets_list, chunks=chunks_list, mask=PATH_mask ,sprefix='voxel', tprefix='time', add_fa=None)

    print('dataset ready')

    poly_detrend(dataset, polyord=1, chunks_attr='chunks')

    dataset = dataset[np.array([l in ['-1', '0', '1', '2']
                               for l in dataset.targets], dtype='bool')]


    # In[22]:

    # Z-score抽出 → データフレーム化
    zscore(dataset, chunks_attr='chunks', param_est=('targets', ['0', '1', '2']), dtype='float32')
    print('z-score')

    VoxelData = pd.DataFrame(np.array(dataset[:,:]))
    print(VoxelData .shape)


    # In[23]:

    voxName = []

    for i in range(len(VoxelData.columns)):

        name = 'Voxel' + str(i+1)
        print(name)

        voxName.append(name)

    VoxelData.columns = voxName


    # In[24]:

    # 全データのcevファイル書き出し
    PATH_all = PATH_RAW + 'all_raw.csv'
    VoxelData.to_csv(PATH_all, index = False)
    print(PATH_all)


    # In[34]:

    splitTask(VoxelData)


# In[27]:




# In[19]:

# もしデータセットの整形でサイズエラーが出た時は以下で.niiファイル読み込みしてサイズを確認する
# nii0 = nib.load('../../Data_mri/tappingState-2fe/20181029rn/64ch/wmaskAll.nii')
# img0 = nii0.get_data()
# img0.shape


# In[ ]:




# In[ ]:
