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

# Time (in unix format) to show room allocations
SHOW_ALLOCATIONS = 9999999999

# Time (in unix format) to open the room survey
SHOW_SURVEY      = 9999999999

# Are room reviews open yet?
ROOM_REVIEWS = False

# The maximum size for syndicates in each year
SYNDICATE_MAXSIZE = {
    1: 6, # First-year syndicates can contain up to 6
    2: 8  # and second-years get up to 8
}
