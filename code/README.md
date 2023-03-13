# Guide to codebase

## [`1_phrase_sampling.py`](code/1_phrase_sampling.py)
* **Description**: Sample tweets containing specific keywords/phrases
* **Inputs**: list of keywords to search (required argument)
* **Outputs**: list of tweets containing the keywords (.csv file)

## [`2_validate_mturk_results.ipynb`](code/2_process_mturk_results.ipynb)
* **Description**: Computes agreement scores of hand-labeled sample using Mechnical Turk; checks for bad workers.
* **Inputs**: list of labeled tweets repeated over multiple workers with filename format 'myth_{myth_name}_sample_{sample_size}_{date}-results.cs>
* **Outputs**: N/A (agreement scores, worker validation)

## [`3_label_mturk_results.py`](code/3_label_mturk_results.py)
* **Description**: Converts MTurk results to the format [tweet_id, text, label]. Base input filepath(s) must be passed as a command-line argument>
* **Inputs**: list of labeled tweets repeated over multiple workers with filename format 'myth_{myth_name}_sample_{sample_size}_{date}-results.cs>
* **Outputs**: list of validated labeled tweets with filename format 'myth_{myth_name}_sample_{sample_size}_{date}-labeled.csv'

## [`4_train_classifiers.ipynb`](code/4_train_classifiers.ipynb)
* **Description**: Trains and evaluates classification models for misinformation detection. Trains k-Nearest Neighbors, Random Forest, Decision T>
* **Inputs**: list of validated labeled tweets with filename format 'myth_{myth_name}_sample_{sample_size}_{date}-labeled.csv'. If negative cases>
* **Outputs**: ML models and vectorizers (with TF-IDF weighting)

## [`5_sample_tweets.ipynb`](code/5_sample_tweets.ipynb)
* **Description**: Uses classifiers trained on labeled tweets (about a myth vs. not) to filter tweets from March to August 2020 (especially April>
* **Inputs**: unlabeled tweets; ML models to use for predictions
* **Outputs**: sample of unlabeled tweets--mostly predicted to be misinformation--for hand-labeling, with filename format '{myth_name}_sample_{sa>

## [`utils.py`](code/utils.py)
* **Description**: Custom function for loading tweets from Google Cloud Storage.
* **Inputs**: Storage bucket name and tweet filepaths
* **Outputs**: Pandas DataFrame containing tweets
