import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from statsmodels.tsa.stattools import acf, pacf

matplotlib.rc('xtick', labelsize=40)
matplotlib.rc('ytick', labelsize=40)

sns.set(style="whitegrid", color_codes=True)

# xma = np.random.randint(1,50000,100)
xma = np.random.normal(0, 25, 1000)

# lets create a MA series having mean 2 and of order 2
y5 = 2 + xma + 0.8*np.roll(xma, -1) + 0.6*np.roll(xma, -2)  # + 0.6 *np.roll(xma,-3)

plt.figure(figsize=(16, 7))

# Plot ACF:
plt.subplot(121)
plt.plot(xma)
plt.subplot(122)
plt.plot(y5)
plt.show()

# calling acf function from stattools
lag_acf = acf(y5, nlags=50)

# Plot ACF:
plt.figure(figsize=(16, 7))
plt.plot(lag_acf, marker="o")
plt.axhline(y=0, linestyle='--', color='gray')
plt.axhline(y=-1.96/np.sqrt(len(y5)), linestyle='--', color='gray')
plt.axhline(y=1.96/np.sqrt(len(y5)), linestyle='--', color='gray')
plt.title('Autocorrelation Function')
plt.xlabel('number of lags')
plt.ylabel('correlation')
plt.tight_layout()
plt.show()

# calling pacf function from stattools
lag_pacf = pacf(y5, nlags=50, method='ols')

# Plot PACF
plt.figure(figsize=(16, 7))
plt.plot(lag_pacf, marker="o")
plt.axhline(y=0, linestyle='--', color='gray')
plt.axhline(y=-1.96/np.sqrt(len(y5)), linestyle='--', color='gray')
plt.axhline(y=1.96/np.sqrt(len(y5)), linestyle='--', color='gray')
plt.title('Partial Autocorrelation Function')
plt.xlabel('number of lags')
plt.ylabel('correlation')
plt.tight_layout()
plt.show()
