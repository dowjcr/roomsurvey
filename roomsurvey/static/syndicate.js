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

	let maxSize = parseInt(document.getElementById("maxsize").value);

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

	if (invitees.length == maxSize) {
		resetInput();
		crsidInput.classList.add("is-invalid");
		feedback.innerHTML = "The maximum syndicate size is "+maxSize.toString()+".";
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

	let year = document.getElementById("myyear").value;
	xhttp.open("GET", "/api/is_syndicatable/"+year+"/"+crsid, true);
	xhttp.send();
}

function showFinalCheck() {
    var contentControl = document.getElementById("content");
    oldHtml = contentControl.innerHTML;

    var html = "<h1>Final check</h1><p>You are about to create a syndicate and invite the following members:</p><ul>";

    inviteeNames.forEach(function(invitee) {
        html = html.concat("<li>" + htmlEncode(invitee) + "</li>");
    });

    html = html.concat('</ul><button class="btn btn-primary" onclick="submit()">Yes, create it.</button> <button class="btn btn-secondary" onclick="restorePage()">No, take me back!</button>')

    contentControl.innerHTML = html;
}

function restorePage() {
    document.getElementById("content").innerHTML = oldHtml;
}

function submit() {
	document.getElementById("invitees").value = JSON.stringify(invitees);
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
