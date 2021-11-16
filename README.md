# fsds
 Cohort agnostic  version of fsds_100719
- Deployment Installations (mac) [[source](https://packaging.python.org/tutorials/packaging-projects/)]:
    - `python3 -m pip install --upgrade pip`
    - `python3 -m pip install --upgrade build`
    - `python3 -m pip install --upgrade twine`
    
    
- Deployment workflow:
    1. generate docs with `python docs/conf.py` (optional)
    2. Commit all changes.
    3. Increase version # with bump2version `bump2version patch` or `bump2version minor`
    4. Build distribution archives: `python -m build`
    5. Upload to twine: `twine upload dist/*`