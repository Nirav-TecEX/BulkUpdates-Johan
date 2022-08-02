import subprocess
import json
import os

##-------------------------------------------------------------------
def get_collection_json(ids: list):
    cwd = os.getcwd()
    json_path = os.path.join(cwd, "HappySoupCollection.json")
    with open(json_path, 'r') as f:
        collection_data = json.load(f)
        for collection_request in collection_data['item']:
            if collection_request['name'] == 'request_dependencies':
                collection_request['request']['body']['raw'] = \
                "OVERWRITE <- ids:[{{fieldId}}]"
    
    json_path = os.path.join(cwd, "Collection.json")
    with open(json_path, 'w+') as f:
        f.write(json.dumps(collection_data, indent=4))

    return json_path
##-------------------------------------------------------------------

##-------------------------------------------------------------------
def main():
    collection_path = get_collection_json(['a'])
    new_cmd = ["newman", "run", collection_path]
    subproc = subprocess.Popen(new_cmd, shell=True)
    try:
        out, errs = subproc.communicate()
    except Exception as e:
        print(e)
##-------------------------------------------------------------------

if __name__=="__main__":
    main()
