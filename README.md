# Identifying High Quality Training Data for Misinformation Detection

## Introduction

This is repository contains code for the submission to [DATA 2023, the 12th International Conference on Data Science, Technology and Applications](https://data.scitevents.org/) titled "Identifying High Quality Training Data for Misinformation Detection". 


## Guide to Codebase

### [`1_phrase_sampling.py`](code/1_phrase_sampling.py)
* **Description**: Sample tweets containing specific keywords/phrases
* **Inputs**: list of keywords to search (required argument)
* **Outputs**: list of tweets containing the keywords (.csv file)

### [`2_validate_mturk_results.ipynb`](code/2_process_mturk_results.ipynb)
* **Description**: Computes agreement scores of hand-labeled sample using Mechnical Turk; checks for bad workers.
* **Inputs**: list of labeled tweets repeated over multiple workers with filename format 'myth_{myth_name}_sample_{sample_size}_{date}-results.csv'.
* **Outputs**: N/A (agreement scores, worker validation)

### [`3_label_mturk_results.py`](code/3_label_mturk_results.py)
* **Description**: Converts MTurk results to the format [tweet_id, text, label]. Base input filepath(s) must be passed as a command-line argument; these will be appended with `-results.csv` to find input data and `-labeled.csv` to save output data.
* **Inputs**: list of labeled tweets repeated over multiple workers with filename format 'myth_{myth_name}_sample_{sample_size}_{date}-results.csv'
* **Outputs**: list of validated labeled tweets with filename format 'myth_{myth_name}_sample_{sample_size}_{date}-labeled.csv'

### [`4_train_classifiers.ipynb`](code/4_train_classifiers.ipynb)
* **Description**: Trains and evaluates classification models for misinformation detection. Trains k-Nearest Neighbors, Random Forest, Decision Tree, Multinomial Naive Bayes, Logistic Regression, Support Vector Machine, and Multi-Layer Perceptron. Uses 10-fold cross-validation to select the best model.
* **Inputs**: list of validated labeled tweets with filename format 'myth_{myth_name}_sample_{sample_size}_{date}-labeled.csv'. If negative cases are needed for a focal myth, may also borrow from labeled positives for other myths (very unlikely a tweet contains both myths)
* **Outputs**: ML models and vectorizers (with TF-IDF weighting)

### [`5_sample_tweets.ipynb`](code/5_sample_tweets.ipynb)
* **Description**: Uses classifiers trained on labeled tweets (about a myth vs. not) to filter tweets from March to August 2020 (especially April-May) to only those with a higher probability of being in the minority class than the majority class. To help the classifier learn to detect both classes amidst our imbalanced data, the new sample is predicted to be 90% minority class and 10% minority class. This sample will be used to select tweets for hand-coding that fall into minority classes, which are hard to capture from the first round of ML models. Data source is tweets with hashtags related to Covid-19.
* **Inputs**: unlabeled tweets; ML models to use for predictions
* **Outputs**: sample of unlabeled tweets--mostly predicted to be misinformation--for hand-labeling, with filename format '{myth_name}_sample_{sample_size}_{date}.csv'

### [`utils.py`](code/utils.py)
* **Description**: Custom function for loading tweets from Google Cloud Storage.
* **Inputs**: Storage bucket name and tweet filepaths
* **Outputs**: Pandas DataFrame containing tweets
    
## Our ML models for misinformation detection 
The [`models/`](models/) folder contains our refined models and vectorizers (with TF-IDF weighting) for identifying each myth related to COVID-19:
* 5G  
* antibiotics  
* disinfectants  
* home_remedies  
* hydroxychloroquine  
* mosquitoes  
* UV light
* weather

We used the following model types: 
* K-Nearest Neighbors
* Decision Tree
* Random Forest
* Multinomial Naive Bayes
* Logistic Regression
* Multi-Layer Perceptron


## Abstract

Misinformation spread through social media poses a grave threat to public health, interfering with sound medical advice most visibly during crises like the COVID-19 pandemic. To track and curb misinformation, an essential first step is to identify and track the spread of lies related to public health. One component of misinformation detection is finding examples of misinformation posts that can serve as training data for misinformation detection algorithms. In this paper, we focus on the challenge of collecting high quality training data in misinformation detection applications. To that end, we propose a simple but effective methodology and show its viability on five myths related to COVID-19. Our methodology uses both keywords and weak learner predictions for sampling, resulting in a high rate of identification for myths in example posts. To aid researchers in adjusting this methodology for other use cases, we use word usage entropy to describe when fewer iterations of sampling and training will be needed to obtain high quality samples. Finally, we present a case study that shows the prevalence of three of our myths on Twitter at the beginning of the pandemic.


