### SET OF PYTHON FUNCTION FOR CALLING BY API POC POISSON
## REFRENCES REGENERATION
# alexandre.liccardi@ofb.gouv.fr, 12/08/2023
# Update : alexandre.liccardi@ofb.gouv.fr, 05/01/2024

## Importing Python packages
import re
from itertools import combinations
from scripts import commons

""" Get a dictionary with all distances between species, from the XLSX file provided by the fish experts.
# Quite complex, cause a parsing of the file is needed.
# xlsx_file_path : relative path to the XLSX file with distance between fixh species (given by the experts).
"""
def get_distances_sp(xlsx_file_path):
    df_sheet_index = commons.read_excel_relative(xlsx_file_path)
    liste_ssp = {}
    nb_empty = 0

    # Setting of the first non-empty element
    for code_alt in df_sheet_index["Code alt"]:
        if code_alt is None or commons.pd.isna(code_alt) or len(code_alt) == 0 or code_alt.lower() == "nan":
            nb_empty += 1
        break
    # 1st round (1st line "0" index) + gap due to empty values
    i = nb_empty - 2

    # Building the list of species
    for code_alt in df_sheet_index["Code alt"]:
        i += 1
        if commons.xlsx_is_null(code_alt):
            continue
        liste_ssp[code_alt] = i

    # Simple dictionary computation
    mat_dist_ssp = {}
    for ssp1_i in liste_ssp.items():
        ssp1_n = ssp1_i[0]
        ssp1_l = ssp1_i[1]
        ssp1_md = {}
        for ssp2_i in liste_ssp.items():
            ssp2_n = ssp2_i[0]
            ssp2_l = ssp2_i[1]
            if ssp2_n in ssp1_md.keys():
                continue
            if ssp1_n == ssp2_n:
                ssp1_md[ssp2_n] = 0
                continue
            corresp = df_sheet_index[ssp2_n][ssp1_l]
            if not commons.xlsx_is_null(corresp):
                ssp1_md[ssp2_n] = corresp
                continue
            corresp = df_sheet_index[ssp1_n][ssp2_l]
            if not commons.xlsx_is_null(corresp):
                ssp1_md[ssp2_n] = corresp
                continue
        mat_dist_ssp[ssp1_n] = ssp1_md
    return mat_dist_ssp

"""  Dictionary ("catalog of image URL") regeneration
# Results are stored in files, returns a dictionary
# export : regenerate files if True
# img_file_path : storage path of images, used to fill the catalog ##PARAM AS STRING##
# xlsx_file_path : XLSX path of species characteristics, provided by fish experts ##PARAM AS STRING##
# img_ssp : URL of images from internet (provided by the API) ##PARAM AS STRING##
# json_file_path : export path for catalog, JSON ##PARAM AS STRING##
# txt_file_path : export path for catalog, JSON text version ##PARAM AS STRING##
"""
def regenReferences_img_urls(
        export = True,
        img_file_path=commons.findConfFromScript("img_file_path","../../pocpoisson/img/"),
        xlsx_file_path=commons.findConfFromScript("char_xlsx_file_path","../resources/referentiel_ssp.xlsx"),
        json_file_path=commons.findConfFromScript("json_file_outputpath","../resourcesGenerated/ssp_url.json"),
        txt_file_path=commons.findConfFromScript("txt_file_outputpath","../resourcesGenerated/ssp_url.txt"),
        img_ssp=commons.findConfFromScript("img_ssp_url","https://annumenv.ofb.fr/pocpoisson/img/")
    ):

    print("###  Conversion xlsx fichier standard especes vers json")
    vars = {"fishName": "lb_nom_commun", "fishNameScientific": "lb_nom", "fishCode": "cd_espece", "inpnLink": "url"}
    results = commons.fileListRelative(img_file_path, ("jpg"))

    # Building list of species
    df_sheet_index = commons.read_excel_relative(xlsx_file_path)
    liste_ssp = {}
    i = -1
    for code_alt in df_sheet_index["cd_espece"]:
        i += 1
        if commons.xlsx_is_null(code_alt):
            continue
        liste_ssp[code_alt] = i

    # For each species, a regex is used to match file names and flag potential candidate images
    data_list = []
    data_dict = {}
    for ssp in liste_ssp.items():
        ssp_mat = {}
        urls_ssp = []
        print("Traitement images URL : "+ssp[0])
        for result in results :
            if re.findall(r".[^a-zA-Z]"+str.lower(ssp[0])+"[^a-zA-Z]", str.lower(result)):
                urls_ssp.append(img_ssp+result)
        print("Trouvés : " + str(len(urls_ssp)))
        for info in vars.items():
            ssp_mat[info[0]] = df_sheet_index[info[1]][ssp[1]]
        ssp_mat["imageUrl"] = urls_ssp
        ssp_mat["nb_urls"] = len(urls_ssp)
        data_dict[ssp[0]] = ssp_mat
        if len(urls_ssp) > 0:
            data_list.append(ssp_mat)

    # JSON export
    data_dict_f = {'catalog': data_list}
    if export :
        commons.save_json(commons.json.dumps(data_dict_f, indent=4, ensure_ascii=False), json_file_path)
        print("Exporté vers : " + json_file_path)
        commons.save_json(data_dict_f, txt_file_path)
        print("Exporté vers : " + json_file_path)
    return data_dict

""" Retrieve additional informations, for each combination (dictionary feed)
# sspref : reference species code
# combination : set of species code
# ssp_dist : distance dictionaryu between species
# mat_ref_urls : subdictionary for the reference species and the distance
"""
def get_combination_details(sspref, combination, ssp_dist, mat_ref_urls):
    sc = 0
    sc_list = []
    sc_nburls = []
    for ssp_c in combination:
        sc += ssp_dist[sspref][ssp_c]
        sc_list.append(ssp_dist[sspref][ssp_c])
        nburl = mat_ref_urls[ssp_c]["nb_urls"] if ssp_c in mat_ref_urls else 0
        sc_nburls.append(nburl)
    return {
        "distance": sc,
        "combinaison": combination,
        "nb_url_min": min(sc_nburls),
        "min_dist": min(sc_list),
        "max_dist": max(sc_list)
    }
""" 
Sequence of combinations regeneration
json_file_path : export file path (auto-generated from call),
xlsx_file_path : xlsx_file_path : relative path to the XLSX file with distance between fixh species (given by the experts),
ssp_ref_list : if provided, sublist of species limiting the references in combinations sets . Default : None,
ssp_challenged_list :  if provided, sublist of species limiting the species for combination sets. Default : None,
"""
def regenReferences_combinations(
                                 json_file_path,
                                 xlsx_file_path,
                                 ssp_ref_list = None,
                                 ssp_challenged_list = None):
    mat_ref_urls = commons.get_data_url()
    ssp_dist = get_distances_sp(xlsx_file_path)
    if ssp_ref_list is None:
        ssp_ref_list = [k for k in get_distances_sp(xlsx_file_path)]
    if ssp_challenged_list is None:
        ssp_challenged_list = mat_ref_urls
    for ssp in ssp_ref_list :
        combinations_ssp = combinations([k for k in ssp_challenged_list if k!= ssp], 3)
        listComb_ssp = {}
        for combination in combinations_ssp:
            detailledCombination = get_combination_details(ssp, combination, ssp_dist, mat_ref_urls)
            idx = "d" + str(detailledCombination["distance"])
            if idx not in listComb_ssp or listComb_ssp[idx] is None:
                listComb_ssp[idx] = []
            listComb_ssp[idx].append(detailledCombination)
        export_path = json_file_path + "combinations_" + ssp.replace("?", "xxx") + ".json"
        commons.save_json(listComb_ssp, export_path)
        print("Exporté vers : " + export_path)

""" 
Sequence of combinations regeneration, one-level limited
level : level of difficulty, see configuration file level_quest.json ##PARAM AS STRING##
loc_file_name : configuration file path for difficulty levels, default : "../conf/level_quest.json" ##PARAM AS STRING##
xlsx_file_path : relative path to the XLSX file with distance between fixh species (given by the experts), default : "../resources/Tab_especes_20230616.xlsx" ##PARAM AS STRING##
json_file_path : output directory, default : "../resourcesGenerated" ##PARAM AS STRING##
"""
def regenReferences_combinations_bylevel(
                                 level,
                                 loc_file_name=commons.findConfFromScript("level_conf_path_fromscript","../conf/level_quest.json"),
                                 xlsx_file_path=commons.findConfFromScript("expert_xlsx_path_fromscript","../resources/Tab_especes_20230616.xlsx"),
                                 json_file_path=commons.findConfFromScript("output_generated_path_fromscript","../resourcesGenerated")):
    print("### Régénération des combinaisons "+level)
    list_ssp = [k["fishCode"] for k in commons.get_data_from_file(loc_file_name)[level]["species"]]
    regenReferences_combinations(json_file_path+"/"+level+"_", xlsx_file_path,list_ssp,list_ssp)

# Default sequence for resources regeneration
regenReferences_img_urls()
regenReferences_combinations_bylevel("easy")
regenReferences_combinations_bylevel("medium")
regenReferences_combinations_bylevel("expert")