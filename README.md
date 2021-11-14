# Simulations

This is an ensemble of scripts using PyGame.

## List of simulations

- [Covid-19](/CovidSimulation.py) : is a basic simulation for Covid-19 contagion.

  ![Covid-19 simulation](/Doc/Covid_sim.png)
  ![Covid-19 results](/Doc/Covid_results.png)

- [Covid-19](/AdvanceCovidSimulation.py) : is an advance simulation for Covid-19 contagion.

  - It takes in consideration the mortality rate.
  - Adds some randomness to the likelihood of fatal infections.
  - Adds randomness margin to the recovery time.
  - Better handling of collisions.
  - Add walls so it can be an enclosed environment.

  ![Covid-19 simulation](/Doc/AdvanceCovid_sim.png)
  ![Covid-19 results](/Doc/AdvanceCovid_results.png)

- [Dum AI](/SimAI.py) : is an simple AI simulation.

  - Choose a random action.
  - Change it action based on the time spend without reward.
  - Keep taking the same action while getting reward.
  - The time spend without depends on its' tolerance.

  ![AI simulation](/Doc/SimAI.png)
  ![AI results](/Doc/ResultAI.png)

## List of games

- [Eat me](/Game.py) : is a game where you use your mouse to eat the blobs.
  ![Game eat me](/Doc/eat_me.png)

## Requirement

- Pygame
- Pymunk
- Matplotlib
- Pandas
- Numpy
