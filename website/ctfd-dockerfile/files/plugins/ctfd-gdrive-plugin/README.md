# CTFd-gdrive-plugin

Plugin that converts CTFd file handler to Google Drive handler

## Requirements

Before you proceed, you need to create a service account and a few more steps:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Enable the Google Drive API for your project. Search for "Drive API" in the library and enable it.
4. Go to the "APIs & Services" > "Credentials" section and click on "Create Credentials." Choose "Service Account" as the credential type. You won't need any additional rights for this account.
5. Go to [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) in your project and in your newly created account go to Keys and generate new json-based key. There, you will find values needed during the installation

## Installation

1. To install clone this repository to the [CTFd/plugins](https://github.com/CTFd/CTFd/tree/master/CTFd/plugins) folder.
2. Install the requirements specified in the [requirements.txt](requirements.txt) file.
3. Add values as environment variables or edit [CTFd/config.py](https://github.com/CTFd/CTFd/blob/master/CTFd/config.py) with the following code:
```python
if UPLOAD_PROVIDER == "googledrive":
    GOOGLE_PROJECT_ID: str = empty_str_cast(config_ini["uploads"]["GOOGLE_PROJECT_ID"])

    GOOGLE_PRIVATE_KEY_ID: str = empty_str_cast(config_ini["uploads"]["GOOGLE_PRIVATE_KEY_ID"])

    GOOGLE_PRIVATE_KEY: str = empty_str_cast(config_ini["uploads"]["GOOGLE_PRIVATE_KEY"])

    GOOGLE_CLIENT_EMAIL: str = empty_str_cast(config_ini["uploads"]["GOOGLE_CLIENT_EMAIL"])

    GOOGLE_CLIENT_ID: str = empty_str_cast(config_ini["uploads"]["GOOGLE_CLIENT_ID"])

    GOOGLE_ROOT_PATH: str = empty_str_cast(config_ini["uploads"]["GOOGLE_ROOT_PATH"], default='/CTFd')

    GOOGLE_SHARED_FOLDER_ID: str = empty_str_cast(config_ini["uploads"]["GOOGLE_ROOT_PATH"], default=None)
```

- `UPLOAD_PROVIDER` set it to "googledrive" to use this plugin.
- `GOOGLE_PROJECT_ID`: The ID of your Google Cloud project.
- `GOOGLE_PRIVATE_KEY_ID`: The private key ID of your service account.
- `GOOGLE_PRIVATE_KEY`: The private key value of your service account.
- `GOOGLE_CLIENT_EMAIL`: The client email address of your service account.
- `GOOGLE_CLIENT_ID`: The client ID of your service account.
- `GOOGLE_ROOT_PATH`: Main directory in Drive (it is not used if `GOOGLE_SHARED_FOLDER_ID` is present)
- `GOOGLE_SHARED_FOLDER_ID`: The ID of a shared folder (you can extract it from the URL of a shared folder when you do it manually via browser). This field is not mandatory. If not set, service account's drive will be used (you won't have access to it through the browser)

> If you want to use shared folder instead of SA's space, you have to share the directory with GOOGLE_CLIENT_EMAIL as a user with Editor rights. If you use shared folder, you will have direct access to all files

If you want to store them in config.ini, the GOOGLE_PRIVATE_KEY variable should look like this:
```
GOOGLE_PRIVATE_KEY = -----BEGIN PRIVATE KEY-----
    ...
    -----END PRIVATE KEY-----
```

## Note

This plugin doesn't have `sync()` implemented. I just didn't think it is useful at all. Our main usage of CTFd was in Kubernetes and local sync of files wasn't a priority. 