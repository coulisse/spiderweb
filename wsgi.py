import bjoern
from lib\webapp import app


bjoern.listen(app, '0.0.0.0', 8080)
bjoern.run()
