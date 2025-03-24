"""
csvデータを離散フーリエ変換
https://watlab-blog.com/2021/04/17/csv-dft/

・コマンドライン引数でファイルを指定（例：> python dft_1.py signals.csv）
"""

import sys
import numpy as np
from scipy import fftpack
import pandas as pd
import matplotlib.pyplot as plt

# フーリエ変換をする関数
def calc_fft(data, samplerate):
    spectrum = fftpack.fft(data)                                     # 信号のフーリエ変換
    amp = np.sqrt((spectrum.real ** 2) + (spectrum.imag ** 2))       # 振幅成分
    amp = amp / (len(data) / 2)                                      # 振幅成分の正規化（辻褄合わせ）
    freq = np.linspace(0, samplerate, len(data))                     # 周波数軸を作成
    return spectrum, amp, freq

# csvから列方向に順次フーリエ変換を行い保存する関数
def csv_fft(in_file, out_file):
    df = pd.read_csv(in_file, encoding='utf-8')                  # ファイル読み込み
    dt = df.T.iloc[0,1]                                              # 時間刻み

    # データフレームを初期化
    df_amp = pd.DataFrame()
    df_fft = pd.DataFrame()

    # 列方向に順次フーリエ変換（DFT）をするコード
    for i in range(len(df.T)-1):
        data = df.T.iloc[i+1]                                        # フーリエ変換するデータ列を抽出
        spectrum, amp, freq = calc_fft(data.values, 1/dt)            # フーリエ変換をする関数を実行
        df_amp[df.columns[i+1] + '_amp'] = pd.Series(amp)            # 列名と共にデータフレームに振幅計算結果を追加

    df_fft['freq[Hz]'] = pd.Series(freq)                             # 周波数軸を作成
    df_fft = df_fft.join(df_amp)                                     # 周波数・振幅データフレームを結合
    df_fft = df_fft.iloc[range(int(len(df)/2) + 1),:]                # ナイキスト周波数でデータを切り捨て
    df_fft.to_csv(out_file)                                          # フーリエ変換の結果をcsvに保存

    return df, df_fft

# 関数を実行してcsvファイルをフーリエ変換するだけの関数を実行
in_file = sys.argv[1]                                                # コマンドライン引数にファイル名
df, df_fft = csv_fft(in_file, out_file='dft.csv')


# -----------------------------------------------------
# グラフ描画
# -----------------------------------------------------

# フォントの種類とサイズを設定する。
plt.rcParams['font.size'] = 14
plt.rcParams['font.family'] = 'Times New Roman'

# 目盛を内側にする。
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'

# グラフの上下左右に目盛線を付ける。
fig = plt.figure(figsize=(10, 5))
ax1 = fig.add_subplot(121)
ax1.yaxis.set_ticks_position('both')
ax1.xaxis.set_ticks_position('both')
ax2 = fig.add_subplot(122)
ax2.yaxis.set_ticks_position('both')
ax2.xaxis.set_ticks_position('both')

# 軸のラベルを設定する。
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Amplitude')
ax2.set_xlabel('Frequency [Hz]')
ax2.set_ylabel('Amplitude')

# データプロットの準備とともに、ラベルと線の太さ、凡例の設置を行う。
size = len(df.T)-1
for i in range(size):
    ax1.plot(df.T.iloc[0], df.T.iloc[i+1], label=df.columns[i+1], lw=1)
    ax2.plot(df_fft.T.iloc[0], df_fft.T.iloc[i+1], label=df_fft.columns[i+1], lw=1)
ax1.legend()
ax2.legend()

# レイアウト設定
fig.tight_layout()

# グラフを表示する。
plt.show()
plt.close()
# ---------------------------------------------------