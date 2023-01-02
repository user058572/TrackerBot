import pandas as pd

olymp_index = []
olymps = []

with open('РсОШ олимпиады.txt', 'r', encoding="utf8") as file:
    olympiad = file.readlines()
    for i in olympiad:
        olymp_index.append(i.split(' - ')[0])
        olymps.append(i.split(' - ')[1][:-1])

print(olymp_index, olymps)
df = pd.DataFrame({
                    'Номер олимпиады': olymp_index,
                    'Олимпиада': olymps
                   })

df = df.sort_values('Олимпиада')
print(df)
df.to_excel('РсОШ олимпиады.xlsx')
