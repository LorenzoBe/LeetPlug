# LeetPlug
This is a browser extension that is able to interact with LeetCode official site.  
The main goal is to be able to track the activities on each problem and all the related events: submissions, time spent coding the solition, repetitions of a problem.  
It is composed of three layers:
- Client side: extension to be installed in the supported browsers
- Server side: data collection Web Service
- Server side: visualisation UI

## Browser extension
The browser extension is the main innovative idea here. Exactly like an AD Blocker extension, it's able to intercept the loading of the page and modify it on the fly to force a different behaviour. Specifically it must be able to:
- Identify when it is loading a LeetCode problem page
- Hide all the relevant information
- Present two buttons: one to start the coding with time tracking, another to start the coding without it (not everybody likes to be tracked every time :D )
- When user clicks on "tracking" button:
  - A timer is started and the value is shown in the UI
  - The start event is sent to the remote LeetPlug server
  - All the Submit requests and the related results are intercepted and sent to the remote LeetPlug server
  - When the Submit result is successful the tracking is stopped
- When user clicks on "no tracking" button:
  - The problem is started without tracking any activity

Since I am a Chrome user, the preliminary version will support this browser. It should be easily ported to support Firefox also.

### How to create an extension?
Coding a browser extension doesn't require any develpment tool or environemnt, I didn't imagin it was so easy!  
This is beacuse the extensions are based on HTML for the UI plus JavaScript for the logic, or at least the simple ones. A very nice tutorial that helped me to create my first extension in 10 minutes is [here](https://www.sitepoint.com/create-chrome-extension-10-minutes-flat/).  
Every extension has a manifest file, where you can specify which privileges you require and some nice triggering options that we'll use.

### How to intercept and modify the LeetCode page
In my case I need access to the current browser tab and I want to execute a script every time a user is loading a LeetCode problem page. This can be easily done in the manifest with the following configuration:
```
"permissions": ["activeTab"],

"content_scripts": [
{
    "matches": ["https://leetcode.com/problems/*"],
    "run_at": "document_start",
    "js": ["thirdParty/jquery-3.5.1.slim.min.js", "src/problemsScript.js"]
}
]
```
The **content_scripts** are executed when the page matches the defined pattern. In "js" element I defined the script to be executed as well as the JQuery library which I will use inside my logic.  
Since the LeetCode page are mostly dynamic, I was not able to easily refer to internal elements. I had to create in the [problemsScript.js](src/problemsScript.js) file a function which polls the page until all the needed elements are created. Then I use JQuery to change the attributes to the elements, to hide some of them and show my control buttons. I also followed the same approach to add the timer inside the page, near the bottom-right Submit button.  

### How to intercept the Submit requests
To be able to track the user activity we need to intercept the Submit requests and the responses. Here the Chrome API sult come to help us! The main documentation is [here](https://developer.chrome.com/extensions/webRequest).

## Application server
Timeseries DB? Multicolumn?
```
{
    "users": ["user1", "user2"],
    "user:user1": ["problem1", "problem2"],
    "user:user2": ["problem3", "problem4"],
    "user:user1:problem1": ["{id:111, event: start, time: 1234567}", "{id:111, event: success, time: 1235555}"],
    "user:user1:problem2": ["{id:333, event: start, time: 4444444}", "{id:333, event: fail, time: 6666666}"]
}
