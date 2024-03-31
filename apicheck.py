import requests
import json
def checksoil(lat,long):
# Define the URL
    url = "https://soil.narc.gov.np/soil/api/soildata"

    params = {
        "lat": lat,
        "lon": long
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return json.dumps("Hey, Can't get you the soil information right now. There is some issues in the server.")

if __name__=="__main__":
    print(checksoil("abc","142"))