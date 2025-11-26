"""
IP Geolocation Utility
Converts IP addresses to geographic locations using free API services
"""
import httpx
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

async def get_location_from_ip(ip_address: str) -> str:
    """
    Get geographic location from IP address using ip-api.com (free, no API key needed)
    
    Args:
        ip_address: The IP address to geolocate
        
    Returns:
        Location string in format "City, State/Region, Country" or "Unknown" if lookup fails
        
    Examples:
        >>> await get_location_from_ip("8.8.8.8")
        "Mountain View, California, United States"
        
        >>> await get_location_from_ip("192.168.1.1")  # Private IP
        "Unknown"
    """
    # Handle private/local IPs
    if ip_address in ["127.0.0.1", "localhost", "0.0.0.0"] or ip_address.startswith("192.168.") or ip_address.startswith("10."):
        return "Local Network"
    
    try:
        # Use ip-api.com (free, 45 requests/minute limit)
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"http://ip-api.com/json/{ip_address}",
                params={"fields": "status,country,regionName,city"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    city = data.get("city", "")
                    region = data.get("regionName", "")
                    country = data.get("country", "")
                    
                    # Build location string
                    location_parts = []
                    if city:
                        location_parts.append(city)
                    if region and region != city:
                        location_parts.append(region)
                    if country:
                        location_parts.append(country)
                    
                    return ", ".join(location_parts) if location_parts else "Unknown"
                else:
                    logger.warning(f"IP geolocation failed for {ip_address}: {data.get('message', 'Unknown error')}")
                    return "Unknown"
            else:
                logger.warning(f"IP geolocation API returned status {response.status_code}")
                return "Unknown"
                
    except httpx.TimeoutException:
        logger.warning(f"Timeout while geolocating IP {ip_address}")
        return "Unknown"
    except Exception as e:
        logger.error(f"Error geolocating IP {ip_address}: {str(e)}")
        return "Unknown"


def parse_user_agent(user_agent: str) -> str:
    """
    Parse User-Agent string to extract device/browser information
    
    Args:
        user_agent: Raw User-Agent header string
        
    Returns:
        Simplified device/browser string
        
    Examples:
        >>> parse_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0")
        "Chrome on Windows 10"
        
        >>> parse_user_agent("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)")
        "Safari on iPhone iOS 17"
    """
    if not user_agent:
        return "Unknown Device"
    
    # Detect mobile devices
    if "iPhone" in user_agent:
        device = "iPhone"
        if "OS " in user_agent:
            try:
                ios_version = user_agent.split("OS ")[1].split(" ")[0].replace("_", ".")
                device = f"iPhone iOS {ios_version}"
            except:
                pass
    elif "iPad" in user_agent:
        device = "iPad"
    elif "Android" in user_agent:
        device = "Android"
        if "Android " in user_agent:
            try:
                android_version = user_agent.split("Android ")[1].split(";")[0]
                device = f"Android {android_version}"
            except:
                pass
    else:
        # Desktop OS
        if "Windows NT 10" in user_agent:
            device = "Windows 10"
        elif "Windows NT 11" in user_agent:
            device = "Windows 11"
        elif "Mac OS X" in user_agent:
            device = "macOS"
        elif "Linux" in user_agent:
            device = "Linux"
        else:
            device = "Unknown OS"
    
    # Detect browser
    if "Edg/" in user_agent or "Edge/" in user_agent:
        browser = "Edge"
    elif "Chrome/" in user_agent and "Edg/" not in user_agent:
        browser = "Chrome"
    elif "Firefox/" in user_agent:
        browser = "Firefox"
    elif "Safari/" in user_agent and "Chrome/" not in user_agent:
        browser = "Safari"
    elif "Opera" in user_agent or "OPR/" in user_agent:
        browser = "Opera"
    else:
        browser = "Unknown Browser"
    
    return f"{browser} on {device}"


def is_foreign_location(location: str) -> bool:
    """
    Check if location is outside the United States (for fraud detection)
    
    Args:
        location: Location string (e.g., "London, UK" or "New York, NY, United States")
        
    Returns:
        True if location is outside USA, False otherwise
    """
    if not location or location == "Unknown" or location == "Local Network":
        return False
    
    # List of countries/indicators that suggest foreign transaction
    foreign_indicators = [
        "UK", "United Kingdom", "London", "Dubai", "UAE", "Singapore",
        "Mexico", "Canada", "Germany", "France", "Italy", "Spain",
        "China", "Japan", "India", "Brazil", "Russia", "Australia"
    ]
    
    return any(indicator in location for indicator in foreign_indicators)
