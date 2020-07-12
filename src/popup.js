document.addEventListener('DOMContentLoaded', function() {
  var loadPageButton = document.getElementById('loadPage');
  loadPageButton.addEventListener('click', function() {

    chrome.tabs.getSelected(null, function(tab) {
      var newUrl = 'https://leetcode.com/problems/insert-into-a-binary-search-tree/';
      chrome.tabs.update(tab.id, {url: newUrl});
    });
  }, false);
}, false);
