from app import app
import os

debug = True
if debug:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


if __name__ == "__main__":
    app.run(debug=debug, host='0.0.0.0')
