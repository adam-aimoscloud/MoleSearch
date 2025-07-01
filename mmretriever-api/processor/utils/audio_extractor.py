# extract audio from video

import ffmpeg
import oss2
import tempfile
import os
import uuid
from typing import Optional
import requests
from urllib.parse import urlparse
from ...utils import logger

class AudioExtractor:
    def __init__(self, oss_access_key_id: str, oss_access_key_secret: str, 
                 oss_endpoint: str, oss_bucket_name: str):
        """
        init audio extractor
        
        Args:
            oss_access_key_id: oss access key id
            oss_access_key_secret: oss access key secret
            oss_endpoint: oss endpoint
            oss_bucket_name: oss bucket name
        """
        self.auth = oss2.Auth(oss_access_key_id, oss_access_key_secret)
        self.bucket = oss2.Bucket(self.auth, oss_endpoint, oss_bucket_name)
        logger.info(f"AudioExtractor initialized with bucket: {oss_bucket_name}")

    def extract_audio(self, video_url: str, audio_prefix: str = "audio") -> str:
        """
        extract audio from video url and upload to oss
        
        Args:
            video_url: video url
            audio_prefix: audio file prefix in oss
            
        Returns:
            str: audio url after uploaded to oss
            
        Raises:
            Exception: any error during extraction or upload
        """
        logger.info(f"Starting audio extraction from video: {video_url}")
        
        temp_video_path = None
        temp_audio_path = None
        
        try:
            # 1. download video to temp file
            temp_video_path = self._download_video(video_url)
            logger.info(f"Video downloaded to: {temp_video_path}")
            
            # 2. extract audio from video
            temp_audio_path = self._extract_audio_from_video(temp_video_path)
            logger.info(f"Audio extracted to: {temp_audio_path}")
            
            # 3. upload audio to oss
            audio_url = self._upload_to_oss(temp_audio_path, audio_prefix)
            logger.info(f"Audio uploaded to OSS: {audio_url}")
            
            return audio_url
            
        except Exception as e:
            logger.error(f"Error during audio extraction: {str(e)}")
            raise
        finally:
            # clean up temp files
            self._cleanup_temp_files(temp_video_path, temp_audio_path)

    def _download_video(self, video_url: str) -> str:
        """
        download video to temp file
        
        Args:
            video_url: video url
            
        Returns:
            str: temp video file path
        """
        # get video file extension
        parsed_url = urlparse(video_url)
        video_extension = os.path.splitext(parsed_url.path)[1] or '.mp4'
        
        # create temp file
        temp_file = tempfile.NamedTemporaryFile(suffix=video_extension, delete=False)
        temp_video_path = temp_file.name
        temp_file.close()
        
        # download video
        logger.info(f"Downloading video from: {video_url}")
        response = requests.get(video_url, stream=True, timeout=300)
        response.raise_for_status()
        
        with open(temp_video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = os.path.getsize(temp_video_path)
        logger.info(f"Video downloaded successfully, size: {file_size} bytes")
        
        return temp_video_path

    def _extract_audio_from_video(self, video_path: str) -> str:
        """
        extract audio from video file using ffmpeg
        
        Args:
            video_path: video file path
            
        Returns:
            str: temp audio file path
        """
        # create temp audio file
        temp_audio_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_audio_path = temp_audio_file.name
        temp_audio_file.close()
        
        logger.info(f"Extracting audio from: {video_path}")
        
        try:
            # extract audio using ffmpeg
            (
                ffmpeg
                .input(video_path)
                .output(
                    temp_audio_path,
                    acodec='pcm_s16le',  # wav format encoding
                    ac=1,                # single channel
                    ar='16000'           # sample rate 16kHz
                )
                .overwrite_output()      # overwrite output file
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            # verify if audio file is created successfully
            if not os.path.exists(temp_audio_path) or os.path.getsize(temp_audio_path) == 0:
                raise Exception("Failed to extract audio: output file is empty or missing")
            
            audio_size = os.path.getsize(temp_audio_path)
            logger.info(f"Audio extracted successfully, size: {audio_size} bytes")
            
            return temp_audio_path
            
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"FFmpeg error: {error_message}")
            raise Exception(f"Failed to extract audio with ffmpeg: {error_message}")

    def _upload_to_oss(self, audio_path: str, audio_prefix: str) -> str:
        """
        upload audio file to oss
        
        Args:
            audio_path: local audio file path
            audio_prefix: audio file prefix in oss
            
        Returns:
            str: audio file url in oss
        """
        # generate unique file name
        unique_id = str(uuid.uuid4())
        oss_key = f"{audio_prefix}/{unique_id}.wav"
        
        logger.info(f"Uploading audio to OSS: {oss_key}")
        
        try:
            # upload file to oss
            result = self.bucket.put_object_from_file(oss_key, audio_path)
            
            if result.status != 200:
                raise Exception(f"Failed to upload to OSS, status: {result.status}")
            
            # build audio url
            audio_url = f"https://{self.bucket.bucket_name}.{self.bucket.endpoint.replace('https://', '')}/{oss_key}"
            logger.info(f"Audio uploaded successfully: {audio_url}")
            
            return audio_url
            
        except oss2.exceptions.OssError as e:
            logger.error(f"OSS upload error: {str(e)}")
            raise Exception(f"Failed to upload to OSS: {str(e)}")

    def _cleanup_temp_files(self, *file_paths):
        """
        clean up temp files
        
        Args:
            *file_paths: file paths to delete
        """
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                    logger.info(f"Cleaned up temp file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp file {file_path}: {str(e)}")

    def get_audio_info(self, audio_url: str) -> dict:
        """
        get audio file info
        
        Args:
            audio_url: audio url
            
        Returns:
            dict: audio info including duration, format, etc.
        """
        try:
            probe = ffmpeg.probe(audio_url)
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
            
            if not audio_stream:
                raise Exception("No audio stream found")
            
            return {
                'duration': float(audio_stream.get('duration', 0)),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': int(audio_stream.get('channels', 0)),
                'codec': audio_stream.get('codec_name', ''),
                'bit_rate': int(audio_stream.get('bit_rate', 0)) if audio_stream.get('bit_rate') else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get audio info: {str(e)}")
            return {}


# convenient function
def extract_audio(video_url: str, oss_config: dict, audio_prefix: str = "audio") -> str:
    """
    convenient function: extract audio from video url and upload to oss
    
    Args:
        video_url: video url
        oss_config: oss config dict, including access_key_id, access_key_secret, endpoint, bucket_name
        audio_prefix: audio file prefix
        
    Returns:
        str: audio url
    """
    extractor = AudioExtractor(
        oss_access_key_id=oss_config['access_key_id'],
        oss_access_key_secret=oss_config['access_key_secret'],
        oss_endpoint=oss_config['endpoint'],
        oss_bucket_name=oss_config['bucket_name']
    )
    
    return extractor.extract_audio(video_url, audio_prefix)


# example usage
if __name__ == "__main__":
    # oss config example
    oss_config = {
        'access_key_id': 'your_access_key_id',
        'access_key_secret': 'your_access_key_secret',
        'endpoint': 'https://oss-cn-hangzhou.aliyuncs.com',
        'bucket_name': 'your_bucket_name'
    }
    
    # video url example
    video_url = "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250107/lbcemt/new+video.mp4"
    
    try:
        # extract audio and upload to oss
        audio_url = extract_audio(video_url, oss_config, "extracted_audio")
        print(f"audio extracted successfully! audio url: {audio_url}")
        
        # get audio info
        extractor = AudioExtractor(**oss_config)
        audio_info = extractor.get_audio_info(audio_url)
        print(f"audio info: {audio_info}")
        
    except Exception as e:
        print(f"audio extraction failed: {str(e)}") 