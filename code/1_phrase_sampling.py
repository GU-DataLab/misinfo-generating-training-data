#!/usr/bin/env python
# coding: utf-8

""" Sample tweets containing specific phrases

@inputs: list of keywords to search (required argument)
@outputs: list of tweets containing the keywords (.csv file)

@usage:
-----

```bash
python -m jobs.sampling.sample_phrases \
    --input "data/PROJECT/FILEPATH.json" \
    --output output/ \
    --phrases \
    "love" \
    --limit 5 \
    --lang "en" \
    --preprocessing_choices 'stopwords' 'lowercase' 'stemmed'
```

"""

###############################################
# Import packages
###############################################

import pyspark.sql.functions as f

from shared.base_job import BaseJob
from shared.job_helpers import construct_output_filename


###############################################
# Define functions
###############################################

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


###############################################
# Execute functions
###############################################

if __name__ == "__main__":

    sp = SamplePhrasesJob()
    sp.run()
