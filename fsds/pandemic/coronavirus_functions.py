from fsds.imports import *
import os,glob,sys,re,shutil

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


import plotly.io as pio
pio.templates.default = "plotly_dark"

import cufflinks as cf
cf.go_offline()
cf.set_config_file(sharing='public',theme='solar',offline=True)



def make_options(menu_choices):
    """Returns list of dictionary with {'label':menu_choice,'value':menu_choice}"""
    options = []
    for choice in menu_choices:
        options.append({'label':choice,'value':choice})
    return options


def load_us_reference_info():
    """Return and save US Reference Data"""
    ## Making Master Lookup CSV
    import pandas as pd
    abbrev = pd.read_csv('Reference Data/united_states_abbreviations.csv')
    pop = pd.read_csv('Reference Data/us-pop-est2019-alldata.csv')
    us_pop = pop.loc[pop['STATE']>0][['NAME','POPESTIMATE2019']].copy()
    us_info = pd.merge(abbrev,us_pop,right_on='NAME',left_on='State',how="inner")
    us_info.drop('NAME',axis=1,inplace=True)
    return us_info


def download_world_pop(data_folder = "Reference Data/",load=True):
    """Downloads world pop zip from kaggle"""
    import os,sys,shutil

    # Download kaggle dataset
    os.system('kaggle datasets download -d tanuprabhu/population-by-country-2020')

    ## Specify file and target folder
    file = 'population-by-country-2020.zip'
    target = os.path.join(data_folder,file)

    ## Move zip file to target
    shutil.move(file,target)
    print(f'File saved to {target}')
    
    ## Load csv 
    if load:
        df = pd.read_csv(target)
    else:
        df = target
    return df


# @add_method(CoronaData)
def download_coronavirus_data(path='New\ Data/',verbose=False):
    """Installs the Kaggle Command Line Interface to clone dataset.
    Then extracts dataset to specified path and displays name of main file.
    Args:
        path(str): Folder to extract dataset into (must end with a '/')
        
    Returns:
        file_list(list): List of full filepaths to downloaded csv files.
    """
    ## Determine if dataset is downloaded via Kaggle CL
    import os,glob
    from zipfile import ZipFile
    from IPython.display import clear_output
    os.makedirs(path, exist_ok=True)

    ## Install Kaggle
    try:
        import kaggle.api as kaggle
    except:
        ## Install Kaggle 
        os.system("pip install kaggle --upgrade")#
        clear_output()
        if verbose: print('\t- Installed kaggle command line tool.')


    ## Using the kaggle.api          
    import kaggle.api as kaggle     
    kaggle.authenticate()
    kaggle.dataset_download_files('sudalairajkumar/novel-corona-virus-2019-dataset',
                            path=path,force=True,unzip=True)                                  
    # ## Delete Zip File
    # zipfile  = path+"novel-corona-virus-2019-dataset.zip"
    # try:
    #     os.system(f"rm {zipfile}"  )
    # except:
    #     print("ERROR DELETING ZIP FILE")
    
    ## Get list of all csvs
    print('[i] Extraction Complete.')    
    file_list = glob.glob(path+"*.csv")
    
    
    ## Find main df 
    main_file = [file for file in file_list if 'covid_19_data.csv' in file]
    if verbose:
        print(f"[i] The main file name is {main_file}")
    return main_file[0] #file_list[index]





#Make a base class
class BaselineData(object):
    _df = pd.DataFrame()

    @property
    def df(self):
        if hasattr(self,'_df_type'):
            print(self._df_type)
        if hasattr(self,'_df'):
            return self._df.copy()
        else:
            return None
        

    @df.setter 
    def df(self,value):
        self._df = value
        
        
    def get_group_ts(self,group_name,group_col='state',
                     ts_col=None,df=None,
                     freq='D', agg_func='sum'):
        """Take df_us and extracts state's data as then Freq/Aggregation provided"""
        from IPython.display import display
        ## 
        if df is None:
            df = self._df.copy()
            
        try:
            ## Get state_df group
            group_df = df.groupby(group_col).get_group(group_name)#.resample(freq).agg(agg)
        except Exception:
            display(df.head())
            return None
        ## Resample and aggregate state data
        group_df = group_df.resample(freq).agg(agg_func)


        ## Get and Rename Sum Cols 
        orig_cols = group_df.columns

        ## Create Renamed Sum columns
        for col in orig_cols:
            group_df[f"{group_name} - {col}"] = group_df[col]

        ## Drop original cols
        group_df.drop(orig_cols,axis=1,inplace=True)

        if ts_col is not None:
            ts_cols_selected = [col for col in group_df.columns if ts_col in col]
            group_df = group_df[ts_cols_selected]

        return group_df 
        

    ### CLASS DISPLAY RELATED ITEMS
    def _self_report(self,private=False,
                     methods=True,attributes=True,
                    workflow=False):
        import inspect
        attr_list = inspect.getmembers(self)
        dashes='---'*20
        report = [dashes]
        report.append("[i] CovidTrackingProject Contents:\n"+dashes)


        method_list=["\nMETHODS:"]
        attribute_list=["\nATTRIBUTES"]
        workflow_list = ["\nWORKFLOW:"]
        
        if private==False:
            startswithcheck = '_'
        else:
            startswithcheck ='__'
        
        ## Loop through all attr
        for item in attr_list:
            item_name = item[0]
            
            ## Exclude Private/Special Attrs
            if item_name.startswith(startswithcheck)== False:
                
                ## Get tf if item is method
                method_check = inspect.ismethod(item[1])
                
                ## If item is a method:
                if method_check==True:
                    method_list.append(item_name)
                ## If item is an attribute
                else: 
                    attribute_list.append(item_name) 
                    
        if workflow:
            ## Get workflow
            workflow_funcs = [self.download_coronavirus_data,
                             self.load_raw_df, self.get_and_clean_US]
            for i,method in enumerate(workflow_funcs):
                workflow_list.append(f"{i+1}. {method.__name__}")

            report.append('\n\t'.join(workflow_list))
        
        if methods:
            report.append('\n\t'.join(method_list))
        if attributes:
            report.append('\n\t'.join(attribute_list))
            
        return '\n'.join(report)
    
    
    def __str__(self):
        return self._self_report()
    
    def __repr__(self):
        return self._self_report()      
    
    
        
        
def get_state_ts(df, state_name,
                     group_col='state', ts_col=None,
                     freq='D', agg_func='sum'):
    """Take df_us and extracts state's data as then Freq/Aggregation provided"""
    
    ## Get state_df group
    state_df = df.groupby(group_col).get_group(state_name)#.resample(freq).agg(agg)
    
    ## Resample and aggregate state data
    state_df = state_df.resample(freq).agg(agg_func)
    
    
    ## Get and Rename Sum Cols 
    orig_cols = state_df.columns

    ## Create Renamed Sum columns
    for col in orig_cols:
        state_df[f"{state_name} - {col}"] = state_df[col]
      
    ## Drop original cols
    state_df.drop(orig_cols,axis=1,inplace=True)
    
    
## Return on columns containing ts_cols
    if ts_col is not None:

        if isinstance(ts_col,str):
            ts_col = [ts_col]

        
        ts_cols_selected=[]
        for column in ts_col:
            ts_cols_selected.extend([col for col in state_df.columns if column in col])
            
        state_df = state_df[ts_cols_selected]
    return state_df
    



def plot_states(df, state_list, plot_cols = ['Confirmed'],df_only=False,
                new_only=False,plot_scatter=True,show=False):
    """Plots the plot_cols for every state in state_list.
    Returns plotly figure
    New as of 06/21"""
    import pandas as pd 
    import numpy as np
    ## Get state dataframes
    concat_dfs = []  
    STATES = {}
    
    ## Get each state
    for state in state_list:

        # Grab each state's df and save to STATES
        dfs = get_state_ts(df,state)
        STATES[state] = dfs

        ## for each plot_cols, find all columns that contain that col name
        for plot_col in plot_cols:
            concat_dfs.append(dfs[[col for col in dfs.columns if col.endswith(plot_col)]])#plot_col in col]])

    ## Concatenate final dfs
    plot_df = pd.concat(concat_dfs,axis=1)#[STATES[s] for s in plot_states],axis=1).iplot()
    
    
    ## Set title and df if new_only
    if new_only:
        plot_df = plot_df.diff()
        title = "Coronavirus Cases by State - New Cases"
    else:
        title = 'Coronavirus Cases by State - Cumulative'
    
    ## Reset Indes
    plot_df.reset_index(inplace=True)
    
    
    ## Return Df or plot
    if df_only==False:

        if np.any(['per capita' in x.lower() for x in plot_cols]):
            value_name = "# of Cases - Per Capita"
        else:
            value_name='# of Cases'


        pfig_df_melt = plot_df.melt(id_vars=['Date'],var_name='State',
                                    value_name=value_name)
        
        if plot_scatter:
            plot_func = px.scatter
        else:
            plot_func = px.line
            
            
        # Plot concatenated dfs
        pfig = plot_func(pfig_df_melt,x='Date',y=value_name,color='State',
                      title=title,template='plotly_dark',width=1000,height=700)        
#         pfig.update_xaxes(rangeslider_visible=True)

                # Add range slider
        pfig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=7,
                             label="1week",
                             step="day",
                             stepmode="backward"),
                        dict(count=14,
                             label="2weeks",
                             step="day",
                             stepmode="backward"),
                        dict(count=1,
                             label="1m",
                             step="month",
                             stepmode="backward"),
                        dict(count=6,
                             label="6m",
                             step="month",
                             stepmode="backward"),

                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )
        
        if show:
            pfig.show()
                
        return pfig
    
    else:
        return plot_df#.reset_index()
    
    
    
    
class CoronaData(BaselineData):
    """
    Dataset from the Novel Coronavirus Kaggle repo

    Args:
        BaselineData (Base Class)
    """
    def __init__(self,data_dir='New Data/',run_workflow=True,
                 download=True,verbose=True):
        """
        [summary]

        Args:
            data_dir (str, optional): [description]. Defaults to 'New Data/'.
            run_workflow (bool, optional): [description]. Defaults to True.
            download (bool, optional): [description]. Defaults to True.
            verbose (bool, optional): [description]. Defaults to True.
        """
        import os
        
        ## Save params for later
        self.__download = download
        self.__verbose = verbose
        self._data_folder = data_dir
        os.makedirs(data_dir,exist_ok=True)
        
        ## Download data or set local filepath
        if download:
#             print("[i] DOWNLOADING DATA FROM KAGGLE:")
            self.download_coronavirus_data(verbose=verbose)
            
        else:
            self.get_data_fpath(data_dir)
        
        
        
        ## Load raw_df and df
        self.load_raw_df(verbose=verbose)
        
        ## Prepare State Data
        if run_workflow:
            self.get_and_clean_US()
            self._make_state_dict()
#             print('\n[!] Full Worfklow Complete:')
#             print('\tself.STATES, self.df_us created.')
            

    # @add_method(CoronaData)
    def download_coronavirus_data(self,path=None,verbose=None):
        """Installs the Kaggle Command Line Interface to clone dataset.
        Then extracts dataset to specified path and displays name of main file.
        Args:
            path(str): Folder to extract dataset into (must end with a '/')

        Returns:
            file_list(list): List of full filepaths to downloaded csv files.
        """        
        if verbose==None:
            verbose = self.__verbose
            
        if verbose:
            print('[i] DOWNLOADING DATA USING KAGGLE API')
            print("\thttps://www.kaggle.com/sudalairajkumar/novel-corona-virus-2019-dataset")

        if path is None:
            path = self._data_folder
                                  
        ## Determine if dataset is downloaded via Kaggle CL
        import os,glob
        from zipfile import ZipFile
        from IPython.display import clear_output
        os.makedirs(path, exist_ok=True)

        try:
            import kaggle.api as kaggle
        except:
            ## Install Kaggle 
            os.system("pip install kaggle --upgrade")#
            clear_output()
            if verbose: print('\t- Installed kaggle command line tool.')


        ## Using the kaggle.api          
        import kaggle.api as kaggle     
        kaggle.authenticate()
        kaggle.dataset_download_files('sudalairajkumar/novel-corona-virus-2019-dataset',
                             path=path,force=True,unzip=True)
        
        ## Run Kaggle Command 
        # cmd = 'kaggle datasets download -d sudalairajkumar/novel-corona-virus-2019-dataset'
        # os.system(cmd)

        # ## Extract ZipFile
        # zip_filepath = 'novel-corona-virus-2019-dataset.zip'
        # with ZipFile(zip_filepath) as file:
        #     file.extractall(path)
            
        if self.__verbose:
            print(f'\t- Downloaded dataset .zip and extracted to:"{path}"')
     
        # ## Delete Zip File
        # try:
        #     os.system(f"rm {path}novel-corona-virus-2019-dataset.zip"  )
        # except:
        #     print("ERROR DELETING ZIP FILE")
            
        self.get_data_fpath(path)

        
    def get_data_fpath(self,path):
        """save self._file_list and self._main_file"""
        import glob
        verbose = self.__verbose
        ## Get list of all csvs
        if verbose: print('\t- Extraction Complete.')    
        file_list = glob.glob(path+"*.csv")

        ## Find main df 
        main_file = [file for file in file_list if 'covid_19_data.csv' in file]
#         if verbose: print(f"- The main file name is {main_file}")
        self._file_list = file_list
        self._main_file = main_file[0]
    
    
    
    def load_raw_df(self,fpath=None,kws={},verbose=True):
        """Performs most basic of preprocessing, including renaming date column to 
        Date and dropping 'Last Update', and 'SNo' columns"""
        import pandas as pd
        from IPython.display import display
        if fpath is None:
            fpath = self._main_file

        ## Default Kws
        read_kws = dict(parse_dates=['ObservationDate','Last Update'])

        ## Add User kws
        read_kws = {**read_kws,**kws}

#         if verbose:
#             print(f"[i] Loading {fpath} with read_csv kws:",end='')
#             display(read_kws)

        ## Read in csv and save as self.raw_df
        df = pd.read_csv(fpath,**read_kws)
        self.raw_df = df.copy()
        ## Drop unwated columns
        df.drop(['Last Update',
                 'SNo'],axis=1,inplace=True)
        

        ## Rename Date columns
        df.rename({'ObservationDate':'Date'},axis=1,inplace=True)

        ## Display some info 
        if verbose:
            display(df.head())
            # Countries in the dataset
            print(f"[i] There are "+str(len(df['Country/Region'].unique()))+" countries in the datatset")

            ## Get first and last date
            start_ts = df["Date"].loc[df['Date'].idxmin()].strftime('%m-%d-%Y')
            end_ts = df["Date"].loc[df['Date'].idxmax()].strftime('%m-%d-%Y')
            # DF['Date'].idxmin(), DF['Date'].idxmax()
            print(f"[i] Dates Covered:\n\tFrom {start_ts} to {end_ts}")

        self._df = df.copy()#self.set_datetime_index(df)
        
        
        
    
    def set_datetime_index(self,df_=None,col='Date'):#,drop_old=False):
        """Returns df with specified column as datetime index"""
        import pandas as pd

        ## Grab df from self if None
        if df_ is None:
            df_ = self.df
            
        ## Copy to avoid edits to orig
        df = df_.copy()
        
        ## Convert to date time
        df[col] = pd.to_datetime(df[col],infer_datetime_format=True)
        
        ## Set as index
        df.set_index(df[col],drop=True,inplace=True)
        
        # Drop the column if it is present
        if col in df.columns:
            df.drop(columns=col,inplace=True)
            
        return df
    
    
    
    def load_us_reference_info(self):
        """Return and save US Reference Data"""
        ## Making Master Lookup CSV
        import pandas as pd
        abbrev = pd.read_csv('Reference Data/united_states_abbreviations.csv')
        pop = pd.read_csv('Reference Data/us-pop-est2019-alldata.csv')
        us_pop = pop.loc[pop['STATE']>0][['NAME','POPESTIMATE2019']].copy()
        us_info = pd.merge(abbrev,us_pop,right_on='NAME',left_on='State',how="inner")
        us_info.drop('NAME',axis=1,inplace=True)
        self.reference_data = us_info
        return us_info
    
    
    def calculate_per_capita(self,df_=None,stat_cols = ['Confirmed','Deaths','Recovered']):
        """Calculate Per Capita columns"""
        if df_ is None:
            df_ = self.df
            
        df = df_.copy()
        
        if 'POPESTIMATE2019' in df.columns==False:
            self.load_us_reference_info()
            
        ## ADDING PER CAPITA DATA 
        for col in stat_cols:
            df[f"{col} Per Capita"] = df[col]/df['POPESTIMATE2019']
        df.drop('POPESTIMATE2019',axis=1,inplace=True)
        return df    

    
    
    def get_and_clean_US(self,df=None,#save_as = 'Reference Data/united_states_abbreviations.csv',
                         make_date_index=True,per_capita=True):
        """Takes raw df loaded and extracts United States and processes
        all state names to create new abbreviation column 'state'.
        """
        import pandas as pd
        if df is None:
            df= self._df.copy()
            
        ## Get only US
        df_us = df.groupby('Country/Region').get_group('US').copy() 
        state_lookup = self.load_us_reference_info()


        ## Make renaming dict for states
        STATE_DICT = dict(zip(state_lookup['State'],state_lookup['Abbreviation']))
        STATE_DICT.update({'Chicago':'IL',
                          'Puerto Rico':'PR',
                          'Virgin Islands':'VI',
                          'United States Virgin Islands':'VI'})

        ## Separately Process Rows that contain a city, state 
        df_city_states = df_us[df_us['Province/State'].str.contains(',')]


        ## Finding City Abbreviations in city_states
        import re
        state_expr = re.compile(r"[A-Z\.]{2,4}")
        df_city_states['state'] = df_city_states['Province/State'].apply(state_expr.findall)
        df_city_states = df_city_states.explode('state')


        ## Seperately process Rows that do not contain a city,state
        df_states = df_us[~df_us['Province/State'].str.contains(',')]
        df_states['state'] =  df_states['Province/State'].map(STATE_DICT)

        ## Combining data frame back together
        df = pd.concat([df_states,df_city_states]).sort_index()
#         df = df.dropna(subset=['state'])

        ## Fix some stragglers (like D.C. vs DC)
        df['state'] = df['state'].replace('D.C.','DC')
        
        ## Combine Cleaned Data 
        df = pd.merge(df, state_lookup,left_on='state',right_on="Abbreviation")
        
        df.rename({'State':'State Name'},inplace=True,axis=1)
        df.drop(columns=['Abbreviation','State Name'],inplace =True)
        
    
        ## Add Population Data
        if per_capita:

            for col in  ['Confirmed','Deaths','Recovered']:
                df[f"{col} Per Capita"] = df[col]/df['POPESTIMATE2019']

            ## Remove Population 
            df.drop('POPESTIMATE2019',axis=1,inplace=True)

        if make_date_index:
            df = self.set_datetime_index(df)
        
#         df.drop(columns=['Province/State'],inplace=True)

        self.df_us = df.copy()
#         self.US = df.copy()
        return df

    
    def _make_state_dict(self,df=None,col='state'):
        if df is None:
            df = self.df_us.copy()
            
        elif col not in df.columns:
            msg = f"{col} not in df.columns.\nColumns include:"+'\n'.join(df.columns)
            raise Exception(msg)
            
        state_list=df[col].unique()

        STATES = {}
        for state in state_list:
            STATES[state] = self.get_group_ts(state,df=df)
        self.STATES = STATES


        

class CovidTrackingProject(BaselineData):

    
    def __init__(self,base_folder="New Data/",
                 download=True,verbose=True,df_type='states'):
        self.base_folder = base_folder
        self.__verbose = verbose
        
        
        if download:
            
            if self.__verbose:
                print(f"[i] DOWNLOADING DATASETS FROM COVID TRACKING PROJECT")
                print("\thttps://covidtracking.com/data")
            
            workflow = [self.download_state_meta,
             self.download_us_daily,self.download_state_daily]
            
            for method in workflow:
                try:
                    method()
                except:
                    print('ERROR')
            
        else:
            raise Exception("Non-download loading not implemented yet.")
        
        ## Set .df attribute
        if df_type.lower()=='states':
            self._df_type = df_type
            self._df = self._data[df_type].copy()#self.STATES[self.columns['good']].copy()
            
        elif df_type.lower()=='us':
            self._df_type = df_type
            self._df = self._data[df_type].copy()


    base_url = f"http://covidtracking.com"
    _data = dict()
    urls = dict(us = base_url+'/api/v1/us/daily.csv',
                states = base_url+'/api/v1/states/daily.csv',
                states_metadata = base_url+"/api/v1/states/info.csv"
               )
    
    ## Store good vs deprecated columns
    columns = {'good':['state','fips',
            'positive','negative','death','recovered',
            'hospitalizedCurrently','hospitalizedCumulative',
            'inIcuCurrently','inIcuCumulative',
            'onVentilatorCurrently','onVentilatorCumulative',
             "pending", "dataQualityGrade", 
            "lastUpdateEt", "totalTestsViral", 
            "positiveTestsViral", "negativeTestsViral", 
            "positiveCasesViral", "positiveIncrease", 
            "totalTestResults", "totalTestResultsIncrease", 
            "deathIncrease", "hospitalizedIncrease"],
                  
                  'deprecated':[
                      'checkTimeEt','commercialScore',
                      'dateChecked','dateModified','grade',
                      'hash','hospitalized','negativeIncrease',
                      'negativeRegularScore','negativeScore',
                      'posNeg','positiveScore','score','total',
                  ]
                  
                  
                  }
    columns_us = dict(
        good = ['positive','negative','death','recovered','hospitalizedCurrently',
                 'hospitalizedCumulative',
                'inIcuCurrently', 'inIcuCumulative', 
                'onVentilatorCurrently','onVentilatorCumulative', 
                'states','pending','dateChecked', 'hash',], 
        
        deprecated = ['hospitalized', 'lastModified', 'total', 
             'totalTestResults', 'posNeg', 'deathIncrease',
            'hospitalizedIncrease', 'negativeIncrease', 'positiveIncrease', 
            'totalTestResultsIncrease'])
        
    def get_df(self,which='states',remove_dep_cols=True):
        """
        Method for retrieving either df_states or df_us (default=df_states) with
        deprecated columns removed by default. 

        Args:
            which (str, optional): Which df to return: 'us' or 'states'. Defaults to 'states'.

            remove_dep_cols (bool, optional): Remove deprecated columns. Defaults to True.

        Returns:
            DataFrame: states or US dataframe 

        """
        
        ## Select the correct df
        if which=='states':
            df = self.df_states.copy()
            col_dict = self.columns
        elif which=='us':
            df= self.df_us.copy()
            col_dict = self.columns_us
        else:
            raise Exception('The value for "which" must be either "us" or "states"')

        ## Remove deprecated columns
        if remove_dep_cols:
            df = df[col_dict['good']].copy()
            
        return df
    
    

    
    
            
    def get_csv_save_load(self,url, fpath,read_kws={'parse_dates':['date']}):
        import pandas as pd
        import requests
        response = requests.get(url).content
        
        with open(fpath,'wb') as file:
            file.write(response)

        state_meta = pd.read_csv(fpath,**read_kws)
        if self.__verbose:
            print(f'\t- File saved as: "{fpath}"')

        return state_meta
    
    
    
    def download_us_daily(self):
        key = 'us'
        data = self._download_data_key(key)
#         setattr(self,key,data)
        return data
        
        
    def download_state_daily(self):
        key = 'states'
        data = self._download_data_key(key)#,read_kws={})
#         setattr(self,key,data)
        return data
    
    def download_state_meta(self):
        
        key = 'states_metadata'
        data = self._download_data_key(key,read_kws={})
        
        return data
         

    
    def _download_data_key(self,key,read_kws={'parse_dates':['date'],
                                             'index_col':'date'}):
        #Fetch the corresponding url from self.urls"
        url = self.urls[key]
        
        ## Get and load csv
        data = self.get_csv_save_load(url,fpath=self.base_folder+key+'.csv',
                                      read_kws=read_kws)
        
        ## Save to data dictionary
        self._data[key] = data.copy()
        
        ## Remove dep cols before saving attr:
        if key=='us':
            good_cols = self.columns_us['good']
        else: 
            good_cols = self.columns['good']
            
        data = data[good_cols].copy()
        
        key_to_save = f"df_{key}"
        setattr(self,key_to_save,data)

        return data
    
#     @property
    def help(self):
        print("\n[HELP] For more information, check the api documentation:")
        print("\thttps://covidtracking.com/api")
    
    
    
def set_datetime_index(df_,col='Date',drop=True):#,drop_old=False):
        """Returns df copy with specified column as datetime index"""
        import pandas as pd
            
        ## Copy to avoid edits to orig
        df = df_.copy()
        
        ## Convert to date time
        df[col] = pd.to_datetime(df[col],infer_datetime_format=True)
        
        ## Set as index
        df.set_index(df[col],drop=False,inplace=True)
        
        if drop:
            # Drop the column if it is present
            if col in df.columns:
                df.drop(columns=col,inplace=True)
            
        return df
    
    
    
def set_freq_resample(df,date_col='Date',freq='D', agg_func='sum'):
    """Resamples the dataframe with Freq and agg_func. If index is not
    a datetime axis, will call set_datetime_index. 
    Helper function for get_group_ts """
    ## Make index datetime if it is not already. 
    if isinstance(df.index,pd.DatetimeIndex)==False:
        df = set_datetime_index(df,col=date_col)
        
    ts  = df.resample(freq).agg(agg_func).copy()
    return ts
    
    
    
def get_group_ts(df,group_name,group_col='state',
                     ts_col=None, freq='D', agg_func='sum'):
        """Take df_us and extracts state's data as then Freq/Aggregation provided"""
        from IPython.display import display
        try:
            ## Get state_df group
            group_df = df.groupby(group_col).get_group(group_name).copy()
            
        except Exception:
            print("[!] ERROR!")
#             display(df.head())
            return None
        
        ## Resample and aggregate state data
        group_df = set_freq_resample(group_df,freq=freq,agg_func=agg_func)
#         group_df = group_df.resample(freq).agg(agg_func)


        ## Get and Rename Sum Cols 
        orig_cols = group_df.columns

        ## Create Renamed Sum columns
        for col in orig_cols:
            # Group - Column 
            group_df[f"{group_name} - {col}"] = group_df[col]

        ## Drop original cols
        group_df.drop(orig_cols,axis=1,inplace=True)

        ## Return on columns containing ts_cols
        if ts_col is not None:

            if isinstance(ts_col,str):
                ts_col = [ts_col]

            
            ts_cols_selected=[]
            for column in ts_col:
                ts_cols_selected.extend([col for col in group_df.columns if column in col])

            group_df = group_df[ts_cols_selected]

        return group_df 
    
    
    
def plot_group_ts(df, group_list,group_col, plot_cols = ['Confirmed'],
                df_only=False,
                new_only=False,plot_scatter=True,show=False,
                 width=1000,height=700):
    """Plots all columns conatining the words in plot_cols for every group in group_list.
    Returns plotly figure
    New as of 06/21"""
    import pandas as pd 
    import numpy as np
    
    ## Get state dataframes
    concat_dfs = []  
    GROUPS = {}
    
    ## Get each state
    for group in group_list:

        # Grab each state's df and save to STATES
        dfs = get_group_ts(df,group,group_col)
        GROUPS[group] = dfs

        ## for each plot_cols, find all columns that contain that col name
        for plot_col in plot_cols:
            concat_dfs.append(dfs[[col for col in dfs.columns if col.endswith(plot_col)]])

    ## Concatenate final dfs
    plot_df = pd.concat(concat_dfs,axis=1)
    
    
    ## Set title and df if new_only
    if new_only:
        plot_df = plot_df.diff()
        title = f"New Coronavirus Cases by {group_col}"
    else:
        title = f'Cumulative Coronavirus Cases by {group_col}'
    
    ## Reset Indes
    plot_df.reset_index(inplace=True)
  
    ## Return Df or plot
    if df_only:
         return plot_df#.reset_index()
    
    else:
        ## If any columns are per capita, change titleß
        if np.any(['per capita' in x.lower() for x in plot_cols]):
            value_name = "# of Cases - Per Capita"
        else:
            value_name='# of Cases'
            
            
        ## Melt Data for plotting
        pfig_df_melt = plot_df.melt(id_vars=['Date'],var_name='Group',
                                    value_name=value_name)
        
        ## Set plotting function
        if plot_scatter:
            plot_func = px.scatter
        else:
            plot_func = px.line
    
        # Plot concatenated dfs
        pfig = plot_func(pfig_df_melt,x='Date',y=value_name,color='Group',
                      title=title,template='plotly_dark',width=width,height=height)     
        
        ## Add range slider
        pfig.update_xaxes(rangeslider_visible=True)
        
        ## Display?
        if show:
            pfig.show()
                
        return pfig
    
    
    


# ## funtionize diagnosing
# def diagnose_model(model):
#     """Takes a fit statsmodels model and displays the .summary 
#     and plots the built-in plot.diagnostics()"""
#     display(model.summary())
#     model.plot_diagnostics()
#     plt.tight_layout()
    
    
# def get_df_from_pred(forecast_or_pred,forecast_label='Forecast'):
#     """Takes a PredictionResultsWrapper from statsmodels
#     extracts the confidence intervals and predicted mean and returns in a df"""
#     forecast_df = forecast_or_pred.conf_int()
#     forecast_df.columns = ['Lower CI','Upper CI']
#     forecast_df[forecast_label] = forecast_or_pred.predicted_mean
#     return forecast_df

# def plot_forecast_from_df(forecast_df,ts_diff=None,orig_label='True Data',
#                           forecast_label='Forecast',
#                           last_n_lags=52,figsize=(10,4)):
#     """Takes a forecast_df from get_df_from_pred and optionally 
#     the training/original time series.
    
#     Plots the original ts, the predicted mean and the 
#     confidence invtervals (using fill between)"""
#     fig,ax = plt.subplots(figsize=figsize)

#     if ts_diff is not None:
#         ts_diff.iloc[-last_n_lags:].plot(label='True Data')
        
   
#     forecast_df['Forecast'].plot(ax=ax,label=forecast_label)
#     ax.fill_between(forecast_df.index,
#                     forecast_df['Lower CI'], 
#                     forecast_df['Upper CI'],color='g',alpha=0.3)
#     ax.legend()
#     ax.set(title=f'Forecasted {ts_diff.name}')
#     return fig,ax
        
        
        
### FORECAST SPECIFIC FUNCTIONS

# def get_forecast(model,steps=12):
#     pred = model.get_forecast(steps=steps)
#     forecast = pred.conf_int()
#     forecast.columns = ['Lower CI','Upper CI']
#     forecast['Forecast'] = pred.predicted_mean
#     return forecast

    
# def plot_forecast(model,ts,last_n_lags=365,future_steps=12):
#     forecast_df = get_forecast(model,steps=future_steps)

#     fig,ax = plt.subplots(figsize=(12,5))
#     ts.iloc[-last_n_lags:].plot(label='True Data')
#     forecast_df['Forecast'].plot(ax=ax)
#     ax.fill_between(forecast_df.index,
#                     forecast_df['Lower CI'], forecast_df['Upper CI'],alpha=0.6)
#     ax.legend()
#     ax.set(title=f'Forecasted {ts.name}')
#     return fig,ax


# def evaluate_model(model,ts,last_n_lags =52,steps=12):
#     display(model.summary())
#     model.plot_diagnostics();
#     fig,ax=plot_forecast(model,ts,future_steps=steps,last_n_lags=last_n_lags)
#     return fig,ax

# def evaluate_model(model,ts,test_ts, last_n_lags =,steps=None):
#     diagnose_model(model)
    
#     if steps is None:
#         steps=len(test_ts)
    
#     forecast = model.get_forecast(steps=steps)
#     forecast_df = get_df_from_pred(forecast,)
    
#     fig, ax = plot_forecast_from_df(forecast_df,ts_diff=ts,
#                                     last_n_lags=last_n_lags)
    
#     if test_ts is not None:
#         test_ts.plot(ax=ax)
#     return fig,ax
           