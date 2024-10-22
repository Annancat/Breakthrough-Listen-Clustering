import requests
import json
import urllib

URL = "http://seti.berkeley.edu/opendata"
API_URL = "http://seti.berkeley.edu/opendata/api/"


class OpendataAPI:

    def test_connection(self):
        response = requests.get(f"{URL}")
        if response.status_code == 200:
            print("Connection working.")
        else:
            raise Exception(f"Connection failed. Api error code {response.status_code}")

    def list_targets(self):
        response = requests.get(f"{API_URL + 'list-targets'}")
        if response.status_code == 200:
            print("Successfully fetched the data with parameters provided")
            return self.formatted_return(response.json())
        else:
            raise Exception(f"Fetching target list failed. Api error code {response.status_code}")

    def list_file_types(self):
        response = requests.get(f"{API_URL + 'list-file-types'}")
        if response.status_code == 200:
            print("Successfully fetched the file types")
            return self.formatted_return(response.json())
        else:
            raise Exception(f"Fetching file types failed. Api error code {response.status_code}")

    def query_files(self, parameters):
        response = requests.get(f"{API_URL + 'query-files'}", params=parameters)
        if response.status_code == 200:
            print("Successfully fetched the target data with specified parameters")
            return self.formatted_return(response.json())
        else:
            raise Exception(f"Fetching target data failed. Api error code {response.status_code}")

    # API is not reliable when it comes to cadence files. Expect entries to be missed!
    def get_cadence(self, target):
        try:
            with urllib.request.urlopen(API_URL + 'get-cadence/-' + target) as url:
                data = json.loads(url.read().decode())
                return data["data"]
        except urllib.error.HTTPError as error:
            raise Exception(f"Fetching cadence {target} failed. Api error code {error.code}")
        except urllib.error.URLError as error:
            raise Exception(f"Fetching cadence {target} failed. URL error code {error.code}")
        except Exception:
            raise Exception(f"Fetching cadence {target} failed. Unknown error.")

    def formatted_return(self, obj):
        text = json.loads(json.dumps(obj, sort_keys=True, indent=4))
        return text

    def __init__(self):
        self.test_connection()


def get_urls():
    api_call = OpendataAPI()
    targets = api_call.list_targets()
    parameters = {
        "target": "",
        "telescopes": ["gbt", "parkes"],
        "file-types": "filterbank",
        "cadence": True
    }
    with open("urls.txt", "a") as writer:
        for i in range(0, len(targets)):  # does not get data if requesting with ""
            parameters["target"] = targets[i]
            print("Target " + str(i) + " of " + str(len(targets)))
            print("Target name: " + parameters["target"])
            try:
                cur_target = api_call.query_files(parameters)
                writer.writelines(cur_target["data"][0]["cadence_url"] + " \n")
            except Exception:
                continue


def process_urls():
    with open("urls.txt", "r") as reader:
        urls = []
        line = reader.readline()
        while line != "":
            urls.append(line[-9:-2])
            line = reader.readline()
    cleaned_urls = set(urls)
    with open("urls_cleaned.txt", "w") as writer:
        while len(cleaned_urls) > 0:
            writer.writelines(str(cleaned_urls.pop()) + "\n")
