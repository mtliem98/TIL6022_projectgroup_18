import pandas as pd
import matplotlib.pyplot as plt

# cities, number of inhabitants, daily travelers (NS Dashboard)
cities = [["Steenwijk", 17500, 3007,],
            ["Heerenveen", 31000, 5001],
            ["Meppel", 32000, 6386],
            ["Beilen", 115000, 1824],
            ["Hoogeveen", 41000, 3782],
            ["Wolvega", 13500, 1394],
            ["Haren", 18500, 1104],
            ["Dronten", 31000, 2931],
            ["Kampen", 38830, 1618],
            ["Lelystad", 85000, 12592],
            ["Groningen", 211500, 12592],
            ["Leeuwarden", 92000, 7705],
            ["Assen", 70000, 7548],
            ["Akkrum", 3000, 769]]


df = pd.DataFrame (cities, columns=['city','inhabitants', 'travelers per day'])

# Excluding cities bigger than 50 000 inhabitants and cities smaller than 10 000 inhabitants
df = df[df['inhabitants'] <= 50000]
df = df[df['inhabitants'] >= 10000]
print(df)

# calculating factor: number of daily travelers / number of inhabitants
factors = []
for i in range(len(df)):
    factor = df.iloc[i,2]/df.iloc[i,1]
    print(f"{df.iloc[i, 0]}: {factor:.4f}")
    factors.append(factor)
    average = sum(factors)/(len(factors))

print(f"average factor: {average:.4f}")

# calculating the amount of travelers per day for Drachten and Emmeloord
Inhabitants_Emmeloord = 27500
Inhabitants_Drachten = 46000

Predicted_travelers_Emmeloord = Inhabitants_Emmeloord * average
Predicted_tarvelers_Drachten = Inhabitants_Drachten * average

print(f"Travelers Emmeloord: {Predicted_travelers_Emmeloord:.0f}")
print(f"Travelers Drachten: {Predicted_tarvelers_Drachten:.0f}")

# Plotting inhabitants and travelers per day 
df['factor'] = df['travelers per day'] / df['inhabitants']
print(df[['city', 'factor']])

plt.scatter(df['inhabitants'], df['travelers per day'])
plt.xlabel('Number of inhabitants')
plt.ylabel('Travelers per day NS station')
plt.title('City population and daily travelers at NS stations')
plt.show()