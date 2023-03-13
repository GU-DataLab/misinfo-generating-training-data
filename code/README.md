## Guide to Codebase

### [`1_phrase_sampling.py`](1_phrase_sampling.py)
    * **Description**: Sample tweets containing specific keywords/phrases
    * **Inputs**: list of keywords to search (required argument)
    * **Outputs**: list of tweets containing the keywords (.csv file)

### [`2_validate_mturk_results.ipynb`](2_process_mturk_results.ipynb)
    * **Description**: Computes agreement scores of hand-labeled sample using Mechnical Turk; checks for bad workers.
    * **Inputs**: list of labeled tweets repeated over multiple workers with filename format 'myth_{myth_name}_sample_{sample_size}_{date}-results.csv'.
    * **Outputs**: N/A (agreement scores, worker validation)

### [`3_label_mturk_results.py`](3_label_mturk_results.py)
    * **Description**: Converts MTurk results to the format [tweet_id, text, label]. Base input filepath(s) must be passed as a command-line argument; these will be appended with `-results.csv` to find input data and `-labeled.csv` to save output data.
    * **Inputs**: list of labeled tweets repeated over multiple workers with filename format 'myth_{myth_name}_sample_{sample_size}_{date}-results.csv'
    * **Outputs**: list of validated labeled tweets with filename format 'myth_{myth_name}_sample_{sample_size}_{date}-labeled.csv'

### [`4_train_classifiers.ipynb`](4_train_classifiers.ipynb)
    * **Description**: Trains and evaluates classification models for misinformation detection. Trains k-Nearest Neighbors, Random Forest, Decision Tree, Multinomial Naive Bayes, Logistic Regression, Support Vector Machine, and Multi-Layer Perceptron. Uses 10-fold cross-validation to select the best model.
    * **Inputs**: list of validated labeled tweets with filename format 'myth_{myth_name}_sample_{sample_size}_{date}-labeled.csv'. If negative cases are needed for a focal myth, may also borrow from labeled positives for other myths (very unlikely a tweet contains both myths)
    * **Outputs**: ML models and vectorizers (with TF-IDF weighting)

### [`5_sample_tweets.ipynb`](5_sample_tweets.ipynb)
    * **Description**: Uses classifiers trained on labeled tweets (about a myth vs. not) to filter tweets from March to August 2020 (especially April-May) to only those with a higher probability of being in the minority class than the majority class. To help the classifier learn to detect both classes amidst our imbalanced data, the new sample is predicted to be 90% minority class and 10% minority class. This sample will be used to select tweets for hand-coding that fall into minority classes, which are hard to capture from the first round of ML models. Data source is tweets with hashtags related to Covid-19.
    * **Inputs**: unlabeled tweets; ML models to use for predictions
    * **Outputs**: sample of unlabeled tweets--mostly predicted to be misinformation--for hand-labeling, with filename format '{myth_name}_sample_{sample_size}_{date}.csv'

### [`utils.py`](utils.py)
    * **Description**: Custom function for loading tweets from Google Cloud Storage.
    * **Inputs**: Storage bucket name and tweet filepaths
    * **Outputs**: Pandas DataFrame containing tweets