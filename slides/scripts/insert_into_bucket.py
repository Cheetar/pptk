import logging

import boto3
from botocore.exceptions import ClientError
from decouple import config


def put_object(dest_bucket_name, dest_object_name, src_data):
    """Add an object to an Amazon S3 bucket

    The src_data argument must be of type bytes or a string that references
    a file specification.

    :param dest_bucket_name: string
    :param dest_object_name: string
    :param src_data: bytes of data or string reference to file spec
    :return: True if src_data was added to dest_bucket/dest_object, otherwise
    False
    """

    # Construct Body= parameter
    if isinstance(src_data, bytes):
        object_data = src_data
    elif isinstance(src_data, str):
        try:
            object_data = open(src_data, 'rb')
            # possible FileNotFoundError/IOError exception
        except Exception as e:
            logging.error(e)
            return False
    else:
        logging.error('Type of ' + str(type(src_data)) +
                      ' for the argument \'src_data\' is not supported.')
        return False

    # Put the object
    Access_Key_ID = config("Access_Key_ID")
    Secret_Access_Key = config("Secret_Access_Key")
    s3 = boto3.client('s3', aws_access_key_id=Access_Key_ID, aws_secret_access_key=Secret_Access_Key)

    try:
        s3.put_object(Bucket=dest_bucket_name, Key=dest_object_name, Body=object_data)
    except ClientError as e:
        # AllAccessDisabled error == bucket not found
        # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
        logging.error(e)
        return False
    finally:
        if isinstance(src_data, str):
            object_data.close()
    return True


def main():
    """Exercise put_object()"""

    # Assign these values before running the program
    test_bucket_name = 'pptk.slides'
    test_object_name = 'example_file'
    filename = 'requirements.txt'
    # Alternatively, specify object contents using bytes.
    # filename = b'This is the data to store in the S3 object.'

    # Set up logging
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(asctime)s: %(message)s')

    # Put the object into the bucket
    success = put_object(test_bucket_name, test_object_name, filename)
    if success:
        logging.info('Added {0} to {1}'.format(test_object_name, test_bucket_name))


if __name__ == '__main__':
    main()
