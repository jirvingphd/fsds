import sklearn.metrics as metrics
import matplotlib.pyplot as plt

def evaluate_classification(model,X_test,y_test,classes=None,
                           normalize='true',cmap='Purples',label=''):
    """Accepts an sklearn-compatible classification model + test data 
    and displays several sklearn.metrics functions: 
    - classifciation_report
    - plot_confusion_matrix
    - plot_roc_curve
    """
     
    ## Get Predictions
    y_hat_test = model.predict(X_test)
    
    
    ## Classification Report / Scores 
    table_header = "[i] CLASSIFICATION REPORT"
    
    ## Add Label if given
    if len(label)>0:
        table_header += f" {label}"
        
    
    ## PRINT CLASSIFICATION REPORT
    dashes = '---'*20
    print(dashes,table_header,dashes,sep='\n')

    print(metrics.classification_report(y_test,y_hat_test,
                                    target_names=classes))
    
    report = metrics.classification_report(y_test,y_hat_test,
                                               target_names=classes,
                                          output_dict=True)
    print(dashes+"\n\n")
    
    

    ## MAKE FIGURE
    fig, axes = plt.subplots(figsize=(10,4),ncols=2)
    
    ## Plot Confusion Matrix 
    metrics.plot_confusion_matrix(model, X_test,y_test,
                                  display_labels=classes,
                                  normalize=normalize,
                                 cmap=cmap,ax=axes[0])
    axes[0].set(title='Confusion Matrix')
    
    ## Plot Roc Curve
    roc_plot = metrics.plot_roc_curve(model, X_test, y_test,ax=axes[1])
    axes[1].legend()
    axes[1].plot([0,1],[0,1],ls=':')
    axes[1].grid()
    axes[1].set_title('Receiving Operator Characteristic (ROC) Curve') 
    fig.tight_layout()
    plt.show()
    
    return report #fig,axes



import tzlocal
import datetime as dt

class Stopwatch:

    
    def __init__(self,fmt='%m/%d/%Y - %I:%M:%S %p', start=True,
                label=''):
        """
        Create the Stopwatch instanct and set the time display format. 
        By default the timer will start upon initialization ( start=True) 

        Args:
            fmt (str, optional): Time format code for .strftime; Defaults to '%m/%d/%Y - %I:%M:%S %p'.
            start (bool, optional): Start the stopwatch when initialized. Defaults to True.
            label (str, optional): Label to add to start. Defaults to ''.
        """
        self.fmt = fmt
        self.tz = tzlocal.get_localzone()
        self._summary = []
        
        if start:
            self.start(label=label)
        
    def _get_time(self):
        import datetime as dt
        return dt.datetime.now(self.tz)
    
    def _print_append(self,msg):
        self._summary.append(msg)
        print(msg)
        
    def start(self,label=''):
        self._start = self._get_time()
        self._print_append(f"Timer started at {self._start.strftime(self.fmt)}")
    
        if len(label) >0:
            self._print_append(f'\t- Process being timed: {label}\n')
            
    
    def stop(self,label=''):
        
        self._stop = self._get_time()
        
        self._print_append(f"Timer stopped at {self._stop.strftime(self.fmt)}")
        self._print_append(f'\tElapsed Time = {self._stop-self._start}')
        if len(label) >0:
            self._print_append(f'\tResults:\t{label}')
            
    def __repr__(self):
        return '\n'.join(self._summary)
    
    def __str__(self):
        return self.__repr__()
    
    
    def __call__(self):
        time = self._get_time()
        return time.strftime(self.fmt)