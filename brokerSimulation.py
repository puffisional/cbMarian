from cbMarian.broker import Broker
from cbMarian.simulatedClient import SimulatedClient
from coinbasepro.authenticated_client import AuthenticatedClient

from simulatedEnvironment import SimulatedEnvironment

if __name__ == "__main__":

    simEnv = SimulatedEnvironment()
    sc = SimulatedClient(simEnv, 0)
    print(sc.get_currencies())

    ac = Broker("LTC-EUR", *Broker.getCredentials())

    lastBrokerDeals = ac.brokerDeals["closed"]

    side = lastBrokerDeals[0]["side"]
    dealList = []
    for index, lastBrokerDeal in enumerate(lastBrokerDeals):
        dealList.append((float(lastBrokerDeal["price"]), lastBrokerDeal))
        if lastBrokerDeal["side"] != side:
            # lastBrokerDeal = lastBrokerDeals[index - 1]
            break

    sortedDeals = sorted(dealList, key=lambda x: x[0])
    print(sortedDeals)