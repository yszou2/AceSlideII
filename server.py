# -*- coding: utf-8 -*-

import imp
import os
import uuid
import functools
from os.path import join

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.template


from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

tornado.options.parse_command_line()


IL = tornado.ioloop.IOLoop.instance()

class BaseHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ('GET', 'POST', 'DELETE', 'PUT', 'OPTIONS')

    def initialize(self):
        '处理构建特殊方法'
        _method = self.get_argument('_method', None)
        if _method is not None:
            self.request.method = _method.upper()

    def finish(self, *args, **kargs):
        self.set_header('Connection', 'close')
        super(BaseHandler, self).finish(*args, **kargs)

class TestHandler(BaseHandler):
    def get(self):
        return self.write('it works!')


class DojoHandler(BaseHandler):
    '获取Dojo的文件'

    def get(self):
        with open(join(os.path.dirname(__file__), 'dojo.js'), 'rb') as f:
            data = f.read()
        self.set_header('Content-Type', 'text/javascript');
        return self.write(data)


class AceSlideHandler(BaseHandler):
    '获取ace-slide-II文件'

    def get(self):
        with open(join(os.path.dirname(__file__), 'ace-slide-II.js'), 'rb') as f:
            data = f.read()
        self.set_header('Content-Type', 'text/javascript');
        return self.write(data)


class ControlHandler(BaseHandler):
    '获取control文件'

    def get(self):
        with open(join(os.path.dirname(__file__), 'control.js'), 'rb') as f:
            data = f.read()
        self.set_header('Content-Type', 'text/javascript');
        return self.write(data)


class UploadHandler(BaseHandler):
    '''接收上传的数据,先返回一串js代码去掉多余的script,
    再上传,再返回重定向js代码'''

    JS = '''
dojo.addOnLoad(function(){
    var node_list = dojo.query('script');
    dojo.destroy(node_list[0]); //reg
    dojo.destroy(node_list[2]); //upload
    dojo.create('script',
        {innerHTML: "'^^^^ACE-SLIDE-II.JS^^^^'"}, dojo.query('script')[0], 'after');
    var data = encodeURIComponent(dojo.doc.documentElement.innerHTML);
    dojo.create('script',
        {src: 'http://%(ip)s/upload?_method=post&name=%(name)s&pass=%(password)s' + '&data=' + data, type: 'text/javascript'}, dojo.query('script')[0], 'before');
});
    '''

    def get(self):
        name = self.get_argument('name', '')
        password = self.get_argument('pass', '')
        self.set_header('Content-Type', 'text/javascript')
        return self.write(self.__class__.JS % {'name': name,
                                               'password': password,
                                               'ip': RegisterHandler.SLIDE[name]['ip']})

    def post(self):
        name = self.get_argument('name', '')
        password = self.get_argument('pass', '')
        data = self.get_argument('data', '')
        self.set_header('Content-Type', 'text/javascript')
        if not (name and password):
            return self.write('alert("缺少参数");')

        if name not in RegisterHandler.SLIDE:
            return self.write('alert("错误的名字");')

        obj = RegisterHandler.SLIDE[name]
        if obj.get('password', '') != password:
            return self.write('alert("错误的密码");')

        obj['data'] = '<!DOCTYPE html><html>%s</html>' % \
                        data.replace("<script>'^^^^ACE-SLIDE-II.JS^^^^'</script>",
         '<script type="text/javascript" src="http://%(ip)s/ace-slide-II.js"></script><script type="text/javascript" src="http://%(ip)s/control.js"></script>' % {'ip': obj['ip']}, 1)
        return self.write('window.location.href="http://%(ip)s/%(name)s"' % obj)


class SlideHandler(BaseHandler):
    '返回一个文档的内容'

    def get(self, name):
        if name not in RegisterHandler.SLIDE:
            return self.send_error(404)

        return self.write(RegisterHandler.SLIDE[name]['data'])



class PullHandler(BaseHandler):
    '获取服务器端的消息'

    CONN = {}

    @tornado.web.asynchronous
    def post(self):
        name = self.get_argument('name', '')
        sync = self.get_argument('sync', '-1')
        if not name or (name not in RegisterHandler.SLIDE):
            return self.finish({'result': 1, 'msg': u'错误的名字'})
        try:
            sync = int(sync)
        except ValueError:
            return self.finish({'result': 2, 'msg': u'sync参数错误'})
        sync += 1

        cmd_list = PushHandler.CMD.get(name, [])

        if sync == len(cmd_list):
            #最新情况
            cls = self.__class__
            self.sync = sync
            self.name = name
            if name in cls.CONN:
                cls.CONN[name].append(self)
            else:
                cls.CONN[name] = [self]
            return

        if sync > len(cmd_list):
            return self.finish({'result': 0, 'msg': '', 'cmd_list': [], 'sync': len(cmd_list) - 1})
        else:
            return_list = cmd_list[sync:]
        return self.finish({'result': 0, 'msg': '', 'cmd_list': return_list, 'sync': len(cmd_list) - 1})

    def release(self):
        cmd_list = PushHandler.CMD.get(self.name, [])
        return_list = cmd_list[self.sync:]
        try:
            return self.finish({'result': 0, 'msg': '', 'cmd_list': return_list, 'sync': len(cmd_list) - 1})
        except:
            pass

    def on_finish(self):
        #print self.__class__.CONN.get('test', [])
        return


class PushHandler(BaseHandler):
    '往服务器端发送消息'
    SUPPORTED_METHODS = ('POST', 'APPLY')

    CMD = {}
    TOKEN = {}

    def post(self):
        token = self.get_argument('token', '')
        cmd = self.get_argument('cmd', '')
        cls = self.__class__
        if token not in cls.TOKEN:
            return self.write({'result': 1, 'msg': u'token错误'})

        name = cls.TOKEN[token]
        if name not in cls.CMD:
            cls.CMD[name] = [cmd]
        else:
            cls.CMD[name].append(cmd)

        [conn.release() for conn in PullHandler.CONN.get(name, [])]
        PullHandler.CONN[name] = []
        return self.write({'result': 0, 'msg': ''})

    def apply(self):
        '申请push的token'
        name = self.get_argument('name', '')
        password = self.get_argument('pass', '')

        if not (name and password):
            return self.write({'result': 1, 'msg': u'缺少参数'})
        if name not in RegisterHandler.SLIDE:
            return self.write({'result': 2, 'msg': u'不存在的项目名'})
        if password != RegisterHandler.SLIDE[name]['password']:
            return self.write({'result': 3, 'msg': u'密码错误'})

        token = uuid.uuid4().hex
        self.__class__.TOKEN[token] = name
        return self.write({'result': 0, 'msg': '', 'token': token})


class IndexHandler(BaseHandler):
    '显示页面'

    TEMPLATE = tornado.template.Template(
    '''
     <div>当前存在的文档 ({{ len(conns) }})</div>
     <ul>
        {% for k,v in conns.items() %}
            <li><a href="/{{ k }}">{{ k }} ({{ v }})</a></li>
        {% end %}
     </ul>
    ''')

    def get(self):
        slide_list = RegisterHandler.SLIDE.keys()
        conns = {}
        for k in slide_list:
            conns[k] = len(PullHandler.CONN.get(k, []))

        r = self.__class__.TEMPLATE.generate(conns=conns)
        return self.write(r)


class RegisterHandler(BaseHandler):
    '''注册一个新实例,返回一串js代码'''

    JS = '''
var n=document.createElement('script');
n.type='text/javascript';
n.src='http://%(ip)s/dojo.js';
document.getElementsByTagName('head')[0].appendChild(n);
var n2=document.createElement('script');
n2.type='text/javascript';
n2.src='http://%(ip)s/upload?name=%(name)s&pass=%(password)s';
document.getElementsByTagName('head')[0].appendChild(n2);
    '''
    SLIDE = {}

    def get(self):
        ip = self.get_argument('ip', '')
        password = self.get_argument('pass', '')
        name = self.get_argument('name', '')

        self.set_header('Content-Type', 'text/javascript');

        if not (ip and password and name):
            return self.write('alert("缺少参数");')
        else:
            if name in self.__class__.SLIDE:
                return self.write('alert("此名字已被使用");')
            else:
                obj = {'name': name, 'ip': ip, 'password': password, 'data': None}
                self.__class__.SLIDE[name] = obj
            return self.write(self.__class__.JS % obj)


Handlers = (
    ("/", IndexHandler),
    ("/dojo.js", DojoHandler),
    ("/ace-slide-II.js", AceSlideHandler),
    ("/control.js", ControlHandler),
    ("/reg", RegisterHandler),
    ("/upload", UploadHandler),
    ("/pull", PullHandler),
    ("/push", PushHandler),
    ("/(.+)", SlideHandler),

    ("/test", TestHandler),
)


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            cookie_secret="}x3iu3b}N}k0m9c*",
            login_url="/login",
            xsrf_cookies=False,
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            template_path = os.path.join(os.path.dirname(__file__), "template"),
            debug=True,
        )
        tornado.web.Application.__init__(self, Handlers, **settings)


def main():
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen(options.port)
    print 'running on %s ...' % options.port
    IL.start()


if __name__ == "__main__":
    main()
