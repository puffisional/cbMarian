from cbMarian.broker import Broker
from cbMarian.simulatedClient import SimulatedClient
from coinbasepro.authenticated_client import AuthenticatedClient

from simulatedEnvironment import SimulatedEnvironment

if __name__ == "__main__":

    simEnv = SimulatedEnvironment()
    sc = SimulatedClient(simEnv, 0)
    print(sc.get_currencies())

    ac = AuthenticatedClient(*Broker.getCredentials())
    print(ac.get_fundings())