""" Sample tweets containing specific phrases

Usage
-----

```bash
python -m jobs.sampling.sample_phrases \
    --input "data/election2020/#2020election_20190616.json" \
    --output output/ \
    --phrases \
    "love" \
    --limit 5 \
    --lang "en" \
    --preprocessing_choices 'stopwords' 'lowercase' 'stemmed'
```

```bash
spark-submit \
   --py-files dist/shared.zip \
    jobs/sampling/sample_phrases.py \
    --input "data/election2020/#2020election_20190616.json" \
    --output output/ \
    --phrases \
    "already" \
    "cut the field" \
    --limit 5 \
    --lang "en" \
    --phrase_conditional 'AND'
```

```bash
gcloud dataproc jobs submit pyspark \
    --cluster "colton" \
    --region "us-east4" \
    --py-files "gs://build-artifacts/pyspark-shared.zip" \
    gs://build-artifacts/pyspark-jobs/sampling/sample_phrases.py \
    -- \
    --input \
    "gs://project_gun-violence/raw/hashtag/2017" \
    --output output/ \
    --phrases \
    "efforts" \
    "speak" \
    "election" \
    --limit 2000 \
    --lang "en"
```

"""

import pyspark.sql.functions as f

from shared.base_job import BaseJob
from shared.job_helpers import construct_output_filename


class SamplePhrasesJob(BaseJob):

    def __init__(self):

        # invoke `BaseJob` constructor
        super().__init__(name="Sample Tweets by Phrase")

        # support additional parameters
        self.parser.add_argument(
            "--phrases",
            required=True,
            nargs="+",
            help="one or more words or phrases to search in `full_text`"
        )
        self.parser.add_argument(
            "--limit",
            type=int,
            help="number of tweets to return"
        )
        self.parser.add_argument(
            "--phrase_conditional",
            choices=['AND', 'OR'],
            default='OR',
            help="conditional expressions for phrases"
        )
        # support for additional attributes
        self.parser.add_argument(
            "--additional_col_attributes", nargs="+",
            help="Additional attributes to include in the output "
        )

        # Default pre-processing options
        self.parser.set_defaults(preprocessing_choices=['lowercase', 'contractions', 'punctuation'])

    def process(self):

        # construct output filename from parameters
        filename_components = [self.args.start_date, self.args.end_date,
                               self.args.dataset, "Sample", self.args.limit,
                               self.args.target_attr]
        output = construct_output_filename(None, self.args.output, filename_components)
        self.args.output = output + ".csv"
        print("output file: ", self.args.output)

        # OR conditional: one of the phrases must be present in the text
        if self.args.phrase_conditional == 'OR':
            PHRASE_REGEX = r'(^|\s)(' + '|'.join(self.args.phrases).lower() + r')(\s|$)'

        # AND conditional - all of the phrases must be present in the text
        #  - https://regex101.com/r/i2jy0J/4
        #  - https://www.ocpsoft.org/tutorials/regular-expressions/and-in-regex/
        elif self.args.phrase_conditional == 'AND':
            PHRASE_REGEX = "".join([r"(?=.*\b" + w.lower() + r"\b)" for w in self.args.phrases])

        # Finding entries matching regular expression
        self.df = self.df.where(f.lower(f.col(self.args.target_attr)).rlike(PHRASE_REGEX))

        # Limit number of tweets returned if optional argument is provided
        if self.args.limit:
            self.df = self.df \
                .orderBy(f.rand()) \
                .limit(self.args.limit) \

        # if we need to add any additional attributes to the output
        if self.args.additional_col_attributes:
            # select appropriate default columns
            cols = [
                "id_str",
                "date",
                self.args.target_attr,
            ]

            for attr in self.args.additional_col_attributes:
                if attr in self.df.columns:
                    cols += [attr]

            self.df = self.df.select(cols)

        # write out default cols
        else:
            self.df = self.df.select("id_str", "date", self.args.target_attr)


if __name__ == "__main__":

    sp = SamplePhrasesJob()
    sp.run()
