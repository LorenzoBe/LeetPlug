console.log('Problems page intercepted');
window.addEventListener("load", onLoadPage, false);

// Configuration consts
var problemDescriptionElement = "[data-key='description-content']";
var codingPanelElement = ".content__Ztw-";
var runCodeButton = "[data-cy='run-code-btn']";
var resetCodeButton = ".reset-code-btn__3ADT";

var customControlButtons = `
<div id='controlButtons'>
<p id="controlButtonsText" class="text_style">Choose how to start the problem:</p>
<p id="showProblemWithTimer" class="round_style">Show the problem with time tracking</p>
<p id="showProblemNoTimer" class="round_style">Show the problem without time tracking</p>
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

// JQuery helper to check for an attribute existence
$.fn.hasAttribute = function(name) {
    return this.attr(name) !== undefined;
}

// Timer functions
function pad ( val ) {
    return val > 9 ? val : "0" + val;
}
function updateTimer() {
    $("#timer").html(pad(parseInt(sec/60,10)) + " Minutes " + pad(++sec%60) + " Seconds");
}
function startTimer() {
    var updateTimerInterval = setInterval (updateTimer, 1000);
}
function hideTimer() {
    $("#timer").attr("style", "display: none;");
}

// Show original hidden elements
function showAll() {
    $("#showProblemWithTimer").attr("style", "display: none;");
    $("#showProblemNoTimer").attr("style", "display: none;");
    $(problemDescriptionElement).attr("style", "display: visible;");
    $(codingPanelElement).attr("style", "visibility: visible;");
}

function onLoadPage (evt) {
    // insert the styles for the custom components
    var styleSheet = document.createElement("style")
    styleSheet.type = "text/css"
    styleSheet.innerText = timerStyle
    document.head.appendChild(styleSheet)

    // this function will be called in a loop to wait for dynamic elements creation
    function checkForJSLoadComplete () {
        // check if the problem description element has been created
        if ($(problemDescriptionElement).length && !$(problemDescriptionElement).hasAttribute("style")) {
            console.log('Problem description found');
            // hide the problem description
            // used "display" to free up the space and put the button instead
            $(problemDescriptionElement).attr("style", "display: none;");
            $(customControlButtons).insertBefore($(problemDescriptionElement))

            // set the callbacks on click on button
            $("#showProblemWithTimer").click(function(e) {
                // if the coding panel is not clean
                if ($(resetCodeButton)[0] !== undefined) {
                    // trigger the reset of the code
                    $(resetCodeButton)[0].click();
                } else {
                    showAll();
                    startTimer();
                }
            });
            $("#showProblemNoTimer").click(function(e) {
                showAll();
                hideTimer();
            });
        }
        // check if the coding panel has been created
        if ($(codingPanelElement).length && !$(codingPanelElement).hasAttribute("style")) {
            console.log('Problem coding frame found');
            // hide the coding panel
            // use "visibility" to keep the space in the layout
            $(codingPanelElement).attr("style", "visibility: hidden;");

            // add the timer near the submission buttons
            $('<label id="timer" class="timer_style">00 Minutes 00 Seconds</label>').insertBefore($(runCodeButton))
        }
        // check if all the required elements have been found
        if ($(problemDescriptionElement).length && $(codingPanelElement).length) {
            console.log('Found all the required elements. Disabling polling timer');
            // disable the loop which checks the page content
            clearInterval(jsInitChecktimer);
        }
    }

    // start the polling loop to check when the dynamics components are created
    var jsInitChecktimer = setInterval(checkForJSLoadComplete, 200);
}
