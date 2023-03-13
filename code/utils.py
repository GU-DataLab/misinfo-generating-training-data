import io
import glob
import os
import gzip
import pandas as pd
import tqdm

from google.cloud import storage

def read_file(file_path):
    """
    Read a JSON spark file from given file path and return a dataframe
    """

    file_path = file_path[:-1] if file_path[-1] == '/' else file_path

    # Check if the given file_path is a directory or file
    if os.path.isdir(file_path):

        # list all JSON files in directory
        files = glob.glob(file_path+"/*.json")

        # read each JSON file into a dataframe, and append to the dataframe list
        dfs = []
        print("Reading JSON file")
        for ix, f in enumerate(tqdm.tqdm(files)):
            # print("Reading JSON file: {:04d}/{:04d}".format(ix+1, len(files)))
            df = pd.read_json(f, lines=True)
            dfs.append(df)

        # combine dataframes
        df = pd.concat(dfs)

    elif os.path.isfile(file_path):
        if is_spark_json(file_path):
            df = pd.read_json(file_path, lines=True)
        else:
            df = pd.read_json(file_path, orient='records')
    else:
        raise ValueError(
            "It is a special file (socket, FIFO, device file) or file not found")

    return df

def is_spark_json(fp):
    """
    Check if the given file path is spark json
    """
    with open(fp, 'r') as f:
        # line = f.readline().strip() # Very slow
        for line in f:
            if line[0] == '{' and line[-1] == '}':
                return True
            break
    return False


client = storage.Client()
def gcs_read_json_gz(gcs_filepath, nrows=None):
    # Validate input path
    if not gcs_filepath.startswith("gs://") or not gcs_filepath.endswith(".json.gz"):
        raise ValueError(F"Invalid path: {gcs_filepath}")

    # Get the bucket
    bucket_name = gcs_filepath.split("/")[2]
    bucket = client.get_bucket(bucket_name)
    # bucket = client.get_bucket("project_coronavirus")

    # Get the blob object
    blob_name = "/".join(gcs_filepath.split("/")[3:])
    # blob_name = "raw/hashtag/2020-week14/#2019nCoV_20200330.json.gz"
    blob = bucket.get_blob(blob_name)

    # Convert blob into string and consider as BytesIO object. Still compressed by gzip
    data = io.BytesIO(blob.download_as_string())

    # Open gzip into csv
    with gzip.open(data) as gz:
        # Read compressed file as a file object
        file = gz.read()
        # Decode the byte type into string by utf-8
        blob_decompress = file.decode('utf-8')
        # StringIO object
        s = io.StringIO(blob_decompress)

    df = pd.read_json(s, precise_float="high", nrows=nrows, lines=True)

    return df

