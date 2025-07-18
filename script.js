// --- Constants ---
const SCREEN_WIDTH = 800;
const SCREEN_HEIGHT = 600;
const FPS = 60;

// Colors
const WHITE = "#FFFFFF";
const BLACK = "#000000";
const RED = "#FF0000";
const GREEN = "#00FF00";
const BLUE = "#0000FF";
const YELLOW = "#FFFF00";
const PURPLE = "#800080";
const ORANGE = "#FFA500";
const CYAN = "#00FFFF";
const GREY = "#808080";

// Game States
const MAIN_MENU = "MAIN_MENU";
const LEVEL_TRANSITION = "LEVEL_TRANSITION";
const GAMEPLAY = "GAMEPLAY";
const PAUSE = "PAUSE";
const GAME_OVER = "GAME_OVER";

// --- Game Class ---
class Game {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext("2d");
        this.gameState = MAIN_MENU;
        this.score = 0;
        this.currentLevelIndex = 0;
        this.lives = 3;
        this.levelStartTime = 0;
        this.lastEnemySpawnTime = 0;
        this.enemySpawnInterval = 2000;
        this.allSprites = [];
        this.enemies = [];
        this.playerBullets = [];
        this.enemyBullets = [];
        this.powerUps = [];
        this.stars = [];
        this.player = null;
        this.levelDuration = 60000;
        this.levelEnemyPhaseActive = true;
        this.currentBoss = null;
        this.bossActive = false;
        this.levelCompleteMessageActive = false;
        this.levelCompleteStartTime = 0;
        this.activePowerUpHudInfo = null;
    }

    newGame() {
        this.score = 0;
        this.currentLevelIndex = 0;
        this.lives = 3;
        this.allSprites = [];
        this.enemies = [];
        this.playerBullets = [];
        this.enemyBullets = [];
        this.powerUps = [];
        this.stars = [];

        for (let i = 0; i < 50; i++) {
            const star = new Star();
            this.stars.push(star);
            this.allSprites.push(star);
        }

        this.player = new Player(this);
        this.allSprites.push(this.player);

        this.loadLevel(this.currentLevelIndex);
    }

    loadLevel(levelIdx) {
        this.currentLevelIndex = levelIdx;
        this.levelStartTime = Date.now();
        this.gameState = LEVEL_TRANSITION;
        this.levelEnemyPhaseActive = true;
        this.lastEnemySpawnTime = Date.now();

        if (this.currentLevelIndex === 0) {
            this.levelDuration = 60000;
            this.enemySpawnInterval = 3000;
        } else if (this.currentLevelIndex === 1) {
            this.levelDuration = 75000;
        } else if (this.currentLevelIndex === 2) {
            this.levelDuration = 90000;
        }

        this.allSprites = this.allSprites.filter(sprite => sprite instanceof Star || sprite instanceof Player);
        this.enemies = [];
        this.playerBullets = [];
        this.enemyBullets = [];
        this.powerUps = [];

        if (this.currentBoss) {
            this.currentBoss.kill();
        }
        this.currentBoss = null;
        this.bossActive = false;
        this.levelCompleteMessageActive = false;
    }

    startBossFight() {
        this.bossActive = true;
        if (this.currentLevelIndex === 0) {
            this.currentBoss = new TheWarden(this);
        }
        if (this.currentBoss) {
            this.allSprites.push(this.currentBoss);
        } else {
            this.bossActive = false;
        }
    }

    endBossFight(won) {
        if (!this.bossActive) return;

        if (this.currentBoss) {
            this.currentBoss.kill();
            this.currentBoss = null;
        }
        this.bossActive = false;

        if (won) {
            this.levelCompleteMessageActive = true;
            this.levelCompleteStartTime = Date.now();
        }
    }

    checkCollision(sprite1, sprite2) {
        if (!sprite1 || !sprite2) {
            return false;
        }
        return (
            sprite1.x < sprite2.x + sprite2.width &&
            sprite1.x + sprite1.width > sprite2.x &&
            sprite1.y < sprite2.y + sprite2.height &&
            sprite1.y + sprite1.height > sprite2.y
        );
    }

    run() {
        this.handleInput();
        this.update();
        this.draw();
        requestAnimationFrame(() => this.run());
    }

    handleInput() {
        // Input handling will be implemented later
    }

    update() {
        if (this.gameState === GAMEPLAY) {
            this.allSprites.forEach(sprite => sprite.update());

            const currentTime = Date.now();
            const levelElapsedTime = currentTime - this.levelStartTime;

            if (this.levelEnemyPhaseActive && !this.bossActive && levelElapsedTime > this.levelDuration) {
                this.levelEnemyPhaseActive = false;
                this.startBossFight();
            }

            if (this.levelEnemyPhaseActive && !this.bossActive) {
                if (currentTime - this.lastEnemySpawnTime > this.enemySpawnInterval) {
                    this.lastEnemySpawnTime = currentTime;
                    if (this.currentLevelIndex === 0) {
                        const drone = new Drone(this);
                        this.allSprites.push(drone);
                        this.enemies.push(drone);
                    }
                }
            }

            // Collision detection
            // Player Bullet -> Enemy/Boss
            this.playerBullets.forEach(bullet => {
                this.enemies.forEach(enemy => {
                    if (this.checkCollision(bullet, enemy)) {
                        enemy.hit(1);
                        bullet.kill();
                    }
                });

                if (this.currentBoss && this.bossActive && this.checkCollision(bullet, this.currentBoss)) {
                    this.currentBoss.hit(1);
                    bullet.kill();
                }
            });

            // Player -> Enemy/Boss/Enemy Bullet
            if (this.player) {
                // Player -> Regular Enemy
                this.enemies.forEach(enemy => {
                    if (this.checkCollision(this.player, enemy)) {
                        if (!this.player.isInvincible) {
                            this.player.loseLife();
                        }
                        enemy.kill();
                        this.score += 5;
                    }
                });

                // Player -> Boss
                if (this.currentBoss && this.bossActive && this.checkCollision(this.player, this.currentBoss)) {
                    if (!this.player.isInvincible) {
                        this.player.loseLife();
                    }
                }

                // Player -> Enemy Bullet
                this.enemyBullets.forEach(bullet => {
                    if (this.checkCollision(this.player, bullet)) {
                        if (!this.player.isInvincible) {
                            this.player.loseLife();
                        }
                        bullet.kill();
                    }
                });

                // Player -> PowerUp
                this.powerUps.forEach(powerUp => {
                    if (this.checkCollision(this.player, powerUp)) {
                        powerUp.applyEffect();
                    }
                });
            }

            // Player Bullet <-> Enemy Bullet
            this.playerBullets.forEach(playerBullet => {
                this.enemyBullets.forEach(enemyBullet => {
                    if (this.checkCollision(playerBullet, enemyBullet)) {
                        playerBullet.kill();
                        enemyBullet.kill();
                    }
                });
            });


            if (this.levelCompleteMessageActive) {
                if (currentTime - this.levelCompleteStartTime > 3000) {
                    this.levelCompleteMessageActive = false;
                    this.currentLevelIndex++;
                    if (this.currentLevelIndex < 3) {
                        this.loadLevel(this.currentLevelIndex);
                    } else {
                        this.gameState = GAME_OVER;
                    }
                }
            }
        } else if (this.gameState === LEVEL_TRANSITION) {
            if (Date.now() - this.levelStartTime > 3000) {
                this.gameState = GAMEPLAY;
                this.levelStartTime = Date.now();
                this.lastEnemySpawnTime = Date.now();
                this.bossActive = false;
                this.levelEnemyPhaseActive = true;
            }
        }
    }

    drawText(text, font, color, x, y, center = false) {
        this.ctx.fillStyle = color;
        this.ctx.font = font;
        if (center) {
            this.ctx.textAlign = "center";
            this.ctx.textBaseline = "middle";
        } else {
            this.ctx.textAlign = "left";
            this.ctx.textBaseline = "top";
        }
        this.ctx.fillText(text, x, y);
    }

    draw() {
        this.ctx.fillStyle = BLACK;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        if (this.gameState === MAIN_MENU) {
            this.stars.forEach(star => star.draw(this.ctx));
            this.drawText("Flappy Impact", "72px sans-serif", YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3, true);
            this.drawText("Press Enter to Start", "36px sans-serif", WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, true);
            this.drawText("Press SPACE to Flap", "24px sans-serif", WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50, true);
            this.drawText("Press X to Shoot", "24px sans-serif", WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 80, true);
        } else if (this.gameState === LEVEL_TRANSITION) {
            this.stars.forEach(star => star.draw(this.ctx));
            this.drawText(`LEVEL ${this.currentLevelIndex + 1}`, "72px sans-serif", WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, true);
        } else if (this.gameState === GAMEPLAY) {
            this.allSprites.forEach(sprite => sprite.draw(this.ctx));

            this.drawText(`SCORE: ${this.score.toString().padStart(6, '0')}`, "36px sans-serif", WHITE, 10, 10);
            this.drawText(`LIVES: ${'♥'.repeat(this.lives)}`, "36px sans-serif", RED, SCREEN_WIDTH - 150, 10);
            this.drawText(`LEVEL: ${this.currentLevelIndex + 1}`, "36px sans-serif", WHITE, 10, SCREEN_HEIGHT - 40);

            if (this.activePowerUpHudInfo) {
                const { name, endTime } = this.activePowerUpHudInfo;
                const remainingTime = (endTime - Date.now()) / 1000;
                if (remainingTime > 0) {
                    this.drawText(`POWER-UP: ${name} ${remainingTime.toFixed(1)}s`, "36px sans-serif", YELLOW, SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT - 40);
                }
            }

            if (this.bossActive && this.currentBoss) {
                const healthPercentage = this.currentBoss.health / this.currentBoss.totalHealth;
                const barWidth = SCREEN_WIDTH / 2;
                const barHeight = 20;
                const fillWidth = barWidth * healthPercentage;
                this.ctx.fillStyle = RED;
                this.ctx.fillRect((SCREEN_WIDTH - barWidth) / 2, 10, barWidth, barHeight);
                this.ctx.fillStyle = GREEN;
                this.ctx.fillRect((SCREEN_WIDTH - barWidth) / 2, 10, fillWidth, barHeight);
                this.drawText("BOSS", "36px sans-serif", WHITE, SCREEN_WIDTH / 2, 35, true);
            }

            if (this.levelCompleteMessageActive) {
                this.drawText("LEVEL COMPLETE!", "72px sans-serif", GREEN, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, true);
                this.drawText(`Score: ${this.score}`, "36px sans-serif", WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50, true);
            }
        } else if (this.gameState === PAUSE) {
            this.allSprites.forEach(sprite => sprite.draw(this.ctx));
            this.drawText(`SCORE: ${this.score.toString().padStart(6, '0')}`, "36px sans-serif", WHITE, 10, 10);
            this.drawText(`LIVES: ${'♥'.repeat(this.lives)}`, "36px sans-serif", RED, SCREEN_WIDTH - 150, 10);
            this.drawText(`LEVEL: ${this.currentLevelIndex + 1}`, "36px sans-serif", WHITE, 10, SCREEN_HEIGHT - 40);
            this.drawText("PAUSED", "72px sans-serif", WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, true);
            this.drawText("Press P to Resume", "36px sans-serif", WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50, true);
        } else if (this.gameState === GAME_OVER) {
            this.drawText("GAME OVER", "72px sans-serif", RED, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3, true);
            this.drawText(`Final Score: ${this.score}`, "36px sans-serif", WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, true);
            this.drawText("Press Enter to Restart", "36px sans-serif", WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50, true);
        }
    }
}

// --- Sprite Classes (to be implemented) ---
class Sprite {
    constructor(game) {
        this.game = game;
        this.x = 0;
        this.y = 0;
        this.width = 0;
        this.height = 0;
    }
    update() {}
    draw(ctx) {}
    kill() {
        this.game.allSprites = this.game.allSprites.filter(sprite => sprite !== this);
        if (this instanceof Enemy) {
            this.game.enemies = this.game.enemies.filter(enemy => enemy !== this);
        }
        if (this instanceof Bullet) {
            this.game.playerBullets = this.game.playerBullets.filter(bullet => bullet !== this);
        }
        if (this instanceof EnemyBullet) {
            this.game.enemyBullets = this.game.enemyBullets.filter(bullet => bullet !== this);
        }
        if (this instanceof PowerUp) {
            this.game.powerUps = this.game.powerUps.filter(powerUp => powerUp !== this);
        }
    }
}

class Player extends Sprite {
    constructor(game) {
        super(game);
        this.width = 30;
        this.height = 20;
        this.x = 50;
        this.y = SCREEN_HEIGHT / 2;
        this.velocityY = 0;
        this.gravity = 0.2;
        this.flapStrength = -6;
        this.fireCooldown = 300;
        this.lastShotTime = 0;
        this.lastHitTime = 0;
        this.invincibilityDuration = 1500;
        this.isInvincible = false;
        this.flashTimer = 0;
        this.flashInterval = 100;
        this.activePowerUpType = null;
        this.powerUpEndTime = 0;
        this.originalFireCooldown = this.fireCooldown;
        this.alpha = 1;
    }

    update() {
        if (this.activePowerUpType && Date.now() > this.powerUpEndTime) {
            this.deactivatePowerUp();
        }

        this.velocityY += this.gravity;
        this.y += this.velocityY;

        if (this.y < 0) {
            this.y = 0;
            this.velocityY = 0;
            this.loseLife();
        }
        if (this.y + this.height > SCREEN_HEIGHT) {
            this.y = SCREEN_HEIGHT - this.height;
            this.velocityY = 0;
            this.loseLife();
        }

        if (this.isInvincible) {
            if (Date.now() - this.lastHitTime > this.invincibilityDuration) {
                this.isInvincible = false;
                this.alpha = 1;
            } else {
                this.flashTimer += 1000 / FPS;
                if (this.flashTimer > this.flashInterval) {
                    this.flashTimer = 0;
                    this.alpha = this.alpha === 1 ? 0.5 : 1;
                }
            }
        } else {
            this.alpha = 1;
        }
    }

    draw(ctx) {
        ctx.save();
        ctx.globalAlpha = this.alpha;
        ctx.fillStyle = YELLOW;
        ctx.beginPath();
        ctx.moveTo(this.x, this.y);
        ctx.lineTo(this.x + this.width, this.y + this.height / 2);
        ctx.lineTo(this.x, this.y + this.height);
        ctx.closePath();
        ctx.fill();
        ctx.restore();

        if (this.activePowerUpType === "shield" || (this.isInvincible && this.activePowerUpType !== "shield")) {
            ctx.strokeStyle = CYAN;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(this.x + this.width / 2, this.y + this.height / 2, this.width, 0, Math.PI * 2);
            ctx.stroke();
        }
    }

    flap() {
        this.velocityY = this.flapStrength;
    }

    shoot() {
        const currentTime = Date.now();
        if (currentTime - this.lastShotTime > this.fireCooldown) {
            this.lastShotTime = currentTime;
            const bullet = new Bullet(this.x + this.width, this.y + this.height / 2, this.game);
            this.game.allSprites.push(bullet);
            this.game.playerBullets.push(bullet);
        }
    }

    activateRapidFire() {
        if (this.activePowerUpType) {
            this.deactivatePowerUp();
        }
        this.activePowerUpType = "rapid_fire";
        this.powerUpEndTime = Date.now() + 10000;
        this.fireCooldown = 100;
        this.game.activePowerUpHudInfo = { name: "Rapid Fire", endTime: this.powerUpEndTime };
    }

    deactivatePowerUp() {
        if (this.activePowerUpType === "rapid_fire") {
            this.fireCooldown = this.originalFireCooldown;
        } else if (this.activePowerUpType === "shield") {
            this.isInvincible = false;
        }
        this.activePowerUpType = null;
        this.powerUpEndTime = 0;
        this.game.activePowerUpHudInfo = null;
    }

    activateShield() {
        if (this.activePowerUpType) {
            this.deactivatePowerUp();
        }
        this.activePowerUpType = "shield";
        this.powerUpEndTime = Date.now() + 10000;
        this.isInvincible = true;
        this.game.activePowerUpHudInfo = { name: "Shield", endTime: this.powerUpEndTime };
    }

    loseLife() {
        if (!this.isInvincible) {
            this.game.lives--;
            if (this.game.lives <= 0) {
                this.game.gameState = GAME_OVER;
            } else {
                this.isInvincible = true;
                this.lastHitTime = Date.now();
                this.flashTimer = 0;
                this.y = SCREEN_HEIGHT / 2;
                this.velocityY = 0;
            }
        }
    }
}

class Bullet extends Sprite {
    constructor(x, y, game) {
        super(game);
        this.width = 15;
        this.height = 5;
        this.x = x;
        this.y = y - this.height / 2;
        this.speed = 10;
    }

    update() {
        this.x += this.speed;
        if (this.x > SCREEN_WIDTH) {
            this.kill();
        }
    }

    draw(ctx) {
        ctx.fillStyle = WHITE;
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }
}

class Enemy extends Sprite {
    constructor(game) {
        super(game);
        this.health = 1;
    }

    hit(damage) {
        this.health -= damage;
        if (this.health <= 0) {
            this.kill();
            this.game.score += 10;
            if (Math.random() < 0.15) {
                const powerUpType = Math.random() < 0.5 ? "rapid_fire" : "shield";
                const powerUp = new PowerUp(this.game, this.x + this.width / 2, this.y + this.height / 2, powerUpType);
                this.game.allSprites.push(powerUp);
                this.game.powerUps.push(powerUp);
            }
        }
    }

    update() {
        this.x -= this.speed;
        if (this.x + this.width < 0) {
            this.kill();
        }
    }
}

class Drone extends Enemy {
    constructor(game) {
        super(game);
        this.width = 30;
        this.height = 30;
        this.x = SCREEN_WIDTH;
        this.y = Math.random() * (SCREEN_HEIGHT - 100) + 50;
        this.speed = Math.random() * 3 + 2;
        this.health = 1;
    }

    draw(ctx) {
        ctx.fillStyle = RED;
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }
}

class EnemyBullet extends Sprite {
    constructor(x, y, game, speedX = -5, speedY = 0, width = 10, height = 10, color = RED, isEnergyBall = false) {
        super(game);
        this.width = width;
        this.height = height;
        this.x = x - this.width / 2;
        this.y = y - this.height / 2;
        this.speedX = speedX;
        this.speedY = speedY;
        this.color = color;
        this.isEnergyBall = isEnergyBall;
    }

    update() {
        this.x += this.speedX;
        this.y += this.speedY;
        if (this.x + this.width < 0 || this.x > SCREEN_WIDTH || this.y + this.height < 0 || this.y > SCREEN_HEIGHT) {
            this.kill();
        }
    }

    draw(ctx) {
        ctx.fillStyle = this.color;
        if (this.isEnergyBall) {
            ctx.beginPath();
            ctx.arc(this.x + this.width / 2, this.y + this.height / 2, this.width / 2, 0, Math.PI * 2);
            ctx.fill();
        } else {
            ctx.fillRect(this.x, this.y, this.width, this.height);
        }
    }
}

class Star extends Sprite {
    constructor() {
        super(null);
        this.size = Math.random() * 3 + 1;
        this.x = Math.random() * SCREEN_WIDTH;
        this.y = Math.random() * SCREEN_HEIGHT;
        this.speed = Math.random() * 2 + 1;
    }

    update() {
        this.x -= this.speed;
        if (this.x + this.size < 0) {
            this.x = SCREEN_WIDTH;
            this.y = Math.random() * SCREEN_HEIGHT;
        }
    }

    draw(ctx) {
        ctx.fillStyle = WHITE;
        ctx.fillRect(this.x, this.y, this.size, this.size);
    }
}

class Boss extends Enemy {
    constructor(game, health, scoreValue) {
        super(game);
        this.totalHealth = health;
        this.health = health;
        this.scoreValue = scoreValue;
        this.isBoss = true;
        this.bossFightActive = false;
    }

    hit(damage) {
        if (!this.bossFightActive) return;
        this.health -= damage;
        if (this.health <= 0) {
            this.health = 0;
            this.kill();
            this.game.score += this.scoreValue;
            this.game.endBossFight(true);
        }
    }
}

class TheWarden extends Boss {
    constructor(game) {
        super(game, 100, 1000);
        this.width = 80;
        this.height = 150;
        this.x = SCREEN_WIDTH;
        this.y = SCREEN_HEIGHT / 2 - this.height / 2;
        this.entrySpeed = 2;
        this.targetX = SCREEN_WIDTH - 100;
        this.isEntering = true;
        this.attackPhase = 0;
        this.lastAttackTime = 0;
        this.burstPause = 2000;
        this.energyBallPause = 3000;
        this.chargeTime = 1000;
        this.isCharging = false;
        this.chargeStartTime = 0;
        this.bulletsFiredInBurst = 0;
    }

    update() {
        if (this.isEntering) {
            this.x -= this.entrySpeed;
            if (this.x <= this.targetX) {
                this.x = this.targetX;
                this.isEntering = false;
                this.bossFightActive = true;
                this.lastAttackTime = Date.now();
            }
            return;
        }

        if (!this.bossFightActive) {
            return;
        }

        const currentTime = Date.now();

        if (this.isCharging) {
            if (currentTime - this.chargeStartTime > this.chargeTime) {
                this.fireEnergyBall();
                this.isCharging = false;
                this.attackPhase = 0;
                this.lastAttackTime = currentTime;
            }
            return;
        }

        if (this.attackPhase === 0) {
            if (currentTime - this.lastAttackTime > this.burstPause) {
                this.attackPhase = 1;
                this.lastAttackTime = currentTime;
                this.bulletsFiredInBurst = 0;
            } else if (this.bulletsFiredInBurst < 3 && currentTime - this.lastAttackTime > (this.burstPause / 4) * (this.bulletsFiredInBurst + 1)) {
                this.fireBurstBullet();
            }
        } else if (this.attackPhase === 1) {
            if (currentTime - this.lastAttackTime > this.energyBallPause) {
                this.isCharging = true;
                this.chargeStartTime = currentTime;
                this.attackPhase = 2;
            }
        } else if (this.attackPhase === 2) {
            if (this.isCharging && currentTime - this.chargeStartTime > this.chargeTime) {
                this.fireEnergyBall();
                this.isCharging = false;
                this.attackPhase = 0;
                this.lastAttackTime = currentTime;
            }
        }
    }

    fireBurstBullet() {
        this.bulletsFiredInBurst++;
        const bullet = new EnemyBullet(this.x, this.y + this.height / 2 - 15 + (this.bulletsFiredInBurst * 15), this.game, -7, 0, 15, 5, RED);
        this.game.allSprites.push(bullet);
        this.game.enemyBullets.push(bullet);
    }

    fireEnergyBall() {
        const energyBall = new EnemyBullet(this.x, this.y + this.height / 2, this.game, -3, 0, 40, 40, ORANGE, true);
        this.game.allSprites.push(energyBall);
        this.game.enemyBullets.push(energyBall);
    }

    draw(ctx) {
        ctx.fillStyle = GREY;
        ctx.fillRect(this.x, this.y, this.width, this.height);
        ctx.fillStyle = BLACK;
        ctx.fillRect(this.x + 50, this.y + 65, 30, 20);
    }
}

class PowerUp extends Sprite {
    constructor(game, x, y, type) {
        super(game);
        this.width = 25;
        this.height = 25;
        this.x = x - this.width / 2;
        this.y = y - this.height / 2;
        this.type = type;
        this.spawnTime = Date.now();
        this.lifetime = 10000;
        this.speedX = -1;
    }

    update() {
        this.x += this.speedX;
        if (Date.now() - this.spawnTime > this.lifetime || this.x + this.width < 0) {
            this.kill();
        }
    }

    draw(ctx) {
        if (this.type === "rapid_fire") {
            ctx.fillStyle = BLUE;
            ctx.fillRect(this.x, this.y, this.width, this.height);
            ctx.fillStyle = WHITE;
            ctx.font = "20px sans-serif";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText("R", this.x + this.width / 2, this.y + this.height / 2);
        } else if (this.type === "shield") {
            ctx.fillStyle = CYAN;
            ctx.fillRect(this.x, this.y, this.width, this.height);
            ctx.fillStyle = WHITE;
            ctx.font = "20px sans-serif";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText("S", this.x + this.width / 2, this.y + this.height / 2);
        }
    }

    applyEffect() {
        if (this.type === "rapid_fire") {
            this.game.player.activateRapidFire();
        } else if (this.type === "shield") {
            this.game.player.activateShield();
        }
        this.kill();
    }
}

// --- Main Execution ---
window.addEventListener("load", () => {
    const canvas = document.getElementById("gameCanvas");
    const game = new Game(canvas);

    function resizeCanvas() {
        const aspectRatio = SCREEN_WIDTH / SCREEN_HEIGHT;
        const newWidth = window.innerWidth;
        const newHeight = window.innerHeight;
        const newAspectRatio = newWidth / newHeight;
        let finalWidth, finalHeight;

        if (newAspectRatio > aspectRatio) {
            finalHeight = newHeight;
            finalWidth = finalHeight * aspectRatio;
        } else {
            finalWidth = newWidth;
            finalHeight = finalWidth / aspectRatio;
        }

        canvas.style.width = `${finalWidth}px`;
        canvas.style.height = `${finalHeight}px`;
    }

    window.addEventListener("resize", resizeCanvas);
    resizeCanvas();

    game.run();

    window.addEventListener("keydown", e => {
        if (game.gameState === MAIN_MENU) {
            if (e.key === "Enter") {
                game.newGame();
            }
        } else if (game.gameState === GAMEPLAY) {
            if (e.key === " ") {
                game.player.flap();
            } else if (e.key === "x") {
                game.player.shoot();
            } else if (e.key === "p") {
                game.gameState = PAUSE;
            }
        } else if (game.gameState === GAME_OVER) {
            if (e.key === "Enter") {
                game.gameState = MAIN_MENU;
            }
        } else if (game.gameState === PAUSE) {
            if (e.key === "p") {
                game.gameState = GAMEPLAY;
            }
        }
    });
});
