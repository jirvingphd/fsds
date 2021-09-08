# !pip install -U fsds
from fsds.pandemic import legacy_data_acquisition as legacy
from fsds.imports import *
import pandas as pd

import os,zipfile,json,joblib

# import sys
# sys.path.append('.')

# import functions as fn
import datetime as dt
today = dt.date.today().strftime("%m-%d-%Y")

def load_raw_ts_file(jhu_data_zip, save_fpath,file = 'RAW_us_confirmed_cases.csv',
                      
                     mapper_path='reference_data/state_names_to_codes_map.joblib',
                    verbose=True):
    
    if verbose: 
        print(f"- Loading data from {file}")
    state_to_abbrevs_meta = joblib.load(mapper_path)
    
    ## Extract and load csv
    jhu_data_zip.extract(file,path=save_fpath)
    
    data = pd.read_csv(os.path.join(save_fpath,file))
    
    ## Drop states not included in metadata
    data.insert(1,'State_Code',data['Province_State'].map(state_to_abbrevs_meta))
    data.dropna(subset=['State_Code'],inplace=True)
    return data



def melt_df_to_ts(df_cases,value_name, var_name='Date',
                  multi_index_cols=['State_Code','Date'],
                  id_cols = ['Province_State',"State_Code",'Admin2'],
                  cols_to_drop=['iso2','iso3','code3','UID','Country_Region',
                                'Combined_Key','Lat','Long_','FIPS']):
    
#     value_cols = [c for c in df_cases.columns if c not in [*cols_to_drop,*id_cols]]
    
    ## Remove any cols not in the actual dataframe
    id_cols = [c for c in id_cols if c in df_cases.columns] 
    cols_to_drop = [c for c in cols_to_drop if c in df_cases.columns] 
    
    ## CHECKING FOR NON-DATE COLS TO REMOVE
    value_cols = [c for c in df_cases.columns if c not in [*id_cols,*cols_to_drop]]
    value_cols = list(filter(lambda x: len(x.split('/'))>1,value_cols))
    
    
    df_cases_ts = pd.melt(df_cases, 
                          id_vars=id_cols, value_vars=value_cols,
                          var_name=var_name, value_name=value_name)
    
    df_cases_ts['Date'] = pd.to_datetime(df_cases_ts['Date'])
    df_cases_ts = df_cases_ts.set_index(multi_index_cols).sort_index()
    return df_cases_ts
# help(fn)


def get_hospital_data(verbose=False):
    offset = 0
    ## Getting Hospital Capacity Data
    base_url = 'https://healthdata.gov/resource/g62h-syeh.csv'
    page = 0
    results = []
    print(f"[i] Retrieving hospital data from {base_url}")

    ## seting random, large page-len
    page_len = 1000

    while (page_len>0):
        try:
            if verbose:
                print(f"   - Page {page} (offset = {offset})")
            url = base_url+f"?$offset={offset}"
            df_temp = pd.read_csv(url)
            results.append(df_temp)

            page_len = len(df_temp)
            offset+=page_len
            page+=1
        except Exception as e:
            print('[!] ERROR:')
            print(e)
            print('-- returning raw results list instead of dataframe..')
            return results
        
    return pd.concat(results)

class ColumnDict(dict):
    """Inherits from a normal dictionary.
    
    Methods:
        find_expr_cols: methods for finding columns based on expressions
                        saves the column names under with the expression  as key
        get_all_values: gets list of all unique values stored in dict
    Adds 
    Also saved keep_keys True/False dict of expressions that should be kept or dropped
    """
    keep_keys = {True:list(),False:list(),'id':list()} # Expressions 
    keep_cols = {True:list(),False:list()} # column names
    
    def __init__(self, id_cols=[],*args,**kwargs):

        self.id_cols=id_cols
        ## Empty list of keep keys/cols
#         self['id'] = self.id_cols
        self.keep_keys = {True:list(),False:list(),'id':self.id_cols} # Expressions 
        self.keep_cols = {True:[*self.id_cols],False:list()} # column names
    #     id_cols = list() ## id columns to be auto-kept 
        super().__init__(*args,**kwargs)
    

    
    def get_all_values(self,keep=None):
        """Retrieves list of unique column names:
        Args:
            keep (None, True, False): determines subset of columns returned
            # Adapter from: https://www.geeksforgeeks.org/python-concatenate-dictionary-value-lists/
            """
        if keep is None:
            from itertools import chain
            return [*self.id_cols,*set(list(chain(*self.values())))]
        
        elif keep==True:
            col_list = list(set(self.keep_cols[keep]))
            return [*self.id_cols, *[c for c in col_list if c not in self.id_cols]]
#             return list(set([*self.id_cols,*]))
        elif keep==False:
            return list(set(self.keep_cols[keep]))

        
        
    def find_expr_cols(self,expressions,df,keep,exlcude_known_cols=None):
        """Saves lists of column names as values in dict
        Args:
            Expresssions (str,list): patterns to find in column names 
            df (DataFrame): dataframe to check
            keep (bool): saves expr and cols keep_cols/keep_keys as True or False
            
        TO DO:
            exlcude_known_cols (NOT IMPLEMENTED YET): will check if found columns 
                                are already in any of the known lists of cols
                                
                                
                                
        EXAMPLE USAAGE:
        >>> COLUMNS = ColumnDict()
        >>> COLUMNS.find_expr_cols(['staffing','previous_day','coverage'],
                                    df1,keep=False)
        """
            
        if isinstance(expressions,str):
                expressions = [expressions]
                
        for expr in expressions:
            found_cols = [c for c in df.columns if expr in c]
            self[expr] = found_cols

            ## Save exression and fond_cols to keep_keys/keep_cols
            self.keep_keys[keep].append(expr)
            
            [self.keep_cols[keep].append(c) for c in found_cols if c not in self.keep_cols[keep]]






##################################################################################
def FULL_WORKFLOW(save_state_csvs=False,fpath_raw = r"./data_raw/",
                  fpath_clean = r"./data/", fpath_reference = r"./reference_data/",
                  merge_hospital_data=False,
                  new_to_final_names = {'Deaths':'Deaths',
                                        'Cases':'Cases',
                                        'total_adult_patients_hospitalized_confirmed_covid':'Hospitalized Currently',
                                        'adult_icu_bed_covid_utilization_numerator':'ICU-Covid Currently'}):
    """Run entire data acquisiton process

    Returns:
        df_states (Frame): combined dataframe of all state data 
        STATES (dict): dict of individual state data
    """
    import sys
    
    start = dt.datetime.now()
    
    print(f"========= RUNNING FULL WORKFLOW =========")
    ## Specifying data storage folders
    # fpath_raw = r"./data_raw/"
    # fpath_clean = r"./data/"
    # [os.makedirs(fpath,exist_ok=True) for fpath in [fpath_clean,fpath_raw]]
    [os.makedirs(fpath,exist_ok=True) for fpath in [fpath_clean,fpath_raw,fpath_reference]];

    print("[i] Retrieving kaggle dataset: antgoldbloom/covid19-data-from-john-hopkins-university")
    
    try:
        ## Download kaggle jhu data and make zipfile object
        os.system(f'kaggle datasets download -p "{fpath_raw}" -d antgoldbloom/covid19-data-from-john-hopkins-university')
        jhu_data_zip = zipfile.ZipFile(os.path.join(fpath_raw,'covid19-data-from-john-hopkins-university.zip'))
    except:
        if 'google' in sys.modules:
            from fsds.pandemic import upload_kaggle_json
            upload_kaggle_json()


    ## Getting State Abbrevs
    state_abbrevs = pd.read_csv("https://raw.githubusercontent.com/jirvingphd/predicting-the-pandemic/main/reference_data/united_states_abbreviations.csv")#os.path.join(fpath_reference,'united_states_abbreviations.csv'))

    ## Making dicts of Name:Abbrev and Abbrev:Name
    state_to_abbrevs_map = dict(zip(state_abbrevs['State'],state_abbrevs['Abbreviation']))
    abbrev_to_state_map = dict(zip(state_abbrevs['Abbreviation'],state_abbrevs['State']))
    # state_to_abbrevs_map


    # prep df_metadata
    file = 'CONVENIENT_us_metadata.csv'
    jhu_data_zip.extract(file,path=fpath_raw)
    df_metadata = pd.read_csv(os.path.join(fpath_raw,file))

    ## Adding State Abbrevas to kaggle metadata
    df_metadata.insert(1,'State_Code',df_metadata['Province_State'].map(state_to_abbrevs_map))
    # print(df_metadata.isna().sum())

    ## Dropping us territories
    df_metadata.dropna(subset=['State_Code'], inplace=True)

    ## Saving county info
    df_metadata.to_csv(os.path.join(fpath_reference,"us_metadata_counties.csv"),index=False)


    ## Saving a states-only version with aggregated populations and mean lat/long
    df_state_metadata = df_metadata.groupby('Province_State',as_index=False).agg({'Population':'sum',
                                                "Lat":'mean',"Long":"mean"})
    df_state_metadata.insert(1,'State_Code',df_state_metadata['Province_State'].map(state_to_abbrevs_map))
    df_state_metadata.to_csv(os.path.join(fpath_reference,"us_metadata_states.csv"),index=False)


    ## Making and saving remapping dicts

    state_to_abbrevs_meta = dict(zip(df_state_metadata['Province_State'],df_state_metadata['State_Code']))
    abbrev_to_state_meta = dict(zip(df_state_metadata['State_Code'],df_state_metadata['Province_State']))

    joblib.dump(state_to_abbrevs_meta, os.path.join(fpath_reference,'state_names_to_codes_map.joblib'))
    joblib.dump(abbrev_to_state_meta, os.path.join(fpath_reference,'state_codes_to_names_map.joblib'))

    ## save mapper fo state to code for function
    mapper_path = os.path.join(fpath_reference,'state_names_to_codes_map.joblib')
    mapper_path
    
    
    ## Prep ` df_cases_ts`
    df_cases = load_raw_ts_file(jhu_data_zip, save_fpath=fpath_raw, file = 'RAW_us_confirmed_cases.csv',)
    df_cases_ts = melt_df_to_ts(df_cases,'Cases')
    df_cases_ts
    
    
    ## Prep df_deaths_ts
    df_deaths = load_raw_ts_file(jhu_data_zip,save_fpath=fpath_raw,file = 'RAW_us_deaths.csv')
    df_deaths_ts = melt_df_to_ts(df_deaths,'Deaths')

    ## Merge df_cases_ts and df_deaths_ts
    df_cases_deaths_ts = pd.merge(df_cases_ts.reset_index(), df_deaths_ts.reset_index())
    df_cases_deaths_ts

    df_cases_deaths_ts.to_csv(os.path.join(fpath_clean,'us_states_cases_deaths.csv'),index=True)

    ## Resample to Daily State Data
    df_daily_cases_deaths_ts = df_cases_deaths_ts.set_index('Date')\
                                .groupby('State_Code').resample("D")\
                                    .sum().reset_index()
    df_daily_cases_deaths_ts.to_csv(os.path.join(fpath_clean,'us_states_daily_cases_deaths.csv'),index=True)
    df_daily_cases_deaths_ts
    
    ##### HOSPITAL DATA
    ## Get hispital Data
    df1 = get_hospital_data()
    df1 = df1.rename({'state':'State_Code',
                     'date':'Date'},axis=1)
    df1['Date'] = pd.to_datetime(df1['Date'])
    df1 = df1.sort_values(['State_Code','Date'])
    
    #### SIFT THROUGH COLUMNS
    COLUMNS = ColumnDict(id_cols=['State_Code','Date'])

    ## saving names to DROP to COLUMNS dict
    drop_col_expressions = ['staff','previous_day','coverage','onset']
    COLUMNS.find_expr_cols(drop_col_expressions,df1,keep=False)


    ## saving names to KEEP to COLUMNS dict
    keep_col_expressions = ['inpatient_bed','adult_icu_bed','utilization',
                            'total_adult_patients','total_pediatric_patients',
                        'percent_of_inpatients_with_covid','deaths']
    COLUMNS.find_expr_cols(keep_col_expressions,df1,keep=True)


    ## Making df_hospitals
    df_hospitals = df1[COLUMNS.get_all_values(keep=True)].copy()
    df_hospitals = df_hospitals.set_index(COLUMNS.id_cols).sort_index()
    df_hospitals.reset_index().to_csv(os.path.join(fpath_raw,'hospital_data.csv'))

    df_hospitals#.loc['MD',['inpatient_beds_utilization']].plot()
    joblib.dump(COLUMNS,os.path.join(fpath_reference,'COLUMNS.joblib'))
    
    #### combine all data
    df = pd.merge(df_daily_cases_deaths_ts,df_hospitals.reset_index())
    df.to_csv(os.path.join(fpath_clean,'combined_us_states_full_data.csv'),index=False)
    df
    
    
    ## Saving State CSVs
    if save_state_csvs:
        DATA_FOLDER = os.path.join(fpath_clean,'state_data/')
        os.makedirs(DATA_FOLDER,exist_ok=True)

    ## make STATES dict
    unique_states = df['State_Code'].unique()
    df_states = df.set_index(['State_Code','Date']).sort_index()

    STATES = {}
    for state in unique_states:    
        df_state = df_states.loc[state].copy()
        if save_state_csvs:
            df_state.to_csv(f"{DATA_FOLDER}combined_data_{state}.csv.gz",compression='gzip')   
        STATES[state] = df_state.copy()


    joblib.dump(STATES,os.path.join(fpath_clean,'STATE_DICT.joblib'))
    
    end = dt.datetime.now()
    print('[i] Workflow completed.')
    print(f'\tRun time={end-start} sec.')
    print('[i]The final files of note:')
    print(f"\t{os.path.join(fpath_clean,'combined_us_states_full_data.csv')}")
    print(f"\t{os.path.join(fpath_clean,'STATE_DICT.joblib')}")
    
    if merge_hospital_data:
        ## saving final version of dataset
        FINAL_STATES = {} #pd.DataFrame(index=date_index)

        for state, state_df in STATES.items():
            
            state_df = state_df[list(new_to_final_names.keys())].copy().sort_index()
            state_df = state_df.rename(new_to_final_names,axis=1)
            
            ## Renamaed columns to process
            hospital_cols = ['Hospitalized Currently','ICU-Covid Currently']
            cumulative_cols = ['Deaths','Cases'] # cols to diff
            
            ## fill hospital cols with 0
            state_df[hospital_cols] = state_df[hospital_cols].fillna(0)

            for col in cumulative_cols:
                state_df[f"{col}-New"] = state_df[col].diff().fillna(0)
            state_df

        #     state_df.columns = [f"{state}: {c}" for c in state_df.columns]
            FINAL_STATES[state]= state_df.copy()


        DF = pd.concat(FINAL_STATES)

        ## Saving Final Combined DataFrame as both comnpressed csv and pickle
        fpath_final_df_csv = os.path.join(fpath_clean,'FINAL_STATES.csv.gz')
        fpath_final_df_pickle = fpath_final_df_csv.replace('.csv.gz','.pickle')

        DF.to_csv( fpath_final_df_csv,compression='gzip')
        print(f"[i] Final joined data (DF) saved as {fpath_final_df_csv}")

        DF.to_pickle( fpath_final_df_pickle)
        print(f"[i] Final joined data (DF) saved as {fpath_final_df_pickle}")

        return DF,FINAL_STATES
    else:
        return df_states, STATES



if __name__=='__main__':
    FULL_WORKFLOW()