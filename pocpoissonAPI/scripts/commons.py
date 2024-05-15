import json
import os
from pathlib import Path

import pandas as pd


"""
Retrieve a file from an absolute path, computed from the script repo (and not the Python one)
Returns a readable json file (dictionary).
relative_path : Relative path of resource
"""
def get_data_from_file(relative_path):
    return json.loads((Path(__file__).parent / relative_path).read_text())

def read_excel_relative(relative_path, sn = 0):
    return pd.read_excel((Path(__file__).parent / relative_path).resolve(), sheet_name=sn)

def save_json(contents_json, relative_path):
    target = str((Path(__file__).parent / relative_path).resolve())
    with open(target, 'w', encoding='utf-8') as json_file_handler:
        json_file_handler.write(json.dumps(contents_json, indent=4, ensure_ascii=True))
        json_file_handler.close()

def xlsx_is_null(value):
    if value is None or pd.isna(value) or len(str(value)) == 0 or str(value).lower() == "nan":
        return True
    return False

def fileList(source, prefixlist):
    matches = []
    for root, dirnames, filenames in os.walk(source):
        for filename in filenames:
            if filename.lower().endswith(prefixlist):
                matches.append(filename)
    return matches

def fileListRelative(relative_path, prefixlist):
    target = (Path(__file__).parent / relative_path).resolve()
    return fileList(target, prefixlist)



VAR = get_data_from_file("../conf/call_conf.json")
def findConfFromScript(varName,defaultvalue):
    ret = None
    if varName in VAR :
       return VAR[varName]["value"]
    if ret is None:
        return defaultvalue

    """ Get URL as a catalog, from stored file
    # json_file_path_url : relative path to the catalog file ##PARAM AS STRING##
    """

def get_data_url(
        json_file_path_url=findConfFromScript("txt_file_outputpath", "../resourcesGenerated/ssp_url.txt")):
        mat_urls = get_data_from_file(json_file_path_url)
        mat_kssps = {}
        for ssp in mat_urls["catalog"]:
            mat_kssps[ssp["fishCode"]] = ssp
        return mat_kssps