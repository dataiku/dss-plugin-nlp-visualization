import dataiku
import logging
logger = logging.getLogger(__name__)
import traceback
from flask import request
import json
import pandas as pd
import spacy.lang
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import random
from dataiku.customwebapp import get_webapp_config


def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    # Return the color function used in the wordcloud
    color_list = ['hsl(205,71%,41%)', 'hsl(214,56%,80%)', 'hsl(28,100%,53%)', 'hsl(30,100%,74%)',
                  'hsl(120,57%,40%)', 'hsl(110,57%,71%)']

    return random.choice(color_list)


def get_wordcloud_svg(text, colour_func):
    # Return the wordcloud as an svg file
    wordcloud = WordCloud(background_color='white', scale=2, margin=4, max_words=100, collocations=False)\
        .generate(text).recolor(color_func=color_func, random_state=3)

    svg = wordcloud.to_svg(embed_font=True)
    return svg
    

@app.route('/get_svg/<path:params>')
def get_svg(params):
    try:
        # Load parameters
        params_dict = json.loads(params)
        logging.info('Webapp parameters loaded: {}'.format(params_dict))

        dataset_name = params_dict.get('dataset_name', None)
        text_column = params_dict.get('text_column', None)
        language = params_dict.get('language', None)
        subchart_column = params_dict.get('subchart_column', None)

        # Load input dataframe
        necessary_columns = [column for column in [text_column, subchart_column] if column != None]
        df = dataiku.Dataset(dataset_name).get_dataframe(columns=necessary_columns)
        if df.empty:
            raise Exception("Dataframe is empty")
        else:
            logging.info('Read dataset of shape: {}'.format(df.shape))

        if subchart_column == None:
            text = df[text_column].str.cat(sep=' ')

            # Generate wordcloud
            svg = get_wordcloud_svg(text, color_func)
            logging.info('Wordcloud generated')

            response = [{'subchart': None, 'svg':svg}]
            return json.dumps(response)
        else:
            # Group data
            df.dropna(subset=[subchart_column], inplace=True)
            df_grouped = df.groupby(subchart_column)

            texts = []
            subcharts = []
            for name, group in df_grouped:
                texts.append(group[text_column].str.cat(sep=' '))
                subcharts.append(name)

            # Generate wordclouds
            svgs = [get_wordcloud_svg(text, color_func) for text in texts]
            logging.info('Wordclouds generated')

            response = [{'subchart':subchart, 'svg':svg} for subchart, svg in zip(subcharts, svgs)]
            return json.dumps(response)
    
    except:
        logger.error(traceback.format_exc())
        return traceback.format_exc(), 500


