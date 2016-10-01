import os, sys
from netifaces import interfaces, ifaddresses, AF_INET
import time_uuid
import pickle
import ConfigParser
from watchdog.observers import Observer
#from constants import *
from exceptions import *
from constants.events import *
from constants.states import *
from communication import *
from communication.election_communication import *
from watching import *
from shared.book import CommonlogBook
from config import SERVER_DAEMON_HOST, SERVER_DAEMON_PORT, FOLDER, MCAST_IP, MCAST_PORT
from protocols import FilemonitorClientFactory, FilemonitorClientProtocol
from utils.utils import get_ips
from twisted.internet import reactor
from consensus.beacon import *
from server import *


def update_about_file_changes():
    factory = FilemonitorClientFactory()
    reactor.connectTCP(SERVER_DAEMON_HOST, SERVER_DAEMON_PORT, factory)

def main():
    ips = get_ips()
    print ips
    ip = input('Enter index of ip addr:')
    timeuuid = time_uuid.TimeUUID.with_utcnow()  # generate uuid
    book = CommonlogBook(identity=timeuuid, state=0, ip = ips[ip-1])  # creating shared memory between server and election daemon

    Config = ConfigParser.ConfigParser()
    print os.path.expanduser('~')
    print os.path.join(os.path.expanduser('~'), 'iwant.conf')
    Config.read(os.path.join('/home/'+os.getenv('SUDO_USER'),'iwant.conf'))
    SHARING_FOLDER = Config.get('Paths', 'share')
    if not os.path.exists(SHARING_FOLDER):
        raise MainException(1)

    try:
        reactor.listenMulticast(MCAST_ADDR[1], CommonroomProtocol(book), listenMultiple=True)  # spawning election daemon
        endpoints.serverFromString(reactor, 'tcp:{0}'.format(SERVER_DAEMON_PORT)).listen(backendFactory(SHARING_FOLDER, book))  # spawning server daemon
        ScanFolder(SHARING_FOLDER, update_about_file_changes)  # spawning filemonitoring daemon
        reactor.run()
    except KeyboardInterrupt:
        observer.stop()
        reactor.stop()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

if __name__ == '__main__':
    main()