class User:

    def __init__(self, firstname, lastname, username):
        self.firstname = firstname
        self.lastname = lastname
        self.displayname = firstname + lastname
        self.username = username