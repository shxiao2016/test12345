# This is a package.
#
# Please do not add the code to this file unless absolutely
# necessary because __init__.py files are not needed with Python 3
import logging
from linkedin.web import create_app
from zephyrlixweb.models import db
from zephyrlixweb import config
from zephyrlixweb.lix_scheduler import LIXScheduler
from flask_jsglue import JSGlue

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (%(name)s) %(message)s')
log = logging.getLogger(__name__)

app = create_app(__name__)
jsglue = JSGlue(app)

app.config['SECRET_KEY'] = app.secret_key
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CACHE_TYPE'] = 'simple'


app.config['SQLALCHEMY_POOL_SIZE'] = 100

app.config['SQLALCHEMY_DATABASE_URI'] = config.getConfig(app.config['DEBUG'])
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600


db.app = app
db.init_app(app)
scheduler = LIXScheduler()
scheduler.schedule_run()
scheduler.schedule_email()
log.info(msg="App started.")
