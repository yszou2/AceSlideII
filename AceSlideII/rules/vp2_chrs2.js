//北欧女神战魂
define(['require', 'dojo/query', 'dojo/dom-construct'], function(require, query, cstr){
  var ready_html = function(html_list, callback){
    console.log(html_list);
    //callback();
  }


  var rule = function(callback){
    var href_list = [];
    query('td > div > a:first-child').forEach(function(item){
      href_list.push(item.href);
    });

    var html_list = [];
    for(var i = 0, l = href_list.length; i < l; i++){
      require(['dojo/text!' + href_list[0]], function(html){
        html_list.push(cstr.create('div', {innerHTML: html}));
        if(html_list.length == href_list.length){
          ready_html(html_list, callback);
        }
      });
    }

    //callback();
  }
  return rule;
});
