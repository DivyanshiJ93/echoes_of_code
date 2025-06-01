


# Echoes of Code



**Echoes of Code** is a 2D top-down puzzle game built with Python and PyGame. In this game, you play as a software engineer trapped in a glitched digital world. Every 10 seconds, time resets, and your past actions are replayed by ghost clones called "echoes." Use these echoes strategically to solve puzzles and escape the loop.

## 🧩 Gameplay Overview

- **Time Loop Mechanics**: Every 10 seconds, the game resets, and your previous actions are replayed by echoes.
- **Echo Collaboration**: Utilize echoes to activate pressure plates, open gates, and solve complex puzzles.
- **Strategic Planning**: Plan your moves carefully to ensure your echoes assist rather than hinder your progress.

## 🚀 Features

- **Innovative Time-Loop Mechanic**: Collaborate with past versions of yourself to solve puzzles.
- **Interactive Game Objects**: Engage with pressure plates, gates, and other interactive elements.
- **Modular Level Design**: Easily extend the game with new levels and challenges.
- **Cross-Platform Compatibility**: Runs on Windows, macOS, and Linux.

## 🖥️ Installation

### Prerequisites

- Python 3.6 or higher
- pip package manager

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/echoes-of-code.git
   cd echoes-of-code
````

2. **Create a Virtual Environment (Optional but Recommended)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Game**

   ```bash
   python echoes_of_code.py
   ```

## 🎮 Controls

* **Arrow Keys**: Move the player character.
* **Spacebar**: Interact with objects (e.g., pressure plates).
* **R**: Reset the current level.
* **Esc**: Quit the game.

## 🛠️ Development

### Directory Structure

```plaintext
echoes-of-code/
├── assets/                 # Game assets (images, sounds)
├── levels/                 # Level definitions
├── echoes_of_code.py       # Main game file
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

### Key Modules

* **TimerManager**: Handles the time loop mechanics.
* **Player**: Manages player actions and interactions.
* **Echo**: Replays recorded player actions.
* **LevelManager**: Loads and manages game levels.

## 🧪 Testing

To run the test suite:

```bash
python -m unittest discover tests
```

Ensure all tests pass before submitting a pull request.

## 📦 Packaging

To package the game for distribution:

1. **Install PyInstaller**

   ```bash
   pip install pyinstaller
   ```

2. **Create Executable**

   ```bash
   pyinstaller --onefile echoes_of_code.py
   ```

The executable will be located in the `dist/` directory.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.

2. Create a new branch:

   ```bash
   git checkout -b feature/YourFeatureName
   ```

3. Commit your changes:

   ```bash
   git commit -m "Add your message here"
   ```

4. Push to your forked repository:

   ```bash
   git push origin feature/YourFeatureName
   ```

5. Open a pull request detailing your changes.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📬 Contact

For questions or suggestions:

* **GitHub Issues**: [Submit an issue](https://github.com/DivyanshiJ93/echoes-of-code/issues)

---

*Happy looping!*

```
