import os

from google.cloud import secretmanager
from google.oauth2 import service_account

class GcpSecretsManager():
    def __init__(self, json_path=None):
        if json_path is None:
            self.client = secretmanager.SecretManagerServiceClient()
        else:
            json_path = os.path.expanduser(json_path)
            credentials = service_account.Credentials.from_service_account_file(json_path)
            self.client = secretmanager.SecretManagerServiceClient(credentials=credentials)

    def access_secret(self, project, secret_id, version):
        name = self.client.secret_version_path(project, secret_id, version)
        response = self.client.access_secret_version(name)
        return response.payload.data.decode("utf-8")

