angular.module('checkit')
.controller('TodoListController', ['$http', function($http) {

  this.new_todo_list = {}
  this.lists = [];
  this.user_id = null;

  // Updates lists attribute of the controller
  var ctrl = this;
  this.update_lists = function() {
    $http.get('/v1/users/' + ctrl.user_id + '/lists').success(function(data){
      ctrl.lists = data['lists'];
    });
  };

  this.addTodoList = function() {
    var list_data = {"description": this.new_todo_list.description};
    $http.post('/v1/users/' + ctrl.user_id + '/lists', list_data).success(function(data){
      ctrl.lists.push(data);
    });
    this.new_todo_list = {};
  }

  this.addTodoItem = function(){
    console.log("Adding new todo item");
  };

}]);
