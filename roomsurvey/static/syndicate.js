var invitees = [];
var inviteeNames = [];
var oldHtml;

function clearUsers() {
    var mycrsid = document.getElementById("mycrsid").value;
	var myname = document.getElementById("myname").value;
	inviteeNames = [myname];
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
    inviteeNames.forEach(function(invitee) {
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

	var feedback = document.getElementById("invalid-feedback");

	// Validate the input

	function resetInput() {
		crsidInput.removeAttribute("disabled");
		crsidInput.value = "";
		crsidInput.classList.remove("is-invalid");
		feedback.innerHTML = "";
	}

	if (invitees.includes(crsid)) {
		resetInput();
		crsidInput.classList.add("is-invalid");
		feedback.innerHTML = "You have already added this person.";
		return;
	}

	if (invitees.length == 8) {
		resetInput();
		crsidInput.classList.add("is-invalid");
		feedback.innerHTML = "The maximum syndicate size is 8";
		return;
	}
	
	crsidInput.setAttribute("disabled", "true");
	crsidInput.value = "Please wait...";

	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {

		if (this.readyState == 4 && this.status == 200) {
			var resp = JSON.parse(xhttp.responseText);

			resetInput();

			if (resp["ok"]) {
				invitees.push(crsid);
				inviteeNames.push(resp["name"]);
				updateUserList();
				return;
			}

			crsidInput.classList.add("is-invalid");
			feedback.innerHTML = resp["reason"];
		} else if (this.readyState == 4) {
			// The request has finished but was not successful
			// just allow it anyway, the _real_ validation is server-side
			console.log("WARN: request failed");
			resetInput();
		}

	};

	xhttp.open("GET", "/api/is_syndicatable/"+crsid, true);
	xhttp.send();
}

function showFinalCheck() {
    var contentControl = document.getElementById("content");
    oldHtml = contentControl.innerHTML;

    var html = "<h1>Final check</h1><p>You are about to create a syndicate and invite the following members:</p><ul>";

    inviteeNames.forEach(function(invitee) {
        html = html.concat("<li>" + htmlEncode(invitee) + "</li>");
    });

    html = html.concat('</ul><div class="form-check"><input class="form-check-input" id="want-to-stay-input" type="checkbox" /><label class="form-check-label" for="want-to-stay-input">Please tick this box if your syndicate hope to stay in their current rooms.</label></div><br /><button class="btn btn-primary" onclick="submit()">Yes, create it.</button> <button class="btn btn-secondary" onclick="restorePage()">No, take me back!</button>')

    contentControl.innerHTML = html;
}

function restorePage() {
    document.getElementById("content").innerHTML = oldHtml;
}

function submit() {
	document.getElementById("invitees").value = JSON.stringify(invitees);
	
	var wantToStay = document.getElementById("want-to-stay-input").checked;
	document.getElementById("want-to-stay").value = wantToStay ? "yes" : "no";

	document.getElementById("syndicate-form").submit();
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
