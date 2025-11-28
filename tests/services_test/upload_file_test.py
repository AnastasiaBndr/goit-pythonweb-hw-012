import pytest
from unittest.mock import patch, MagicMock

from src.services.upload_file import UploadFileService


class FakeFile:
    def __init__(self):
        self.file = b"data"


@pytest.mark.asyncio
class TestUploadFiles:
    @pytest.fixture
    def service(self):
        return UploadFileService(
            cloud_name="test",
            api_key="123",
            api_secret="secret"
        )

    async def test_upload_file(self, service):
        file = FakeFile()
        username = "name"
        with patch('cloudinary.uploader.upload') as mock_upload, \
                patch('cloudinary.CloudinaryImage') as mock_image:

            mock_upload.return_value = {"version": "5"}

            mock_img_instance = MagicMock()
            mock_img_instance.build_url.return_value = "https://fake.url/image.jpg"
            mock_image.return_value = mock_img_instance

            result = service.upload_file(file, username)

            mock_upload.assert_called_once_with(
                file.file,
                public_id="RestApp/name"
            )

            mock_img_instance.build_url.assert_called_once()

            assert result == "https://fake.url/image.jpg"
