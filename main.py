import random

def introduction():
    val = 1
    platforms = []
    print("Hello! Welcome to gamespace!")
    genre = input("1. What is your favorite game genre? Example: RPG\n")
    platform = input("2. Do you have PC, Playstation, Xbox, Nintendo (Press 0 after all platforms are submitted) \nPlatform 1: ")
    while True:   
        val+=1
        platform = input(f"Platform {val}: ")
        platforms.append(platform)
        if platform == "0":
            break

    return genre, platforms

def results_and_calculations(genre, platforms):
    print("Searching the Cosmos...")

introduction()
results_and_calculations()
# add random game feature maybe?

