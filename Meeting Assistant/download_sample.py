"""Download the sample meeting WAV used in the IBM lab."""

import requests

URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "hTqGqoC-LrW6S79HjuJUkg/trimmed-02.wav"
)
OUT = "sample-meeting.wav"

response = requests.get(URL, timeout=60)
if response.status_code == 200:
    with open(OUT, "wb") as f:
        f.write(response.content)
    print(f"Saved {OUT}")
else:
    print(f"Download failed: HTTP {response.status_code}")
