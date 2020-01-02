import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from statsmodels.tsa.stattools import acf, pacf

matplotlib.rc('xtick', labelsize=40)
matplotlib.rc('ytick', labelsize=40) 

sns.set(style="whitegrid", color_codes=True)

t = np.linspace(0, 10, 500)
# normal distributed values
ys = np.random.normal(0, 5, 500)

# exponential series to get the trend
ye = np.exp(t**0.5)
# adding normally distributed series in exponential series
y = ys+ye
# plot
plt.figure(figsize=(16, 7))
plt.plot(t, y)
plt.show()

# calling auto correlation function
lag_acf = acf(y, nlags=300)
# Plot PACF:
plt.figure(figsize=(16, 7))
plt.plot(lag_acf, marker='+')
plt.axhline(y=0, linestyle='--', color='gray')
plt.axhline(y=-1.96 / np.sqrt(len(y)), linestyle='--', color='gray')
plt.axhline(y=1.96 / np.sqrt(len(y)), linestyle='--', color='gray')
plt.title('Autocorrelation Function')
plt.xlabel('number of lags')
plt.ylabel('correlation')
plt.tight_layout()
plt.show()

# calling partial correlation function
lag_pacf = pacf(y, nlags=30, method='ols')
# Plot PACF:
plt.figure(figsize=(16, 7))
plt.plot(lag_pacf, marker='+')
plt.axhline(y=0, linestyle='--', color='gray')
plt.axhline(y=-1.96 / np.sqrt(len(y)), linestyle='--', color='gray')
plt.axhline(y=1.96 / np.sqrt(len(y)), linestyle='--', color='gray')
plt.title('Partial Autocorrelation Function')
plt.xlabel('Number of lags')
plt.ylabel('correlation')
plt.tight_layout()
plt.show()
