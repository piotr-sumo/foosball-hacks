from flask import Flask, escape, request
from camera import ContinuousCamera
import os
import secrets

app = Flask(__name__)

camera = ContinuousCamera()

@app.route("/save_recording")
def save_recording():
    filename = f"recording{secrets.token_hex(15)}"

    camera.dump_to_file(filename)
    os.system(f"./camera_process.sh {filename} &")

    return filename


app.run(host="0.0.0.0", port="8080")
