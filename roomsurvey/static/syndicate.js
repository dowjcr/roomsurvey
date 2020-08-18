var invitees = [];
var oldHtml;

function clearUsers() {
    var mycrsid = document.getElementById("mycrsid").value;
    invitees = [mycrsid];
    updateUserList();
}

function htmlEncode(str) {
    return str.replace(/[\u00A0-\u9999<>\&]/gim, function(i) {
        return '&#'+i.charCodeAt(0)+';';
    });
}

function updateUserList() {
    var userListControl = document.getElementById("userlist");
    var userList = "";
    var first = true;
    invitees.forEach(function(invitee) {
        if (first) {
            first = false;
        } else {
            userList = userList.concat(", ");
        }

        userList = userList.concat(htmlEncode(invitee));
    });

    userListControl.innerHTML = userList;
}

function addUser() {
    var crsidInput = document.getElementById("crsid");
    var crsid = crsidInput.value;
    crsidInput.value = "";

    // TODO: some soft validation here

    invitees.push(crsid);

    updateUserList();
}

function showFinalCheck() {
    var contentControl = document.getElementById("content");
    oldHtml = contentControl.innerHTML;

    var html = "<h1>Final check</h1><p>You are about to create a syndicate and invite the following members:</p><ul>";

    invitees.forEach(function(invitee) {
        html = html.concat("<li>" + htmlEncode(invitee) + "</li>");
    });

    html = html.concat('</ul><button class="btn btn-primary" onclick="submit()">Yes, create it.</button> <button class="btn btn-secondary" onclick="restorePage()">No, take me back!</button>')

    contentControl.innerHTML = html;
}

function restorePage() {
    document.getElementById("content").innerHTML = oldHtml;
}

function submit() {
    alert("ok");
}

clearUsers();

(function() {
    document.getElementById("crsid").addEventListener("keyup", function(ev) {
        if (ev.keyCode === 13) {
            ev.preventDefault();
            addUser();
        }
    });
})();
