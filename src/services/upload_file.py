"""
File upload service using Cloudinary.

Handles uploading user files (e.g., avatars) and returns the public URL.
"""

import cloudinary
import cloudinary.uploader


class UploadFileService:
    """
    Service to upload files to Cloudinary.

    Parameters
    ----------
    cloud_name : str
        Cloudinary cloud name.
    api_key : str
        Cloudinary API key.
    api_secret : str
        Cloudinary API secret.
    """

    def __init__(self, cloud_name, api_key, api_secret):
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    def upload_file(self, file, username) -> str:
        """
        Upload a file to Cloudinary under a user-specific path.

        Parameters
        ----------
        file : UploadFile
            File object to upload.
        username : str
            Username to organize the file in a unique folder.

        Returns
        -------
        str
            URL of the uploaded file.
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
