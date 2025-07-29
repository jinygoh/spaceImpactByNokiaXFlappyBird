# Flappy Impact Crash Course

This document provides a high-level overview of the Flappy Impact game's codebase.

## File Structure

- `index.html`: The main entry point of the application. It contains the basic HTML structure and includes the CSS and JavaScript files.
- `style.css`: Contains the styling for the game, including the canvas and game container.
- `script.js`: The core of the game. It contains all the game logic, including the game loop, entities, and state management.
- `CRASH_COURSE.md`: This file.

## Game Architecture

The game is built using a simple game loop and a state machine. The main components are:

### Game Class

The `Game` class is the central part of the application. It manages:

- **Game State**: The game can be in one of the following states: `MAIN_MENU`, `LEVEL_TRANSITION`, `GAMEPLAY`, `PAUSE`, or `GAME_OVER`.
- **Game Loop**: The `run()` method in the `Game` class is the main game loop. It calls `handleInput()`, `update()`, and `draw()` on every frame.
- **Entities**: The game manages all game objects (player, enemies, bullets, etc.) in arrays within the `Game` class.
- **Levels**: The game has a simple level system that increases the difficulty and introduces a boss at the end of each level.

### Sprite Classes

All game objects inherit from the `Sprite` class. The main sprite classes are:

- **Player**: The player's ship, controlled by the user.
- **Enemy**: The base class for all enemies. There are different types of enemies with unique behaviors:
    - `Drone`: A simple enemy that moves from right to left.
    - `Weaver`: An enemy that moves in a sine wave pattern.
    - `Shooter`: An enemy that shoots bullets at the player.
- **Boss**: A powerful enemy that appears at the end of each level.
- **Bullet**: A projectile fired by the player.
- **EnemyBullet**: A projectile fired by enemies.
- **PowerUp**: An item that gives the player a temporary advantage.
- **Star**: A background object that creates a parallax effect.

### State Management

The `gameState` property in the `Game` class determines the current state of the game. The `draw()` method renders different screens based on the current game state.

### Collision Detection

The `checkCollision()` method in the `Game` class is used to detect collisions between game objects. The `update()` method checks for collisions between:

- Player and enemies/bullets
- Player bullets and enemies/boss
- Player bullets and enemy bullets

## How to Play

- **Start**: Press `Enter` on the main menu to start the game.
- **Flap**: Press the `Space` bar to make the player's ship "flap" upwards.
- **Shoot**: Press the `X` key to shoot bullets.
- **Pause**: Press the `P` key to pause and resume the game.
- **Restart**: Press `Enter` on the game over screen to return to the main menu.
