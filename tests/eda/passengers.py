from pandas import read_csv
from matplotlib import pyplot
from statsmodels.tsa.stattools import adfuller

series = read_csv('../data/international-airline-passengers.csv', header=0, index_col=0, squeeze=True)

series.plot()
pyplot.show()

series.hist()
pyplot.show()

# Summary stats
X = series.values
split = int(len(X) / 2)
X1, X2 = X[0:split], X[split:]
mean1, mean2 = X1.mean(), X2.mean()
var1, var2 = X1.var(), X2.var()
print('mean1=%f, mean2=%f' % (mean1, mean2))
print('variance1=%f, variance2=%f' % (var1, var2))

# Augmented Dickey-Fuller test for stationarity (H0: series has unit root; i.e., is non-stationary)
result = adfuller(X)
print('ADF Statistic: %f' % result[0])
print('p-value: %f' % result[1])
print('Critical Values:')
for key, value in result[4].items():
    print('\t%s: %.3f' % (key, value))
