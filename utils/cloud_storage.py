"""
Google Cloud Storage Manager
Handles image uploads and management for construction site photos
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from PIL import Image
import io


class CloudStorageManager:
    """Manage construction site images in Google Cloud Storage"""

    def __init__(self, project_id: str = None, bucket_name: str = None):
        """
        Initialize Cloud Storage manager

        Args:
            project_id: GCP project ID
            bucket_name: Cloud Storage bucket name
        """
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID')
        self.bucket_name = bucket_name or os.getenv('GCS_BUCKET', 'constrite-images')

        if not self.project_id:
            print("⚠️ Warning: GCP_PROJECT_ID not set. Cloud Storage disabled.")
            self.client = None
            self.bucket = None
            return

        try:
            self.client = storage.Client(project=self.project_id)
            self.bucket = self.client.bucket(self.bucket_name)
            print(f"✅ Cloud Storage initialized: gs://{self.bucket_name}")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize Cloud Storage: {e}")
            self.client = None
            self.bucket = None

    def create_bucket_if_not_exists(self, location: str = 'US') -> bool:
        """
        Create bucket if it doesn't exist

        Args:
            location: Bucket location

        Returns:
            True if successful or already exists
        """
        if not self.client:
            return False

        try:
            # Check if bucket exists
            if self.bucket.exists():
                print(f"✅ Bucket already exists: {self.bucket_name}")
                return True

            # Create bucket
            bucket = self.client.create_bucket(
                self.bucket_name,
                location=location
            )

            # Set lifecycle policy to delete old files after 90 days
            bucket.add_lifecycle_delete_rule(age=90)
            bucket.patch()

            print(f"✅ Bucket created: {self.bucket_name}")
            return True

        except Exception as e:
            print(f"❌ Error creating bucket: {e}")
            return False

    def upload_image(
        self,
        image_path: str,
        site_id: str = None,
        optimize: bool = True,
        max_size: Tuple[int, int] = (1920, 1080)
    ) -> Optional[str]:
        """
        Upload construction site image to Cloud Storage

        Args:
            image_path: Local path to image file
            site_id: Optional site identifier for organizing files
            optimize: Whether to optimize/compress image before upload
            max_size: Maximum dimensions for optimization

        Returns:
            Public URL of uploaded image, or None if failed
        """
        if not self.client or not self.bucket:
            print("⚠️ Cloud Storage not initialized. Skipping upload.")
            return None

        try:
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_id = str(uuid.uuid4())[:8]
            extension = os.path.splitext(image_path)[1].lower()

            if site_id:
                blob_name = f"sites/{site_id}/{timestamp}_{file_id}{extension}"
            else:
                blob_name = f"uploads/{timestamp}_{file_id}{extension}"

            # Optimize image if requested
            if optimize:
                image_data = self._optimize_image(image_path, max_size)
            else:
                with open(image_path, 'rb') as f:
                    image_data = f.read()

            # Upload to GCS
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(
                image_data,
                content_type=self._get_content_type(extension)
            )

            # Get public URL (bucket has uniform bucket-level access enabled)
            public_url = blob.public_url
            print(f"✅ Image uploaded: {public_url}")

            return public_url

        except Exception as e:
            print(f"❌ Error uploading image: {e}")
            return None

    def upload_from_bytes(
        self,
        image_bytes: bytes,
        filename: str,
        site_id: str = None,
        content_type: str = 'image/jpeg'
    ) -> Optional[str]:
        """
        Upload image from bytes data

        Args:
            image_bytes: Image data as bytes
            filename: Original filename (for extension)
            site_id: Optional site identifier
            content_type: MIME type of image

        Returns:
            Public URL of uploaded image, or None if failed
        """
        if not self.client or not self.bucket:
            return None

        try:
            # Generate blob name
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_id = str(uuid.uuid4())[:8]
            extension = os.path.splitext(filename)[1].lower()

            if site_id:
                blob_name = f"sites/{site_id}/{timestamp}_{file_id}{extension}"
            else:
                blob_name = f"uploads/{timestamp}_{file_id}{extension}"

            # Upload
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(image_bytes, content_type=content_type)

            # Get public URL (bucket has uniform bucket-level access enabled)
            return blob.public_url

        except Exception as e:
            print(f"❌ Error uploading from bytes: {e}")
            return None

    def _optimize_image(
        self,
        image_path: str,
        max_size: Tuple[int, int]
    ) -> bytes:
        """
        Optimize image by resizing and compressing

        Args:
            image_path: Path to image file
            max_size: Maximum dimensions (width, height)

        Returns:
            Optimized image as bytes
        """
        try:
            # Open image
            img = Image.open(image_path)

            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # Resize if larger than max_size
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save to bytes with compression
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)

            return output.read()

        except Exception as e:
            print(f"⚠️ Error optimizing image, using original: {e}")
            with open(image_path, 'rb') as f:
                return f.read()

    def _get_content_type(self, extension: str) -> str:
        """Get MIME type from file extension"""
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp'
        }
        return content_types.get(extension.lower(), 'application/octet-stream')

    def get_signed_url(
        self,
        blob_name: str,
        expiration_minutes: int = 60
    ) -> Optional[str]:
        """
        Generate signed URL for private blob access

        Args:
            blob_name: Name of blob in bucket
            expiration_minutes: URL expiration time in minutes

        Returns:
            Signed URL or None
        """
        if not self.bucket:
            return None

        try:
            blob = self.bucket.blob(blob_name)
            url = blob.generate_signed_url(
                expiration=timedelta(minutes=expiration_minutes),
                method='GET'
            )
            return url

        except Exception as e:
            print(f"❌ Error generating signed URL: {e}")
            return None

    def delete_image(self, blob_name: str) -> bool:
        """
        Delete image from Cloud Storage

        Args:
            blob_name: Name of blob to delete

        Returns:
            True if successful, False otherwise
        """
        if not self.bucket:
            return False

        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            print(f"✅ Image deleted: {blob_name}")
            return True

        except Exception as e:
            print(f"❌ Error deleting image: {e}")
            return False

    def list_site_images(
        self,
        site_id: str,
        max_results: int = 50
    ) -> list:
        """
        List all images for a specific site

        Args:
            site_id: Site identifier
            max_results: Maximum number of results

        Returns:
            List of blob names
        """
        if not self.bucket:
            return []

        try:
            prefix = f"sites/{site_id}/"
            blobs = self.client.list_blobs(
                self.bucket_name,
                prefix=prefix,
                max_results=max_results
            )

            return [blob.name for blob in blobs]

        except Exception as e:
            print(f"❌ Error listing images: {e}")
            return []

    def get_storage_stats(self) -> Optional[dict]:
        """
        Get storage statistics

        Returns:
            Dictionary with storage stats
        """
        if not self.bucket:
            return None

        try:
            blobs = list(self.client.list_blobs(self.bucket_name))

            total_size = sum(blob.size for blob in blobs)
            total_files = len(blobs)

            # Group by site
            site_counts = {}
            for blob in blobs:
                if blob.name.startswith('sites/'):
                    parts = blob.name.split('/')
                    if len(parts) >= 2:
                        site_id = parts[1]
                        site_counts[site_id] = site_counts.get(site_id, 0) + 1

            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'sites_with_images': len(site_counts),
                'site_counts': site_counts
            }

        except Exception as e:
            print(f"❌ Error getting storage stats: {e}")
            return None


# Test the module
if __name__ == "__main__":
    print("Testing Cloud Storage Manager...\n")

    # Initialize manager
    manager = CloudStorageManager()

    if manager.client:
        # Create bucket if needed
        success = manager.create_bucket_if_not_exists()

        if success:
            print("\n✅ Cloud Storage is ready")

            # Get stats
            stats = manager.get_storage_stats()
            if stats:
                print(f"\n📊 Storage Statistics:")
                print(f"  Total files: {stats['total_files']}")
                print(f"  Total size: {stats['total_size_mb']} MB")
                print(f"  Sites with images: {stats['sites_with_images']}")
    else:
        print("⚠️ Cloud Storage not available. Set GCP_PROJECT_ID to test.")
