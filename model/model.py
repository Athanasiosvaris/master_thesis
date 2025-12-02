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

#LSTM model

#create_dataset
#converts an array of values into a dataset matrix - prepares the dataset for LSTM input 
#Example:
#dataset = np.array([[1],[2],[3],[4],[5]])
#look_back = 2

#Output :X = [[1,2],[2,3],[3,4]]
#Y = [3,4,5]

def create_dataset(dataset,look_back=1):
    dataX, dataY =[],[]
    for i in range(len(dataset)-look_back): #for look_back = 20 this for loop will run 40 times
        a = dataset[i:(i+look_back),0] #consider 0 as non existent 
        dataX.append(a)
        dataY.append(dataset[i+look_back,0]) #consider 0 as non existent 
    return np.array(dataX), np.array(dataY)

# fix random seed for reproducibility
np.random.seed(5)

#if (new_day) => retrain model based on the last X messages (between timestamp_X and timestamp_Z) else just predict

# load the dataset
df = read_csv("data2.csv",index_col=None, delimiter=',')


all_values = df['sensor_value'].values
dataset = all_values.reshape(-1,1) #Reshaping in NumPy refers to modifying the dimensions of an existing array without changing its data. The reshape() function is used for this purpose. It reorganizes the elements into a new shape, which is useful in machine learning, matrix operations and data preparation.

#print(dataset.ndim) #Now the dataframe is a pandarray with 2 dimmensions [N,1]
print(dataset)

#split into train and test set.50% test data, 50% training data
train_size = int(len(dataset)*0.5)
test_size = len(dataset) - train_size
train, test = dataset[0:train_size,:], dataset[train_size:len(dataset),:] #train datasets has elements from 0th element (included) up to 59th element(included) and test dataset has 60th element (included) up to 119th element(included)


#reshape into X=t and Y=t+1, timestemp 20
look_back = 20
trainX, trainY = create_dataset(train,look_back)
print("trainX")
print(trainX)
print("TrainY")
print(trainY)

testX, testY = create_dataset(test,look_back)


#reshape input to be [samples,time stemps,features]
trainX = np.reshape(trainX,(trainX.shape[0],trainX.shape[1],1)) #It makes trainX 3d.
testX = np.reshape(testX,(testX.shape[0],testX.shape[1],1))

#crate and fit the LSTM network, optimizer=adam, 25 neurons,dropout 0.1
model = Sequential()
model.add(LSTM(25,input_shape=(look_back,1)))
model.add(Dropout(0.1))
model.add(Dense(1))
model.compile(loss='mse', optimizer='adam')
model.fit(trainX, trainY, epochs=1000, batch_size=240, verbose=1) 

#make predictions
trainPredict = model.predict(trainX) #trainPredict.size = 40
testPredict = model.predict(testX) # testPredict.size = 40


# calculate root mean squared error
trainScore = math.sqrt(mean_squared_error(trainY, trainPredict[:,0]))
print('Train Score: %.2f RMSE' % (trainScore))
testScore = math.sqrt(mean_squared_error(testY, testPredict[:,0]))
print('Test Score: %.2f RMSE' % (testScore))

# shift train predictions for plotting
trainPredictPlot = np.empty_like(dataset)
trainPredictPlot[:,:] = np.nan
trainPredictPlot[look_back:len(trainPredict)+look_back, :] = trainPredict

# shift test predictions for plottingx
testPredictPlot = np.empty_like(dataset)
testPredictPlot[:, :] = np.nan

start = len(trainPredict) + look_back * 2
end = start + len(testPredict)
testPredictPlot[start:end, :] = testPredict

# plot baseline and predictions
plt.plot(dataset)
plt.plot(trainPredictPlot)
testPrices=dataset[test_size+look_back:] 
#The first value that the LTSM model predicts is the 81th value (of the original dataset).
#Test dataset has values from 60th element (from original set) up to 120th value(of the original set). The first 20 values (60th - 80th) are the look_back.
#So first value that model predicts is 81th value. So the test price are from 81th up to 120th (40 values)

print('testPrices:')
print(testPrices)
#print("Test Price size:")
#print(testPrices.size)

#print('testPredictions:')
#print(testPredict)
#print("Test Predict size:")
#print(testPredict.size)

df = pd.DataFrame(data={"prediction": np.around(list(testPredict.reshape(-1)), decimals=5), "test_price": np.around(list(testPrices.reshape(-1)), decimals=5)})
df.to_csv("lstm_result.csv", sep=';', index=None)

# plot the actual price, prediction in test data=red line, actual price=blue line
plt.plot(testPredictPlot)
plt.show()