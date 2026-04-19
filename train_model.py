import pickle
from sklearn.ensemble import RandomForestClassifier

X = [
    [20, 1],
    [100, 0],
    [30, 1],
    [120, 0],
]

y = [0, 2, 0, 2]

model = RandomForestClassifier()
model.fit(X, y)

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("model created")