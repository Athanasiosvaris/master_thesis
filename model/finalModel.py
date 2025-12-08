import pandas as pd
import matplotlib.pyplot as plt
from pandas import read_csv
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.metrics import mean_squared_error
from keras.layers import Dense, Activation, Dropout
import numpy as np
import tensorflow as tf


def create_dataset(dataset,look_back=1):
    dataX, dataY =[],[]
    for i in range(len(dataset)-look_back): #for look_back = 20 this for loop will run 40 times
        a = dataset[i:(i+look_back),0] #consider 0 as non existent 
        dataX.append(a)
        dataY.append(dataset[i+look_back,0]) #consider 0 as non existent 
    return np.array(dataX), np.array(dataY)

model = tf.keras.models.load_model('LSTM_model.keras')

#load the dataset
df = read_csv("test_data.csv",index_col=None, delimiter=',')

id_values = df['sensor_id'].values
timestamp_values = df['sensor_timestamp'].values

final_results = []
#=============== Here the 
sensor_values = df['sensor_value'].values
values_dataset = sensor_values.reshape(-1,1) #Reshaping in NumPy refers to modifying the dimensions of an existing array without changing its data. The reshape() function is used for this purpose. It reorganizes the elements into a new shape, which is useful in machine learning, matrix operations and data preparation.
look_back = 20
train_size = 21
x = 0

while (x < values_dataset.size - look_back) : #From the dataset that it gets the model uses the first 20 values as look_back and predicts the rest
    test = values_dataset[x:train_size,:]

    #reshape into X=t and Y=t+1, timestemp 20
    testX, testY = create_dataset(test,look_back)

    #reshape input to be [samples,time stemps,features]
    testX = np.reshape(testX,(testX.shape[0],testX.shape[1],1)) #It makes trainX 3d.
    trainPredict = model.predict(testX) 
    
    #df = pd.DataFrame(data={"sensor_id":id_values_last50, "sensor_value": np.around(list(testPrices.reshape(-1)), decimals=5),"sensor_timestamp":timestamp_values_last50,"sensor_prediction": np.around(list(testPredict.reshape(-1)), decimals=5)})
    #df = pd.DataFrame(data={"sensor_value": np.around(list(testPrices.reshape(-1)), decimals=5),"sensor_prediction": np.around(list(testPredict.reshape(-1)), decimals=5)})
    #df.to_csv("lstm_result2.csv", sep=';', index=None)
    
    final_results.append({"sensor_id": 1 ,"sensor_value": sensor_values[train_size-1],"sensor_timestamp": timestamp_values[train_size-1],"sensor_predicted_value":trainPredict.tolist()})
    x += 1 
    train_size += 1
    

print("Final_results")
print("Final_results length", len(final_results))
print("Predicted values:")
for dicts in final_results:
    #print(dicts.get('sensor_id'))
    print(dicts.get('sensor_value'))
    print(dicts.get('sensor_timestamp'))
    print(dicts.get('sensor_predicted_value'))
    print()

    

