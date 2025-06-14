$(document).ready(function () {
    
    eel.expose(hideStart);
    function hideStart() {
        console.log("hideStart called"); // <-- Debug log
        $("#Start").hide();              // Hide Start
        setTimeout(function () {         // Add a 5-second timeout
            $("#Oval").show();           // Show Oval after timeout
            $("#Oval").addClass("animate__animated animate__zoomIn"); // Add animation
        }, 5000); // 5000 milliseconds = 5 seconds
    }

});