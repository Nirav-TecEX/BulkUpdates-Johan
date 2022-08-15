"""
This function allows the user to send an api to HappySoup.
HappySoup then does a bulk call on SalesForce objects.
This data can be used to checkout the objects in out org. 
"""

import subprocess
import json
import os
from datetime import datetime
from time import sleep
import re 
from pandas import read_csv

##-------------------------------------------------------------------
def output_to_excel(destination_path: str):
    data = read_csv(destination_path, "\t")
    # data.to_excel("output_file.xlsx")
    return data
##-------------------------------------------------------------------

##-------------------------------------------------------------------
def parse_data(newman_output_path: str, destination_path:str):
    with open(newman_output_path, 'r', encoding='utf-8') as f:
        data_out = f.read()
    
    list_of_lines = data_out.split("get_dependencies")[1].split("┌")[1] \
                    .replace("│", "").replace("'", "").replace('"', "") \
                    .replace("\\r\\n", "").replace("\\t", "\t")         \
                    .replace("└", "").split("+\n")
    
    with open(destination_path, "a", encoding="utf-8") as f:
        for i in range(0, len(list_of_lines)):
            line = list_of_lines[i]
            line = re.sub(r"\n ? ? ? ? ? ?", "", line).strip(" ")+"\n"
            line = line.replace("\\t", "\t")
            line = line.replace("\\r", "")
            line = line.replace("\\n", "")
            f.write(line)
##-------------------------------------------------------------------

##-------------------------------------------------------------------
def run_newman(collection_path: str, newman_output_path: str):
    new_cmd = ["newman", "run", collection_path]
    subproc = subprocess.Popen(new_cmd, shell=True, stdout=subprocess.PIPE)
    try:
        out, errs = subproc.communicate()
    except Exception as e:
        print(e)
    
    with open(newman_output_path, 'a', encoding='utf-8') as f:
        outs = out.decode('utf-8')
        f.write(outs)
        sleep(1)
##-------------------------------------------------------------------

##-------------------------------------------------------------------
def get_collection_json(ids: str, cookie: str):
    cwd = os.getcwd()
    json_path = os.path.join(cwd, "HappySoupCollection.json")
    with open(json_path, 'r') as f:
        collection_data = json.load(f)
        for collection_request in collection_data['item']:
            try:
                if "ids" in collection_request['request']['body']['raw']:
                    collection_request['request']['body']['raw'] = \
                    f'{{\"ids\":[{ids}]}}'
            except KeyError as e:
                print("No body.")

            try:
                if collection_request['request']["header"][0]["key"].lower() \
                    == "cookie":
                    collection_request['request']["header"][0]["value"] \
                        = cookie
            except KeyError as e:
                print("No headers. ")
    
    json_path = os.path.join(cwd, "Collection.json")
    with open(json_path, 'w+') as f:
        f.write(json.dumps(collection_data, indent=4))

    return json_path
##-------------------------------------------------------------------

##-------------------------------------------------------------------
def main(ids: str, cookie: str) -> bytes:
    """ Run this function to generate an excel with the data.
        Takes a string of ids and a cookie (for now) and returns the
        data it wrote to an excel (can ignore). The excel is located 
        in the current working directory and is called 
        "output_file.xlsx".

        Call the function like:
        
            <snip>
            
            _ = main(ids, cookie)
            
            <snip>

        param ids     :: note the string format below 
            '"id_1", "id_2", "...", ...' 
        param cookie  :: cookie string
    """
    
    cwd = os.getcwd()
    newman_output_path = os.path.join(cwd, "output.txt")
    destination_path = os.path.join(cwd, "destination.txt") 

    with open(newman_output_path, 'w+') as f:
        f.write(f"{datetime.now()}\n")
    with open(destination_path, 'w+') as f:
        f.write("")

    collection_path = get_collection_json(ids, cookie)
    run_newman(collection_path, newman_output_path)

    # output_path = os.path.join(os.getcwd(), "output.txt")
    parse_data(newman_output_path, destination_path)
    data = output_to_excel(destination_path)
    return data
##-------------------------------------------------------------------

if __name__=="__main__":
    main('"00N0Q0000027ibuUAA","00N0Q0000027jnzUAA","00N0Q0000027stpUAA","00N1v000100Sl5VlEAJ"', "connect.sid=s:NY36hpqf4ZXpbJ0JGXaJxAvkAU5Z67MR.YB7Q8AtCWlIU6jm68wIxiYHBLg3WQeZttsq39czT0D4")
