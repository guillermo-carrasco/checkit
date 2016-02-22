angular.module('checkit')
.controller('TodoListController', ['$http', function($http) {

  // Two-way bingin objects for the front end. When these are updated, so it is the front page.
  this.new_todo_list = {};
  this.new_item = {};
  this.lists = [];

  // copy the scope to an external variable to be used within $http calls
  var ctrl = this;

  // Update array of lists
  this.update_lists = function(user_id) {
    $http.get('/v1/users/' + user_id + '/lists').success(function(data){
      ctrl.lists = data['lists'];
    });
  };

  this.addTodoList = function(user_id) {
    var list_data = {"description": this.new_todo_list.description};
    $http.post('/v1/users/' + user_id + '/lists', list_data).success(function(data){
      // Update local array of lists after creating the new list
      data['items'] = [];
      ctrl.lists.push(data);
    });
    this.new_todo_list = {};
  };

  this.delete_list = function(list) {
    var user_id = list.user_id;
    $http.delete('/v1/users/' + user_id + '/lists/' + list.id).success(function(data){
      // Remove list from the array of lists
      ctrl.lists.splice(ctrl.lists.indexOf(list), 1);
    });
  };

  this.addTodoItem = function(user_id, list_data){
    var list_id = list_data['id'];
    var item_data = {"description": ctrl.new_item[list_id], "todo_list_id": list_id};
    $http.post('/v1/users/' + user_id + '/lists/' + list_id + '/items', item_data).success(function(data){
      list_data['items'].push(data);
      ctrl.new_item[list_id] = '';
    });
  };

  this.updateItem = function(user_id, list, item) {
    // Get item's list index, and change the attribute in the item
    var l_index = ctrl.lists.indexOf(list);
    var i_index = ctrl.lists[l_index]['items'].indexOf(item);
    ctrl.lists[l_index]['items'][i_index].checked = !ctrl.lists[l_index]['items'][i_index].checked;

    $http.put('/v1/users/' + user_id + '/lists/' + item['todo_list_id'] + '/items/' + item['id'], item).success(function(data){
      console.log("Item updated correctly");
    });
  };

}]);
