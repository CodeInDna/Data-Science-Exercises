from flask import Flask, render_template, request

import pandas as pd
from sqlalchemy import create_engine
import joblib
import os.path

import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

import json
import plotly
from plotly.graph_objs import Bar

import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# load data
engine = create_engine('sqlite:///../data/Disaster_Dataset.db')
df = pd.read_sql_table('Messages', engine)

def tokenize(text):
    """Normalize, Tokenize and Stemmize(Lemmatize) text"""

    # Normalizing Text (Remove Punctuations & lower case)
    text = re.sub(r'[^a-zA-Z0-9]', ' ', text.lower())
    
    # Tokenizing Text
    tokens = word_tokenize(text)

    # Removing Stop Words
    words = [word for word in tokens if word not in stopwords.words("english")]

    # Lemmatizing Words 
    clean_tokens = []
    lemmatizer = WordNetLemmatizer()

    for word in words:
        clean_tokens.append(lemmatizer.lemmatize(word).strip())

    return clean_tokens

# load model
model = joblib.load('../model/classifier.pkl')

# Routes
@app.route('/')
def index():

	# for data visuals 
	# genres and its count
	genre_counts = df.genre.value_counts()
	genre_names = list(genre_counts.index)

	# Top five categories
	top_cat_count = df.iloc[:, 4:].sum().sort_values(ascending=False)[1:6]
	top_cat_names = list(top_cat_count.index)

	# create visuals
	graphs = [{
		'data': [
			Bar(
				x=genre_names,
				y=genre_counts,
				marker=dict(color='rgb(80,54,153)')
			)
		],

		'layout': {
			'title': 'Distribution of Message Genres',
			'xaxis': {
				'title': "Genre"
			},
			'y_axis': {
				'title': "Count"
			}
		}
	},
	{
		'data': [
				Bar(
					x=top_cat_names,
					y=top_cat_count,
					marker=dict(color='rgb(200,71,124)')
				)
			],

			'layout': {
				'title': 'Distribution of Top Five Categories',
				'xaxis': {
					'title': "Categories"
				},
				'y_axis': {
					'title': "Count"
				}
			}
	}
	]

	# encode in json
	ids = [f"graph-{i}" for i, _ in enumerate(graphs)]
	graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

	return render_template('index.html', ids=ids, graphJSON=graphJSON)

@app.route('/go')
def go():
	# user input
	query = request.args.get('query')

	# use model to predict result
	predicted_labels = model.predict([query])[0]

	results = dict(zip(df.columns[4:], predicted_labels))

	return render_template('go.html', query=query, results=results)

def main():
    app.run(host='127.0.0.1', port=5000, debug=True)

if __name__ == '__main__':
    main()

