console.log('Problems page intercepted');
window.addEventListener("load", onLoadPage, false);

// Configuration consts
const problemDescriptionParent = "[data-key='description-content']";
const problemDescriptionElement = "[class*='description__']";
const problemDescriptionTabElement = "[data-key='description']";
const submissionResultElement = "[class*='result__']";
const submissionSuccessElement = "[class*='success__']";
const submissionErrorElement = "[class*='error__']";
const codeAreaElement = "[data-cy='code-area']";
const codingPanelElement = "[class*='content__']";
const runCodeButton = "[data-cy='run-code-btn']";
const submitCodeButton = "[data-cy='submit-code-btn']";
const resetCodeButton = "[class*='reset-code-btn__']";
const resetCodeButtonWarn = "[class*='reset-code-btn-warn__']";
const questionTitleElement = "[data-cy='question-title']";
const difficultyEasyElement = "[diff='easy']";
const difficultyMediumElement = "[diff='medium']";
const difficultyHardElement = "[diff='hard']";

const easyId = 1;
const mediumId = 10;
const hardId = 100;


const customControlButtons = `
<div id='controlButtons'>
<p id="controlButtonsTitle" class="title_style">LeetPlug mask</p>
<p id="controlButtonsText" class="text_style">Choose how to start the problem:</p>
<p id="showProblemWithStopwatchAndTrack" class="round_style">Show the problem with visible stopwatch and remote tracking</p>
<p id="showProblemNoStopwatchButTrack" class="round_style">Show the problem with hidden stopwatch and remote tracking</p>
<p id="showProblemNoStopwatchNoTrack" class="round_style">Show the problem without any tracking</p>
</div>
`

// Styles definition
var timerStyle = `
.timer_style {
    border-radius: 2px;
    border:1px solid #E8E8E8;
    background-color: #FAFAFA;
    color: black;
    font-weight: bold;
    padding: 5px;
    margin-right: 10px;
}
.title_style {
    margin: 10;
    text-align: center;
    font-color: #FAFAFA;
    font-weight: bold;
    font-size: 150%;
}
.text_style {
    margin: 10;
    text-align: center;
    font-color: #FAFAFA;
}
.round_style {
    margin: 10;
    text-align: center;
    font-weight: bold;
    border-radius: 2px;
    border:1px solid #E8E8E8;
    background: #FAFAFA;
    padding: 20px; 
    width: 100%;
    height: auto;
}
.round_style:hover {
    background: #FFFFFF;
}

#controlButtons {
    margin: auto;
}
`
// Globals
var sec = 0;
var userId = "";
var userKey = "";
var currentProblem = "";
var problemDifficulty = 'Unknown';
var session = 0;
var webAppURL = "";
var webAppBasic = "";
var jsSubmissionChecktimer;

// Get information from background page (warning, this is totally async!)
chrome.runtime.sendMessage({method: "getWebAppURL"}, function(response) {
    webAppURL = response.data;
    //console.log(webAppURL)
});
chrome.runtime.sendMessage({method: "getWebAppBasic"}, function(response) {
    webAppBasic = response.data;
    //console.log(webAppBasic)
});
chrome.runtime.sendMessage({method: "geUserId"}, function(response) {
    userId = response.data;
    //console.log(userId)
});
chrome.runtime.sendMessage({method: "getUserKey"}, function(response) {
    userKey = response.data;
    //console.log(userKey)
});

// JQuery helper to check for an attribute existence
$.fn.hasAttribute = function(name) {
    return this.attr(name) !== undefined;
}

// Timer functions
var startTime;
var updatedTime;
var difference;
var tInterval;
var savedTime;
var running = 0;

function pad ( val ) {
    return val > 9 ? val : "0" + val;
}

function startTimer(){
    if(!running){
      startTime = new Date().getTime();
      tInterval = setInterval(getShowTime, 1000);
      paused = 0;
      running = 1;
    }
}

function stopTimer(){
    clearInterval(tInterval);
    savedTime = 0;
    difference = 0;
    paused = 0;
    running = 0;
}

function pauseTimer(){
    if (difference && !paused) {
        clearInterval(tInterval);
        savedTime = difference;
        paused = 1;
        running = 0;
    } else {
        startTimer();
    }
}

function resetTimer(){
    clearInterval(tInterval);
    savedTime = 0;
    difference = 0;
    paused = 0;
    running = 0;
    showTime();
}

// Thanks to https://medium.com/@olinations/stopwatch-script-that-keeps-accurate-time-a9b78f750b33
// for the nice timer :D
function getTime() {
    updatedTime = new Date().getTime();
    if (savedTime){
        difference = (updatedTime - startTime) + savedTime;
    } else {
        difference =  updatedTime - startTime;
    }
}

function showTime() {
    var hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((difference % (1000 * 60)) / 1000);

    $("#timer").html(pad(hours) + " Hours " + pad(minutes) + " Minutes " + pad(seconds) + " Seconds");
}

function getShowTime() {
    getTime();
    showTime();
}

// Show the timer
function showTimer() {
    $("#timer").attr("style", "display: visible;");
    timerVisible = true;
}

// Hide the timer
function hideTimer() {
    $("#timer").attr("style", "display: none;");
    timerVisible = false;
}

// Hide the original elements and just show the buttons
function enableMask() {
    $("#controlButtonsTitle").attr("style", "display: visible;");
    $("#controlButtonsText").attr("style", "display: visible;");
    $("#showProblemWithStopwatchAndTrack").attr("style", "display: visible;");
    $("#showProblemNoStopwatchButTrack").attr("style", "display: visible;");
    $("#showProblemNoStopwatchNoTrack").attr("style", "display: visible;");
    $(problemDescriptionElement).attr("style", "display: none;");
    $(codeAreaElement).children(codingPanelElement).attr("style", "visibility: hidden;");

    maskEnabled = true;
}

// Show original hidden elements
function disableMask() {
    $("#controlButtonsTitle").attr("style", "display: none;");
    $("#controlButtonsText").attr("style", "display: none;");
    $("#showProblemWithStopwatchAndTrack").attr("style", "display: none;");
    $("#showProblemNoStopwatchButTrack").attr("style", "display: none;");
    $("#showProblemNoStopwatchNoTrack").attr("style", "display: none;");
    $(problemDescriptionElement).attr("style", "display: visible;");
    $(codeAreaElement).children(codingPanelElement).attr("style", "visibility: visible;");

    maskEnabled = false;
}

// Send the event related to the problem (start, submit) to the remote web service
function sendProblemEvent(problem, event, session) {
    console.log('Info: ' + userId + " " + userKey);
    if (userId == "" || userKey == "") return;

    const req = new XMLHttpRequest();
    let url = new URL(webAppURL + '/events');
    var formData = new FormData();
    formData.append('id', userId);
    formData.append('key', userKey);
    formData.append('clientVersion', chrome.runtime.getManifest().version);
    formData.append('problem', problem);
    formData.append('difficulty', problemDifficulty);
    formData.append('event', event);
    formData.append('session', session);
    console.log('Sending message to: ' + url);

    req.open("POST", url, true)
    req.setRequestHeader('Authorization', webAppBasic);
    req.send(formData);
}

// Get the problem identifier from token of the URL
function getProblem(pageURL) {
    var tokens = pageURL.split("/");

    if (tokens.length >= 2)
        return tokens[tokens.length - 2];

    return "NA";
}

// Get the problem difficulty
function getProblemDifficulty() {
    if ($(questionTitleElement).parent().children().children(difficultyEasyElement).length)
        return easyId;
    if ($(questionTitleElement).parent().children().children(difficultyMediumElement).length)
        return mediumId;
    if ($(questionTitleElement).parent().children().children(difficultyHardElement).length)
        return hardId;
}

// This function can identify if the submit was completed and stop the polling cycle
function checkForSubmitComplete () {
    $(submissionSuccessElement).each(function( index ) {
        if ($(this).parent('[class*=result__]').length) {
            clearInterval(jsSubmissionChecktimer);
            console.log("SUCCESS");
            stopTimer();
            sendProblemEvent(currentProblem, "result_ok", session);
        }
    });
    $(submissionErrorElement).each(function( index ) {
        if ($(this).parent('[class*=result__]').length) {
            clearInterval(jsSubmissionChecktimer);
            console.log("ERROR");
            sendProblemEvent(currentProblem, "result_ko", session);
        }
    });
}

var descriptionTrigger = true;
var codeAreaTrigger = true;
var maskEnabled = true;
var timerVisible = true;
var currenDescriptionLink = "";

function prepareSession() {
    session = Date.now();
    currentProblem = getProblem(currenDescriptionLink);
    console.log("PROBLEM: " + currentProblem);
    disableMask();
    problemDifficulty = getProblemDifficulty();
}

function checkForMutations () {
    if (currenDescriptionLink != "" &&
        $(problemDescriptionTabElement).find('a').attr('href') != currenDescriptionLink) {
        currenDescriptionLink = $(problemDescriptionTabElement).find('a').attr('href');
        console.log("NEW PROBLEM: " + currenDescriptionLink);
        clearInterval(jsSubmissionChecktimer);
        resetTimer();
        showTimer();
        enableMask();
    }

    if (!$(problemDescriptionElement).length) {
        descriptionTrigger = true;
    } else if ($(problemDescriptionElement).length && descriptionTrigger) {
        descriptionTrigger = false;
        console.log("DESC CREATED!");

        if (maskEnabled) {
            $(problemDescriptionElement).attr("style", "display: none;");

            if (!$('#controlButtons').length) {
                // store the current Description URL, that will later used to understand if the
                // content is changed
                currenDescriptionLink = $(problemDescriptionTabElement).find('a').attr('href');

                $(customControlButtons).insertBefore($(problemDescriptionElement));

                // set the callbacks on click on button
                $("#showProblemWithStopwatchAndTrack").click(function(e) {
                    // if the coding panel is not clean
                    if ($(resetCodeButton)[0] !== undefined) {
                        // trigger the reset of the code
                        $(resetCodeButton)[0].click();
                    } else if ($(resetCodeButtonWarn)[1] !== undefined) {
                        // trigger the reset of the code
                        $(resetCodeButtonWarn)[1].click();
                    } else {
                        prepareSession();
                        startTimer();
                        sendProblemEvent(currentProblem, "start", session);
                    }
                });
                $("#showProblemNoStopwatchButTrack").click(function(e) {
                    // if the coding panel is not clean
                    if ($(resetCodeButton)[0] !== undefined) {
                        // trigger the reset of the code
                        $(resetCodeButton)[0].click();
                    } else if ($(resetCodeButtonWarn)[1] !== undefined) {
                        // trigger the reset of the code
                        $(resetCodeButtonWarn)[1].click();
                    } else {
                        prepareSession();
                        hideTimer();
                        sendProblemEvent(currentProblem, "start", session);
                    }
                });
                $("#showProblemNoStopwatchNoTrack").click(function(e) {
                    prepareSession();
                    hideTimer();
                    sendProblemEvent(currentProblem, "start_no_track", session);
                });
            }
        }
    }

    if (!$(codeAreaElement).length &&
        !$(codeAreaElement).children(codingPanelElement).length) {
        codeAreaTrigger = true;
        clearInterval(jsSubmissionChecktimer);
    } else if ($(codeAreaElement).length &&
                $(codeAreaElement).children(codingPanelElement).length &&
                codeAreaTrigger) {
        codeAreaTrigger = false;
        console.log("CODE CREATED!");

        if (maskEnabled) {
            // hide the coding panel
            // use "visibility" to keep the space in the layout
            $(codeAreaElement).children(codingPanelElement).attr("style", "visibility: hidden;");
        }

        // add the timer near the submission buttons
        $('<label id="timer" class="timer_style" style="display: none;">00 Hours 00 Minutes 00 Seconds</label>').insertBefore($(runCodeButton));
        if (timerVisible)
            showTimer();

        $(submitCodeButton).click(function(e) {
            console.log("SUBMIT");
            clearInterval(jsSubmissionChecktimer);
            jsSubmissionChecktimer = setInterval(checkForSubmitComplete, 500);
        });
    }
};

// Main onLoadPage function, starts the cycles needed to discover the elements inside the page
// and to attach listeners to them
function onLoadPage (evt) {
    // insert the styles for the custom components
    var styleSheet = document.createElement("style")
    styleSheet.type = "text/css"
    styleSheet.innerText = timerStyle
    document.head.appendChild(styleSheet)

    setInterval(checkForMutations, 500);
}
