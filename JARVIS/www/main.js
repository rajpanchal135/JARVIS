$(document).ready(function () {

    $('.text').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "bounceIn",
        },
        out: {
            effect: "bounceOut",
        },

    });

    // Siri configuration
    var siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: 800,
        height: 200,
        style: "ios9",
        amplitude: "1",
        speed: "0.30",
        autostart: true
      });

    // Siri message animation
    $('.siri-message').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "fadeInUp",
            sync: true,
        },
        out: {
            effect: "fadeOutUp",
            sync: true,
        },

    });

    // mic button click event

    $("#MicBtn").click(function () { 
        eel.playAssistantSound()
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        eel.allCommands()()
    });

    function doc_keyUp(e) {
        // this would test for whichever key is 40 (down arrow) and the ctrl key at the same time

        if (e.key === 'j' && e.metaKey) {
            eel.playAssistantSound()
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            eel.allCommands()()
        }
    }
    document.addEventListener('keyup', doc_keyUp, false);

    eel.expose(hideOval)
    function hideOval() {
        $("#Oval").attr("hidden", true);
    }

    eel.expose(showSiriWave)
    function showSiriWave() {
        $("#SiriWave").attr("hidden", false);
    }

    // // to play assisatnt 
    function PlayAssistant(message) {

        if (message != "") {

            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            eel.allCommands(message);
            $("#chatbox").val("")
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);

        }

    }

    // // toogle fucntion to hide and display mic and send button 
    function ShowHideButton(message) {
        if (message.length == 0) {
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);
        }
        else {
            $("#MicBtn").attr('hidden', true);
            $("#SendBtn").attr('hidden', false);
        }
    }

    // // key up event handler on text box
    $("#chatbox").keyup(function () {

        let message = $("#chatbox").val();
        ShowHideButton(message)
    
    });
    
    // send button event handler
    $("#SendBtn").click(function () {
    
        let message = $("#chatbox").val()
        PlayAssistant(message)
    
    });
    

    // enter press event handler on chat box
    $("#chatbox").keypress(function (e) {
        key = e.which;
        if (key == 13) {
            let message = $("#chatbox").val()
            PlayAssistant(message)
        }
    });

    // Time and Date Widget
    function updateTime() {
        const now = new Date();
        let hours = now.getHours();
        let minutes = now.getMinutes();
        let ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; // the hour '0' should be '12'
        minutes = minutes < 10 ? '0' + minutes : minutes;
        
        const timeString = hours + ':' + minutes + ' ' + ampm;
        document.getElementById('clock-display').innerText = timeString;

        const options = { weekday: 'long', month: 'short', day: 'numeric' };
        document.getElementById('date-display').innerText = now.toLocaleDateString(undefined, options).toUpperCase();
    }
    setInterval(updateTime, 1000);
    updateTime();

    // System Stats Widget
    setInterval(async function() {
        try {
            let stats = await eel.get_system_stats()();
            if (stats) {
                document.getElementById('cpu-stat').innerText = stats.cpu + '%';
                document.getElementById('ram-stat').innerText = stats.ram + '%';
                document.getElementById('bat-stat').innerText = stats.battery + '%';
            }
        } catch (e) {
            console.log("Waiting for backend...");
        }
    }, 2000);

});

// Settings Functions
function changeTheme() {
    let color = document.getElementById("themeColor").value;
    document.documentElement.style.setProperty('--primary-color', color);
    
    // Also update UI specific elements like text shadow
    document.getElementById("clock-display").style.color = color;
    document.getElementById("clock-display").style.textShadow = `0 0 10px ${color}`;
    
    // Tell Python backend to save it
    savePreferences();
}

function savePreferences() {
    let theme = document.getElementById("themeColor").value;
    let voice = document.getElementById("voiceAccent").value;
    let wakeWord = document.getElementById("wakeWord").value;
    
    eel.save_preferences(theme, voice, wakeWord)();
}

// Load preferences on startup
async function loadPreferences() {
    let prefs = await eel.get_preferences()();
    if(prefs) {
        document.getElementById("themeColor").value = prefs.theme || "#00e5ff";
        document.getElementById("voiceAccent").value = prefs.voice || "en-in";
        document.getElementById("wakeWord").value = prefs.wakeWord || "jarvis";
        
        changeTheme(); // Apply the theme immediately
    }
}
loadPreferences();