import dataiku
import logging
import traceback
from flask import request
import json
import pandas as pd
import spacy.lang
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import random
from dataiku.customwebapp import get_webapp_config

# Initiate logger
logger = logging.getLogger(__name__)

def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    # Return the color function used in the wordcloud
    color_list = ['hsl(205,71%,41%)', 'hsl(214,56%,80%)', 'hsl(28,100%,53%)', 'hsl(30,100%,74%)',
                  'hsl(120,57%,40%)', 'hsl(110,57%,71%)']
    return random.choice(color_list)

def get_wordcloud_svg(text, colour_func):
    # Return the wordcloud as an svg file
    wordcloud = WordCloud(background_color='white', scale=2, margin=4, max_words=100)\
        .generate(text).recolor(color_func=color_func, random_state=3)
    svg = wordcloud.to_svg(embed_font=True)
    return svg
    
# Load dataset
config = get_webapp_config().get("webAppConfig")
dataset_name = config.get('dataset')
df = dataiku.Dataset(dataset_name).get_dataframe()


@app.route('/get_svg/<path:params>')
def get_svg(params):

    params_dict = json.loads(params)
    logging.info('Webapp parameters loaded: {}'.format(params_dict))

    dataset_name = params_dict.get('dataset_name')
    #df = dataiku.Dataset(dataset_name).get_dataframe()

    text_col = params_dict.get('text_column', None)
    language = params_dict.get('language', None)
    subchart_column = params_dict.get('subchart_column', None)

    if subchart_column == None:

        text = df[text_col].str.cat(sep=' ')
        svg = get_wordcloud_svg(text, color_func)
        logging.info('Wordcloud generated')
        response = [{'subchart': None, 'svg':svg}]
        return json.dumps(response)

    else:

        df_grouped = df.groupby(subchart_column)
        subcharts = df[subchart_column].unique().tolist()
        texts = [df_grouped.get_group(subchart)[text_col].str.cat(sep=' ') for subchart in subcharts]
        svgs = [get_wordcloud_svg(text, color_func) for text in texts]
        logging.info('Wordclouds generated')
        response = [{'subchart':subchart, 'svg':svg} for subchart, svg in zip(subcharts, svgs)]
        return json.dumps(response)


    #text = str(df[text_col])

    #logging.info('4')

    # Generate a word cloud image
    #print('Starting to generate wordcloud')
    #logging.info('Starting to generate wordcloud')
    #wordcloud = WordCloud(background_color='white', scale = 2 , margin=4, max_words=100)\
    #.generate(text).recolor(color_func=color_func, random_state=3)

    #chart_svg = wordcloud.to_svg(embed_font=True)
    #print('Wordcloud generated')
    #logging.info('Wordcloud generated')
    #return json.dumps({'chart': 'wordcloud', 'svg':chart_svg})

