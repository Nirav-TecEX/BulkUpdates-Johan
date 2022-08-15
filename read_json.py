import json
import os
from io import StringIO

def load_newman_data_from_response():
    file_path = os.path.join(os.getcwd(), "newman",
                "newman-run-report-2022-08-15-11-31-06-481-0.json")
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

    return full_str
    # with open('abc.txt','w+') as f:
    #     f.write(full_str)

def get_newman_response_filename():

    search_dir = os.path.join(os.getcwd(), "newman")
    files = os.listdir(search_dir)
    files = [os.path.join(search_dir, f) for f in files] # add path to each file
    files.sort(key=lambda x: os.path.getmtime(x))
    newest_file = files[0]
    # return newman_response_file

get_newman_response_filename()
print("Here")