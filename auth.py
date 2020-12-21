import os
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


def authenticate():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)


    if os.path.exists('credentials.p'):
        credentials = pickle.load(open('credentials.p', 'rb'))
    else:
        credentials = flow.run_console()
        pickle.dump(credentials, open('credentials.p', 'wb'))

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials, cache_discovery=False)
    return youtube

