import sklearn.metrics as metrics
import matplotlib.pyplot as plt





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