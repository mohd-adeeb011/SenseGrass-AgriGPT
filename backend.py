from flask import Flask, request, jsonify, render_template
import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
from flask_cors import CORS

app = Flask(__name__,static_url_path='/static')
CORS(app)
load_dotenv()

class WeatherAssistant:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.api_key = os.getenv("WEATHER_API_KEY")  
        self.chat_history = []

    def get_current_weather(self, location):
        """Get the current weather in a given location"""
        url = "https://ai-weather-by-meteosource.p.rapidapi.com/find_places"
        querystring = {"text": location}
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "ai-weather-by-meteosource.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        try:                
            place_output = response.json()[0]
            weather_url = "https://ai-weather-by-meteosource.p.rapidapi.com/current"
            weatherstring = {"place_id": place_output['place_id']}
            weather_response = requests.get(weather_url, headers=headers, params=weatherstring).json()
        except:
            return json.dumps("Sorry, Can't get you weather related data right now.")
        return weather_response

    def get_soil_information(self,lat, long):
        url = "https://soil.narc.gov.np/soil/api/soildata"

        params = {
            "lat": int(lat),
            "lon": int(long)
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            return json.dumps("Hey, Can't get you the soil information right now. There is some issues in the server.")
    def run_conversation(self, user_prompt,chat_history=None):
        if chat_history:
            self.chat_history = chat_history
        else:
            self.chat_history = []
        function_discriptions = [
            {
                "name": "get_current_weather",
                "description": "Give the weather parameters to user which they have asked. If they need report or detailed information then give them that as well.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state",
                        },
                    },
                    "required": ["location"],
                },
            },
                    {
        "name": "get_soil_information",
        "description": "Provides information about the soil at a given location specified by latitude and longitude. This can include details like soil type, composition, and suitability for various purposes.",
        "parameters": {
            "type": "object",
            "properties": {
            "lat": {
                "type": "number",
                "description": "The geographic latitude in decimal degrees (between -90 and 90)"
            },
            "long": {
                "type": "number",
                "description": "The geographic longitude in decimal degrees (between -180 and 180)"
            }
            },
            "required": ["lat", "long"]
        }
        }
        ]

        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0613",
            messages=[{"role": "user", "content": user_prompt}],
            functions=function_discriptions,
            function_call="auto",
        )
        response = completion.choices[0].message
        if response.function_call is not None:
            params = json.loads(response.function_call.arguments)
            chosen_function = getattr(self, response.function_call.name)
            weather_content = chosen_function(**params)
            second_completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": user_prompt},
                    {"role": "function", "name": response.function_call.name, "content": str(weather_content)},
                ],
                functions=function_discriptions,
            )
            response = second_completion.choices[0].message.content
            print(response)

            self.chat_history.append({"role": "user", "content": user_prompt})
            self.chat_history.append({"role": "assistant", "content": response})

            return response, self.chat_history
        else:
            return response.content, self.chat_history

@app.route("/weather", methods=["POST"])
def get_weather():
    data = request.get_json()
    user_prompt = data.get("user_prompt")
    chat_history = data.get("chat_history", [])
    weather_assistant = WeatherAssistant()
    response, updated_chat_history = weather_assistant.run_conversation(user_prompt, chat_history)
    return jsonify({"response": response, "chat_history": updated_chat_history})


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0')



