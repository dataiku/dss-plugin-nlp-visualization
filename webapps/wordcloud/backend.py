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

logger = logging.getLogger(__name__)

#input_dataset = dataiku.Dataset("tweet_data_prepared")
#input_dataset = get_webapp_config()['dataset']


#text_col = get_webapp_config()['text_col']

#export_folder = dataiku.Folder("AA1eOTbv")
#folder_path = export_folder.get_path()

#try:

#except Exception as e:
#    logger.error(traceback.format_exc())
    #return str(e), 500

# Generate a custom color palette
def color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    color_list = ['hsl(205,71%,41%)', 'hsl(214,56%,80%)', 'hsl(28,100%,53%)', 'hsl(30,100%,74%)',
                  'hsl(120,57%,40%)', 'hsl(110,57%,71%)']
    return random.choice(color_list)

#Load text
#text = str(df[text_col])

# Generate a word cloud image
#wordcloud = WordCloud(background_color='white', width=800, height=400, margin=4, max_words=100)\
#.generate(text).recolor(color_func=color_func, random_state=3)

#chart_svg = wordcloud.to_svg(embed_font=True)
#value = Markup('<strong>{}</strong>'.format(chart_svg))

#render_template('body.html', svg=value)

@app.route('/get_svg')
def get_svg():

    config = get_webapp_config().get("webAppConfig")
    logging.info('Webapp config loaded: {}'.format(config))

    dataset_name = config.get('dataset')
    df = dataiku.Dataset(dataset_name).get_dataframe()

    text_col = config.get('text_col')
    language = config.get('language')

    text = str(df[text_col])

    # Generate a word cloud image
    print('Starting to generate wordcloud')
    logging.info('Starting to generate wordcloud')
    wordcloud = WordCloud(background_color='white', scale = 8 , margin=4, max_words=100)\
    .generate(text).recolor(color_func=color_func, random_state=3)

    chart_svg = wordcloud.to_svg(embed_font=True)
    print('Wordcloud generated')
    logging.info('Wordcloud generated')
    return json.dumps({'chart': 'wordcloud', 'svg':chart_svg})

