import os
import io
import zipfile
from datetime import timedelta
from minio import Minio
from minio.error import S3Error, MinioException
from polls.views import ROOT_MODEL_DIR

from ku_djangoo.settings import (
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_API_ADDR,
    MINIO_BUCKET1_ADDR,
)

MINUTE_AS_SECONDS = 60
HOUR_AS_SECONDS = 3600
DAY_AS_SECONDS = 86400

def create_minio_client(
        endpoint=MINIO_API_ADDR, 
        access_key=MINIO_ACCESS_KEY, 
        secret_key=MINIO_SECRET_KEY, 
        secure=False
):
    try:
        return Minio(endpoint, access_key, secret_key, secure=secure)
    except Exception as e:
        print(f"Error connecting to MinIO: {e}")
        return None

def isnone_or_empty(a):
    if a is None or a == "":
        return True
    return False

class MinioService:
    bucket = MINIO_BUCKET1_ADDR

    def __init__(self, minio_client):
        self.minio_client = minio_client
        
    def minio_client_is_none(self):
        if self.minio_client is None:
            print("Minio client not initialised")
            return True
        return False
    
    def bucket_is_none(self, bucket = ''):
        bucket = bucket or self.bucket
        if bucket is None or bucket == "":
            return True
        return False

    def object_is_none(self, object_name = ''):
        object_name = object_name or self.object_name
        if object_name is None or object_name == "":
            return True
        return False

    def list_buckets(self):
        if self.minio_client_is_none():
            return "Could not store in the server"

        try:
            buckets = self.minio_client.list_buckets()
            return [bucket.name for bucket in buckets]
        except Exception as e:
            print(f"Error listing buckets: {e}")
            return "Could not list buckets"
        
    
    def save_file_as_object(self, object_name, source_file):
        try:
            self.minio_client.fput_object(
                self.bucket,
                object_name, 
                source_file
            )
        except Exception as e:
            print(f'Error uploading {source_file} to MinIO: {e}')
            return "Error. Could not save file in the server"

    def test_connect_minio_bucket(self):
        source_file = "static/image/2018-07-5-Suboptimal-bar-chart-variable-1024x590-e1541666684430.jpg"
        object_name = "my-test-file.jpg"

        found = self.minio_client.bucket_exists(self.bucket)
        if not found:
            self.minio_client.make_bucket(self.bucket)
            print("Created bucket", self.bucket)
        else:
            print("Bucket", self.bucket, "already exists")

        self.minio_client.fput_object(
            self.bucket, object_name, source_file,
        )
        print(
            source_file, "successfully uploaded as object",
            object_name, "to bucket", self.bucket,
        )
    
    def read_file_from_minio(self, object_name, bucket=''):
        """Reads a file from MinIO and returns its content as bytes.
        Use Presigned URL to send directly from MinIO to client, instead of sending through this API server.
        """

        bucket = bucket or self.bucket

        if self.minio_client_is_none():
            return None
        if isnone_or_empty(bucket):
            return None
        if isnone_or_empty(object_name):
            return None

        try:
            self.minio_client.stat_object(bucket, object_name)

            data = self.minio_client.get_object(bucket, object_name)
            file_content_bytes = data.read()

            try:
                text_content = file_content_bytes.decode('utf-8')
                return text_content
            except UnicodeDecodeError:
                return file_content_bytes 
            finally:
                data.close()
                data.release_conn()

        except S3Error as e:
            print(f"Error reading object: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def get_zipped_file(self, prefix, bucket=''):
        bucket = bucket or self.bucket

        if self.minio_client_is_none():
            return "MinIO client not initialized", 500
        
        try:
            objects = self.minio_client.list_objects(bucket, prefix=prefix, recursive=True)

            memory_file = io.BytesIO()
            with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for obj in objects:
                    try:
                        data = self.minio_client.get_object(bucket, obj.object_name)
                        file_content = data.read()
                        data.close()
                        data.release_conn()
                        zipf.writestr(obj.object_name.replace(prefix, ''), file_content) 
                    except Exception as e:
                        print(f"Error zipping file {obj.object_name}: {e}")
                        continue 
            memory_file.seek(0)
            return memory_file.getvalue(), None
        except Exception as e:
            print(f'Error: {e}')
            return f"Error: {e}", 500

    def generate_presigned_url(self, object_name, expiry_seconds = HOUR_AS_SECONDS, method="GET"):
        """Generates a presigned URL for a MinIO object (GET or PUT).
            This URL enables to send directly from MinIO to client, instead of making a temporary data copy in API server and then sending response back through this API server.
        """

        if self.minio_client_is_none():
            return None

        try:
            url = self.minio_client.get_presigned_url(
                method,
                self.bucket,
                object_name,
                expires=timedelta(seconds=expiry_seconds)
            )
            return url
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return None

    def generate_presigned_get_url(self, object_name, expiry_seconds = HOUR_AS_SECONDS):
        """Generates a presigned URL for getting from MinIO (GET)."""
        return self.generate_presigned_url(object_name, expiry_seconds, method="GET")

    def generate_presigned_upload_url(self, object_name, expiry_seconds = HOUR_AS_SECONDS):
        """Generates a presigned URL for uploading to MinIO (PUT). Create/Overwrite/Update. """
        return self.generate_presigned_url(object_name, expiry_seconds, method="PUT")
 
    def generate_presigned_post_url(self, object_name, expiry_seconds=HOUR_AS_SECONDS):
        """Generates a presigned URL for posting form data to MinIO (POST)."""
        return self.generate_presigned_url(object_name, expiry_seconds, method="POST")
    
    def generate_presigned_delete_url(self, object_name, expiry_seconds=HOUR_AS_SECONDS):
        """Generates a presigned URL for deleting a MinIO object (DELETE)."""
        return self.generate_presigned_url(object_name, expiry_seconds, method="DELETE")

    def remove_object(self, object_name, bucket=''):
        bucket = bucket or self.bucket
        
        if self.minio_client_is_none():
            return False
        if isnone_or_empty(bucket):
            print('bucket name is invalid')
            return False        
        if isnone_or_empty(object_name):
            print('object name is invalid')
            return False
        try:
            self.minio_client.remove_object(self.bucket, object_name)
            return True
        except Exception as e:
            print(f"Error removing object: {e}")
            return False

    def delete_all_object_versions(self, object_name, bucket_name=''):
        """Deletes all versions of an object from a MinIO bucket."""
        bucket_name = bucket_name or self.bucket
        try:
            objects = self.minio_client.list_objects(
                bucket_name, 
                object_name, 
                include_version=True,
                recursive=True
            )
            for obj in objects:
                self.minio_client.remove_object(bucket_name, object_name, version_id=obj.version_id)
                print(f'{obj.object_name}')
            print(f"Successfully deleted all versions of: {object_name}")
            return True
        except S3Error as e:
            print(f"Error deleting object versions of {object_name}: {e}")
            return False
    
    def check_object_deleted(self, object_name):
        try:
            self.minio_client.stat_object(self.bucket, object_name)
        except Exception as e:
            print(f'The object is already deleted or error occurred checking object: {e}')
            return None

        try:
            objects = self.minio_client.list_objects(self.bucket, prefix=object_name)
            for obj in objects:
                if obj.is_dir:
                    continue 
                if obj.object_name == object_name:
                    return False 
            return True 
        except Exception as e:
            print(f"Error listing objects: {e}")
            return None 
        
    def print_list_object(self, prefix=None):
        try:
            objects = self.minio_client.list_objects(self.bucket, prefix=prefix)
            for obj in objects:
                print(obj.object_name)
            return True 
        except Exception as e:
            print(f"Error listing objects: {e}")
            return None 


minio_client = create_minio_client()
minio_service = MinioService(minio_client)