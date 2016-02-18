// Angular js application
(function() {
  var app = angular.module('checkit', ['satellizer'])
    .config(function($authProvider){
      $authProvider.github({
        clientId: '86d321052fddc2afcc16'
      });
    });
})();
