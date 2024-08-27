# Pendulum Balancing AI

This Python program simulates a double pendulum on a cart that can move within the range of -1 ≤ x ≤ 1. An AI, trained using reinforcement learning, balances the pendulum upside down.

AI inputs:

- horizontal position of the cart
- horizontal velocity of the cart
- horizontal position of the first bob
- vertical position of the first bob
- angular velocity of the first bob
- horizontal position of the second bob
- vertical position of the second bob
- angular velocity of the second bob

AI output:

- horizontal acceleration for the cart

## Dependencies

- [`pygame`](https://www.pygame.org): used for rendering
- [`numpy`](https://numpy.org): used for ai training and execution
- [`psutil`](https://pypi.org/project/psutil/): only used for training; optional
- [`pytest`](https://docs.pytest.org): required for testing, otherwise optional

## File overview

- `src/render.py` - run to simulate the pendulum <b>without</b> the AI
- `src/render_ai.py` - run to simulate the pendulum <b>with</b> the AI
- `src/train.py` - run to train the AI
- `src/ai` - core of the AI with the classes "Agent" and "ReinforcementLearningModel"
- `src/pendulum.py` - pendulum simulation
- `src/util.py` - two dimensional vector class `Vec`
- `tests/*` - run using `pytest`
- `src/gen/*` - files containing the best weights and biases of individual generations
- `showcase/*` - example videos

## Usage

### Running program

Simulate the pendulum without the AI:
`python3 src/render.py`

> Optional arguments:
>
> - `--angular-damping [float]` (default: 0.1)
> - `--horizontal-damping [float]` (default: 0.3)
> - `--gravity [float]` (default: 9.81)

> User inputs:
>
> - `r` - reset pendulum
> - `scroll` - accelerate the pendulum to the left or right

Simulate the pendulum with the AI:
`python3 src/render_ai.py`

> Optional arguments:
>
> - `--gen [int]` (default: -1)
> - `--angular-damping [float]` (default: 0.1)
> - `--horizontal-damping [float]` (default: 0.3)
> - `--gravity [float]` (default: 9.81)

> User inputs:
>
> - `r` - reset pendulum
> - `t` - toggle ai
> - `scroll` - accelerate the pendulum to the left or right

Train the AI:
`python3 src/train.py`

> Optional arguments:
>
> - `--time [float]` (default: 60)
> - `--random-start [bool]` (default: False)
> - `--distract [bool]` (default: False)

## Generations

The training process has saved the state of each generation in the `src/gen/` directory.

## Todo

- save the parameters for every generation
- save the score function for every generation
- add external options file to replace command line arguments
- fix physics or create more readable & understandable equation
- documentation
