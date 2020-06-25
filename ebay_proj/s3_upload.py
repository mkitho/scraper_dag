import boto3
import os
from datetime import datetime as dt


def connect_s3():
	return boto3.resource('s3')


def upload_json_to_s3(s3_conn):

	# get all JSON scraped today
	json_output_path = './scraped_json'
	print('hello')
	today_date = dt.today().strftime('%y%m%d')
	fileslist = [f for f in os.listdir(json_output_path) if today_date in f]
	print(fileslist)

	# upload each one to S3
	for filename in fileslist:
		localfile = os.path.join(json_output_path, filename)
		s3_conn.Bucket('ebay-res').upload_file(localfile, filename)


if __name__=='__main__':
	s3 = connect_s3()
	upload_json_to_s3(s3)
