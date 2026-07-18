$(document).ready(function () {



    // Display Speak Message
    eel.expose(DisplayMessage)
    function DisplayMessage(message) {

        $(".siri-message li:first").text(message);
        $('.siri-message').textillate('start');

    }

    // Display hood
    eel.expose(ShowHood)
    function ShowHood() {
        $("#Oval").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
    }

    // All about chat history box  
    eel.expose(senderText)
    function senderText(message) {
        var chatBox = document.getElementById("chat-canvas-body");
        if (message.trim() !== "") {
            var row = document.createElement('div');
            row.className = 'row justify-content-end mb-4';
            var widthDiv = document.createElement('div');
            widthDiv.className = 'width-size';
            var msgDiv = document.createElement('div');
            msgDiv.className = 'sender_message';
            msgDiv.textContent = message;
            widthDiv.appendChild(msgDiv);
            row.appendChild(widthDiv);
            chatBox.appendChild(row);
    
            // Scroll to the bottom of the chat box
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }

    eel.expose(receiverText)
    function receiverText(message) {

        var chatBox = document.getElementById("chat-canvas-body");
        if (message.trim() !== "") {
            var row = document.createElement('div');
            row.className = 'row justify-content-start mb-4';
            var widthDiv = document.createElement('div');
            widthDiv.className = 'width-size';
            var msgDiv = document.createElement('div');
            msgDiv.className = 'receiver_message';
            msgDiv.textContent = message;
            widthDiv.appendChild(msgDiv);
            row.appendChild(widthDiv);
            chatBox.appendChild(row);
    
            // Scroll to the bottom of the chat box
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        
    }

   

});