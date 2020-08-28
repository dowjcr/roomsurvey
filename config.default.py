# This is used to sign sessions
# change it and keep it secret!!
SECRET_KEY = "development1337"

# Trusted hostnames for Raven authentication
# TRUSTED_HOSTS = {"localhost"}
TRUSTED_HOSTS = {"ballot.downingjcr.co.uk"}

# URL to the embedded CognitoForms page
COGNITOFORMS_URL = "https://www.cognitoforms.com/f/your_form"

# Key to be sent by CognitoForms along with the form data
# change it and keep it secret!!
COGNITOFORMS_KEY = "development1337"

# Time (in unix format) to close syndicate creation
CLOSE_SYNDICATES = 9999999999
