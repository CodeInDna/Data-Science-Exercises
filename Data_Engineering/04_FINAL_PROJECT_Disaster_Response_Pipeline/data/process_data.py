import sys
import pandas as pd
from sqlalchemy import create_engine

def load_data(messages_fp, categories_fp):
	"""load_data: loads the messages and categories dataframe.

	Arguments:
	messages_fp: Messages Dataset File Path
	categories_fp : Categories Dataset File Path

	Return:
	Merged (Messages + Categories) DataFrame
	"""

	messages = pd.read_csv(messages_fp)
	categories = pd.read_csv(categories_fp)

	df = pd.merge(messages, categories, on='id')

	return df

def clean_data(df):
	"""clean_data: It cleans the dataframe categories, by performing ETL step, 
	creating 36 columns of different categories, converting and 
	then concatenating followed by removing duplicates

	Arguments:
	df : Merged DataFrame
	"""
	
	# Creating a DataFrame of the 36 Individual Category Columns
	categories = df.categories.str.split(';', expand=True)

	# Extracting Column Names 
	row = categories.iloc[0,:]
	categories_colnames = row.apply(lambda x: x[:-2])
	categories.columns = categories_colnames

	# Extracting Values and converting it to integer
	for column in categories:
		categories[column] = categories[column].apply(lambda x: x[-1]).astype(int)

	# Replace categories column in df
	df = df.drop('categories', axis=1)

	# Concatenate the dataframe(df) with the new `categories` dataframe
	df = pd.concat([df, categories], axis=1)

	# Drop Duplicates
	df.drop_duplicates(inplace=True)

	return df

def save_data(df, db_filename):
	"""save_data: Saves Cleaned Data in DB

	Arguments:
	df:  Cleaned DataFrame, 
	db_filename: filename you want to save data in
	"""
	engine = create_engine('sqlite:///'+db_filename)
	df.to_sql(db_filename, engine, index=False)

def main():
	"""main: Perform ETL"""
	if len(sys.argv)==4:
		messages_fp, categories_fp, db_fp = sys.argv[1:]

		print(f"LOADING DATA...\n MESSAGES: {messages_fp}\n CATEGORIES: {categories_fp}")
		df = load_data(messages_fp, categories_fp)

		print('CLEANING DATA...')
		df = clean_data(df)

		print(f"SAVING DATA TO DATABASE: {db_fp}")
		save_data(df, db_fp)

		print('Data Cleaning DONE!!!')
	else:
		print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')

if __name__ == '__main__':
	main()