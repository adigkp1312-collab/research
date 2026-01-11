"""
Meta Ads Library Tool for Research Hub.

Provides access to Facebook/Instagram ad data via Meta's Ad Library API.
"""

import os
import requests
import time
from typing import Dict, Any, Optional, List, Iterator
from datetime import datetime, timedelta
from urllib.parse import urlencode

from ..config import META_ACCESS_TOKEN, META_APP_ID, META_APP_SECRET


class MetaAdsLibraryTool:
    """
    Meta Ad Library API tool for researching competitor ads.

    Capabilities:
    - Search ads by keyword, page, or advertiser
    - Filter by country, platform, active status
    - Get ad creatives, spend ranges, impressions
    - Analyze competitor ad strategies

    Note: Full access requires ads in EU or political/social issue ads.
    For commercial ads outside EU, data may be limited.
    """

    BASE_URL = "https://graph.facebook.com"
    API_VERSION = "v21.0"

    def __init__(
        self,
        access_token: str = None,
        app_id: str = None,
        app_secret: str = None,
    ):
        self.access_token = access_token or META_ACCESS_TOKEN
        self.app_id = app_id or META_APP_ID
        self.app_secret = app_secret or META_APP_SECRET
        self._token_expiry: Optional[datetime] = None

    @property
    def is_configured(self) -> bool:
        """Check if Meta API is configured."""
        return bool(self.access_token) or bool(self.app_id and self.app_secret)

    @property
    def api_url(self) -> str:
        """Get the base API URL with version."""
        return f"{self.BASE_URL}/{self.API_VERSION}"

    def _get_access_token(self) -> str:
        """Get or refresh access token."""
        if self.access_token:
            return self.access_token

        if self.app_id and self.app_secret:
            # Get app access token (limited permissions)
            url = f"{self.BASE_URL}/oauth/access_token"
            params = {
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "grant_type": "client_credentials",
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                return self.access_token

        raise Exception("No valid access token available")

    def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Make a request to the Meta Graph API."""
        token = self._get_access_token()
        params["access_token"] = token

        url = f"{self.api_url}/{endpoint}"

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_data = {}
            try:
                error_data = e.response.json()
            except:
                pass
            return {"error": str(e), "details": error_data}
        except Exception as e:
            return {"error": str(e)}

    def search_ads(
        self,
        search_terms: str = None,
        page_ids: List[str] = None,
        countries: List[str] = None,
        ad_active_status: str = "ALL",
        ad_type: str = "ALL",
        publisher_platforms: List[str] = None,
        limit: int = 25,
        fields: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Search the Meta Ad Library.

        Args:
            search_terms: Keywords to search for in ads
            page_ids: List of Facebook Page IDs to search
            countries: List of country codes (e.g., ['US', 'GB'])
            ad_active_status: 'ACTIVE', 'INACTIVE', or 'ALL'
            ad_type: 'POLITICAL_AND_ISSUE_ADS', 'ALL', etc.
            publisher_platforms: ['facebook', 'instagram', 'messenger']
            limit: Max results per page (max 25)
            fields: Specific fields to retrieve

        Returns:
            Dict with ad data and pagination info
        """
        if not self.is_configured:
            return {"error": "Meta API not configured", "data": []}

        # Default fields
        if fields is None:
            fields = [
                "id",
                "page_id",
                "page_name",
                "ad_snapshot_url",
                "ad_creative_bodies",
                "ad_creative_link_captions",
                "ad_creative_link_titles",
                "ad_delivery_start_time",
                "ad_delivery_stop_time",
                "currency",
                "spend",
                "impressions",
                "publisher_platforms",
                "languages",
                "target_locations",
                "target_ages",
                "target_gender",
                "bylines",
            ]

        params = {
            "ad_reached_countries": countries or ["US"],
            "ad_active_status": ad_active_status,
            "ad_type": ad_type,
            "fields": ",".join(fields),
            "limit": min(limit, 25),  # API max is 25
        }

        if search_terms:
            params["search_terms"] = search_terms

        if page_ids:
            params["search_page_ids"] = ",".join(page_ids)

        if publisher_platforms:
            params["publisher_platforms"] = publisher_platforms

        result = self._make_request("ads_archive", params)

        # Format the response
        if "error" in result:
            return result

        ads = result.get("data", [])
        paging = result.get("paging", {})

        return {
            "ads": ads,
            "count": len(ads),
            "has_more": "next" in paging,
            "next_cursor": paging.get("cursors", {}).get("after"),
            "searched_at": datetime.utcnow().isoformat(),
        }

    def search_ads_paginated(
        self,
        search_terms: str = None,
        page_ids: List[str] = None,
        countries: List[str] = None,
        ad_active_status: str = "ALL",
        ad_type: str = "ALL",
        publisher_platforms: List[str] = None,
        fields: List[str] = None,
        max_ads: int = 100,
        delay_between_requests: float = 0.5,
    ) -> Iterator[Dict[str, Any]]:
        """
        Generator that yields ads with automatic pagination.

        Args:
            search_terms: Keywords to search for in ads
            page_ids: List of Facebook Page IDs to search
            countries: List of country codes
            ad_active_status: 'ACTIVE', 'INACTIVE', or 'ALL'
            ad_type: 'POLITICAL_AND_ISSUE_ADS', 'ALL', etc.
            publisher_platforms: ['facebook', 'instagram', 'messenger']
            fields: Specific fields to retrieve
            max_ads: Maximum total ads to fetch (default 100)
            delay_between_requests: Seconds to wait between API calls (rate limiting)

        Yields:
            Individual ad dictionaries
        """
        if not self.is_configured:
            return

        ads_fetched = 0
        next_cursor = None

        while ads_fetched < max_ads:
            # Calculate how many to request (max 25 per API call)
            remaining = max_ads - ads_fetched
            limit = min(25, remaining)

            result = self._fetch_ads_page(
                search_terms=search_terms,
                page_ids=page_ids,
                countries=countries,
                ad_active_status=ad_active_status,
                ad_type=ad_type,
                publisher_platforms=publisher_platforms,
                fields=fields,
                limit=limit,
                after_cursor=next_cursor,
            )

            if "error" in result:
                break

            ads = result.get("ads", [])
            if not ads:
                break

            for ad in ads:
                yield ad
                ads_fetched += 1
                if ads_fetched >= max_ads:
                    break

            # Check for more pages
            if not result.get("has_more"):
                break

            next_cursor = result.get("next_cursor")
            if not next_cursor:
                break

            # Rate limiting delay
            if delay_between_requests > 0:
                time.sleep(delay_between_requests)

    def _fetch_ads_page(
        self,
        search_terms: str = None,
        page_ids: List[str] = None,
        countries: List[str] = None,
        ad_active_status: str = "ALL",
        ad_type: str = "ALL",
        publisher_platforms: List[str] = None,
        fields: List[str] = None,
        limit: int = 25,
        after_cursor: str = None,
    ) -> Dict[str, Any]:
        """Fetch a single page of ads (internal helper)."""
        if fields is None:
            fields = [
                "id", "page_id", "page_name", "ad_snapshot_url",
                "ad_creative_bodies", "ad_creative_link_captions",
                "ad_creative_link_titles", "ad_delivery_start_time",
                "ad_delivery_stop_time", "currency", "spend", "impressions",
                "publisher_platforms", "languages", "target_locations",
                "target_ages", "target_gender", "bylines",
            ]

        params = {
            "ad_reached_countries": countries or ["US"],
            "ad_active_status": ad_active_status,
            "ad_type": ad_type,
            "fields": ",".join(fields),
            "limit": min(limit, 25),
        }

        if search_terms:
            params["search_terms"] = search_terms
        if page_ids:
            params["search_page_ids"] = ",".join(page_ids)
        if publisher_platforms:
            params["publisher_platforms"] = publisher_platforms
        if after_cursor:
            params["after"] = after_cursor

        result = self._make_request("ads_archive", params)

        if "error" in result:
            return result

        ads = result.get("data", [])
        paging = result.get("paging", {})

        return {
            "ads": ads,
            "count": len(ads),
            "has_more": "next" in paging,
            "next_cursor": paging.get("cursors", {}).get("after"),
        }

    def search_ads_all(
        self,
        search_terms: str = None,
        page_ids: List[str] = None,
        countries: List[str] = None,
        ad_active_status: str = "ALL",
        ad_type: str = "ALL",
        publisher_platforms: List[str] = None,
        fields: List[str] = None,
        max_ads: int = 100,
        delay_between_requests: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Fetch all ads with automatic pagination (up to max_ads).

        This method handles the 25 ads per request limitation by
        automatically fetching multiple pages.

        Args:
            search_terms: Keywords to search for in ads
            page_ids: List of Facebook Page IDs to search
            countries: List of country codes
            ad_active_status: 'ACTIVE', 'INACTIVE', or 'ALL'
            ad_type: 'POLITICAL_AND_ISSUE_ADS', 'ALL', etc.
            publisher_platforms: ['facebook', 'instagram', 'messenger']
            fields: Specific fields to retrieve
            max_ads: Maximum total ads to fetch (default 100, max 500)
            delay_between_requests: Seconds between API calls (default 0.5)

        Returns:
            Dict with all ads and metadata
        """
        if not self.is_configured:
            return {"error": "Meta API not configured", "data": []}

        # Cap max_ads at 500 to prevent excessive API calls
        max_ads = min(max_ads, 500)

        all_ads = list(self.search_ads_paginated(
            search_terms=search_terms,
            page_ids=page_ids,
            countries=countries,
            ad_active_status=ad_active_status,
            ad_type=ad_type,
            publisher_platforms=publisher_platforms,
            fields=fields,
            max_ads=max_ads,
            delay_between_requests=delay_between_requests,
        ))

        return {
            "ads": all_ads,
            "count": len(all_ads),
            "max_requested": max_ads,
            "searched_at": datetime.utcnow().isoformat(),
        }

    def get_page_ads(
        self,
        page_id: str,
        countries: List[str] = None,
        active_only: bool = True,
        limit: int = 25,
    ) -> Dict[str, Any]:
        """
        Get all ads for a specific Facebook Page.

        Args:
            page_id: Facebook Page ID
            countries: Country filter
            active_only: Only return active ads
            limit: Max results

        Returns:
            Dict with page's ads
        """
        return self.search_ads(
            page_ids=[page_id],
            countries=countries,
            ad_active_status="ACTIVE" if active_only else "ALL",
            limit=limit,
        )

    def search_competitor_ads(
        self,
        competitor_name: str,
        countries: List[str] = None,
        platforms: List[str] = None,
        max_ads: int = 100,
    ) -> Dict[str, Any]:
        """
        Search for a competitor's ads by name with automatic pagination.

        Args:
            competitor_name: Name of the competitor/brand
            countries: Countries to search in
            platforms: Platforms to filter
            max_ads: Maximum ads to fetch (default 100)

        Returns:
            Competitor ad data
        """
        result = self.search_ads_all(
            search_terms=competitor_name,
            countries=countries or ["US"],
            publisher_platforms=platforms,
            ad_active_status="ALL",
            max_ads=max_ads,
        )

        if "error" in result:
            return result

        # Analyze the ads
        ads = result.get("ads", [])

        analysis = {
            "competitor": competitor_name,
            "total_ads_found": len(ads),
            "active_ads": sum(1 for ad in ads if not ad.get("ad_delivery_stop_time")),
            "platforms": {},
            "ad_samples": [],
            "messaging_themes": [],
            "searched_at": datetime.utcnow().isoformat(),
        }

        # Analyze platforms
        for ad in ads:
            platforms = ad.get("publisher_platforms", [])
            for platform in platforms:
                analysis["platforms"][platform] = analysis["platforms"].get(platform, 0) + 1

        # Get sample ads with creatives
        for ad in ads[:10]:
            sample = {
                "page_name": ad.get("page_name"),
                "snapshot_url": ad.get("ad_snapshot_url"),
                "bodies": ad.get("ad_creative_bodies", []),
                "titles": ad.get("ad_creative_link_titles", []),
                "start_date": ad.get("ad_delivery_start_time"),
                "spend": ad.get("spend"),
                "impressions": ad.get("impressions"),
            }
            analysis["ad_samples"].append(sample)

            # Extract messaging themes from bodies
            for body in ad.get("ad_creative_bodies", []):
                if body and len(body) > 20:
                    analysis["messaging_themes"].append(body[:200])

        return analysis

    def analyze_ad_creative(
        self,
        search_terms: str,
        countries: List[str] = None,
        max_ads: int = 100,
    ) -> Dict[str, Any]:
        """
        Analyze ad creative patterns for a topic/brand with automatic pagination.

        Args:
            search_terms: Topic or brand to analyze
            countries: Countries to analyze
            max_ads: Maximum ads to analyze (default 100)

        Returns:
            Creative analysis insights
        """
        result = self.search_ads_all(
            search_terms=search_terms,
            countries=countries or ["US"],
            max_ads=max_ads,
        )

        if "error" in result:
            return result

        ads = result.get("ads", [])

        analysis = {
            "query": search_terms,
            "ads_analyzed": len(ads),
            "creative_patterns": {
                "headline_styles": [],
                "body_copy_themes": [],
                "cta_patterns": [],
                "link_captions": [],
            },
            "targeting_insights": {
                "age_ranges": {},
                "genders": {},
                "locations": [],
            },
            "platform_distribution": {},
            "ad_examples": [],
        }

        for ad in ads:
            # Analyze headlines
            for title in ad.get("ad_creative_link_titles", []):
                if title:
                    analysis["creative_patterns"]["headline_styles"].append(title)

            # Analyze body copy
            for body in ad.get("ad_creative_bodies", []):
                if body:
                    analysis["creative_patterns"]["body_copy_themes"].append(body[:300])

            # Analyze link captions (often contain CTAs)
            for caption in ad.get("ad_creative_link_captions", []):
                if caption:
                    analysis["creative_patterns"]["cta_patterns"].append(caption)

            # Platform distribution
            for platform in ad.get("publisher_platforms", []):
                analysis["platform_distribution"][platform] = \
                    analysis["platform_distribution"].get(platform, 0) + 1

            # Targeting insights
            if ad.get("target_ages"):
                age_range = ad["target_ages"]
                key = f"{age_range.get('min', '?')}-{age_range.get('max', '?')}"
                analysis["targeting_insights"]["age_ranges"][key] = \
                    analysis["targeting_insights"]["age_ranges"].get(key, 0) + 1

            if ad.get("target_gender"):
                gender = ad["target_gender"]
                analysis["targeting_insights"]["genders"][gender] = \
                    analysis["targeting_insights"]["genders"].get(gender, 0) + 1

            # Add example
            if len(analysis["ad_examples"]) < 5:
                analysis["ad_examples"].append({
                    "page_name": ad.get("page_name"),
                    "snapshot_url": ad.get("ad_snapshot_url"),
                    "headline": (ad.get("ad_creative_link_titles") or [None])[0],
                    "body": (ad.get("ad_creative_bodies") or [None])[0],
                })

        # Deduplicate themes
        analysis["creative_patterns"]["headline_styles"] = \
            list(set(analysis["creative_patterns"]["headline_styles"]))[:20]
        analysis["creative_patterns"]["body_copy_themes"] = \
            list(set(analysis["creative_patterns"]["body_copy_themes"]))[:10]
        analysis["creative_patterns"]["cta_patterns"] = \
            list(set(analysis["creative_patterns"]["cta_patterns"]))[:10]

        return analysis

    def get_ad_spend_insights(
        self,
        page_ids: List[str] = None,
        search_terms: str = None,
        countries: List[str] = None,
        max_ads: int = 100,
    ) -> Dict[str, Any]:
        """
        Get ad spend insights for pages or search terms with automatic pagination.

        Note: Spend data is only available for political/issue ads
        or ads in regions with transparency requirements.

        Args:
            page_ids: Specific page IDs to analyze
            search_terms: Or search by terms
            countries: Countries to analyze
            max_ads: Maximum ads to analyze (default 100)

        Returns:
            Spend analysis
        """
        result = self.search_ads_all(
            page_ids=page_ids,
            search_terms=search_terms,
            countries=countries or ["US"],
            fields=[
                "page_name",
                "spend",
                "impressions",
                "currency",
                "ad_delivery_start_time",
                "ad_delivery_stop_time",
            ],
            max_ads=max_ads,
        )

        if "error" in result:
            return result

        ads = result.get("ads", [])

        # Analyze spend
        spend_data = {
            "ads_with_spend_data": 0,
            "total_min_spend": 0,
            "total_max_spend": 0,
            "currency": None,
            "by_page": {},
            "active_campaigns": 0,
        }

        for ad in ads:
            spend = ad.get("spend")
            if spend:
                spend_data["ads_with_spend_data"] += 1
                spend_data["currency"] = spend.get("currency")

                lower = spend.get("lower_bound", 0)
                upper = spend.get("upper_bound", 0)

                spend_data["total_min_spend"] += int(lower) if lower else 0
                spend_data["total_max_spend"] += int(upper) if upper else 0

                page = ad.get("page_name", "Unknown")
                if page not in spend_data["by_page"]:
                    spend_data["by_page"][page] = {"min": 0, "max": 0, "ad_count": 0}

                spend_data["by_page"][page]["min"] += int(lower) if lower else 0
                spend_data["by_page"][page]["max"] += int(upper) if upper else 0
                spend_data["by_page"][page]["ad_count"] += 1

            if not ad.get("ad_delivery_stop_time"):
                spend_data["active_campaigns"] += 1

        return spend_data


# Factory function
def create_meta_ads_tool(
    access_token: str = None,
    app_id: str = None,
    app_secret: str = None,
) -> MetaAdsLibraryTool:
    """Create a Meta Ads Library tool instance."""
    return MetaAdsLibraryTool(
        access_token=access_token,
        app_id=app_id,
        app_secret=app_secret,
    )
