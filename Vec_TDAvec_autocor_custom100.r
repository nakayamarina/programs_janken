# TDAによる特徴抽出とベクトル化（穴の種類やきざみ時間変更可）

# ---

# 引数：raw_rock.csv/raw_scissor.csv/raw_paper.csv, 時間遅れτのcsvファイルがあるディレクトリまでのパス

# ---

# 入力：raw_rock.csv/raw_scissor.csv/raw_paper.csv, 時間遅れτのcsvファイル(TAUautocre.csv)

# ---

# 出力：
# * TDAvec_autocor_rock_(パラメータ).csv：前処理をしたrock時のデータの特徴抽出を行ったもの
# * TDAvec_autocor_scissor_(パラメータ).csv：前処理をしたscissor時のデータの特徴抽出を行ったもの
# * TDAvec_autocor_paper_(パラメータ).csv：前処理をしたpaper時のデータの特徴抽出を行ったもの
#
# 場合に応じて
# * TDAvec_autocor_attractor/voxel[ボクセル番号]_rock.png
# * TDAvec_autocor_attractor/Voxel[ボクセル番号]_scissor.png
# * TDAvec_autocor_attractor/Voxel[ボクセル番号]_paper.png
# * TDAvec_autocor_barcode/voxel[ボクセル番号]_rock.png
# * TDAvec_autocor_barcode/voxel[ボクセル番号]_scissor.png
# * TDAvec_autocor_barcode/voxel[ボクセル番号]_paper.png


# ---

# 前処理をした

# * rock時のデータ
# * scissor時のデータ
# * paper時のデータ

# の特徴抽出をTDAを用いて行う．

# (1) 3次元空間への写像
# rock,scissor,paper時の各ボクセルの時間遅れτを用いて
# 各ボクセルの時系列データにおいてある時刻tの値，t+τの値，t+2*τの値で3次元データとし，アトラクタ図形を得る

# (2) TDA適用
# 3次元データに対してTDAのPersistent Homology適用しバーコードダイアグラムを得る

# (3) ベクトル化
# 穴の数をkizamiNumber(TDAvec関数の変数)回数えることでベクトル化する

if (!require(package = "TDA")) {
  install.packages(pkgs = "TDA")
}

if (!require(package = "scatterplot3d")) {
  install.packages(pkgs = "scatterplot3d")
}

library(TDA)
library(scatterplot3d)

print('################ TDAvec_autocor.r excution ###################')

# コマンドライン引数でraw_tap.csv/raw_rest.csv, TAUautocor.csvがあるディレクトリまでのパスを取得

# PATH <- '../State-2fe_Active/20181029rn/64ch/RawData/'
PATH = commandArgs(trailingOnly=TRUE)[1]

# 読み込みたいファイルのパス
PATH_rock <- paste(PATH, 'raw_rock.csv', sep = "")
PATH_scissor <- paste(PATH, 'raw_scissor.csv', sep = "")
PATH_paper <- paste(PATH, 'raw_paper.csv', sep = "")
PATH_tau <- paste(PATH, 'TAUautocor.csv', sep = "")

# TDAvec関数で使うripsDiagのmaxsxaleの値設定
ms<- 2

# BettiNumberCount関数で使う穴を数える回数
kizamiNum <- 100
parameters <- paste("012dim", kizamiNum, sep = "")



# アトラクタ図，バーコードを出力する(1) or しない (0)
# 出力する場合の保存ディレクトリ名
atrct_output <- 1
barcode_output <- 1
atrctName <- 'TDAvec_autocor_attractor'
barcodeName <- 'TDAvec_autocor_barcode'


# main関数

main <- function(){

  # csvファイルの読み込み
  rock <- read.csv(PATH_rock)
  scissor <- read.csv(PATH_scissor)
  paper <- read.csv(PATH_paper)
  taus <- read.csv(PATH_tau)

  # ベクトル化したデータを格納する配列
  rockVec <- c()
  scissorVec <- c()
  paperVec <- c()

  # ボクセルの数だけ繰り返す
  for(i in 1:nrow(taus)){

    messe <- paste('----- excution voxel.', i, ' ---')
    print(messe)

    # i番目のボクセルデータ
    voxel_rock <- rock[i]
    voxel_scissor <- scissor[i]
    voxel_paper <- paper[i]

    # i番目のボクセルの時間遅れτ
    tau_rock <- taus[i, 1]
    tau_scissor <- taus[i, 2]
    tau_paper <- taus[i, 3]

    attractor_rock <- Attractor(voxel_rock, tau_rock, i, "rock")
    attractor_scissor <- Attractor(voxel_scissor, tau_scissor, i, "scissor")
    attractor_paper <- Attractor(voxel_paper, tau_paper, i, "paper")

    print("Rock vectorize")
    rockVec <- rbind(rockVec, TDAvec(attractor_rock, i, "rock"))

    print("Scissor vectorize")
    scissorVec <- rbind(scissorVec, TDAvec(attractor_scissor, i, "scissor"))

    print("Paper vectorize")
    paperVec <- rbind(paperVec, TDAvec(attractor_paper, i, "paper"))

  }


  # csv書き出し
  PATH_rockVec <- paste(PATH, 'TDAvec_autocor_rock_', parameters, '.csv', sep = "")
  write.csv(as.data.frame(rockVec), PATH_rockVec, quote = FALSE, row.names = FALSE)

  PATH_scissorVec <- paste(PATH, 'TDAvec_autocor_scissor_', parameters, '.csv', sep = "")
  write.csv(as.data.frame(scissorVec), PATH_scissorVec, quote = FALSE, row.names = FALSE)

  PATH_paperVec <- paste(PATH, 'TDAvec_autocor_paper_', parameters, '.csv', sep = "")
  write.csv(as.data.frame(paperVec), PATH_paperVec, quote = FALSE, row.names = FALSE)

}


# Attractor関数
# 引数としてi番目のボクセルデータをVoxel，時間遅れτをtau，何番目のボクセルかをvoxel_no，タスク名をtaskで受けとる
# * 時間遅れτを使って，ある時刻tの値，t+τの値，t+2*τの値で3次元データを作る
# * 3次元データを返す

Attractor <- function(voxel, tau, voxel_no, task){

  # データをずらすことで長さが変わるので注意！

  # 元データ
  x <- voxel[1:(nrow(voxel) - (2*tau)), 1]
  # 元データからτ分ずらしたデータ
  y <- voxel[(1 + tau):(nrow(voxel) - (tau)), 1]
  # 元データから2*τ分ずらしたデータ
  z <- voxel[(1 + (2*tau)):nrow(voxel), 1]

  # 3次元データとして結合
  xyz <- cbind(x, y, z)

  # アトラクタ図を出力する場合
  if (atrct_output == 1){

    # 出力するアトラクタ図を保存するのディレクトリ名・パス
    DIR_attractor <- paste(PATH, atrctName, sep="")
    PATH_attractor <- paste(DIR_attractor, '/', sep="")

    # すでに存在する場合は何もせず，存在していない場合はディレクトリ作成
    if(!file.exists(PATH_attractor)) {
      dir.create(DIR_attractor)
    }

    # この後にplotするアトラクタ図のタイトル
    graph_name <- paste("Mapping to 3dim space : ", task, "-voxel", voxel_no, sep="")

    # この後に出力するpngファイル名
    PATH_graph <- paste(PATH_attractor, "voxel", voxel_no, '_', task, '.png', sep="")

    # 3次元データをplot，出力
    png(PATH_graph)
    scatterplot3d(xyz, xlab = "x = t", ylab = "y = t + τ", zlab = "z = t + 2*τ", pch = 16, type="o", main = graph_name)
    dev.off()

    print(PATH_graph)

  }

  return (xyz)

}

# TDAvec関数
# 引数としてi番目のボクセルデータを3次元データにしたものをattractor，何番目のボクセルかをvoxel_no，タスク名をtaskで受けとる
# * ripsDiagで3次元データにTDAのPersistent Homologyを適用
# * 各次の穴情報それぞれに対してBattiNumberCount関数を使って穴の数を数え，横結合することでベクトル化
# * ベクトル化したデータを返す

TDAvec <- function(attractor, voxel_no, task){

  # TDAのPersistent Homologyを適用
  tda <- ripsDiag(X = attractor, maxdimension = 2, maxscale = ms)

  if (barcode_output == 1){

    # バーコードを保存するディレクトリ名・パス
    DIR_tda <- paste(PATH, barcodeName, sep="")
    PATH_tda <- paste(DIR_tda, '/', sep="")

    # すでに存在する場合は何もせず，存在していない場合はディレクトリ作成
    if(!file.exists(PATH_tda)) {
      dir.create(DIR_tda)
    }

    # この後でplotするバーコードのタイトル
    barcode_name <- paste("Barcode Diagram (TDA) : ", task, "-voxel", voxel_no, sep="")

    # この後で出力するpngファイル名
    PATH_barcode <- paste(PATH_tda, "voxel", voxel_no, '_', task, '.png', sep="")

    # バーコードをplot，出力
    png(PATH_barcode)
    plot(tda$diagram, barcode = TRUE, main = barcode_name)
    dev.off()

    print(PATH_barcode)

  }

  # 穴情報を抽出
  df_tda <- as.data.frame(tda$diagram[, 1:3])

  # 各次の穴情報を分割
  zeroDim <- subset(df_tda, df_tda$dimension == 0)
  oneDim <- subset(df_tda, df_tda$dimension == 1)
  twoDim <- subset(df_tda, df_tda$dimension == 2)


  # 各次の穴の数を数え横結合することでベクトル化
  tdaVec <- c(BettiNumberCount(zeroDim), BettiNumberCount(oneDim), BettiNumberCount(twoDim))

  return(tdaVec)

}

# BettiNumberCount関数
# 引数として各次の穴情報をholeで受け取る
# * 穴を数える回数（kizamiNum）などのパラメータを決める
# * 穴情報はそれぞれの穴発生時の直径（Birth），穴消滅時の直径（Death）が記録されており，ある時刻timeの時の穴の数を数える
# * 1×kizamiNumのデータを返す

BettiNumberCount <- function(hole){


  # 穴をkizamiNum回数えるために時間幅を求める
  # もともとの時間はms，kizamiNumで割ることでどれぐらいずつ時刻timeをずらせばいいかわかる
  kizamiWidth <- ms/kizamiNum

  # 時刻
  time <- 0

  # 穴を数えた回数
  k <- 0

  # kizamiNum回数えた結果を格納する配列
  bettiNumbers <- numeric(kizamiNum)

  # 穴が発生していればTrue
  if(nrow(hole) >= 1){

    # kizamiNumber回穴の数を数えるまでループ
    while(k != kizamiNum){

      # 時刻timeの時の穴の数
      bettiCount <- 0

      # 発生したそれぞれの穴に対して調べる
      for(j in 1:nrow(hole)){

        # 時刻timeがある穴の発生時間中（Birth <= time <= Death）であればbettiCountに1足す
        if((hole$Birth[j] <= time) && (time <= hole$Death[j])){

          bettiCount = bettiCount + 1

        }

      }

      # bettiCountを配列に格納
      bettiNumbers[k] <- bettiCount

      # 時刻timeをずらす
      time = time + kizamiWidth

      # 穴の数を数えたのでkに1足す
      k = k + 1

    }

  } else {

    # そもそも穴が発生していなければ0をkizamiNum個格納
    bettiNumbers <- numeric(kizamiNum)

  }

  return(bettiNumbers)

}

# Execute main function
main()
