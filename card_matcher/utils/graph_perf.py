import matplotlib.pyplot as plt
import json
import os

main_dir = os.path.dirname(os.path.abspath(__file__))

with open(f'{main_dir}/performance.json', 'r') as infile:
    data = json.load(infile)

fig, ax = plt.subplots(len(data))

for i, name in enumerate(data):
    time = data[name]['time']
    sim = data[name]['sim']
    ax[i].plot(time)
    ax[i].set_xlim([0, len(time)])
    ax[i].set_ylim([0, 0.2])
    ax[i].set_xlabel(name)

    ax2 = ax[i].twinx()
    ax2.plot(sim)
    ax2.set_ylim([0, 100])

# plt.xlim([0, 50])
plt.show()
