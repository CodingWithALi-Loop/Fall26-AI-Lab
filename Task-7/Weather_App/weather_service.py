"""
Weather Service Module
Handles all API interactions with OpenWeatherMap API
"""

import requests
from typing import Dict, Optional, Tuple
from datetime import datetime


class WeatherService:
    """Service class for fetching weather data from OpenWeatherMap API"""
    
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    
    def __init__(self, api_key: str):
        """
        Initialize WeatherService with API key
        
        Args:
            api_key (str): OpenWeatherMap API key
        """
        self.api_key = api_key
        self.timeout = 10
    
    def get_weather(self, city: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Fetch weather data for a given city
        
        Args:
            city (str): City name
            
        Returns:
            Tuple[bool, Optional[Dict], Optional[str]]: 
                (success, weather_data, error_message)
        """
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, response.json(), None
            elif response.status_code == 404:
                return False, None, f"City '{city}' not found. Please check the spelling."
            elif response.status_code == 401:
                return False, None, "Invalid API key. Please check your OpenWeatherMap API key."
            else:
                return False, None, f"API Error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, None, "Request timeout. Please check your internet connection."
        except requests.exceptions.ConnectionError:
            return False, None, "Connection error. Please check your internet connection."
        except Exception as e:
            return False, None, f"Unexpected error: {str(e)}"
    
    @staticmethod
    def get_weather_condition(description: str) -> str:
        """
        Classify weather condition for styling
        
        Args:
            description (str): Weather description from API
            
        Returns:
            str: Weather category (clear, clouds, rain, snow, thunderstorm, etc.)
        """
        description = description.lower()
        
        if "clear" in description or "sunny" in description:
            return "clear"
        elif "cloud" in description:
            return "clouds"
        elif "rain" in description or "drizzle" in description:
            return "rain"
        elif "snow" in description:
            return "snow"
        elif "thunder" in description or "storm" in description:
            return "thunderstorm"
        elif "mist" in description or "fog" in description:
            return "mist"
        else:
            return "default"
    
    @staticmethod
    def format_weather_data(data: Dict) -> Dict:
        """
        Format raw API data into a clean structure
        
        Args:
            data (Dict): Raw weather data from API
            
        Returns:
            Dict: Formatted weather data
        """
        return {
            "city": data["name"],
            "country": data["sys"].get("country", ""),
            "temperature": round(data["main"]["temp"]),
            "temperature_float": data["main"]["temp"],
            "feels_like": round(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "description": data["weather"][0]["description"].capitalize(),
            "main": data["weather"][0]["main"],
            "wind_speed": round(data["wind"]["speed"], 1),
            "cloudiness": data["clouds"]["all"],
            "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]),
            "sunset": datetime.fromtimestamp(data["sys"]["sunset"]),
            "condition": WeatherService.get_weather_condition(
                data["weather"][0]["description"]
            ),
            "icon": data["weather"][0]["icon"]
        }
