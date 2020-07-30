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
  var formData = new FormData();
  formData.append('email', email);

  req.open("POST", url, true)
  req.setRequestHeader('Authorization', webAppBasic);
  req.send(formData);

  req.onreadystatechange = function() { // Call a function when the state changes.
    if (this.readyState === XMLHttpRequest.DONE) {
      if (this.status === 202) {
        alert(this.response);
      } else if (this.status === 409) {
        alert(this.response);
      } else if (this.status >= 500) {
        alert(this.response);
      }
    }
  }
}

document.addEventListener('DOMContentLoaded', function() {
  var leetplugSiteAnchor = document.getElementById("leetplugSiteLink");
  var emailTB = document.getElementById("txtEmail");
  var confirmEmailTB = document.getElementById("txtConfirmEmail");
  var submitButton = document.getElementById('btnSubmit');
  var userIdTB = document.getElementById("txtUserId");
  var userKeyTB = document.getElementById("txtUserKey");
  var saveButton = document.getElementById('btnSave');
  var policyAgreeCB = document.getElementById("policyAgree");

  chrome.storage.local.get(['email', 'policyAgreeCB', 'userId', 'userKey', 'webAppURL', 'webAppBasic'], function(result) {
    if (!(typeof result.email === 'undefined'))
      emailTB.value = result.email;
    if (!(typeof result.policyAgreeCB === 'undefined'))
      policyAgreeCB.checked = result.policyAgreeCB;
    if (!(typeof result.email === 'undefined'))
      confirmEmailTB.value = result.email;
    if (!(typeof result.userId === 'undefined')) {
      userIdTB.value = result.userId;
      leetplugSiteAnchor.href = "https://leetplug.azurewebsites.net/data?userId=" + userIdTB.value;
    }
    if (!(typeof result.userKey === 'undefined'))
      userKeyTB.value = result.userKey;
    if (!(typeof result.webAppURL === 'undefined'))
      webAppURL = result.webAppURL;
    if (!(typeof result.webAppBasic === 'undefined'))
      webAppBasic = result.webAppBasic;
  });

  function triggerBackgroubdSync() {
    chrome.runtime.sendMessage({method: "updateLocalVariables"}, function(response) {
      // nothing to do here
    });
  }
  
  function storeCredentials() {
    chrome.storage.local.set({'userId': userIdTB.value});
    chrome.storage.local.set({'userKey': userKeyTB.value});
    triggerBackgroubdSync();
  }

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

    // check if policy has been accepted
    if (policyAgreeCB.checked != true) {
      alert("Please agree with the LeetPlug Privacy and Security Policy, marking the checkbox.");
      return;
    }

    chrome.storage.local.set({'email': email});
    chrome.storage.local.set({'policyAgreeCB': true});
    requestUserKey(email)
  }, false);

  saveButton.addEventListener('click', function() {
    storeCredentials();
    alert("Configuration complete, please try to access to LeetCode problems.");

    window.close();
  }, false);

  window.addEventListener('blur', function() {
    storeCredentials();
  }, false);

}, false);
