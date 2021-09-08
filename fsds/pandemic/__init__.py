from fsds.pandemic import data_acquisition # as data
from fsds.pandemic import coronavirus_functions as covid
from fsds.pandemic import timeseries_modeling as modeling
from fsds.pandemic.data_acquisition import FULL_WORKFLOW



def upload_kaggle_json(target_folder="/root/.kaggle/"):
    """Helper function to upload kaggle api credentials on Google colab.
    Also pip installs kaggle package. 

    Args:
        target_folder (str, optional):Folder to save kaggle.json to. Defaults to "/root/.kaggle/".

    Raises:
        Exception: If kaggle.json filename not found in uploaded files. 
        
    See this colab notebook for WIP alternatives https://colab.research.google.com/drive/16gL4yExqHQ3jfMHT1ccKhtn_L_H5V2r0?usp=sharing
    """
    from google.colab import files
    import requests,os,json

    ## Make kaggle directory
    os.makedirs(target_folder,exist_ok=True)

    print('[i] You must first create a kaggle.json file from your Accounts page on Kaggle.com.\
    e.g. https://www.kaggle.com/<username>/account')
    print('  - On your local machine, save it to "~/.kaggle/"')
    print('  - Then upload the file using the menu below:')
    ## Upload
    uploaded = files.upload()

    for fn in uploaded.keys():
        print('User uploaded file "{name}" with length {length} bytes'.format(
            name=fn, length=len(uploaded[fn])))


    if 'kaggle.json' in uploaded:
        final_kaggle_fpath = target_folder+'kaggle.json'
        os.rename('kaggle.json',final_kaggle_fpath)

    else:
        raise Exception('kaggle.json not found in uploaded files.')

    # print(f"Contents of {target_folder}")
    # print(os.listdir(target_folder))
    os.chmod(final_kaggle_fpath,600)    

    try:
        import kaggle
    except:
        print('kaggle package not found, installing...')
        os.system("pip install kaggle")
        import kaggle

    print('[i] Kaggle package/API setup complete. You can now "import kaggle".')
    