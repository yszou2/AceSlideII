//北欧女神战魂
define(['require', 'dojo/query', 'dojo/dom-construct'], function(require, query, cstr){

  var do_page = function(html){
    (/<B>(.*?)<\/B>/).exec(html);
    var name = RegExp.$1.replace(/·/g, '');

    (/src="([^>]*?)" width="300"/).exec(html);
    var img = RegExp.$1;

    var node = cstr.create('div', {innerHTML: html});
    var q = query('table', node)[1];
    q = query('div', q);
    q = q[q.length - 1];
    var data = q.innerHTML;

    return {name: name, img: img, data: data};
  }


  var rule = function(callback){
    var href_list = [];
    query('td > div > a:first-child').forEach(function(item){
      href_list.push(item.href);
    });

    for(var i = 0, l = href_list.length; i < l; i++){
      require(['dojo/text!' + href_list[i]], function(html){
        do_page(html);
      });
    }

    //callback();
  }

  return rule;
});
