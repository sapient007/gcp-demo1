from google.cloud import bigquery
client = bigquery.Client()
bucket_name = 'chicago_taxidata_preprocessed_final'
project = 'ml-sandbox-1-191918'
dataset_id = 'chicagotaxi'
table_id = 'processed_taxidata_final'
destination_uri = 'gs://{}/{}'.format(bucket_name, 'file-*.csv')
dataset_ref = client.dataset(dataset_id, project=project)
table_ref = dataset_ref.table(table_id)
job_config = bigquery.job.ExtractJobConfig(print_header=False)
extract_job = client.extract_table(
    table_ref,
    destination_uri,
    # Location must match that of the source table.
    location='US',
    job_config=job_config)  # API request
extract_job.result()  # Waits for job to complete.
print('Exported {}:{}.{} to {}'.format(
    project, dataset_id, table_id, destination_uri))

##run this inside google cloud command line: nano export.py
#copy and paste this code inside of the file then run it : python export.py
#after you will have all the files stored inside the bucket
#once this is finished run: 
# gsutil compose gs://chicago_taxidata_preprocessed_final/file-* gs://chicago_taxidata_preprocessed_final/chicago-taxidata_preprocessed_final.csv
#rename the files accordingly
#in our case the training, testing, and validation data were all split manually
