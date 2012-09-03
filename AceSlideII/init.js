var AceSlideII_Init = function(){
  if(!require){
    setTimeout(AceSlideII_Init, 200);
    return
  } else {
    require([  'dojo/domReady'
             , 'dojo/_base/config'
             , 'AceSlideII/sub.js'
             , 'AceSlideII/canvas.js'
             , 'AceSlideII/frames.js'
             , 'AceSlideII/keys.js'
             , 'AceSlideII/mobile.js'
            ],
      function(ready, config, sub, canvas, frames){
        ready(function(){
          sub(frames(config.fw, config.fh), canvas(config.fw, config.fh));
        });
      }
    ); 
  }
}
AceSlideII_Init();
