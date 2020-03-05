import sys

import pickle
import pandas as pd
from sqlalchemy import create_engine

import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support

nltk.download(['punkt','stopwords','wordnet'])
import warnings
warnings.simplefilter('ignore')

def load_data(database_fp):
    """Load Dataframe from db file using pandas
    Argument:
    database_fp: Database file path
    """
    engine = create_engine('sqlite:///'+database_fp)
    df = pd.read_sql_table('Messages', engine)
    x = df.message
    y = df.iloc[:, 4:]
    return x, y, list(y.columns)

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

def build_model():
    """Model Building using Pipeline"""

    # Models
    pipeline = Pipeline([
        ('vect', CountVectorizer(tokenizer=tokenize)),
        ('tfidf', TfidfTransformer()),
        ('clf', MultiOutputClassifier(RandomForestClassifier()))
        ])

    # Model Paramters
    paramters = { 'vect__min_df': [1, 5],
                  'tfidf__use_idf': [True, False],
                  'clf__estimator__n_estimators': [10, 25],
                  'clf__estimator__min_samples_split': [2, 4]
                  }

    cv = GridSearchCV(pipeline, paramters)

    return cv

def model_evaluation(model, X_test, y_test, category_names):
    """Evaluates Model Performance
    Metrics Used: Recall, Precision, f Score

    Arguments:
    model: Trained model
    X_test: Testing Data
    y_test: Testing Traget Values
    category_names: Feature Names

    Output:
    Scores
    """
    y_pred = model.predict(X_test)

    for i, col in enumerate(category_names):
        precision, recall, fscore, support = precision_recall_fscore_support(y_test[col], y_pred[:, i], average='weighted')

        print(f"Report for the Column: {col}")
        print(f"Precision: {precision}")
        print(f"Recall: {recall}")
        print(f"F-Score: {fscore}")

def save_model(model, model_filepath):
    """Save Model to Pickle File"""
    pickle.dump(model, open(model_filepath, 'wb'))

def main():
    if len(sys.argv) == 3:
        database_fp, model_fp = sys.argv[1:]

        # Loading and Splitting into train and test set
        print(f"Loading Data from DATABASE: {database_fp}....")

        X, y, category_names = load_data(database_fp)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        print(f"Building Model...")
        model = build_model()

        print("Training Model...")
        model.fit(X_train, y_train)

        print("Evaluating Model Performance...")
        model_evaluation(model, X_test, y_test, category_names)

        print("Saving Model to a pickle file...")
        save_model(model, model_fp)
        print("Trained Model Saved!")
    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/Disaster_Dataset.db classifier.pkl')

if __name__ == '__main__':
    main()