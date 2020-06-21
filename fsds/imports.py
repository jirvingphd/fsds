# -*- coding: utf-8 -*-
"""Convience module. 'from bs_ds.imports import *' will pre-load pd,np,plt,mpl,sns"""

def global_imports(modulename,shortname = None, asfunction = False):
        """from stackoverflow: https://stackoverflow.com/questions/11990556/how-to-make-global-imports-from-a-function,
        https://stackoverflow.com/a/46878490"""
        from importlib import import_module

        if shortname is None:
            shortname = modulename

        if asfunction is False:
            globals()[shortname] = import_module(modulename) #__import__(modulename)
        else:
            globals()[shortname] = eval(modulename + "." + shortname)

def clear():
    """Helper function to clear notebook display"""
    import IPython.display as dp
    return dp.clear_output()

def import_packages(import_list_of_tuples = None,  display_table=True): #append_to_default_list=True, imports_have_description = True):
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
        ('numpy','np','scientific computing with Python'),
        ('matplotlib','mpl',"Matplotlib's base OOP module with formatting artists"),
        ('matplotlib.pyplot','plt',"Matplotlib's matlab-like plotting module"),
        ('seaborn','sns',"High-level data visualization library based on matplotlib"),
        ('fsds','fs','Custom data science bootcamp student package'),
        ('IPython.display','dp','Display modules with helpful display and clearing commands.')]#,
        # ('cufflinks','cf','Adds df.iplot() interactive Plotly figs. To use, run >> cf.go_offline()')]

    # if using own list, rename to 'import_list'
    else:
        import_list = import_list_of_tuples


    # Use exec command to create global handle variables and then load in package as that handle
    for package_tuple in import_list:
        package=package_tuple[0]
        handle=package_tuple[1]
        # old way: # exec(f'import {package} as {handle}')
        global_imports(package,handle)


    # Display summary dataframe
    if display_table==True:
        ## Create Columns Names List
        # if imports_have_description==False:
            # columns=['Package','Handle']
        # else:
            # columns=['Package','Handle','Description']

        # create and return styled dataframe
        columns=['Package','Handle','Description']
        df_imported= pd.DataFrame(import_list, columns=columns)
        
        df_imported=pd.concat([df_imported['Handle'],df_imported[['Package','Description']]],axis=1)
        dfs = df_imported.sort_values('Package').style.hide_index().set_caption('Loaded Packages and Handles')
        import fsds as fs
        print(f"fsds v{fs.__version__} loaded.  Read the docs: https://fs-ds.readthedocs.io/en/latest/ ")
        display(dfs)

    # or just print statement
    else:
        return print('Modules successfully loaded.')
    


try:
    from IPython.display import clear_output
    clear_output()
except:
    pass
finally:
    fs = None
    import_packages()
    
try:
    import cufflinks as cf 
    cf.go_offline()
    print('[i] Pandas .iplot() method activated.')
except:
    pass

    