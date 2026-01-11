"""
YouTube Data API Tool for Research Hub.

Provides video and channel research capabilities using YouTube Data API v3.
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..config import YOUTUBE_API_KEY


class YouTubeTool:
    """
    YouTube Data API tool for video and channel research.

    Capabilities:
    - Search videos by query
    - Get video details and statistics
    - Get channel information
    - Analyze video metadata for patterns
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or YOUTUBE_API_KEY
        self._youtube = None

    @property
    def is_configured(self) -> bool:
        """Check if YouTube API is configured."""
        return bool(self.api_key)

    def _get_client(self):
        """Get or create YouTube API client."""
        if self._youtube is None and self.is_configured:
            try:
                from googleapiclient.discovery import build
                self._youtube = build('youtube', 'v3', developerKey=self.api_key)
            except ImportError:
                raise ImportError("google-api-python-client is required for YouTube tool")
        return self._youtube

    def search_videos(
        self,
        query: str,
        max_results: int = 10,
        order: str = "relevance",
        video_type: str = None,
        published_after: str = None,
        region_code: str = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for videos matching query.

        Args:
            query: Search query
            max_results: Maximum results to return (max 50)
            order: Sort order (relevance, date, rating, viewCount)
            video_type: Filter by type (episode, movie)
            published_after: Filter by publish date (ISO 8601)
            region_code: Filter by region (e.g., "US")

        Returns:
            List of video metadata
        """
        if not self.is_configured:
            return []

        youtube = self._get_client()
        if not youtube:
            return []

        try:
            request_params = {
                "q": query,
                "part": "snippet",
                "type": "video",
                "maxResults": min(max_results, 50),
                "order": order,
            }

            if video_type:
                request_params["videoType"] = video_type
            if published_after:
                request_params["publishedAfter"] = published_after
            if region_code:
                request_params["regionCode"] = region_code

            request = youtube.search().list(**request_params)
            response = request.execute()

            videos = []
            for item in response.get('items', []):
                videos.append({
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel_id': item['snippet']['channelId'],
                    'channel_title': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail_url': item['snippet']['thumbnails'].get('high', {}).get('url', ''),
                })

            return videos

        except Exception as e:
            return [{"error": str(e)}]

    def get_video_details(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed information for videos.

        Args:
            video_ids: List of video IDs (max 50)

        Returns:
            List of video details with statistics
        """
        if not self.is_configured or not video_ids:
            return []

        youtube = self._get_client()
        if not youtube:
            return []

        try:
            # Limit to 50 videos per request
            video_ids = video_ids[:50]

            request = youtube.videos().list(
                id=','.join(video_ids),
                part='snippet,statistics,contentDetails',
            )
            response = request.execute()

            details = []
            for item in response.get('items', []):
                stats = item.get('statistics', {})
                snippet = item.get('snippet', {})
                content = item.get('contentDetails', {})

                details.append({
                    'video_id': item['id'],
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'duration': content.get('duration', ''),
                    'view_count': int(stats.get('viewCount', 0)),
                    'like_count': int(stats.get('likeCount', 0)),
                    'comment_count': int(stats.get('commentCount', 0)),
                    'tags': snippet.get('tags', []),
                    'category_id': snippet.get('categoryId', ''),
                    'published_at': snippet.get('publishedAt', ''),
                    'channel_id': snippet.get('channelId', ''),
                    'channel_title': snippet.get('channelTitle', ''),
                    'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                    'definition': content.get('definition', ''),
                })

            return details

        except Exception as e:
            return [{"error": str(e)}]

    def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """
        Get channel information.

        Args:
            channel_id: YouTube channel ID

        Returns:
            Channel information and statistics
        """
        if not self.is_configured or not channel_id:
            return {}

        youtube = self._get_client()
        if not youtube:
            return {}

        try:
            request = youtube.channels().list(
                id=channel_id,
                part='snippet,statistics,brandingSettings,contentDetails',
            )
            response = request.execute()

            if not response.get('items'):
                return {}

            item = response['items'][0]
            stats = item.get('statistics', {})
            snippet = item.get('snippet', {})
            branding = item.get('brandingSettings', {}).get('channel', {})

            return {
                'channel_id': item['id'],
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'custom_url': snippet.get('customUrl', ''),
                'country': snippet.get('country', ''),
                'published_at': snippet.get('publishedAt', ''),
                'subscriber_count': int(stats.get('subscriberCount', 0)),
                'video_count': int(stats.get('videoCount', 0)),
                'view_count': int(stats.get('viewCount', 0)),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'keywords': branding.get('keywords', ''),
            }

        except Exception as e:
            return {"error": str(e)}

    def get_channel_videos(
        self,
        channel_id: str,
        max_results: int = 10,
        order: str = "date",
    ) -> List[Dict[str, Any]]:
        """
        Get recent videos from a channel.

        Args:
            channel_id: YouTube channel ID
            max_results: Maximum videos to return
            order: Sort order (date, rating, viewCount)

        Returns:
            List of video metadata
        """
        if not self.is_configured or not channel_id:
            return []

        youtube = self._get_client()
        if not youtube:
            return []

        try:
            request = youtube.search().list(
                channelId=channel_id,
                part='snippet',
                type='video',
                maxResults=min(max_results, 50),
                order=order,
            )
            response = request.execute()

            videos = []
            for item in response.get('items', []):
                videos.append({
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail_url': item['snippet']['thumbnails'].get('high', {}).get('url', ''),
                })

            return videos

        except Exception as e:
            return [{"error": str(e)}]

    def analyze_video_trends(
        self,
        query: str,
        max_videos: int = 20,
    ) -> Dict[str, Any]:
        """
        Analyze video trends for a topic.

        Args:
            query: Topic to analyze
            max_videos: Number of videos to analyze

        Returns:
            Trend analysis with patterns
        """
        # Search for videos
        videos = self.search_videos(query, max_results=max_videos, order="viewCount")
        if not videos or (len(videos) == 1 and "error" in videos[0]):
            return {"error": "Failed to fetch videos", "query": query}

        # Get detailed stats
        video_ids = [v['video_id'] for v in videos if 'video_id' in v]
        details = self.get_video_details(video_ids)

        # Analyze patterns
        total_views = 0
        total_likes = 0
        total_comments = 0
        all_tags = []
        durations = []
        titles = []

        for video in details:
            if "error" not in video:
                total_views += video.get('view_count', 0)
                total_likes += video.get('like_count', 0)
                total_comments += video.get('comment_count', 0)
                all_tags.extend(video.get('tags', []))
                titles.append(video.get('title', ''))

        # Count tag frequency
        tag_counts = {}
        for tag in all_tags:
            tag_lower = tag.lower()
            tag_counts[tag_lower] = tag_counts.get(tag_lower, 0) + 1

        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20]

        video_count = len([d for d in details if "error" not in d])

        return {
            "query": query,
            "videos_analyzed": video_count,
            "total_views": total_views,
            "average_views": total_views // video_count if video_count > 0 else 0,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "engagement_rate": (total_likes + total_comments) / total_views if total_views > 0 else 0,
            "top_tags": [{"tag": t[0], "count": t[1]} for t in top_tags],
            "sample_titles": titles[:10],
            "analyzed_at": datetime.utcnow().isoformat(),
        }

    def extract_video_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats.

        Args:
            url: YouTube video URL

        Returns:
            Video ID or None
        """
        import re

        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None


# Factory function
def create_youtube_tool(api_key: str = None) -> YouTubeTool:
    """Create a YouTube tool instance."""
    return YouTubeTool(api_key=api_key)
