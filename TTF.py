# -*- coding: utf-8 -*-


%matplotlib inline

import numpy as np
import pandas as pd
import matplotlib as mlp
import matplotlib.pyplot as plt
from numpy                 import array
from sklearn               import metrics

import seaborn as sns

#載入google druver
from google.colab import drive
drive.mount('/content/drive')

#讀入資料
ttf= pd.read_csv('/content/drive/MyDrive/軟體應用資料庫/TTF價格.csv')
stoxx = pd.read_csv("/content/drive/MyDrive/軟體應用資料庫/STOXX600.csv")
temperature = pd.read_csv("/content/drive/MyDrive/軟體應用資料庫/歐盟區每日均溫(1).csv")
ng = pd.read_csv("/content/drive/MyDrive/軟體應用資料庫/天然氣價格專題資料庫.csv")
inventory = pd.read_csv("/content/drive/MyDrive/軟體應用資料庫/天然氣庫存量.csv")

#合併資料
df0 = pd.merge(ng, inventory,on="Date",how="outer")
df1 = pd.merge(df0, temperature,on="Date",how="outer")
df2 = pd.merge(df1, stoxx,on="Date",how="outer")
df = pd.merge(df2, ttf,on="Date",how="outer")

#看缺漏值
df.isnull().sum()

#把未交易日去掉
#df = df.fillna(method='ffill')
df = df.dropna()

#再檢查缺漏值
df.isnull().sum()

# 將資料轉換為時間序列
df['Date'] = pd.to_datetime(df['Date'])
df_show = df.set_index('Date')

# TTF價格
plt.plot(df['TTF open Price'])
plt.xlabel('Date')
plt.ylabel('TTF open Price')
plt.show()

# 俄國管線輸氣量
plt.plot(df['Russia'])
plt.xlabel('Date')
plt.ylabel('Russia')
plt.show()

# 海運液化天然氣輸氣量
plt.plot(df['LNG'])
plt.xlabel('Date')
plt.ylabel('LNG')
plt.show()

# 挪威管線輸氣量
plt.plot(df['Norway'])
plt.xlabel('Date')
plt.ylabel('Norway')
plt.show()

# 荷蘭自生產量
plt.plot(df['Netherlands'])
plt.xlabel('Date')
plt.ylabel('Netherlands')
plt.show()

# 亞塞拜然管線輸氣量
plt.plot(df['Azerbaijan'])
plt.xlabel('Date')
plt.ylabel('Azerbaijan')
plt.show()

# 阿爾及利亞管線輸氣量
plt.plot(df['Algeria'])
plt.xlabel('Date')
plt.ylabel('Algeria')
plt.show()

#成長比較(非輸氣量)
df_gas=df_show[['Netherlands', 'Azerbaijan','Russia','Norway','Algeria',"Libya",'LNG']].loc['2017-10-23':'2022-05-23']
cmap = sns.color_palette()
plt.style.use('seaborn')
df_cret = df_gas.div(df_gas.iloc[0,:])
df_cret.plot()
plt.show()

#在2021年末2022年初天然氣危機，主要進口來源:俄羅斯管線、挪威管線、阿爾及利亞管線、海運液化天然氣，運送量成長比較
df_gas=df_show[['Russia','Norway','Algeria', 'LNG']].loc['2020-11-23':'2022-05-23']
cmap = sns.color_palette()
plt.style.use('seaborn')
df_cret = df_gas.div(df_gas.iloc[0,:])
df_cret.plot()
plt.show()

#再增加歐盟區天然氣儲存量，. 歐盟區平均氣溫，歐盟區金融市場狀況(泛歐600)
df=df[['Date', 'Netherlands','Azerbaijan','Russia','Norway','Algeria',"Libya",'LNG','Gas in storage (TWh)','stoxx600 low price',
                      'stoxx600 hight price', 'AVG.(celsius)','TTF open Price','TTF open Price t+1']]
df

df['Date'] = pd.to_datetime(df['Date'])
df_VAR = df.set_index('Date')

#先看一下彼此間的相關係數
correlation_matrix = df_VAR.corr().round(2)
plt.figure(figsize=(32,16))
sns.heatmap(data=correlation_matrix, annot = True)
plt.show()

#載入ADF檢定套件
from statsmodels.tsa.stattools import adfuller

#測試平穩性
for col in df_VAR.columns:
    result = adfuller(df_VAR[col])
    print(col + ':')
    print('\tADF Statistic: %f' % result[0])
    print('\tp-value: %f' % result[1])
    print('\tCritical Values:')
    for key, value in result[4].items():
        print('\t\t%s: %.3f' % (key, value))

#有些不平穩，差分一次
df_VAR = df_VAR.diff().dropna()

#再看一次平穩性
for col in df_VAR.columns:
    result = adfuller(df_VAR[col])
    print(col + ':')
    print('\tADF Statistic: %f' % result[0])
    print('\tp-value: %f' % result[1])
    print('\tCritical Values:')
    for key, value in result[4].items():
        print('\t\t%s: %.3f' % (key, value))

#差分兩次(如果有必要)
df_VAR = df_VAR.diff().dropna()

#再看一次平穩性
for col in df_VAR.columns:
    result = adfuller(df_VAR[col])
    print(col + ':')
    print('\tADF Statistic: %f' % result[0])
    print('\tp-value: %f' % result[1])
    print('\tCritical Values:')
    for key, value in result[4].items():
        print('\t\t%s: %.3f' % (key, value))

from statsmodels.tsa.vector_ar.var_model import VAR

# 建立VAR向量自我回歸模型
model = VAR(df_VAR)

order = model.select_order()
order.summary()

# 擬合VAR模型，返回Estimation結果
results = model.fit()
results.summary()

# 預測目標'TTF close Price +1'
predictions = results.forecast(df_VAR.values, steps=1)

from statsmodels.tsa.stattools import grangercausalitytests
# 載入葛蘭傑因果分析
# 指定檢定對象
granger_test = grangercausalitytests(df_VAR[['TTF open Price t+1', 'TTF open Price']], maxlag=2)
# 顯示結果
granger_test

from statsmodels.tsa.stattools import grangercausalitytests
# 載入葛蘭傑因果分析
# 指定檢定對象
granger_test = grangercausalitytests(df_VAR[['TTF open Price t+1', 'AVG.(celsius)']], maxlag=2)
# 顯示結果
granger_test

# 指定檢定對象
granger_test = grangercausalitytests(df_VAR[['TTF open Price t+1', 'stoxx600 low price']], maxlag=2)
# 顯示結果
granger_test

# 指定檢定對象
granger_test = grangercausalitytests(df_VAR[['TTF open Price t+1', 'stoxx600 hight price']], maxlag=2)
# 顯示結果
granger_test

# 指定檢定對象
granger_test = grangercausalitytests(df_VAR[['TTF open Price t+1', 'Netherlands']], maxlag=2)
# 顯示結果
granger_test

# 指定檢定對象
granger_test = grangercausalitytests(df_VAR[['TTF open Price t+1', 'Azerbaijan']], maxlag=2)
# 顯示結果
granger_test

# 指定檢定對象
granger_test = grangercausalitytests(df_VAR[['TTF open Price t+1', 'Norway']], maxlag=2)
# 顯示結果
granger_test

# 指定檢定對象
granger_test = grangercausalitytests(df_VAR[['TTF open Price t+1', 'Algeria']], maxlag=2)
# 顯示結果
granger_test

# 指定檢定對象
granger_test = grangercausalitytests(df_VAR[['TTF open Price t+1', 'Libya']], maxlag=2)
# 顯示結果
granger_test

# 指定檢定對象
granger_test = grangercausalitytests(df_VAR[['TTF open Price t+1', 'Russia']], maxlag=2)
# 顯示結果
granger_test

# 指定檢定對象
granger_test = grangercausalitytests(df_VAR[['TTF open Price t+1', 'LNG']], maxlag=2)
# 顯示結果
granger_test

# 指定檢定對象
granger_test = grangercausalitytests(df_VAR[['TTF open Price t+1', 'Gas in storage (TWh)']], maxlag=2)
# 顯示結果
granger_test

