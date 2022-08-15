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
from io import StringIO

##-------------------------------------------------------------------
def output_to_excel(destination_path: str):
    data = read_csv(destination_path, "\t")
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
    new_cmd = ["newman", "run", collection_path, "-r", "json"]
    # new_cmd = ["newman", "run", collection_path]
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
def load_newman_data_from_response(newman_response_file_path):
    file_path = os.path.join(os.getcwd(), "newman",
                newman_response_file_path)
    with open(file_path,'r') as f:
        file_data = f.read()
        file_data = json.loads(file_data)
    output = file_data["run"]["executions"][1]["response"]["stream"]["data"]

    temp = ''
    for i in output:
        temp = temp + chr(i)

    temp = json.loads(temp)

    headings = temp['response']['datatable']['columns']
    headings_list = []
    fields_list = []
    full_str = ''

    for heading in headings:
        if headings_list == []:
            full_str = full_str + heading['header']
            headings_list.append(heading['header'])
            fields_list.append(heading['field'])
        else:
            if heading['header'] in headings_list:
                for i in range(0, 100):
                    h2 = heading['header'] + f'.{i}'
                    if not (h2 in full_str):
                        full_str = full_str + '\t' + heading['header']
                        headings_list.append('\t' + h2)
                        fields_list.append(heading['field'])
                        break
            full_str = full_str + '\t' + heading['header']
            headings_list.append('\t' + heading['header'])
            fields_list.append(heading['field'])
    full_str = full_str + '\n'
    full_str.replace('\t\n', '\n')
    headings_list.append('\n')

    all_data = temp['response']['datatable']['data']
    for data in all_data:
        line = ""
        for field in fields_list:
            # print(f"{field} :: {data[field]}\t")
            if line == "":
                line = line + f"{data[field]}"
            else:
                line = line + f"\t{data[field]}"
        line = line + '\n'
        full_str = full_str + line
    

    csvStringIO = StringIO(full_str)

    data = read_csv(csvStringIO, "\t")
    return data
##-------------------------------------------------------------------

##-------------------------------------------------------------------
def get_newman_response_filename():
    search_dir = os.path.join(os.getcwd(), "newman")
    files = os.listdir(search_dir)
    files = [os.path.join(search_dir, f) for f in files] # add path to each file
    files.sort(key=lambda x: os.path.getmtime(x))
    newman_response_file_path = files[0]
    return newman_response_file_path
##-------------------------------------------------------------------

##-------------------------------------------------------------------
def main(ids: str, cookie: str) -> bytes:
    """ Run this function to generate an excel with the data.
        Takes a string of ids and a cookie (for now) and returns a
        pandas dataframe with the data.

        Call the function like:
        
            <snip>
            
            data_out = main(ids, cookie)
            
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

    newman_response_file_path = get_newman_response_filename()
    data = load_newman_data_from_response(newman_response_file_path)
    return data
##-------------------------------------------------------------------

if __name__=="__main__":
    # main('"00N0Q0000027ibuUAA","00N0Q0000027jnzUAA","00N0Q0000027stpUAA","00N1v000100Sl5VlEAJ"', "connect.sid=s:NY36hpqf4ZXpbJ0JGXaJxAvkAU5Z67MR.YB7Q8AtCWlIU6jm68wIxiYHBLg3WQeZttsq39czT0D4")
    _ = main(
        '"00N0Q0000027ibuUAA","00N0Q0000027jnzUAA","00N0Q0000027stpUAA", \
        "00N0Q0000027stqUAA","00N0Q0000027strUAA","00N0Q0000027stsUAA",  \
        "00N0Q0000027sttUAA","00N0Q0000027stuUAA","00N0Q0000027stvUAA",  \
        "00N0Q0000027stwUAA","00N0Q0000027stxUAA","00N0Q0000027styUAA",  \
        "00N0Q0000027stzUAA","00N0Q0000027su0UAA","00N0Q0000027t02UAA",  \
        "00N0Q0000027t03UAA","00N0Q0000027t04UAA","00N0Q0000027t05UAA",  \
        "00N0Q0000027t06UAA","00N0Q0000027t07UAA","00N0Q0000027t08UAA",  \
        "00N0Q0000027t09UAA","00N0Q0000027t0AUAQ","00N0Q0000027t0BUAQ",  \
        "00N0Q0000027t0CUAQ","00N0Q0000027t0DUAQ","00N0Q0000027t0EUAQ",  \
        "00N0Q0000027t0FUAQ","00N0Q0000027t0GUAQ","00N0Q0000027t0HUAQ",  \
        "00N0Q0000027t0bUAA","00N0Q0000027t1AUAQ","00N0Q0000027tbsUAA",  \
        "00N0Q000002KUM5UAO","00N0Q000002KUNNUA4","00N0Q000002KUNSUA4",  \
        "00N0Q000002KUNXUA4","00N0Q000002KUPdUAO","00N0Q000002KUXTUA4",  \
        "00N0Q000002KUXUUA4"',
        "connect.sid=s:oUCHKZQ8Twjp-MMGgdsrDaR-HqVDO1MV.8WFlM1v4gNPqqhcKtIVDoKU5R9gFhMSJDp+ZSI8h1+U"
    )

    _.to_excel("output_file.xlsx")
    print("Complete!")
