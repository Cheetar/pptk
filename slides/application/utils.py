from urllib import request

import boto3
from botocore.exceptions import ClientError
from decouple import UndefinedValueError, config
from flask import current_app as app


def get_slides_info(slides):
    """Gets summarized information about the slides.

    Parameters:
        slides: Iterable of Slide objects

    Returns:
        dictionary: contains summarized information about the slides
    """
    slides_with_funniness = [slide for slide in slides if slide["funniness"] is not None]
    total_funniness = sum(slide["funniness"] for slide in slides_with_funniness)
    no_slides_with_funniness = len(slides_with_funniness)
    avg_funniness = float(total_funniness) / no_slides_with_funniness if no_slides_with_funniness > 0 else 0
    max_funniness = max(slide["funniness"] for slide in slides_with_funniness) if no_slides_with_funniness > 0 else 0
    min_funniness = min(slide["funniness"] for slide in slides_with_funniness) if no_slides_with_funniness > 0 else 0

    return {'no_slides': len(slides),
            'avg_funniness': avg_funniness,
            'max_funniness': max_funniness,
            'min_funniness': min_funniness
            }


def put_into_s3(dest_object_name, src_data):
    """Add an object to an Amazon S3 bucket

    The src_data argument must be of type bytes or a string that references
    a file specification.

    Parameters:
        dest_object_name (string): Name of the file after upload
        src_data: Bytes of data or string reference to file spec

    Returns:
        bool: True if src_data was added to dest_bucket/dest_object, otherwise
            False
    """

    if isinstance(src_data, bytes):
        object_data = src_data
    elif isinstance(src_data, str):
        try:
            object_data = open(src_data, 'rb')
            # possible FileNotFoundError/IOError exception
        except Exception as e:
            app.logger.error("Unable to open the file %s: %s") % src_data, e
            return False
    else:
        app.logger.error('Type of ' + str(type(src_data)) + ' for the argument \'src_data\' is not supported.')
        return False

    # Get the config from env
    try:
        Access_Key_ID = config("Access_Key_ID")
        Secret_Access_Key = config("Secret_Access_Key")
        dest_bucket_name = config("BUCKET_NAME")
    except UndefinedValueError as e:
        app.logger.error(e)
        return False

    # Initialize the connection
    s3 = boto3.client('s3', aws_access_key_id=Access_Key_ID, aws_secret_access_key=Secret_Access_Key)

    try:
        s3.put_object(Bucket=dest_bucket_name, Key=dest_object_name, Body=object_data, ACL='public-read')
    except ClientError as e:
        # AllAccessDisabled error == bucket not found
        # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
        app.logger.error(e)
        return False
    finally:
        if isinstance(src_data, str):
            object_data.close()
    return True


def read_data_from_url(url):
    """ Read the image data from the url

    Parameters:
    url (string)

    Returns:
        Bytes of data read from the url
    """
    return request.urlopen(url).read()
