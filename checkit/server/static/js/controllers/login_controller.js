/* Angularjs controller to manage loging with GitHub

https://github.com/sahat/satellizer
*/
angular.module('checkit')
  .controller('LoginCtrl', function($scope, $auth) {
    // Check if user_id is in local storage, if so, call update lists in listsCtrl
    $scope.user_id = null;
    if (localStorage.user_id) {
      $scope.user_id = localStorage.user_id;
      $scope.listsCtrl.update_lists($scope.user_id);
    }

    var loginCtrl = $scope;
    $scope.authenticate = function(provider) {
      $auth.authenticate(provider).then(function(response){
        loginCtrl.user_id = response.data.user_id;
        localStorage.user_id = angular.toJson(response.data.user_id);
        // Update TODO lists once we have the user_id
        loginCtrl.listsCtrl.update_lists(response.data.user_id);
      });
    };

    $scope.logOut = function() {
      localStorage.clear();
      loginCtrl.user_id = null;
    };

  });
