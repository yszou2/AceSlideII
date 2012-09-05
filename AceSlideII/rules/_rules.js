//映射各种规则
define([], function(){
  var rules = [
      [/^http:\/\/zouyesheng\.com.*$/, 'default']
    , [/^http:\/\/localhost.*$/, 'default']
  ];
  return rules;
});
