from whales import engine_futures, db_path_futures, engine
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.histpricemodel import HistPrice
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

import pmdarima as pm

dataset = pd.read_csv('data/ada_prices.csv', parse_dates=True)
dataset.sort_index(ascending=True, inplace=True)

#dataset.drop(columns=['Unnamed: 0', 'id', 'pair', 'ignore'], axis=1, inplace=True)

dataset['returns'] = dataset['Close'].diff(12)
dataset['logReturns'] = np.log(dataset['returns'])
#dataset['diff'] = np.log(dataset['returns']).diff()

data = dataset.iloc[:,-1].copy()
data.dropna(inplace=True)

Ntest = 300
train = data.iloc[:-Ntest]
test = data.iloc[-Ntest:]

print(data.shape, train.shape, test.shape)

model = pm.auto_arima(train,
                      error_action='ignore', trace=True,
                      suppress_warnings=True, maxiter=10,
                      seasonal=False)

model.summary()

model.get_params()

def plot_result(model, fulldata, train, test):
  params = model.get_params()
  d = params['order'][1]

  train_pred = model.predict_in_sample(start=d, end=-1)
  test_pred, confint = model.predict(n_periods=Ntest, return_conf_int=True)

  fig, ax = plt.subplots(figsize=(10, 5))
  ax.plot(fulldata.index, fulldata, label='data')
  ax.plot(train.index[d:], train_pred, label='fitted')
  ax.plot(test.index, test_pred, label='forecast')
  ax.fill_between(test.index, \
                  confint[:,0], confint[:,1], \
                  color='red', alpha=0.3)
  ax.legend()
  
plot_result(model, data, train, test)

def plot_test(model, test):
  test_pred, confint = model.predict(n_periods=Ntest, return_conf_int=True)

  fig, ax = plt.subplots(figsize=(10, 5))
  ax.plot(test.index, test, label='true')
  ax.plot(test.index, test_pred, label='forecast')
  ax.fill_between(test.index, \
                  confint[:,0], confint[:,1], \
                  color='red', alpha=0.3)
  ax.legend()

plot_test(model, test)

def rmse(y, t):
  return np.sqrt(np.mean((t - y)**2))

print("RMSE ARIMA:", rmse(model.predict(Ntest), test))
print("RMSE Naive:", rmse(train.iloc[-1], test))

