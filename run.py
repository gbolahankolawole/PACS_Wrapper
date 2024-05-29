import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', '11110'))
    app.run(debug=True, port=port, threaded=True)



