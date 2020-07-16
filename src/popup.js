// Globals
var webAppURL = "";
var webAppBasic = "";

function validateEmail(email) {
  const re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(email);
}

function requestUserKey(email) {
  const req = new XMLHttpRequest();
  let url = new URL(webAppURL + '/users');
  url.searchParams.set('email', email);

  req.open("GET", url, true)
  req.setRequestHeader('Authorization', webAppBasic);
  req.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  req.send();

  req.onreadystatechange = function() { // Call a function when the state changes.
    if (this.readyState === XMLHttpRequest.DONE) {
      if (this.status === 202) {
        alert(this.response);
      } else if (this.status === 409) {
        alert(this.response);
      }
    }
  }
}

document.addEventListener('DOMContentLoaded', function() {
  var emailTB = document.getElementById("txtEmail");
  var confirmEmailTB = document.getElementById("txtConfirmEmail");
  var submitButton = document.getElementById('btnSubmit');
  var userIdTB = document.getElementById("txtUserId");
  var userKeyTB = document.getElementById("txtUserKey");
  var cancelButton = document.getElementById('btnCancel');
  var saveButton = document.getElementById('btnSave');

  chrome.storage.sync.get(['email', 'userId', 'userKey', 'webAppURL', 'webAppBasic'], function(result) {
    if (!(typeof result.email === 'undefined'))
      emailTB.value = result.email;
    if (!(typeof result.email === 'undefined'))
      confirmEmailTB.value = result.email;
    if (!(typeof result.userId === 'undefined'))
      userIdTB.value = result.userId;
    if (!(typeof result.userKey === 'undefined'))
      userKeyTB.value = result.userKey;
    if (!(typeof result.webAppURL === 'undefined'))
      webAppURL = result.webAppURL;
    if (!(typeof result.webAppBasic === 'undefined'))
      webAppBasic = result.webAppBasic;
  });

  // BUTTON LISTENERS
  submitButton.addEventListener('click', function() {
    email = emailTB.value;
    confirmEmail = confirmEmailTB.value;

    // check if the two email fields are identical
    if (email != confirmEmail) {
        alert("Emails do not match.");
        return;
    }

    // check if the emails are valid
    if (!validateEmail(email) || !validateEmail(confirmEmail)) {
      alert("Email is invalid.");
      return;
    }

    chrome.storage.sync.set({'email': email});
    requestUserKey(email)
  }, false);

  cancelButton.addEventListener('click', function() {
    window.close();
  }, false);

  saveButton.addEventListener('click', function() {
    chrome.storage.sync.set({'userId': userIdTB.value});
    chrome.storage.sync.set({'userKey': userKeyTB.value});

    alert("Configuration complete, please try to access to LeetCode problems.");
    window.close();
  }, false);
}, false);
