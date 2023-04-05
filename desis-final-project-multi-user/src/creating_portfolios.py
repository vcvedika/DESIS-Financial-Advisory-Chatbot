import pickle

Aastha = {'GOOG': 50, 'TSLA': 70}
Dakshita = {'AAPL': 100}
Pranjal = {'GS': 75, 'AAPL': 40}
Soumi = {'GOOG': 200}
Vedika = {'AMZN': 200}

with open('aastha_portfolio.pkl', 'wb') as f1:
    pickle.dump(Aastha, f1)
with open('dakshita_portfolio.pkl', 'wb') as f2:
    pickle.dump(Dakshita, f2)
with open('pranjal_portfolio.pkl', 'wb') as f3:
    pickle.dump(Pranjal, f3)
with open('soumi_portfolio.pkl', 'wb') as f4:
    pickle.dump(Soumi, f4)
with open('vedika_portfolio.pkl', 'wb') as f5:
    pickle.dump(Vedika, f5)

# with open('aastha_portfolio.pkl', 'rb') as f:
#     portfolio = pickle.load(f)

# print(portfolio)
