### SET OF PYTHON FUNCTION FOR CALLING BY API POC POISSON
## API QUESTIONS
# alexandre.liccardi@ofb.gouv.fr, 12/08/2023
# Update : alexandre.liccardi@ofb.gouv.fr, 05/01/2024

## Importing Python packages
import sys
from numpy import random
from scripts import commons



"""
Provide a set of combinations, respecting the distance conditions set by the difficulty level
The difficulty of a combination is given by the cumulative distance from the reference species to each species of the combination, but also by the smallest and the longest distance between the reference and a species of the combination.
i_key : cumulative distance for all species
data : dataset of all combinations, for the reference species
min_dist : minimum distance, from one species to the reference species
max_dist : maximum distance, from one species to the reference species
"""
def check_get_question_u_combinaisons(i_key, data, min_dist, max_dist):
    key = "d" + str(i_key)
    if key in data:
        data_e = [data_d for data_d in data[key] if data_d["min_dist"] >= min_dist and data_d["max_dist"] <= max_dist]
        if data_e is not None and len(data_e) > 0:
            return data_e
    return None

"""
Generate a question (or many, depending on nb_questions) respecting the conditions for ONE SPECIES GIVEN FOR REFERENCE.
Returns a dictionary
level : level of difficulty, see configuration file level_quest.json
ssp_code : code for the species used as a reference
rep_file_path : relative path of the repository, in which previously generated combinations are stored
min_dist : according to difficulty level, shortest distance between the reference and one species in the question
max_dist : according to difficulty level, longest distance between the reference and one species in the question
dist_target : cumulative distance between all species and the reference, targeted by the algorithm
correction_nb_url : number of image URLs sent back, for display is the correction panel
tolerance : levels of difficulty and profiles are given for precise distance between cases (species drawn), but the exact match can be out of reach no matter how many trials are drawn. A "tolerance" factor is used to blur the match (for instance, for a tolerance set at 2, the algorithm reaching for a distance of 2 will target 2, then 1, then 3, then 0, then 4). Default : 4 
data_url : catalog of image URLs
nb_questions : number of question(s) generated. Current use is 1, as the profile is designed to provide a question for each targeted distance . Default : 1 
"""
def get_questions(level, ssp_code, rep_file_path, min_dist, max_dist, dist_target, correction_nb_url, tolerance, data_url, nb_questions=1):
    # Data import from external sources (respectively images URL, list of combination for the reference species)
    data_url_ref = data_url[ssp_code]
    data = commons.get_data_from_file(rep_file_path +"/"+ level+"_" + "combinations_" + ssp_code.replace("?", "xxx") + ".json")

    # Get the combinations according to the distance conditions
    i = 0
    used_dist = dist_target
    data_e = check_get_question_u_combinaisons(used_dist, data, min_dist, max_dist)
    # "Tolerance" parameter use an iterative approach : trying of dist_target - 1, then dist_target + 1, then dist_target - 2, then dist_target + 2... until the cumulative element (here 1 then 2) is greater than the "tolerance" parameter.
    while (data_e is None and i <= tolerance):
        for j in [-1, 1]:
            used_dist = dist_target + i * j
            data_e = check_get_question_u_combinaisons(used_dist, data, min_dist, max_dist)
            if data_e is not None and len(data_e) > 0:
                break
        i += 1
    # If the solution is not found within the full range of "tolerance", None is sent back
    if data_e is None:
        return None
    # Random choice of combinations
    # In pratice, if nb_questions = 1 these lines are unnecessary. They are kept here, because this code is a generalization for more numerous use (i.e. when nb_questions > 1).
    tot_nb_url_min = sum(d['nb_url_min'] for d in data_e)
    proba_nb_url_min = ([d['nb_url_min'] / tot_nb_url_min for d in data_e])
    data_e = random.choice(data_e, nb_questions, p=proba_nb_url_min)
    # Supplementary dictionary information feed
    i_ssp = 0
    for d_question in data_e:
        d_question["used_dist"] = used_dist
        d_question["target_dist"] = dist_target
        d_question["fishCode_reference"] = ssp_code
        pic_url = random.choice(data_url_ref['imageUrl'])
        pic_url_all = []
        while len(pic_url_all) < correction_nb_url:
            pic_url_all.append(random.choice(data_url_ref['imageUrl']))
        inpn = data_url_ref['inpnLink']
        fishNameScientific = data_url_ref['fishNameScientific']
        fishName = data_url_ref['fishName']

        d_question_fishes = []
        d_question_fishes.append(
            {"pic_url": pic_url, "pic_url_all": pic_url_all, "inpn": inpn, "fishCode": ssp_code, "fishName": fishName,
             "fishNameScientific": fishNameScientific})
        for comb in d_question["combinaison"]:
            i_ssp += 1
            pic_url = random.choice(data_url[comb]['imageUrl']) if data_url[comb]['imageUrl'] else None
            inpn = data_url[comb]['inpnLink']
            fishNameScientific = data_url[comb]['fishNameScientific']
            fishName = data_url[comb]['fishName']
            d_question_fishes.append({"fishCode": comb, "pic_url": pic_url, "inpn": inpn, "fishName": fishName,
                                      "fishNameScientific": fishNameScientific})
        d_question['fishes'] = d_question_fishes

    return data_e


"""
Generative function of questions, including specified configuratio for API calling
Returns a stringifyed json, set up to the API specifications for the pool of questions
level : level of difficulty, see configuration file level_quest.json
profile : for difficulty within the level (profile), see configuration file level_quest.json - default : "basic"
correction_nb_url : number of images url sent back in addition to questions,  
n_max_try : it is not guaranteed, that the get_questions function will return a non-empty table (because of iterative draws). Number of trials to get a usefull answer. Default : 10
tolerance : levels of difficulty and profiles are given for precise distance between cases (species drawn), but the exact match can be out of reach no matter how many trials are drawn. A "tolerance" factor is used to blur the match (for instance, for a tolerance set at 2, the algorithm reaching for a distance of 2 will target 2, then 1, then 3, then 0, then 4). Default : 4 
level_conf_path :  file path on url or local resource, for the level configuration file. Default : "../conf/level_quest.json",
rep_file_path :  file path on url or local resource, for the previously generated combinations (once and for each file update). Default : "../resourcesGenerated/" 
"""


def get_questions_conf(level, profile="basic", correction_nb_url=10, n_max_try=10, tolerance=4,
                       level_conf_path=commons.findConfFromScript("level_conf_path_fromscript","../conf/level_quest.json"),
                       rep_file_path=commons.findConfFromScript("output_generated_path_fromscript","../resourcesGenerated")):
    # Importing configuration form conf file into "data" variable and URL catalog
    data = commons.get_data_from_file(level_conf_path)
    data_url = commons.get_data_url()
    # Test whether the value of "level" input is among the permitted values
    if level not in data:
        level_values = str(data.keys())
        return {"error": "level argument MUST be within values : " + level_values}
    # Only the usefull subdatas are kept in "data" variable
    data = data[level]
    # Test whether the value of "profile" input is among the permitted values
    if profile not in data["profiles"]:
        profiles_values = str(data["profiles"].keys())
        return {"error": "level argument MUST be within values : " + profiles_values}
    # For each level, the species list can differ.
    list_ssp = ([d['fishCode'] for d in data["species"]])
    # Calculation of the ponderation of each species, based on "ponderation" configuration
    tot_nb_pond_ssp = sum(d['ponderation'] for d in data["species"])
    proba_pond_ssp = ([d['ponderation'] / tot_nb_pond_ssp for d in data["species"]])

    # Setting up the variable that will contain the returns
    dict_questions = {"level": level, "profile": profile, "questions": []}

    i = 0
    is_error = False

    # The "scenario" of question is given by the profile : each number refers to a question and gives its level of difficulty
    for dist_target in data["profiles"][profile]:
        i += 1
        n_try = 0
        dict_question = None
        # A question is generated for each level of difficulty, considering n_max-try trials
        while dict_question is None and n_try <= n_max_try:
            n_try += 1
            print(list_ssp)
            ssp_code = random.choice(list_ssp, p=proba_pond_ssp)  # Here is the random part that can lead to underachievement
            dict_question = get_questions(level, ssp_code, rep_file_path, data["min_dist"], data["max_dist"], dist_target,
                                          correction_nb_url, tolerance, data_url)
        # If no attempt has succeeded
        if dict_question is None:
            dict_question = {"valid": False,
                             "cause": "Unable to find matching combination after " + str(n_try) + " attempts."}
            is_error = True
        # If at least one attempt has succeeded, string is set in dict_questions["questions"]
        else:
            dict_question = dict_question[0]
            dict_question["valid"] = True
            dict_question["cause"] = str(n_try) + " attempts"
        dict_question["order"] = i
        dict_questions["questions"].append(dict_question)
    dict_questions["missing_questions"] = is_error

    # Formatting the return value for API requirements
    return str(commons.json.dumps(dict_questions, indent=6, ensure_ascii=False)).replace("\/", "/")


## Calling the generative function of questions
print(get_questions_conf(sys.argv[1], sys.argv[2], int(sys.argv[3])))
#print(get_questions_conf("easy"))
