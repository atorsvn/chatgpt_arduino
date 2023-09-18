import json
import quart
import quart_cors
from quart import request
from pyfirmata import Arduino

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

_TODOS = {}

class ArduinoUnoController:
    def __init__(self, port):
        self.board = Arduino(port)
        self.pins = {}  # Store pin references
        
    def set_pin_mode(self, pin, mode):
        """Set the mode for a given pin."""
        self.pins[pin] = self.board.get_pin(f'd:{pin}:{mode}')
        
    def write_digital(self, pin, value):
        """Write a digital value to a given pin."""
        if pin in self.pins:
            self.pins[pin].write(value)
        else:
            self.board.digital[pin].write(value)
        
    def read_digital(self, pin):
        """Read a digital value from a given pin."""
        return self.board.digital[pin].read()
        
    def close(self):
        """Close the connection to the board."""
        self.board.exit()

# Initialize the Arduino controller
arduino = ArduinoUnoController('/dev/ttyACM0')

@app.post("/arduino/pinmode/<int:pin>/<string:mode>")
async def set_pin_mode(pin, mode):
    arduino.set_pin_mode(pin, mode)
    return quart.Response(response='OK', status=200)

@app.post("/arduino/write/digital/<int:pin>/<int:value>")
async def write_digital(pin, value):
    arduino.write_digital(pin, value)
    return quart.Response(response='OK', status=200)

@app.get("/arduino/read/digital/<int:pin>")
async def read_digital(pin):
    value = arduino.read_digital(pin)
    return quart.Response(response=json.dumps({"value": value}), status=200)

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
