var s = window.location.href.split('/');
var name = s[s.length - 1];
var control = {
  is_control: false
}

//处理命令
var do_cmd = function(cmd_list){
  for(var i = 0, l = cmd_list.length; i < l; i++){
    var s_list = cmd_list[i].split(' ');
    var func = ({
        'GOTO': function(s_list){dojo.publish('GOTO', [s_list[1]])}
      , 'DRAW': function(s_list){dojo.publish('DRAW', [dojo.fromJson(s_list[1]),
                                                       dojo.fromJson(s_list[2])])}
      , 'CLEAR': function(s_list){dojo.publish('CLEAR', [])}
    })[s_list[0]];
    func ? func(s_list) : {};
  }
}

var pull = dojo.hitch(
  control,
  function(sync){
    var that = this;
    if(that.is_control){return}
    dojo.xhrPost({
      url: '/pull',
      content: {name: name, sync: sync},
      handleAs: 'json',
      error: function(error, ioArgs){
        alert('出错了, ' + error.message);
        return
      },
      load: function(response, ioArgs){
        if(response==null){return}
        if(response.result != 0){
          return alert('出错了, ' + response.msg);
        } else {
          if(that.is_control){return}
          var cmd_list = response.cmd_list;
          var sync = response.sync;
          pull(sync);
          do_cmd(cmd_list);
        }
      }
    });
  }
);

var push = function(token, cmd){
  dojo.xhrPost({
    url: '/push',
    content: {cmd: cmd, token: token},
    handleAs: 'json',
    error: function(error, ioArgs){
      alert('出错了, ' + error.message);
      return
    },
    load: function(response, ioArgs){
      if(response.result != 0){
        return alert('出错了, ' + response.msg);
      } else {
        return;
      }
    }
  });
}

//请求控制token
var apply_token = function(password, cb){
  dojo.xhrPost({
    url: '/push',
    content: {_method: 'apply', pass: password, name: name},
    handleAs: 'json',
    error: function(error, ioArgs){
      alert('出错了, ' + error.message);
      return
    },
    load: function(response, ioArgs){
      if(response.result != 0){
        return alert('出错了, ' + response.msg);
      } else {
        cb(response.token);
      }
    }
  });
}


//申请控制token
dojo.subscribe('APPLY', control,
  function(){
    var that = this;
    if(that.is_control){return}
    var pass = prompt('请输入当前项目的密码') || '';
    if(pass == ''){return}
    apply_token(pass,
      function(token){
        that.is_control = true;

        dojo.subscribe('GOTO',
          function(i){
            push(token, 'GOTO ' + i);
          }
        );

        dojo.subscribe('DRAW',
          function(origin, path){
            push(token, 'DRAW ' + dojo.toJson(origin) + ' ' + dojo.toJson(path));
          }
        );

        dojo.subscribe('CLEAR',
          function(origin, path){
            push(token, 'CLEAR');
          }
        );
      }
    );
  }
);



dojo.addOnLoad(function(){
  //获取同步消息
  pull(-1);
});
