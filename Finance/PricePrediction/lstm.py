### Part of this code taken from https://github.com/Poddiachyi/CryptocurrencyPricePrediction/blob/master/lstm.ipynb
# LSTM - Long Short Term Memory
# Sergey Kozachenko April 25 2020

# datastructures - dataframes 
import pandas as pd
import time
# statistical data visualization
import seaborn as sns
# data visualization
import matplotlib.pyplot as plt
import datetime
import numpy as np

# keras in ai framework
from keras.models import Sequential
from keras.layers import Activation, Dense
from keras.layers import LSTM
from keras.layers import Dropout

print("Load dataset")
df = pd.read_csv('dataset_for_lstm.csv', index_col=0)

print(df.shape)
# (16678, 9) - (rows, cols)
print(df.head())

# close_off_high represents the gap between the closing price and price high for that day, 
# where values of -1 and 1 mean the closing price was equal to the daily low or daily high, respectively.
# The volatility column is simply the difference between high and low price divided by the opening price.

# adding new calculated columns with data
df['close_off_high'] = 2 * (df['high'] - df['price']) / (df['high'] - df['low']) - 1
df['volatility'] = (df['high'] - df['low']) / (df['open'])

# delete columns with redundant data
df.drop(['ask', 'bid', 'high', 'last', 'low', 'open', 'volumeQuote'], axis=1, inplace=True)

print(df.head())

# rows count * 0.7 - means we take only 70 % of the total amount of rows
split_line = int(df.shape[0] * 0.7)
# training set is 70% of data rows
# test set is other 30% of data rows
# we traing our model using 70 % of historic data and then validate it against last 30% of historic data
training_set, test_set = df[:split_line], df[split_line:]

print("training set shape \n", training_set.shape)

# (11674, 4)

window_len = 10
norm_cols = ['volume']

# generate training input data sets
LSTM_training_inputs = []
for i in range(len(training_set) - window_len):
    # take sub array start i, end i + window [i, i+window]
    temp_set = training_set[i:(i + window_len)].copy()
    for col in norm_cols:
        # calc volume for sub array
        temp_set.loc[:, col] = temp_set[col] / temp_set[col].iloc[0] - 1
    LSTM_training_inputs.append(temp_set)
# weird this is overriden later in line 106, with same expression, why?
#LSTM_training_outputs = (training_set['price'][window_len:].values/training_set['price'][:-window_len].values)-1

# generate test input data sets for validation
LSTM_test_inputs = []
for i in range(len(test_set) - window_len):
    temp_set = test_set[i:(i + window_len)].copy()
    for col in norm_cols:
        temp_set.loc[:, col] = temp_set[col]/temp_set[col].iloc[0] - 1
    LSTM_test_inputs.append(temp_set)
# weird, this is not used anywhere
#LSTM_test_outputs = (test_set['price'][window_len:].values / test_set['price'][:-window_len].values) - 1

print("training inputs \n", LSTM_training_inputs[0])



print("before build model 1")
## probably this is flattening of arrays
LSTM_training_inputs = [np.array(LSTM_training_input) for LSTM_training_input in LSTM_training_inputs]
LSTM_training_inputs = np.array(LSTM_training_inputs)

LSTM_test_inputs = [np.array(LSTM_test_inputs) for LSTM_test_inputs in LSTM_test_inputs]
LSTM_test_inputs = np.array(LSTM_test_inputs)

print("before build model 2")

def build_model(inputs, output_size, neurons, activ_func="linear",
                dropout=0.25, loss="mean_squared_error", optimizer="adam"):
    model = Sequential()

    model.add(LSTM(neurons, input_shape=(inputs.shape[1], inputs.shape[2])))
    model.add(Dropout(dropout))
    model.add(Dense(units=output_size))
    model.add(Activation(activ_func))

    model.compile(loss=loss, optimizer=optimizer)
    return model

np.random.seed(202)

print("build model")
# build  model
model = build_model(LSTM_training_inputs, output_size=1, neurons=20)
LSTM_training_outputs = (training_set['price'][window_len:].values / training_set['price'][:-window_len].values) - 1

print("model fit")
# Trains the model for a fixed number of epochs (iterations on a dataset).
# https://keras.io/models/model/
model_history = model.fit(LSTM_training_inputs, LSTM_training_outputs, 
                            epochs=20, batch_size=32, shuffle=True, validation_split=0.3)

print("ploting training error, MAE")
fig, ax1 = plt.subplots(1,1)
ax1.plot(model_history.epoch, model_history.history['loss'])
ax1.set_title('Training Error')

if model.loss == 'mae':
    ax1.set_ylabel('Mean Absolute Error (MAE)',fontsize=12)
# just in case you decided to change the model loss calculation
else:
    ax1.set_ylabel('Model Loss',fontsize=12)
ax1.set_xlabel('# Epochs',fontsize=12)
plt.show()

# it shows the corelation of actual prices vs predicted prices on 70% of the data which were used for training
fig, ax1 = plt.subplots(1,1)
ax1.plot(df[:split_line].index[window_len:].astype(datetime.datetime),
         training_set['price'][window_len:], label='Actual')
ax1.plot(df[:split_line].index[window_len:].astype(datetime.datetime),
        # Generates output predictions for the input samples.
         ((np.transpose(model.predict(LSTM_training_inputs))+1) * training_set['price'].values[:-window_len])[0], 
         label='Predicted')
fig.set_size_inches(18, 10)
plt.show()

# slow
# shows corelation of actual prices vs predicted prices on 30% of the data which were used for test, validation
# fig, ax1 = plt.subplots(1,1)
# ax1.set_xticks([datetime.date(2018,i+1,1) for i in range(12)])
# ax1.set_xticklabels([datetime.date(2018,i+1,1).strftime('%b %d %Y')  for i in range(12)])
# ax1.plot(df[split_line:].index[window_len:].astype(datetime.datetime),
#          test_set['price'][window_len:], label='Actual')
# ax1.plot(df[split_line:].index[window_len:].astype(datetime.datetime),
#          ((np.transpose(model.predict(LSTM_test_inputs))+1) * test_set['price'].values[:-window_len])[0], 
#          label='Predicted')
# ax1.annotate('MAE: %.4f'%np.mean(np.abs((np.transpose(model.predict(LSTM_test_inputs))+1)-\
#             (test_set['price'].values[window_len:])/(test_set['price'].values[:-window_len]))), 
#              xy=(0.75, 0.9),  xycoords='axes fraction',
#             xytext=(0.75, 0.9), textcoords='axes fraction')
# ax1.set_title('Test Set: Single Timepoint Prediction',fontsize=13)
# ax1.set_ylabel('Price',fontsize=12)
# ax1.legend(bbox_to_anchor=(0.1, 1), loc=2, borderaxespad=0., prop={'size': 14})
# fig.set_size_inches(18, 10)
# plt.show()

### LSTM model to predict crypto prices for the next 5 days

print("LSTM model to predict crypto prices for the next 5 days")

np.random.seed(202)

pred_range = 5

model_5_days = build_model(LSTM_training_inputs, output_size=pred_range, neurons = 20)

# model output is next 5 prices normalised to 10th previous closing price
LSTM_training_outputs = []
for i in range(window_len, len(training_set['price']) - pred_range):
    LSTM_training_outputs.append((training_set['price'][i:i + pred_range].values /
                                  training_set['price'].values[i - window_len])-1)
LSTM_training_outputs = np.array(LSTM_training_outputs)

# train
model_5_days_history = model_5_days.fit(LSTM_training_inputs[:-pred_range], LSTM_training_outputs, 
                            epochs=50, batch_size=32, shuffle=True, validation_split=0.3)

pred_prices = ((model_5_days.predict(LSTM_test_inputs)[:-pred_range][::pred_range]+1)*\
                   test_set['price'].values[:-(window_len + pred_range)][::5].reshape(int(np.ceil((len(LSTM_test_inputs)-pred_range)/float(pred_range))),1))

print("pred_prices.shape", pred_prices.shape)
#print("pred prices.head()\n", pred_prices.head())

pred_colors = ["#FF69B4", "#5D6D7E", "#F4D03F","#A569BD","#45B39D"]
fig, ax1 = plt.subplots(1,1)
ax1.set_xticks([datetime.date(2018,i+1,1) for i in range(12)])
ax1.plot(df[split_line:].index[window_len:].astype(datetime.datetime),
         test_set['price'][window_len:], label='Actual')
for i, pred in enumerate(pred_prices):
    # Only adding lines to the legend once
    if i<5:
        ax1.plot(df[split_line:].index[window_len:].astype(datetime.datetime)[i*pred_range:i*pred_range+pred_range],
                 pred, color=pred_colors[i%5], label="Predicted")
    else: 
        ax1.plot(df[split_line:].index[window_len:].astype(datetime.datetime)[i*pred_range:i*pred_range+pred_range],
                 pred, color=pred_colors[i%5])
ax1.set_title('Test Set: 5 Timepoint Predictions',fontsize=13)
ax1.set_ylabel('Bitcoin Price ($)',fontsize=12)
ax1.set_xticklabels('')
ax1.legend(bbox_to_anchor=(0.13, 1), loc=2, borderaxespad=0., prop={'size': 8})
fig.tight_layout()
fig.set_size_inches(18, 10)
plt.show()
