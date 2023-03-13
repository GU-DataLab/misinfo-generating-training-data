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

import numpy as np
import pandas as pd
import csv
import sys
from tqdm import tqdm, trange
import argparse


###############################################
# Define file paths
###############################################

parser = argparse.ArgumentParser(description='Converts MTurk results to the format [tweet_id, text, label]. Filepaths must be passed as arguments.')

parser.add_argument('-in', '--input_fp', dest='input', help='input file path', nargs = '+', required=True)

args = parser.parse_args()

# Collect base file paths into list
converting_list = args.input


###############################################
# Define helper functions
###############################################

def merge_radios(row, colnames, topic, is_optional=False):
    """
    The radio buttons from the MTurk form store their boolean result in a
    single column. This function combines these into their respective questions.
    
    To be used in an `apply` method to combine boolean radio buttons into a
    single column.
    
    Args:
        is_optional: whether a question is optional, if so, no answer simply means `no`
    """
    
    if row['Answer.{}_yes.on'.format(topic)]:
        return 'yes'
    elif row['Answer.{}_no.on'.format(topic)]:
        return 'no'
    elif row['Answer.{}_unsure.on'.format(topic)]:
        return 'unsure'
    elif 'Answer.{}_broken_links.on'.format(topic) in colnames and row['Answer.{}_broken_links.on'.format(topic)]:
        return 'broken_links'
    else:
        if is_optional:
            return 'no'
        else:
            raise ValueError("The chosen choice is not defined.") # If the worker didn't choose any choices
            print(row.AssignmentId)
            # return None
    
def is_equal_values(values):
    """
    Check if all items in values are equal
    Defaults true if only one item in list
    If false, not all values have the same amount
    Example: values['yes','no','yes'] returns false while values['yes','no'] returns true
    """
    if values is None or len(values) == 0:
        return False
    
    v = values[0]
    for i in range(len(values)):
        if values[i] != v:
            return False
        
    return True

def get_majority_vote_and_score(df_same_HIT, col):
    """
    Get majority vote and score from the given column
    Score of 1 means consistent votes
    """
    
    votes = df_same_HIT.groupby(col).size().sort_values(ascending=False)
    # If all votes values are the same (same number of yes, no, unsure) and there is more than one vote choice
    # We set the overall vote as 'unsure' since conclusive answer
    if len(votes.values) > 1 and is_equal_values(votes.values):
        is_col = 'unsure'
    else:
        is_col = votes.index[0]
    # Score is based on highest vote value / rater_num
    score = votes.values[0] / rater_num
    
    
    # In case the vote is `unsure` and the second vote has the same score but not all choices have same scores
    # We use the second vote instead
    if is_col == 'unsure' and votes.size > 1 and \
        votes.values[0] == votes.values[1] and not is_equal_values(votes.values):
        is_col = votes.index[1]
        score = votes.values[1] / rater_num
        
    return is_col, score

def convert_save(base_filename, rater_number):
    '''
    Master function that converts MTurk results to labeled data by using above functions.
    Reads results file using base_fp + '-results.csv'.
    Saves the labeled data as output using base_fp + '-labeled.csv'.
    
    Args:
        base_fp: base path to results file, e.g. '../data/myth_disinfectants_sample-440'. 
        rater_number: Number of workers per task (usually there are 3).
        
    Returns: 
        N/A (saves data to file)
    '''
    
    
    ## Read and clean data ##
    
    source_fp = f'{base_filename}-results.csv'
    target_fp = f'{base_filename}-labeled.csv'
    
    df = pd.read_csv(source_fp)
    
    df['is_myth_supports'] = df.apply(lambda row: merge_radios(
        row=row, colnames=list(df), topic='myth_supports', is_optional=True), axis=1)
    df['is_myth'] = df.apply(lambda row: merge_radios(
        row=row, colnames=list(df), topic='myth'), axis=1)
    
    
    ## Check data validity ##
    
    # These columns must not be None
    answer_cols = [ e for e in list(df) if e.startswith("Answers.") ]
    for col in answer_cols:
        for v in df[col]:
            if v is None:
                raise ValueError('None exists in {}'.format(col))
    
    # Check that each task has rated values = # raters
    for v in df.groupby('HITId').size():
        if v != rater_number:
            raise ValueError("There is a task with raters not equal to {}, found {}.".format(rater_num, v))
    
    
    ## Filter and convert columns ##
    
    # Get the labels from majority votes
    df = df.sort_values(by=['HITId']) # Sort by taskID
    
    # Create new dataframe
    df_new = pd.DataFrame(columns=['tweet_id', 'text', \
                                   'is_myth', 'myth_score', \
                                   'is_myth_supports', 'myth_supports_score'])
    print(f"Converting MTurk results at {source_fp}...")
    
    j = 0
    for i in trange(0, df.shape[0], rater_number):
        is_myth, myth_score = get_majority_vote_and_score(df.iloc[i:i+rater_number], 'is_myth')
        is_myth_supports, myth_supports_score = get_majority_vote_and_score(df.iloc[i:i+rater_number], 'is_myth_supports')
        
        tweet_id = df.iloc[i]['Input.id_str']
        text = df.iloc[i]['Input.full_text_censored']
        df_new.loc[j] = [tweet_id, text, is_myth, myth_score, is_myth_supports, myth_supports_score]
        j += 1

        
    ## Save labeled data to file ##
    
    df_new.to_csv(target_fp,\
        escapechar='\"', \
        quotechar='\"',\
        quoting=csv.QUOTE_ALL,\
        index=False)
    
    print(f"Converted and saved to {target_fp}!")
    print()

    
###############################################
# Run master conversion function
###############################################

# Declare rater number (number of workers per task)
rater_num = 3

for base_fp in converting_list: # iterate over each input data file
    convert_save(base_fp, rater_num)
    
print(f"Done converting {str(len(converting_list))} MTurk results files.")

sys.exit()
