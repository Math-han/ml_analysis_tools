# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 17:30:25 2020
@author: hany
"""

from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np
from functools import partial
import logging
import re


class EnumString(BaseEstimator, TransformerMixin):
    '''
    select effective columns and transform enum column
    '''

    def __init__(self, max_num_ratio):
        '''
        max_num_ratio: Proportion of numerical data
        '''
        self.max_num_ratio = max_num_ratio

        self.enum_columns = []  # mapping column dict

        self.regex1 = re.compile(r"^[\d\.]\d*%?$|^[\d]\.?\d*%?$")

    def fit(self, df, y=None):

        '''Shape like numerical features which is not numerical transforme into numerical;
           Features' name like channel ,code do not transforme into numerical
        '''

        not_number_cols = df.select_dtypes(exclude=['int', 'float', 'int64', 'float64']).columns.tolist()

        for col in not_number_cols:
            try:
                uniq_val_arr = pd.unique(df[col])
            except TypeError as e:
                continue
            uniq_length = df[col].unique().shape[0]

            # find num in str
            lst_num = []
            for string in uniq_val_arr:
                string = str(string)
                try:
                    string = re.sub('[ ]*', '', string)
                    if self.regex1.findall(string):
                        lst_num.append(self.floatt(string))
                except:
                    print(string)
            if len(lst_num) / uniq_length > self.max_num_ratio:
                self.enum_columns.append(col)

        return self

    def transform(self, df):

        if self.enum_columns is None:
            raise Exception('please fit first!!')

        # create a empty to store df value
        out_df = df.copy()
        regex2 = re.compile(r"(channel)|(code$)")
        for col in self.enum_columns:
            # check whether col in df.columns
            if col not in out_df.columns:
                out_df[col + '_enumstring'] = np.full((out_df.shape[0]), np.nan)
            elif re.findall(regex2, str(col).lower()):
                pass
            else:
                out_df[col + '_enumstring'] = out_df[col].apply(lambda x: self.floatt(x))
        return out_df

    def floatt(self, string):
        try:
            string = re.sub('[ ]*', '', string)
            if self.regex1.findall(string):
                if '%' in string:
                    floatx = float(string.replace('%', '')) / 100
                else:
                    floatx = float(string)
            else:
                floatx = -999
        except Exception as e:
            #            logging.warning('funtion floatt wrong content : {}'.format(e))
            floatx = -9999
        return floatx