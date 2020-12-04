import os

import yaml
from google.cloud import storage
from google.oauth2 import service_account

from .storage import Storage


class GcsStorage(Storage):
    def __init__(self, bucket, path, project=None, json_path=None):
        if bucket is None:
            raise ValueError('Bucket must be supplied to GCS storage')
        if path is None:
            path = 'spinbot/cache'

        self.path = path
        if json_path is not None:
            json_path = os.path.expanduser(json_path)
            credentials = service_account.Credentials.from_service_account_file(json_path)
            if credentials.requires_scopes:
                credentials = credentials.with_scopes(['https://www.googleapis.com/auth/devstorage.read_write'])
            self.client = storage.Client(project=project, credentials=credentials)
        else:
            self.client = storage.Client()

        if self.client.lookup_bucket(bucket) is None:
            self.client.create_bucket(bucket)

        self.bucket = self.client.get_bucket(bucket)

        super().__init__()

    def store(self, key, val):
        origblob = self.bucket.get_blob(self.path)
        if origblob:
            contents = origblob.download_as_string()
        else:
            contents = '{}'

        props = yaml.safe_load(contents)
        if props is None:
            props = {}

        props[key] = val
        # You can't use origblob to upload. Calling `download_as_string` sets
        # the hash field (crc32) on the object. When you upload, since that
        # field is already set, it won't get recalculated it for the new
        # content. So it sends the crc32 to the server and the server says
        # "whoah buddy, your crc32 doesn't match your content" and returns an
        # error. Is this a bug or just confusing library design? The crc32 field
        # on the blob is new, so it's hard for me to say if they intended for it
        # to work this way. It works in google-cloud-storage 1.29.0, but is
        # broken in 1.33.0.
        newblob = self.bucket.blob(self.path)
        newblob.upload_from_string(yaml.safe_dump(props))

    def load(self, key):
        b = self.bucket.get_blob(self.path)
        contents = '{}'
        if b:
            contents = b.download_as_string()

        props = yaml.safe_load(contents)
        if props is None:
            props = {}

        return props.get(key)
