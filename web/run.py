from project import app, db
import os

# Use the following command to run the app on debug mode
# docker run -p 5000:5000 -e DEBUG=1 flask_app_dev

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get('DEBUG') == 1)
    # app.run(debug=True)
