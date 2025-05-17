#!/usr/bin/env python3
"""
Checkers Bot - A script to automatically play checkers as the BLACK player

Before running this script, make sure to install the required dependencies:
pip install requests

Usage:
1. Start the checkers game server
2. Create or join a game
3. Run this script with the game ID
4. The bot will automatically make moves when it's BLACK's turn
"""

import requests
import time
import json
import random

# Configuration
API_BASE_URL = "http://localhost:8080/api/games"  # Adjust this to match your server URL
GAME_ID = ""  # Set this to your game ID
PLAYER = "BLACK"
POLL_INTERVAL = 2  # seconds

def get_game_state():
    """Get the current game state from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/{GAME_ID}/board")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error getting game state: {e}")
        return None

def make_move(move):
    """Send a move to the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/{GAME_ID}/move",
            json=move
        )
        response.raise_for_status()
        print(f"Move sent successfully: {move}")
        return response.json()
    except requests.RequestException as e:
        print(f"Error making move: {e}")
        return None

def find_valid_moves(board, player):
    """Find all valid moves for the given player"""
    valid_moves = []

    # First, look for capture moves (these are mandatory in checkers)
    capture_moves = find_capture_moves(board, player)
    if capture_moves:
        return capture_moves

    # If no captures are available, look for regular moves
    for r in range(8):
        for c in range(8):
            piece = board[r][c]

            # Check if this is a player's piece
            if piece == "b" and player == "BLACK":
                # Regular black piece moves forward (down)
                directions = [(1, -1), (1, 1)]  # Down-left, Down-right
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] == "":
                        valid_moves.append({
                            "from": f"{r}{c}",
                            "to": f"{nr}{nc}",
                            "player": player,
                            "path": []
                        })

            # Check for black kings
            elif piece == "B" and player == "BLACK":
                # King can move in any diagonal direction
                directions = [(1, -1), (1, 1), (-1, -1), (-1, 1)]
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] == "":
                        valid_moves.append({
                            "from": f"{r}{c}",
                            "to": f"{nr}{nc}",
                            "player": player,
                            "path": []
                        })

    return valid_moves

def find_capture_moves(board, player):
    """Find all possible capture moves"""
    capture_moves = []

    for r in range(8):
        for c in range(8):
            piece = board[r][c]

            # Check if this is a player's piece
            if (piece == "b" or piece == "B") and player == "BLACK":
                # For regular pieces, check forward captures
                if piece == "b":
                    directions = [(1, -1), (1, 1)]  # Down-left, Down-right
                else:  # King can capture in any direction
                    directions = [(1, -1), (1, 1), (-1, -1), (-1, 1)]

                for dr, dc in directions:
                    # Position of the piece to capture
                    capture_r, capture_c = r + dr, c + dc
                    # Landing position after capture
                    land_r, land_c = r + 2*dr, c + 2*dc

                    # Check if the capture is valid
                    if (0 <= capture_r < 8 and 0 <= capture_c < 8 and
                        0 <= land_r < 8 and 0 <= land_c < 8):
                        # Check if there's an opponent's piece to capture
                        capture_piece = board[capture_r][capture_c]
                        if (capture_piece == "w" or capture_piece == "W") and board[land_r][land_c] == "":
                            capture_moves.append({
                                "from": f"{r}{c}",
                                "to": f"{land_r}{land_c}",
                                "player": player,
                                "path": [f"{land_r}{land_c}"]  # Path includes the landing position
                            })

    return capture_moves

def main():
    global GAME_ID

    # Get game ID from user if not set
    if not GAME_ID:
        GAME_ID = input("Enter the game ID: ")

    print(f"Starting checkers bot for game {GAME_ID}")
    print(f"Checking for {PLAYER}'s turn every {POLL_INTERVAL} seconds")

    while True:
        # Get current game state
        game_state = get_game_state()

        if game_state:
            # Check if it's our turn
            if game_state["turno"] == PLAYER:
                print(f"It's {PLAYER}'s turn!")

                # Find valid moves
                valid_moves = find_valid_moves(game_state["board"], PLAYER)

                if valid_moves:
                    # Choose a random move from valid moves
                    move = random.choice(valid_moves)
                    print(f"Making move: {move}")

                    # Send the move
                    make_move(move)
                else:
                    print("No valid moves available!")
            else:
                print(f"Waiting for {PLAYER}'s turn... Current turn: {game_state['turno']}")

        # Wait before checking again
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
