# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)


if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db1 = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db1 = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db1)
service = Service()
plugins = PluginManager()

db1.define_table(
    auth.settings.table_user_name,
    Field('first_name', length=128, default=''),
    Field('last_name', length=128, default=''),
    Field('email', length=128, default='', unique=True), # required
    Field('password', 'password', length=512,readable=False, label='Password'), #required
    Field('phone'),
    Field('dp', 'upload'),
    Field('registration_key', length=512,                # required
          writable=False, readable=False, default=''),
    Field('reset_password_key', length=512,              # required
          writable=False, readable=False, default=''),
    Field('registration_id', length=512,                 # required
          writable=False, readable=False, default=''))

custom_auth_table = db1[auth.settings.table_user_name] # get the custom_auth_table
custom_auth_table.first_name.requires =   IS_NOT_EMPTY(error_message=auth.messages.is_empty)
custom_auth_table.last_name.requires =   IS_NOT_EMPTY(error_message=auth.messages.is_empty)
custom_auth_table.password.requires = [IS_STRONG(min=8,special=1,upper=1,number=1), CRYPT()]
custom_auth_table.email.requires = [IS_EMAIL(error_message=auth.messages.invalid_email),IS_NOT_IN_DB(db1, custom_auth_table.email)]

auth.settings.table_user = custom_auth_table # tell auth to use custom_auth_table

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)
# if not auth.is_logged_in():
#    redirect (auth.settings.login_url)
## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
# auth.settings.login_url = URL(r=request, f='user', args='login')
auth.settings.login_next = URL(r=request, f='index')
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)


db = DAL("sqlite://storage.sqlite")

db.define_table('question',
   Field('title', 'list:string'),
   Field('no_ans', default=0),
   Field('file', 'upload'),
   Field('author'),
   Field('email'),
   Field('body', 'text'),
   Field('anonymous', 'boolean'),
   Field('timestamp','datetime',default=request.now))

db.define_table('answer',
   Field('question_id', 'reference question'),
   Field('file', 'upload'),
   Field('asker'),
   Field('author'),
   Field('email'),
   Field('dp'),
   Field('body', 'text'),
   Field('timestamp','datetime',default=request.now),
   Field('likes'))

db.define_table('expreview',
                Field('question_id','reference question'),
                Field('view','text'))

db.define_table('likes',
               Field('question_id','reference question'),
               Field('ans_id','reference answer'),
               Field('liker'),
               Field('upordown'))

db.define_table('userdata',
                Field('email'),
                Field('noofans'),
                Field('badge'))

db.define_table('stars',
                Field('question_id','reference question'),
                Field('user'),
                Field('username'),
                Field('author'),
                Field('timestamp','datetime',default=request.now))

db.define_table('feed',
                Field('email'),
                Field('author'),
                Field('feedback'))

db.question.id.readable=db.question.id.writable=False
db.question.body.requires = IS_NOT_EMPTY()
db.question.author.writable = db.question.author.readable = False
db.question.email.writable = db.question.email.readable = False
db.question.timestamp.writable = db.question.timestamp.readable = False
db.question.no_ans.writable = db.question.no_ans.readable = False

# db.answer.question_id.requires = IS_IN_DB(db, db.question.id, '%(title)s')
db.answer.body.requires = IS_NOT_EMPTY()
db.answer.question_id.writable = db.answer.question_id.readable = False
db.answer.author.writable =db.answer.author.readable= False
db.answer.email.writable = db.answer.email.readable = False
db.answer.asker.writable=db.answer.asker.readable=False
db.answer.likes.writable = db.answer.likes.readable = False
db.answer.timestamp.writable = db.answer.timestamp.readable = False
db.answer.dp.writable =db.answer.dp.readable= False

db.expreview.question_id.writable = db.expreview.question_id.readable = False

db.likes.liker.readable=db.likes.liker.writable=False

db.userdata.email.writable=db.userdata.email.readable=False
db.userdata.noofans.writable=db.userdata.noofans.readable=False

db.feed.author.writable = db.feed.author.readable = False
db.feed.email.writable = db.feed.email.readable = False
