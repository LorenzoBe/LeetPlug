// Configuration
var webAppURL = 'http://127.0.0.1:5000';
var webAppBasic = 'Basic bG9yZW56bzp5YTU2Mm9zMw==';

// Storage sync
chrome.storage.sync.set({'webAppURL': webAppURL});
chrome.storage.sync.set({'webAppBasic': webAppBasic});
