
    
## Lab Function
# from statsmodels.tsa.stattools import adfuller
import statsmodels.tsa.api as tsa
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

def adfuller_test_df(ts,index=['AD Fuller Results']):
    """Returns the AD Fuller Test Results and p-values for the null hypothesis
    that there the data is non-stationary (that there is a unit root in the data)"""
    
    df_res = tsa.stattools.adfuller(ts)

    names = ['Test Statistic','p-value','#Lags Used','# of Observations Used']
    res  = dict(zip(names,df_res[:4]))
    
    res['p<.05'] = res['p-value']<.05
    res['Stationary?'] = res['p<.05']
    
    if isinstance(index,str):
        index = [index]
    res_df = pd.DataFrame(res,index=index)
    res_df = res_df[['Test Statistic','#Lags Used',
                     '# of Observations Used','p-value','p<.05',
                    'Stationary?']]
    return res_df



def stationarity_check(TS,window=8,plot=True,index=['AD Fuller Results']):
    """Adapted from https://github.com/learn-co-curriculum/dsc-removing-trends-lab/tree/solution"""
    
    # Calculate rolling statistics
    roll_mean = TS.rolling(window=window, center=False).mean()
    roll_std = TS.rolling(window=window, center=False).std()
    
    # Perform the Dickey Fuller Test
    dftest = adfuller_test_df(TS,index=index)
    
    if plot:
        
        ## Building in contingency if not a series with a freq
        try: 
            freq = TS.index.freq
        except:
            freq = 'N/A'
            
        # Plot rolling statistics:
        fig = plt.figure(figsize=(12,6))
        plt.plot(TS, color='blue',label=f'Original (freq={freq}')
        plt.plot(roll_mean, color='red', label=f'Rolling Mean (window={window})')
        plt.plot(roll_std, color='black', label = f'Rolling Std (window={window})')
        plt.legend(loc='best')
        plt.title('Rolling Mean & Standard Deviation')
        display(dftest)
        plt.show(block=False)
        
    return dftest

    
    
def plot_acf_pacf(ts,figsize=(9,6), lags=None,suptitle=None,sup_y = 1.01,
                  diff=None):
    """Plot pacf and acf using statsmodels"""
    if diff is not None:
        ts = ts.diff(diff).dropna()
        title_suffix = f" (Diff={diff})"
    else:
        title_suffix=""
        
    fig,axes=plt.subplots(nrows=2,figsize=figsize)
    
    tsa.graphics.plot_acf(ts,ax=axes[0],lags=lags, title=f"Autocorrelation{title_suffix}");
    tsa.graphics.plot_pacf(ts,ax=axes[1],lags=lags,title=f"Partial-Autocorrelation{title_suffix}");
    
    ## Add grid
    [ax.grid(axis='x',which='both') for ax in axes]
    
    if suptitle is not None:
        fig.suptitle(suptitle,y=sup_y,fontweight='bold',fontsize=15)
        
    fig.tight_layout()
    return fig,axes




def train_test_split_ts(ts,test_size=0.9,split_index=None):
    """Uses test size by default, split_index overrides it"""
    if split_index is not None:
        tts_cutoff = split_index
    else:
        tts_cutoff = round(ts.shape[0]*0.9)
    fmt = "%m-%d-%Y"
    cutoff_time = ts.index[tts_cutoff]
    print(f"Using a cutoff index of {tts_cutoff}, which = {cutoff_time.strftime(fmt)}")
    
      ## Use the tts cutoff to do Train test split and plot
    train = ts.iloc[:tts_cutoff]
    test = ts.iloc[tts_cutoff:]

    ## Plot
    ax = train.plot(label='train')
    test.plot(label='test')
    ax.legend()
    ax.set(ylabel=ts.name)
    ax.axvline(cutoff_time,color='k',ls=':',label=cutoff_time.strftime(fmt))
    ax.legend()
    ax.set_title(f"Train Test Split for {ts.name}")
    return train, test


## funtionize diagnosing
def diagnose_model(model): #keep
    """Takes a fit statsmodels model and displays the .summary 
    and plots the built-in plot.diagnostics()"""
    display(model.summary())
    model.plot_diagnostics()
    plt.tight_layout()
    
    
def get_forecast(model,steps=14): #keep
    forecast = model.get_forecast(steps=steps)
    forecast_df = forecast.conf_int()
    forecast_df['Forecast'] = forecast.predicted_mean
    forecast_df.columns = ['Lower CI','Upper CI','Forecast']
    return forecast_df


def plot_forecast(forecast_df,ts,orig_label='True Data',
                  forecast_label='Forecast',
                  forecast_steps=30,
                  last_n_lags=None,figsize=(10,4)):
    """Takes a forecast_df from get_df_from_pred and optionally 
    the training/original time series.
    
    Plots the original ts, the predicted mean and the 
    confidence invtervals (using fill between)"""
    if not isinstance(forecast_df,pd.DataFrame):
        forecast_df = get_forecast(forecast_df,steps=forecast_steps)
        
    fig,ax = plt.subplots(figsize=figsize)

    if last_n_lags is None:
        last_n_lags = len(ts)
        
    ts.iloc[-last_n_lags:].plot(label='True Data')

    
    forecast_df['Forecast'].plot(ax=ax,color='darkgreen',label=forecast_label)
    ax.fill_between(forecast_df.index,
                    forecast_df['Lower CI'], 
                    forecast_df['Upper CI'],
                    color='lightgreen',alpha=0.5,lw=0.5,edgecolor='k')
    ax.set(title=f'Forecasted {ts.name}')
    sep = forecast_df.index[0]
    ax.axvline(sep,label=f"Forecast Starts {sep.strftime('%m-%d-%y')}",lw=1,ls=':',c='k')
    ax.legend()

    return fig,ax

    
def evaluate_model(model,train,test,steps=None,last_n_lags=None):
    diagnose_model(model)
    
    if steps is None:
        steps=len(test)
        
    forecast_df = get_forecast(model,steps=len(test))
    fig, ax = plot_forecast(forecast_df,train,last_n_lags=last_n_lags)
    
    test.plot(ax=ax,label='Test Data')
    ax.legend()
    return fig,ax
           
 
