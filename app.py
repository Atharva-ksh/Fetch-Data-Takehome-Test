import boto3
import json
import psycopg2
from hashlib import sha256
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS SQS Client
sqs = boto3.client('sqs', endpoint_url='http://localstack:4566', region_name='us-east-1')
queue_url = 'http://localstack:4566/000000000000/login-queue'

# PostgreSQL Connection with credentials
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="postgres",
    port="5432"
)
cursor = conn.cursor()

# Maximum idle time before the application stops if no messages are received
MAX_IDLE_TIME = 90

def fetch_messages() -> list:
    """
    Receive messages and log them with error handling

    Returns: 
    list: A list of messages fetched from the SQS queue.

    """
    try:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            VisibilityTimeout=30,
            WaitTimeSeconds=1   # For frequent polling
        )
        logger.info(f"Fetched messages: {response}")
        return response.get('Messages', [])
    except Exception as e:
        logger.error(f"Error fetching messages from SQS: {e}")
        return []

def mask_value(value) -> str:
    """
    Function to mask PII data using sha256 hashing
    
    Args:
    value (str): The value to be masked.

    Returns:
    str: The hashed value.
    
    """
    return sha256(value.encode()).hexdigest()


def validate_message(data) -> bool:
    """
    Function for validating incoming messages to make sure they fit the schema

    Args:
        data (dict): The message data to be validated.

    Returns:
        bool: True if the message contains all required fields, False otherwise.

    """
    required_fields = ['user_id', 'device_type', 'ip', 'device_id', 'app_version', 'locale']
    for field in required_fields:
        if field not in data:
            return False
    return True

def process_and_insert(messages) -> None:
    """
    Entire process pipeline
    
    Args:
    messages (list): List of messages fetched from SQS.

    """
    try:
        for message in messages:
            # Hashmap to load the JSON message
            data = json.loads(message['Body'])
            if not validate_message(data):
                logger.error(f"Invalid message format: {data}")
                continue
            
            logger.info(f"Processing message: {data}")
            masked_ip = mask_value(data['ip'])
            masked_device_id = mask_value(data['device_id'])
            app_version = int(data['app_version'].split('.')[0])  # Extract the major version number since int input
            
            insert_query = """
            INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE)
            """
            cursor.execute(insert_query, (
                data['user_id'],
                data['device_type'],
                masked_ip,
                masked_device_id,
                data['locale'],
                app_version
            ))
        conn.commit()
        logger.info("Data committed to the database.")
    except Exception as e:
        # Graceful error handling
        conn.rollback()
        logger.error(f"Error processing and inserting data: {e}")

if __name__ == "__main__":
    idle_time = 0
    while True:
        messages = fetch_messages()
        if messages:
            process_and_insert(messages)
            idle_time = 0  # Reset idle time after processing messages
        else:
            logger.info("No messages found. Retrying in 5 seconds...")
            idle_time += 5
        
        # Graceful stopping mechanism for this particular use-case
        if idle_time >= MAX_IDLE_TIME:
            logger.info("Max idle time reached. Exiting...")
            break
        
        time.sleep(5)

    cursor.close()
    conn.close()