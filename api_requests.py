import requests
import json

URL = "http://seti.berkeley.edu/opendata"
API_URL = "http://seti.berkeley.edu/opendata/api/"
FORMAT = "filterbank"



class OpendataAPI:

    def test_connection(self):
        response = requests.get(f"{URL}")
        if response.status_code == 200:
            print("Connection working.")
        else:
            raise Exception(f"Connection failed. Api error code {response.status_code}")

    def list_targets(self):
        response = requests.get(f"{API_URL+'list-targets'}")
        if response.status_code == 200:
            print("Successfully fetched the data with parameters provided")
            #self.formatted_print(response.json())
            return self.formatted_return(response.json())
        else:
            raise Exception(f"Fetching target list failed. Api error code {response.status_code}")

    def list_file_types(self):
        response = requests.get(f"{API_URL + 'list-file-types'}")
        if response.status_code == 200:
            print("Successfully fetched the file types")
            # self.formatted_print(response.json())
            return self.formatted_return(response.json())
        else:
            raise Exception(f"Fetching file types failed. Api error code {response.status_code}")

    def query_files(self,parameters):
        response = requests.get(f"{API_URL + 'query-files'}", params=parameters)
        if response.status_code == 200:
            print("Successfully fetched the target data with specified parameters")
            #self.formatted_print(response.json())
            return self.formatted_return(response.json())
        else:
            raise Exception(f"Fetching target data failed. Api error code {response.status_code}")

    def get_cadence(self, url):
        response = requests.get(f"{url}")
        if response.status_code == 200:
            print("Successfully fetched the target data with specified parameters")
            #self.formatted_print(response.json())
            return self.formatted_return(response.json())
        else:
            raise Exception(f"Fetching target data failed. Api error code {response.status_code}")

    def formatted_print(self, obj):
        text = json.dumps(obj, sort_keys=True, indent=4)
        print(text)
    def formatted_return(self,obj):
        text = json.loads(json.dumps(obj, sort_keys=True, indent=4))
        return text

    def __init__(self):
        self.test_connection()

if __name__ == "__main__":

    api_call = OpendataAPI()
    #targets = api_call.list_targets()
    #fileTypes = api_call.list_file_types()
    #print(fileTypes[1])
    #print(str(targets[1]))
    parameters = {
        "target": "",
        "file-types": "filterbank",
        "freq-start": 4000,
        "cadence" : True
    }
    targets = api_call.query_files(parameters)
    api_call.formatted_print(targets)
    cadences = []
    for target in targets["data"]:
        cadences.append(target["url"] + " \n")
    writer = open("urls.txt","w")
    writer.writelines(cadences)

