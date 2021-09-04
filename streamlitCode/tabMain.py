import requests, json, urllib, os, re, time, base64
os.sys.path.append("/home/lj/git/MiniProject_LOL/")

import streamlit as st
import pandas as pd
import numpy as np
import dataRead
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode

# @st.cache(allow_output_mutation=True,suppress_st_warning=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# @st.cache(allow_output_mutation=True,suppress_st_warning=True)
def get_img_with_href(local_img_path, target_url):
    img_format = os.path.splitext(local_img_path)[-1].replace('.', '')
    bin_str = get_base64_of_bin_file(local_img_path)
    html_code = f"""
    <a href="{target_url}">
    <img src="data:image/{img_format};base64,{bin_str}" width="100%" height=100%/>
    </a>"""
    return html_code

# @st.cache(allow_output_mutation=True,suppress_st_warning=True)
def page():
    ############
    # fix list #
    ############
    st.markdown("""
    😐 **추가사항**
    ---
    <span style="color:red">
    1. 챔피언 명, 소환사 명 입력시 페이지 변경<br>
    2. 테이블 사이즈 및 링크 기능<br>
    3. 이미지 정렬 및 링크 기능
    <span style="color:red">
    """, unsafe_allow_html=True)
    
    #############
    # First row #
    #############
    st.header("챔피언 리스트")
    cols = st.columns(3)
    champName = cols[0].text_input("챔피언명을 입력하시오.")
    userName = cols[0].text_input("소환사명을 입력하시오.")

    # radio button
    with cols[2]:
        st.subheader(f"챔피어 티어")
        chosen = st.radio("",("TOP", "MIDDLE", "BOTTOM", "JUNGLE", "Support"))
        
    ##############
    # Second Row #
    ##############
    cols = st.columns([1]*12+[6])
    
    ## champion list
    ref, apikey, data = dataRead.read_output()
    displayColEn = ["championId", "lanePropTot", "win"]
    displayColKr = ["챔피언", "픽률", "승률"]
    displayColFormat = dict(zip(displayColKr,["{:s}", "{:.2f}", "{:.2f}"]))
    data_ = (data["champStats"]
             .query("""laneEdit==@chosen""")
             .loc[:,displayColEn])
    data_ = data_.astype({"championId":"string"}) # output 포맷 정하면 삭제
    data_ = pd.merge(ref.champInfoDto[["key", "id"]], data_, left_on=["key"], right_on=["championId"], how="right")
    data_["championId"] = data_["id"]
    data_.drop(["key", "id"], axis=1, inplace=True)
    data_.sort_values(["lanePropTot", "win"], ascending=False, inplace=True)
    data_.reset_index(drop=True, inplace=True)
    data_.columns = displayColKr
    cols[12].dataframe(data_.style.format(displayColFormat))
    ## champion image
    imgDir = "/data1/lolData/RefData/dragontail-11.17.1/11.17.1/img/champion"
    imgLs = np.sort(os.listdir(imgDir))
    for idx in range(len(imgLs)):
        gif_html = get_img_with_href(os.path.join(imgDir,imgLs[idx]), "http://192.168.150.103:8990/?tab=%EC%B1%94%ED%94%BC%EC%96%B8%ED%86%B5%EA%B3%84")
        cols[idx%12].markdown(gif_html, unsafe_allow_html=True)     