'''
Licence (MIT)
-------------

    Copyright (c) 2010, André Wobst.

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
'''

import functools, hashlib, traceback
import bottle, multipart, sqlalchemy, sqlalchemy.orm

import cfg, tables, orm

app = bottle.Bottle()
engine = sqlalchemy.create_engine(cfg.db_connect_url, connect_args=cfg.db_connect_args)
template = functools.partial(bottle.template,
                             template_lookup=[cfg.template_path],
                             template_adapter=bottle.Jinja2Template,
                             template_settings=dict(autoescape=True))
tables.init(engine)

class Env:
    # The design of this app uses an instance of this class to provide all kind of data to the views.

    app=app
    cfg=cfg

    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(bind=engine))
        return self._db

    def __call__(self, func):
        def wrapper(**kwargs):
            try:
                if kwargs:
                    # The idea of this design is to consume the kwargs here and store the data in self.
                    raise RuntimeError('unprocessed arguments', kwargs)
                if bottle.request.environ.get('REQUEST_METHOD', 'GET').upper() in ['POST', 'PUT']:
                    # As multipart is not (yet) integrated in bottle, we make the request data available
                    # in the environment.
                    try:
                        self.forms, self.files = multipart.parse_form_data(bottle.request.environ,
                            strict=cfg.multipart_strict,
                            memfile_limit=cfg.multipart_memfile_limit*1024,
                            mem_limit=cfg.multipart_mem_limit*1024,
                            disk_limit=cfg.multipart_disk_limit*1024)
                    except multipart.MultipartError as e:
                        bottle.abort(413, e)
                result = func(self)
            except:
                user_agent = bottle.request.environ.get('HTTP_USER_AGENT')
                self.db.add(orm.Log(None, None, None, user_agent, traceback.format_exc()))
                raise
            finally:
                if hasattr(self, '_db'):
                    self.db.commit()
                    self.db.close()
            return result
        return wrapper

@app.get('/', name='form')
@Env()
def form(env):
    return template('form', env=env)

@app.post('/process', name='process')
@Env()
def form(env):
    file = env.files.get('file')
    if file:
        md5 = hashlib.md5()
        while True:
            data = file.file.read(128)
            if not data:
                break
            md5.update(data)
        digest = md5.hexdigest()
    else:
        digest = None
    comment = env.forms.get('comment')
    user_agent = bottle.request.environ.get('HTTP_USER_AGENT')
    if digest:
        env.db.add(orm.Log(file.filename, digest, comment, user_agent, None))
    else:
        env.db.add(orm.Log(None, None, comment, user_agent, None))
    return template('thanks', digest=digest, env=env)

@app.get('/stats', name='stats')
@Env()
def stats(env):
    count = env.db.query(orm.Log).count()
    return template('stats', count=count, env=env)

@app.get('/static/:filename', name='static')
def server_static(filename):
    return bottle.static_file(filename, root=cfg.static_path)

if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(app=app, host='0.0.0.0', reloader=True)
else:
    application = app
