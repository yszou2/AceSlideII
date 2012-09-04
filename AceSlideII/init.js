var AceSlideII_Init = function(){
  if((typeof require) == 'undefined'){
    setTimeout(AceSlideII_Init, 200);
    return
  } else {
    console.log('AceSlideII is starting ...');
    if(window.AceSlideII){
      console.log('AceSlideII has existed.');
      return;
    } else {
      window.AceSlideII = true;
    }
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
          console.log('AceSlideII is OK');
        });
      }
    ); 
  }
}
AceSlideII_Init();
