# -*- coding: utf-8 -*-
"""Convience module. 'from bs_ds.imports import *' will pre-load pd,np,plt,mpl,sns"""

def global_imports(modulename,shortname = None, asfunction = False,check_vers=True):
        """from stackoverflow: https://stackoverflow.com/questions/11990556/how-to-make-global-imports-from-a-function,
        https://stackoverflow.com/a/46878490"""
        from importlib import import_module

        if shortname is None:
            shortname = modulename

        if asfunction is False:
            globals()[shortname] = import_module(modulename) #__import__(modulename)
        else:
            globals()[shortname] = eval(modulename + "." + shortname)
            
        if check_vers:
            return globals()[shortname].__version__

def clear():
    """Helper function to clear notebook display"""
    import IPython.display as dp
    return dp.clear_output()

def import_packages(import_list_of_tuples = None,  display_table=True, check_versions=True,
                    check_packages = ['matplotlib','seaborn','pandas','numpy','sklearn'] ): #append_to_default_list=True, imports_have_description = True):
    """Uses the exec function to load in a list of tuples with:
    [('module','md','example generic tuple item')] formatting.
    >> Default imports_list:
    [('pandas',     'pd',   'High performance data structures and tools'),
    ('numpy',       'np',   'scientific computing with Python'),
    ('matplotlib',  'mpl',  "Matplotlib's base OOP module with formatting artists"),
    ('matplotlib.pyplot',   'plt',  "Matplotlib's matlab-like plotting module"),
    ('seaborn',     'sns',  "High-level data visualization library based on matplotlib"),
    ('IPython.display','dp','Display modules with helpful display and clearing commands.')
    ('fsds','fs','Custom data science bootcamp student package')]
    """


    # import_list=[]
    from IPython.display import display
    import pandas as pd
    # if using default import list, create it:
    if (import_list_of_tuples is None): #or (append_to_default_list is True):
        import_list = [('pandas','pd','High performance data structures and tools'),
                       ('fsds','fs','Custom data science bootcamp student package'),
                       ('numpy','np','scientific computing with Python'),
                       ('matplotlib','mpl',"Matplotlib's base OOP module with formatting artists"),
                       ('matplotlib.pyplot','plt',"Matplotlib's matlab-like plotting module"),
                       ('seaborn','sns',"High-level data visualization library based on matplotlib"),
                       ('IPython.display','dp','Display modules with helpful display and clearing commands.')]#,
        # ('cufflinks','cf','Adds df.iplot() interactive Plotly figs. To use, run >> cf.go_offline()')]

    # if using own list, rename to 'import_list'
    else:
        import_list = import_list_of_tuples


    # Use exec command to create global handle variables and then load in package as that handle
    version_list = [['Package','Version']]
    for package,handle,_ in import_list:
        # old way: # exec(f'import {package} as {handle}')
        # global_imports(package,handle)
         
        global_imports(package,handle,check_vers=False)


    ## Make dataframe of imports
    # create and return styled dataframe
    columns=['Package','Handle','Description']
    df_imported= pd.DataFrame(import_list, columns=columns)
    df_imports = df_imported[['Handle','Package','Description']]
    
    
  
    
    
    ## make dataframe of versions
    if check_versions:
        pkg_vers_df = check_package_versions(packages=check_packages)
        
        df_imports = pd.merge(df_imports, pkg_vers_df,on='Package',how='outer')
        df_imports = df_imports[['Handle','Package','Version','Description']]
        df_imports.fillna(' - ',inplace=True)
    
    
        
        # display(pkg_vers_df.style.hide_index().set_caption('Package Version Report')) 

    # Display summary dataframe
    if display_table==True:            
        ## Create Columns Names List

        # create and return styled dataframe
        # columns=['Package','Handle','Description']
        # df_imported= pd.DataFrame(import_list, columns=columns)
        # # df_imported=pd.concat([df_imported['Handle'],df_imported[['Package','Description']]],axis=1)
        
        # # df_imports = pd.merge(df_imported,pkg_vers_df,on='Package')
        # # df_imports = df_imports[['Handle','Package','Description','Version']]
        # df_imports = df_imported[['Handle','Package','Description']]
        #.sort_values('Package').
        import fsds as fs
        # print(f"fsds v{fs.__version__} loaded.")#  Read the docs: https://fs-ds.readthedocs.io/en/latest/ ")
        dfs = df_imports.style.hide_index().set_caption('Loaded Packages and Handles')
        display(dfs)
        

    # or just print statement
    else:
        print('Modules successfully loaded.')
        

    



def check_package_versions(packages = ['matplotlib','seaborn','pandas','numpy','sklearn'] ):
    """SEEE TESTING NOTEBOOK"""
    import pandas as pd
    version_list = [['Package','Version']]
    
    for package in packages:
        if '.' not in package:
            vers = global_imports(package,None,check_vers=True)
            version_list.append([package,vers])
            
    pkg_vers_df = pd.DataFrame(version_list[1:],columns=version_list[0])
    return pkg_vers_df



try:
    from IPython.display import clear_output
    clear_output()
except:
    pass
finally:
    fs = None
    import_packages()
    
# try:
#     import cufflinks as cf 
#     cf.go_offline()
#     print('[i] Pandas .iplot() method activated.')
# except:
#     pass

    