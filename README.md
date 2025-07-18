# Flappy Impact

Flappy Impact is a dynamic side-scrolling shooter game inspired by Flappy Bird and Space Impact by Nokia, built with HTML5 Canvas and JavaScript. Navigate your ship through waves of enemies, collect power-ups, and confront challenging bosses!

## Table of Contents

- [How to Play](#how-to-play)
  - [Controls](#controls)
  - [Objective](#objective)
  - [Gameplay Mechanics](#gameplay-mechanics)
    - [Player](#player)
    - [Enemies](#enemies)
    - [Bosses](#bosses)
    - [Power-ups](#power-ups)
    - [Scoring](#scoring)
    - [Lives](#lives)
    - [Game States](#game-states)

## How to Play

To play the game, simply open the `index.html` file in a modern web browser (like Chrome, Firefox, or Edge).

### Controls

-   **Spacebar:** Make the player ship "flap" (ascend).
-   **X Key:** Shoot bullets.
-   **P Key:** Pause or resume the game during gameplay.
-   **Enter Key:**
    -   Start the game from the Main Menu.
    -   Restart the game from the Game Over screen.

### Objective

The main objective of Flappy Impact is to survive as long as possible by navigating your ship, avoiding obstacles and enemy fire, shooting down enemies, and defeating powerful bosses at the end of each level. Aim for the highest score!

### Gameplay Mechanics

#### Player

-   You control a ship that is a combination of yellow, orange and blue colors.
-   The ship is always moving forward (screen scrolls left).
-   Pressing **Spacebar** gives the ship an upward boost. Gravity will constantly pull it downwards.
-   Touching the top or bottom edges of the screen results in losing a life.
-   Colliding with enemies or enemy bullets will also result in losing a life, unless you are temporarily invincible after a recent hit.

#### Enemies

-   Various types of enemies will appear from the right side of the screen.
-   **Drones (Silver Squares):** Basic enemies that move horizontally.
-   **Weavers (Purple Squares):** Enemies that move in a sine wave pattern.
-   **Shooters (Orange Rectangles):** Enemies that shoot bullets at the player.
-   Shooting enemies earns you points.
-   Enemies may drop power-ups when destroyed.

#### Bosses

-   At the end of each level, you will face a unique boss.
-   **The Warden (Level 1 Boss):** A large, grey boss with specific attack patterns, including burst fire and energy balls.
-   Bosses have a health bar displayed at the top of the screen during the fight.
-   Defeating a boss allows you to proceed to the next level.

#### Power-ups

-   Destroyed enemies have a chance to drop power-ups.
-   **Rapid Fire (Gold Square with 'R'):** Temporarily increases your ship's firing rate.
-   **Shield (Cyan Square with 'S'):** Makes the player invincible for a short period.
-   **Spread Shot (Green Square with 'W'):** Allows the player to shoot three bullets at once.
-   **Homing Missile (Pink Square with 'H'):** Fires missiles that track and destroy enemies.
-   **Score Multiplier (Purple Square with '2x'):** Doubles the points earned from destroying enemies.
-   **Extra Life (Red Square with '1UP'):** Gives the player an extra life.
-   Power-ups are collected by flying into them and last for a limited time. The active power-up and its remaining duration are displayed at the bottom of the screen.

#### Scoring

-   You earn points by:
    -   Destroying enemies.
    -   Defeating bosses.

#### Lives

-   You start the game with 3 lives.
-   Losing a life occurs when:
    -   Colliding with an enemy.
    -   Being hit by an enemy bullet.
    -   Touching the top or bottom of the screen.
-   When a life is lost, you gain temporary invincibility and your ship will flash.
-   The game ends when you run out of lives. Your current lives are displayed as hearts in the top-right corner.

#### Game States

-   **Main Menu:** The initial screen where you can start a new game.
-   **Level Transition:** A brief screen displaying the current level number before gameplay begins.
-   **Gameplay:** The main state where you control the ship, fight enemies, and progress through the level.
-   **Pause:** The game can be paused by pressing 'P'. Press 'P' again to resume.
-   **Game Over:** Displayed when all lives are lost. Shows your final score and allows you to restart.
-   **Level Complete:** Shown after defeating a boss, before transitioning to the next level.

Good luck, pilot!

