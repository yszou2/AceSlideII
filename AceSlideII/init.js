//初始化函数

define([], function(){
  var init = function(obj){
    var fw = obj.width || 600;
    console.log('AceSlideII is starting ...');
    require([  'AceSlideII/sub'
             , 'AceSlideII/canvas'
             , 'AceSlideII/frames'
             , 'AceSlideII/keys'
             , 'AceSlideII/mobile'
             , 'dojo/domReady!'
            ],
      function(sub, canvas, frames){
        sub(frames(fw, fw * screen.height / screen.width), canvas());
        console.log('AceSlideII is OK');
      }
    ); 
  }
  return init;
});
