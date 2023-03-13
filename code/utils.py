#!/usr/bin/env python
# coding: utf-8

'''
@title: Format converter
@description: Converts MTurk results to the format [tweet_id, text, label]. Base input filepath(s) must be passed as a command-line argument; these will be appended with `-results.csv` to find input data and `-labeled.csv` to save output data.
@usage: 
    ```bash
    python3 3_label_mturk_results.py --input_fp DATA_FP1 DATA_FP2
    ```
@inputs: list of labeled tweets repeated over multiple workers with filename format 'myth_{myth_name}_sample_{sample_size}_{date}-results.csv'
@outputs: list of validated labeled tweets with filename format 'myth_{myth_name}_sample_{sample_size}_{date}-labeled.csv'
'''


###############################################
# Import packages
###############################################

import io
import glob
import os
import gzip
import pandas as pd
import tqdm

from google.cloud import storage
client = storage.Client()


###############################################
# Define helper function(s)
###############################################

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

