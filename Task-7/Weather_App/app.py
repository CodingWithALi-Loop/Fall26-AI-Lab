"""
Professional Weather Dashboard - Flask Application
Built with Flask for a modern, responsive web UI
"""

from flask import Flask, render_template, request, jsonify
from weather_service import WeatherService
import os

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize weather service
SERVICE = WeatherService("")

@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/api/weather', methods=['POST'])
def get_weather():
    """API endpoint to fetch weather data"""
    try:
        data = request.get_json()
        city = data.get('city', '').strip()
        api_key = data.get('api_key', '').strip()
        
        if not city:
            return jsonify({'success': False, 'error': 'Please enter a city name'}), 400
        
        if not api_key:
            return jsonify({'success': False, 'error': 'Please enter your API key'}), 400
        
        # Create service with provided API key
        service = WeatherService(api_key)
        success, weather_data, error = service.get_weather(city)
        
        if success:
            formatted_data = WeatherService.format_weather_data(weather_data)
            return jsonify({
                'success': True,
                'data': {
                    'city': formatted_data['city'],
                    'country': formatted_data['country'],
                    'temperature': formatted_data['temperature'],
                    'feels_like': formatted_data['feels_like'],
                    'description': formatted_data['description'],
                    'humidity': formatted_data['humidity'],
                    'wind_speed': formatted_data['wind_speed'],
                    'pressure': formatted_data['pressure'],
                    'cloudiness': formatted_data['cloudiness'],
                    'sunrise': formatted_data['sunrise'].strftime('%H:%M'),
                    'sunset': formatted_data['sunset'].strftime('%H:%M'),
                    'condition': formatted_data['condition'],
                    'icon': formatted_data['icon']
                }
            }), 200
        else:
            return jsonify({'success': False, 'error': error}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/theme/<condition>')
def get_theme(condition):
    """Get theme colors based on weather condition"""
    themes = {
        'clear': {
            'primary': '#87CEEB',
            'secondary': '#E0F6FF',
            'text': '#333'
        },
        'clouds': {
            'primary': '#B0C4DE',
            'secondary': '#E6E6FA',
            'text': '#333'
        },
        'rain': {
            'primary': '#4A5F7F',
            'secondary': '#2C3E50',
            'text': '#fff'
        },
        'snow': {
            'primary': '#F0F8FF',
            'secondary': '#FFFFFF',
            'text': '#333'
        },
        'thunderstorm': {
            'primary': '#2C2C54',
            'secondary': '#1A1A3A',
            'text': '#fff'
        },
        'mist': {
            'primary': '#A9A9A9',
            'secondary': '#D3D3D3',
            'text': '#333'
        }
    }
    
    theme = themes.get(condition, themes['clear'])
    return jsonify(theme), 200

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
