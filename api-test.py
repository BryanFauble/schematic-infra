import time
import requests
import datetime
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from numbers import Number
import os
from typing import Callable

EXAMPLE_SCHEMA_URL = "https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld"
DATA_FLOW_SCHEMA_URL = "https://raw.githubusercontent.com/Sage-Bionetworks/data_flow/dev/inst/data_flow_component.jsonld"
CONCURRENT_THREADS = 4
RUN_TOTAL_TIMES_PER_ENDPOINT = 3


def fetch(url: str, params: dict):
    return requests.get(url, params=params)


def send_post_request_with_file(url: str, params: dict):
    return requests.post(
        url,
        params=params,
        files={
            "file_name": open(
                "test-manifests/synapse_storage_manifest_patient.csv", "rb"
            )
        },
    )


def get_token():
    token = os.environ.get("TOKEN")
    if token == "":
        return LookupError("Please provide token of asset store")
    else:
        return token


def cal_time_api_call(url: str, params: dict, request_type="get"):
    start_time = time.time()
    with ThreadPoolExecutor() as executor:
        if request_type == "get":
            futures = [
                executor.submit(fetch, url, params) for x in range(CONCURRENT_THREADS)
            ]
        else:
            futures = [
                executor.submit(send_post_request_with_file, url, params)
                for x in range(CONCURRENT_THREADS)
            ]

        for f in concurrent.futures.as_completed(futures):
            try:
                status_code = f.result()
                print("status code", status_code)
            except Exception as exc:
                print(f"generated an exception:{exc}")

    time_diff = time.time() - start_time
    time.sleep(2)
    print(f"duration time of running {url}", time_diff)
    return time_diff


def write_to_txt_file(name_of_endpoint: str, duration: Number):
    with open("duration_cal.txt", "a") as f:
        f.write(f"{name_of_endpoint}: {duration}")
        f.write("\n")
        f.close()


def execute_api_call(url, params, name_of_endpoint):
    time_diff = cal_time_api_call(url, params)

    # write_to_txt_file(name_of_endpoint, time_diff)


def calculate_avg_run_time_per_endpoint(
    function_to_run: Callable, name_of_endpoint: str
):
    sum_time = 0
    for x in range(RUN_TOTAL_TIMES_PER_ENDPOINT):
        run_time = function_to_run()
        sum_time = sum_time + run_time
    avg_time = sum_time / RUN_TOTAL_TIMES_PER_ENDPOINT
    write_to_txt_file(name_of_endpoint, avg_time)


## defining endpoints to test
def find_class_specific_property_req():
    base_url = "https://schematic.dnt-dev.sagebase.org/v1/explorer/find_class_specific_properties"
    params = {"schema_url": EXAMPLE_SCHEMA_URL, "schema_class": "MolecularEntity"}
    time_diff = cal_time_api_call(base_url, params)
    return time_diff


def get_node_dependencies_req():
    base_url = (
        "https://schematic.dnt-dev.sagebase.org/v1/explorer/get_node_dependencies"
    )
    params = {
        "schema_url": EXAMPLE_SCHEMA_URL,
        "source_node": "Patient",
    }
    # execute_api_call(base_url, params, '/explorer/get_node_dependencies')
    time_diff = cal_time_api_call(base_url, params)
    return time_diff


def get_datatype_manifest_req():
    base_url = "https://schematic.dnt-dev.sagebase.org/v1/get/datatype/manifest"
    input_token = get_token()
    params = {
        "input_token": input_token,
        "asset_view": "syn23643253",
        "manifest_id": "syn23643253",
    }
    time_diff = cal_time_api_call(base_url, params)
    return time_diff


def get_manifest_generate_req():
    base_url = "https://schematic.dnt-dev.sagebase.org/v1/manifest/generate"
    params = {
        "schema_url": EXAMPLE_SCHEMA_URL,
        "title": "Example",
        "data_type": ["Patient", "Biospecimen"],
        "use_annotations": False,
    }
    time_diff = cal_time_api_call(base_url, params)
    return time_diff


def download_manifest_req():
    base_url = "https://schematic.dnt-dev.sagebase.org/v1/manifest/download"
    token = get_token()
    params = {
        "input_token": token,
        "asset_view": "syn28559058",
        "dataset_id": "syn28268700",
        "as_json": True,
    }
    time_diff = cal_time_api_call(base_url, params)
    return time_diff


def populate_manifest_req():
    base_url = "https://schematic.dnt-dev.sagebase.org/v1/manifest/populate"
    params = {
        "schema_url": EXAMPLE_SCHEMA_URL,
        "data_type": "Patient",
        "title": "Example",
        "return_excel": True,
    }
    time_diff = cal_time_api_call(base_url, params)
    return time_diff


def model_component_requirements():
    base_url = "https://schematic.dnt-dev.sagebase.org/v1/model/component-requirements"
    params = {
        "schema_url": EXAMPLE_SCHEMA_URL,
        "source_component": "Biospecimen",
        "as_graph": False,
    }
    time_diff = cal_time_api_call(base_url, params)
    return time_diff


def model_submit_req():
    ### Can't concurrently modify the same object
    base_url = "https://schematic.dnt-dev.sagebase.org/v1/model/submit"
    token = get_token()
    params = {
        "schema_url": EXAMPLE_SCHEMA_URL,
        "data_type": "Patient",
        "dataset_id": "syn45794337",
        "manifest_record_type": "table",
        "restrict_rules": False,
        "input_token": token,
        "asset_view": "syn23643253",
    }
    time_diff = cal_time_api_call(base_url, params, request_type="post-file")
    return time_diff


def model_submit_big_manifest():
    base_url = "https://schematic.dnt-dev.sagebase.org/v1/model/submit"
    token = get_token()
    params = {
        "schema_url": DATA_FLOW_SCHEMA_URL,
        "data_type": "DataFlow",
        "dataset_id": "syn38212343",
        "manifest_record_type": "table",
        "restrict_rules": False,
        "input_token": token,
        "asset_view": "syn20446927",
    }
    r = requests.post(
        base_url,
        params=params,
        files={
            "file_name": open(
                "test-manifests/synapse_storage_manifest_dataflow.csv", "rb"
            )
        },
    )
    print(r.status_code)


def model_validate_req():
    base_url = "https://schematic.dnt-dev.sagebase.org/v1/model/validate"
    params = {
        "schema_url": EXAMPLE_SCHEMA_URL,
        "data_type": "Patient",
    }

    time_diff = cal_time_api_call(base_url, params, request_type="post")
    return time_diff


def execute_all_endpoints():
    with open("duration_cal.txt", "w") as f:
        f.write(
            f"when sending {CONCURRENT_THREADS} requests at the same time, we calculate the avg duration time of finishing running the endpoint"
        )
        f.write("\n")
        f.close()

    # calculate_avg_run_time_per_endpoint(find_class_specific_property_req, "explorer/find_class_specific_property")
    # calculate_avg_run_time_per_endpoint(get_node_dependencies_req, "explorer/get_node_dependencies")
    # calculate_avg_run_time_per_endpoint(get_datatype_manifest_req, "get/datatype/manifest")
    # calculate_avg_run_time_per_endpoint(get_manifest_generate_req, "manifest/generate")
    # calculate_avg_run_time_per_endpoint(download_manifest_req, "manifest/download")
    # calculate_avg_run_time_per_endpoint(populate_manifest_req, "manifest/populate")
    # calculate_avg_run_time_per_endpoint(
    #     model_component_requirements, "model/component-requirements"
    # )
    # calculate_avg_run_time_per_endpoint(model_submit_req, "manifest/submit")
    calculate_avg_run_time_per_endpoint(model_validate_req, "model/validate")


execute_all_endpoints()