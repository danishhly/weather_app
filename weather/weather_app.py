import datetime
import os
import sys
from http.client import responses

import requests
from dotenv import load_dotenv
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel,
                             QLineEdit, QPushButton, QVBoxLayout)
from PyQt5.QtCore import Qt

# Load environment variables from .env
load_dotenv()

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.city_label = QLabel("Enter the City: ", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Weather App")

        vbox = QVBoxLayout()

        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)

        self.setLayout(vbox)

        self.setFixedSize(800, 600)
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")

        self.setStyleSheet("""
            QWidget {
                background-color: #f0f4f8;
                font-family: Calibri, sans-serif;
            }

            QLabel#city_label {
                font-size: 36px;
                font-style: italic;
                color: #333;
                margin-bottom: 10px;
            }

            QLineEdit#city_input {
                font-size: 24px;
                padding: 10px;
                border: 2px solid #ccc;
                border-radius: 12px;
                background-color: #fff;
                margin-bottom: 20px;
                qproperty-alignment: AlignCenter;
            }

            QPushButton#get_weather_button {
                font-size: 20px;
                font-weight: bold;
                padding: 12px 24px;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 10px;
            }

            QPushButton#get_weather_button:hover {
                background-color: #357ABD;
            }

            QLabel#temperature_label {
                font-size: 60px;
                color: #2c3e50;
                margin-top: 15px;
            }

            QLabel#emoji_label {
                font-size: 90px;
                font-family: "Segoe UI Emoji";
                margin-top: 10px;
            }

            QLabel#description_label {
                font-size: 28px;
                color: #555;
                margin-top: 10px;
                font-style: italic;
            }
        """)

        self.get_weather_button.clicked.connect(self.fetch_weather)

    def fetch_weather(self):
        api_key = os.getenv("OPENWEATHER_API_KEY")
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data["cod"] == 200:
                current_time = datetime.datetime.utcnow().timestamp()
                self.display_weather(data, current_time)

        except requests.exceptions.HTTPError as http_error:
            match response.status_code:
                case 400:
                    self.display_error("Bad request:\nPlease check your input")
                case 401:
                    self.display_error("Unauthorized:\nInvalid API key")
                case 403:
                    self.display_error("Forbidden:\nAccess is denied")
                case 404:
                    self.display_error("Not found:\nCity not found")
                case 500:
                    self.display_error("Internal server Error:\nPlease try again later")
                case 502:
                    self.display_error("Bad Gateway:\nInvalid response from the server")
                case 503:
                    self.display_error("Service Unavailable:\nServer is down")
                case 504:
                    self.display_error("Gateway timeout:\nNo response from the server")
                case _:
                    self.display_error(f"HTTP error occurred:\n{http_error}")

        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error:\nCheck your internet connection")
        except requests.exceptions.Timeout:
            self.display_error("Timeout error:\nThe request timed out")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many redirects:\nCheck the URL")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error:\n{req_error}")

    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px;")
        self.temperature_label.setText(message)
        self.emoji_label.clear()
        self.description_label.clear()

    def display_weather(self, data, current_time):
        self.temperature_label.setStyleSheet("font-size: 70px;")
        temperature_k = data["main"]["temp"]
        temperature_f = (temperature_k * 9 / 5) - 459.67
        weather_id = data["weather"][0]["id"]
        sunrise = data["sys"]["sunrise"]
        sunset = data["sys"]["sunset"]
        description = data["weather"][0]["description"]

        self.temperature_label.setText(f"{temperature_f:.0f}°F")
        self.emoji_label.setText(self.get_weather_emoji(weather_id, sunrise, sunset, current_time))
        self.description_label.setText(description)

    @staticmethod
    def get_weather_emoji(weather_id, sunrise, sunset, current_time):
        if 200 <= weather_id <= 232:
            return "⛈️"
        elif 300 <= weather_id <= 321:
            return "🌦️"
        elif 500 <= weather_id <= 504:
            return "🌧️"
        elif weather_id == 511:
            return "🌨️"
        elif 520 <= weather_id <= 531:
            return "🌦️"
        elif 600 <= weather_id <= 622:
            return "❄️"
        elif 701 <= weather_id <= 711:
            return "🌫️"
        elif weather_id == 721:
            return "🌁"
        elif 731 <= weather_id <= 741:
            return "🌬️"
        elif weather_id == 751:
            return "🏜️"
        elif weather_id == 761:
            return "🌪️"
        elif weather_id == 762:
            return "🌋"
        elif weather_id == 771:
            return "💨"
        elif weather_id == 781:
            return "🌪️"
        elif weather_id == 800:
            if sunrise < current_time < sunset:
                return "☀️"
            else:
                return "🌙"
        elif weather_id == 801:
            return "🌤️"
        elif weather_id == 802:
            return "⛅"
        elif weather_id == 803:
            return "🌥️"
        elif weather_id == 804:
            return "☁️"
        else:
            return "❓"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
