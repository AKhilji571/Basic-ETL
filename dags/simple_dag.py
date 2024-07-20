from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
import zipfile

zip_file = '/Users/pro/downloads/Data.zip'  # Replace with your zip file path
extract_to = '/Users/pro/documents'  # Replace with your desired extraction directory

def read_fix_file(file_path):
    # Implement your fixed-width file reading logic here
    pass

def read_tsv_file(file_path):
    try:
        data = pd.read_csv(file_path, sep='\t')
        print(f"Data successfully read from {file_path}")
        return data
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def transform(**kwargs):
    ti = kwargs['ti']
    csv_data = ti.xcom_pull(key='data', task_ids='task2')
    if csv_data is not None:
        data = pd.DataFrame.from_dict(csv_data)
        # Example transformation (cleaning data)
        cleaned_data = data.dropna()  # Placeholder for actual transformation
        ti.xcom_push(key='cleaned_data', value=cleaned_data.to_dict())

def consolidate(**kwargs):
    ti = kwargs['ti']
    csv_data = ti.xcom_pull(key='data', task_ids='task2')
    if csv_data is not None:
        csv_df = pd.DataFrame.from_dict(csv_data)
        # Example consolidation logic
        consolidated_data = csv_df.groupby('some_column').sum()  # Placeholder for actual logic
        ti.xcom_push(key='consolidated_data', value=consolidated_data.to_dict())

def dataextract(**kwargs):
    path = extract_to + "/diabetes.csv"  # Adjust as per your extraction logic
    try:
        data = pd.read_csv(path)
        print(f"Data successfully read from {path}")
        kwargs['ti'].xcom_push(key='data', value=data.to_dict())
        return data
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None

def unarchive():
    try:
        airflow_home = os.getenv('AIRFLOW_HOME', '/opt/airflow')  # Example Airflow home path
        target_dir = os.path.join(airflow_home, 'extracted_data')  # Example target directory within Airflow home
        os.makedirs(target_dir, exist_ok=True)
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        print("Successfully unzipped the file to", target_dir)
    except Exception as e:
        print(f"Error during unarchive: {e}")
        raise  # Raise the exception to fail the task in Airflow


# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 16),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Instantiate the DAG
dag = DAG(
    'simple_airflow_dag',
    default_args=default_args,
    description='A simple DAG for demonstration purposes',
    schedule_interval=timedelta(days=1),  # Run daily
)

# Define the tasks in the DAG
task1 = PythonOperator(
    task_id='task1',
    python_callable=unarchive,
    dag=dag,
)

task2 = PythonOperator(
    task_id='task2',
    python_callable=dataextract,
    dag=dag,
)

task3 = PythonOperator(
    task_id='task3',
    python_callable=consolidate,
    dag=dag,
)

task4 = PythonOperator(
    task_id='task4',
    python_callable=transform,
    dag=dag,
)

# Define task dependencies
task1 >> task2 >> task3 >> task4


"""
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pandas as pd 
import numpy as np
import os
import zipfile

zip_file = '/Users/pro/downloads/data.zip'  # Replace with your zip file path
extract_to = '/Users/pro/documents'  # Replace with your desired extraction directory


def read_fix_file(file_path):
 fwf_file_path = 'path/to/your/file.fwf'
 column_specs = [(0, 10), (10, 20), (20, 30)]
 fwf_data = read_fix_file(fwf_file_path, column_specs) 
 if fwf_data is not None:
    print(fwf_data.head())  # Display the first few rows of the DataFrame


def read_tsv_file(file_path   ):
    try:
        data = pd.read_csv(file_path, sep='\t')
        print(f"Data successfully read from {file_path}")
        return data
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None   
    


def transform(**kwargs):
    ti = kwargs['ti']
    csv_data = ti.xcom_pull(key='data', task_ids=['read_tsv_file', 'read_fix_file'])
    
    # Convert the dictionary back to a pandas DataFrame
    data = pd.DataFrame.from_dict(csv_data[0])  # Assuming you want to work on the first dataset

    # Example: Remove outliers using the IQR method for numerical columns
    def remove_outliers(df):
        numeric_cols = df.select_dtypes(include=['number']).columns
        Q1 = df[numeric_cols].quantile(0.25)
        Q3 = df[numeric_cols].quantile(0.75)
        IQR = Q3 - Q1
        is_not_outlier = ~((df[numeric_cols] < (Q1 - 1.5 * IQR)) | (df[numeric_cols] > (Q3 + 1.5 * IQR))).any(axis=1)
        return df[is_not_outlier]

    cleaned_data = remove_outliers(data)
    
    # Push the cleaned data back to XCom
    ti.xcom_push(key='cleaned_data', value=cleaned_data.to_dict())

def consolidate(**kwargs):
    ti = kwargs['ti']
    csv_data = ti.xcom_pull(key='data', task_ids='task1')
    csv_df = pd.DataFrame.from_dict(tsv_data)
    # Push the consolidated data to XCom
    ti.xcom_push(key='csv_df', value=csv_df.to_dict())

def dataextract(**kwargs):
    path=extract_to+"/diabetes.csv"
    try:
        data = pd.read_csv(path)
        print(f"Data successfully read from {file_path}")
        kwargs['ti'].xcom_push(key='data',value=data.to_dict())
        return data
    except Exception as e:
        print(f"Error reading {extract_to}: {e}")
        return None



def unarchive():
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Successfully unzipped the file")

# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 16),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Instantiate the DAG
dag = DAG(
    'simple_airflow_dag',
    default_args=default_args,
    description='A simple DAG for demonstration purposes',
    schedule_interval=timedelta(days=1),  # Run daily
)

# Define the tasks in the DAG
task1 = PythonOperator(
    task_id='task1',
    python_callable=unarchive,  # Corrected function name
    dag=dag,
)

task2=PythonOperator(
     task_id='task2',
     python_callable=dataextract,
     dag=dag

)
task3=PythonOperator(
     task_id='task3',
     python_callable=consolidate,
     dag=dag

)

task4=PythonOperator(
 task_id='task4',
 python_callable=transform,
 dag=dag
)
task1>>task2>>task3>>task4
"""

# You can define more tasks here if needed

# Define the task dependencies, if any
# task1 >> task2

"""

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pandas as pd 
import numpy as np
import os
import zipfile

zip_file = '/Users/pro/downloads/data.zip'  # Replace with your zip file path
extract_to = '/Users/pro/documents'  # Replace with your desired extraction directory

def unarchive(**kwargs):
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Successfully unzipped the file")
    # Push the extracted path to XCom
    kwargs['ti'].xcom_push(key='extract_to', value=extract_to)

def read_tsv_file(**kwargs):
    ti = kwargs['ti']
    extract_to = ti.xcom_pull(key='extract_to', task_ids='unarchive')
    file_path = os.path.join(extract_to, 'your_file.tsv')  # Replace with your actual TSV file name
    try:
        data = pd.read_csv(file_path, sep='\t')
        print(f"Data successfully read from {file_path}")
        ti.xcom_push(key='data', value=data.to_dict())
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

def read_fix_file(**kwargs):
    ti = kwargs['ti']
    extract_to = ti.xcom_pull(key='extract_to', task_ids='unarchive')
    file_path = os.path.join(extract_to, 'your_file.fwf')  # Replace with your actual fixed-width file name
    column_specs = [(0, 10), (10, 20), (20, 30)]  # Define your column specifications here
    try:
        data = pd.read_fwf(file_path, colspecs=column_specs)
        print(f"Data successfully read from {file_path}")
        ti.xcom_push(key='data', value=data.to_dict())
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

def transform(**kwargs):
    ti = kwargs['ti']
    csv_data = ti.xcom_pull(key='data', task_ids=['read_tsv_file', 'read_fix_file'])
    
    # Convert the dictionary back to a pandas DataFrame
    data = pd.DataFrame.from_dict(csv_data[0])  # Assuming you want to work on the first dataset

    # Example: Remove outliers using the IQR method for numerical columns
    def remove_outliers(df):
        numeric_cols = df.select_dtypes(include=['number']).columns
        Q1 = df[numeric_cols].quantile(0.25)
        Q3 = df[numeric_cols].quantile(0.75)
        IQR = Q3 - Q1
        is_not_outlier = ~((df[numeric_cols] < (Q1 - 1.5 * IQR)) | (df[numeric_cols] > (Q3 + 1.5 * IQR))).any(axis=1)
        return df[is_not_outlier]

    cleaned_data = remove_outliers(data)
    
    # Push the cleaned data back to XCom
    ti.xcom_push(key='cleaned_data', value=cleaned_data.to_dict())

def consolidate(**kwargs):
    ti = kwargs['ti']
    tsv_data = ti.xcom_pull(key='data', task_ids='read_tsv_file')
    fwf_data = ti.xcom_pull(key='data', task_ids='read_fix_file')
    
    tsv_df = pd.DataFrame.from_dict(tsv_data)
    fwf_df = pd.DataFrame.from_dict(fwf_data)
    
    # Example consolidation: concatenate the two DataFrames
    consolidated_data = pd.concat([tsv_df, fwf_df], axis=0)
    
    # Push the consolidated data to XCom
    ti.xcom_push(key='consolidated_data', value=consolidated_data.to_dict())

# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 16),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Instantiate the DAG
dag = DAG(
    'simple_airflow_dag',
    default_args=default_args,
    description='A simple DAG for demonstration purposes',
    schedule_interval=timedelta(days=1),  # Run daily
)

# Define the tasks in the DAG
task1 = PythonOperator(
    task_id='unarchive',
    python_callable=unarchive,
    provide_context=True,
    dag=dag,
)

task2 = PythonOperator(
    task_id='read_tsv_file',
    python_callable=read_tsv_file,
    provide_context=True,
    dag=dag,
)

task3 = PythonOperator(
    task_id='read_fix_file',
    python_callable=read_fix_file,
    provide_context=True,
    dag=dag,
)

task4 = PythonOperator(
    task_id='transform',
    python_callable=transform,
    provide_context=True,
    dag=dag,
)

task5 = PythonOperator(
    task_id='consolidate',
    python_callable=consolidate,
    provide_context=True,
    dag=dag,
)

# Define task dependencies
task1 >> [task2, task3] >> task4 >> task5


"""