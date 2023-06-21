#!python
# melt, pivot or unpivot columns
# operation:
# - melt: columns to rows (wide table to long table)
# - pivot: rows to columns (long table to wide table)
# - unpivot: similar to melt but using numeric prefixes
# input_path: path to source data
# columns:
# - melt: which columns will be melted into long form
# - pivot: 
# v1.0 02/2019 paulo.ernesto
'''
usage: $0 operation%melt,pivot,unpivot input_path*csv,xls,xlsx,xlsm,dm keys#column:input_path pivot_var:input_path values#column:input_path fill99@ output_path*csv,xlsx
'''
import sys, os.path

import pandas as pd
import numpy as np
import re

# import modules from a pyz (zip) file with same name as scripts
sys.path.insert(0, os.path.splitext(sys.argv[0])[0] + '.pyz')

from _gui import usage_gui, commalist, pd_load_dataframe, pd_save_dataframe, list_any


def db_melt_table(operation, input_path, keys, pivot_var, values, fill99, output_path):
  print("# db_melt_table", file=sys.stderr)

  if pd.__version__ < '0.20':
    from pandas_core_reshape import melt, pivot_table
    pd.DataFrame.melt = melt
    pd.DataFrame.pivot_table = pivot_table

  if isinstance(input_path, pd.DataFrame):
    df = input_table
  else:
    df = pd_load_dataframe(input_path)
  if not keys:
    keys = None
  elif isinstance(keys, (commalist, str)):
    keys = keys.split(';')
  if isinstance(values, (commalist, str)):
    values = values.split(';')

  if operation == 'melt':
    if not pivot_var:
      pivot_var = None
    if not list_any(values):
      values = None
    df = df.melt(keys, values, pivot_var)

  if operation == 'pivot':
    df = df.pivot_table(values, keys, pivot_var)
  
  if operation == 'unpivot':
    odf = None
    if not pivot_var:
      pivot_var = None
    vl = {}
    
    for v0 in values:
      for v1 in df.columns:
        if v1.endswith(v0):
          k = v1[:-1]
          if k not in vl:
            vl[k] = []
          vl[k].append(v1)
    for k,v in vl.items():
      kdf = df.melt(keys, v, pivot_var, k)
      #kdf[pivot_var].str.removeprefix(k)
      #pd.Series.str.removeprefix(kdf[pivot_var], k)
      #kdf[pivot_var].replace(k, '', inplace=True)
      kdf[pivot_var] = kdf[pivot_var].apply(lambda _: re.sub(k, '', _))
      if odf is None:
        odf = kdf
      else:
        odf = pd.merge(odf, kdf, 'outer', keys + [pivot_var])
      #df = df.melt(keys, values, pivot_var)
    df = odf

  if int(fill99):
    df.fillna(-99.0, inplace=True)
  else:
    df.fillna('', inplace=True)


  if not output_path:
    print(df.to_string())
  else:
    #pd_flat_columns(df)
    pd_save_dataframe(df, output_path)

  print("finished", file=sys.stderr)


main = db_melt_table

if __name__=="__main__" and sys.argv[0].endswith('db_melt_table.py'):
  usage_gui(__doc__)
