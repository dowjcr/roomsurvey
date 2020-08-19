var crsid = document.getElementById("mycrsid").value;
var formToken = document.getElementById("myformtoken").value;

Cognito.prefill({ CRSid: crsid, FormToken: formToken });
