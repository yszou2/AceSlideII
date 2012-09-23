//google搜索结果
define(['dojo/dom', 'dojo/query', 'dojo/dom-construct', 'dojo/_base/window', 'dojo/dom-attr'],
  function(dom, query, cstr, win, attr){
    var rule = function(callback){
      var wrapper = dom.byId('rso');
      query('li', wrapper).forEach(function(item){
        cstr.create('hr', {}, item, 'after');
      });
      cstr.place(wrapper, win.body(), 'after');
      cstr.empty(win.body());
      cstr.place(wrapper, win.body(), 'first');
      attr.set(win.body(), 'style', 'visibility: visible !important');
      callback();
    }
    return rule;
  }
);
