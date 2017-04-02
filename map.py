#!/usr/bin/env python3
import subprocess, string, sys, BTEdb, base64, json, random, collections, time, traceback
import twisted.protocols.basic
from twisted.internet import reactor, protocol, ssl

#debug = True
debug = False

maps = collections.defaultdict(lambda: 0)

def handle(lines):
    if len(lines) == 0:
        return
    try:
        path = [k.split()[1] for k in lines if "Path" in k][0].split("!")
        i = 0
        while i < len(path) - 1:
            p = ("\"" + path[i + 1] + "\" -> \"" + path[i] + "\"")
            maps[p] = maps[p] + 1
            i += 1
    except:
        print(traceback.format_exc())


class client(twisted.protocols.basic.LineReceiver):
    delimeter = "\n"
    MAX_LENGTH = 16384 * 100

    def sl(self, line):
        if debug:
            print("Send: " + line)
        self.sendLine(line.encode("utf-8"))

    def __init__(self):
        self.max = 0
        self.min = 0
        self.in_message = False
        self.this_message = []
        self.groups = ["ctl", "overchan.overchan", "overchan.random", "overchan.test"]

    def lineReceived(self, data):
        data = data.decode("utf-8")
        if debug:
            print("Recv: " + data)
        if len(data.split()) == 0:
            self.this_message.append("")
            return
        elif self.in_message:
            if data == "." or (len(data.split()) > 0 and data.split()[0] == "430"):
                self.in_message = False
                handle(self.this_message)
                self.cur += 1
                if self.cur < self.max:
                    print("On article " + str(self.cur))
                    self.sl("ARTICLE " + str(self.cur))
                    self.in_message = True
                    self.this_message = []
                else:
                    if len(self.groups) == 0:
                        self.sl("QUIT")
                    else:
                        self.sl("GROUP " + self.groups[0])
                        self.groups = self.groups[1:]
            else:
                self.this_message.append(data)
        data = data.split()
        if data[0] == "200":  # posting allowed
            # self.sl("AUTHINFO USER " + user)
        # if data[0] == "381":  # password required
            # self.sl("AUTHINFO PASS " + pw)
        # if data[0] == "281":  # authentication success
            self.sl("GROUP " + self.groups[0])
            self.groups = self.groups[1:]
        if data[0] == "211":  # group stats
            self.min = int(data[2])
            self.max = int(data[3])
            #self.max = 20 # DEBUG!!
            self.cur = self.min
            self.sl("ARTICLE " + str(self.min))
            self.in_message = True
        if data[0] == "205":  # bai
            reactor.stop()
            # sys.exit(0)
    def lineLengthExceeded(self, line):
        print("super long line")
        if "\n" in line.decode("utf-8"):
            print("FUCK")


class fac(protocol.ClientFactory):
    protocol = client


# this connects the protocol to a server running on port 8000
reactor.connectTCP("10.8.0.1", 1199, fac())
reactor.run()

# print(messages)
final = """digraph test {
    ratio=1;
    splines=true;
    overlap=false;
    graph [overlap = false];
""" + "\n\t".join([x + " [label = " + str(y) + "];" for x, y in maps.items()]) + "\n" + "}"
print(final)
open("test", "w").write(final)
