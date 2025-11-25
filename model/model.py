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
    for i in range(len(dataset)-look_back-1):
        a = dataset[i:(i+look_back),0] #consider 0 as non existent 
        dataX.append(a)
        dataY.append(dataset[i+look_back,0]) #consider 0 as non existent 
    return np.array(dataX), np.array(dataY)

# fix random seed for reproducibility
np.random.seed(5)

# load the dataset
df = read_csv("data2.csv",index_col=None, delimiter=',')
#print(df)
#print(df.head(n=5))

all_values = df['value'].values
dataset = all_values.reshape(-1,1) #Reshaping in NumPy refers to modifying the dimensions of an existing array without changing its data. The reshape() function is used for this purpose. It reorganizes the elements into a new shape, which is useful in machine learning, matrix operations and data preparation.

#print(dataset.ndim) #Now the dataframe is a pandarray with 2 dimmensions [N,1]
#print(dataset)

#split into train and test set.50% test data, 50% training data
train_size = int(len(dataset)*0.5)
test_size = len(dataset) - train_size
train, test = dataset[0:train_size,:], dataset[train_size:len(dataset),:]

#reshape into X=t and Y=t+1, timestemp 20
look_back = 20
trainX, trainY = create_dataset(train,look_back)
testX, testY = create_dataset(test,look_back)

#print("Train X")
#print(trainX)
#print("TrainX shape")
#print(trainX.shape) # TrainX shape : (89, 20) => It has 89 rows and 20 columns (Total elements of TrainX :1780) (Train.shape gives a tuple giving the size along each dimension )

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
trainPredict = model.predict(trainX)
testPredict = model.predict(testX)

# calculate root mean squared error
trainScore = math.sqrt(mean_squared_error(trainY, trainPredict[:,0]))
print('Train Score: %.2f RMSE' % (trainScore))
testScore = math.sqrt(mean_squared_error(testY, testPredict[:,0]))
print('Test Score: %.2f RMSE' % (testScore))

# shift train predictions for plotting
trainPredictPlot = np.empty_like(dataset)
trainPredictPlot[:,:] = np.nan
trainPredictPlot[look_back:len(trainPredict)+look_back, :] = trainPredict

# shift test predictions for plotting
testPredictPlot = np.empty_like(dataset)
testPredictPlot[:, :] = np.nan
testPredictPlot[len(trainPredict)+(look_back*2)+1:len(dataset)-1, :] = testPredict

# plot baseline and predictions
plt.plot(dataset)
plt.plot(trainPredictPlot)
print('testPrices:')
testPrices=dataset[test_size+look_back:]

print('testPredictions:')
print(testPredict)

# plot the actual price, prediction in test data=red line, actual price=blue line
plt.plot(testPredictPlot)
plt.show()