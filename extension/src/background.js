// Configuration
var userId = '';
var userKey = '';
var webAppURL = 'https://leetplug.azurewebsites.net';
// This is mostly useless, just to avoid lamers to spam
var webAppBasic = 'Basic bG9yZW56bzp5YTU2Mm9zMw==';

// Sync to/from chrome storage
chrome.storage.local.set({'webAppURL': webAppURL});
chrome.storage.local.set({'webAppBasic': webAppBasic});

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    chrome.storage.local.get(['userId', 'userKey'], function(result) {
        if (!(typeof result.userId === 'undefined'))
            userId = result.userId;
        if (!(typeof result.userKey === 'undefined'))
            userKey = result.userKey;
    });

    if (request.method == "getWebAppURL")
        sendResponse({data: webAppURL});
    else if (request.method == "getWebAppBasic")
        sendResponse({data: webAppBasic});
    else if (request.method == "geUserId")
        sendResponse({data: userId});
    else if (request.method == "getUserKey")
        sendResponse({data: userKey});
    else
        sendResponse({data: ''}); // snub them.
});
