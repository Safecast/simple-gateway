import requests

url = "https://grafana.safecast.jp/post/:8000/measurements?api_key=q1LKu7RQyxunnDW"
headers = {"Content-Type": "application/json"}
data = {
    "bat_voltage": "3.7",
    "dev_temp": "25",
    "device": "2830364905",
    "device_sn": "65000",
    "device_urn": "urn:dev:12345",
    "env_temp": "30",
    "lnd_7128ec": "60",
    "lnd_7318c": "",
    "lnd_7318u": "20",
    "loc_country": "US",
    "loc_lat": "37.7749",
    "loc_lon": "-122.4194",
    "loc_name": "San Francisco",
    "pms_pm02_5": "12.5",
    "device_class": "geigiecast-zen",
    "when_captured": "2024-11-02T15:30:00"
}
response = requests.post(url, json=data, headers=headers)
print(response.status_code, response.text)