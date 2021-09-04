import os, re
os.sys.path.append("/home/lj/git/MiniProject_LOL/")

import streamlit as st
import pandas as pd
import lolApi, lolRef

# read output
# @st.cache(allow_output_mutation=True,suppress_st_warning=True)
def read_output():
    ref = lolRef.Ref()
    apikey = lolApi.loadKey("/data1/lolData/RefData/product_keys.txt")
    outputDir  = "/data1/lolData/cgLeague/sampleOutput"
    data = dict()
    for file in os.listdir(outputDir):
        data[re.sub("_|[0-9]|.csv|.ftr","", file)] = pd.read_csv(f"{outputDir}/{file}")
    
    return ref, apikey, data