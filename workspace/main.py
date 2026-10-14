import sys
import os

# Sicherstellen, dass das Verzeichnis im Pfad liegt
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core import Player, Item
from src.economy import Merchant

def main():
    print("========================================")
    print("  Willkommen im KI-RPG & Wirtschaftssim! ")
    print("========================================")
    
    player_name = input("\nGib den Namen deines Helden ein: ").strip()
    if not player_name:
        player_name = "Held"
        
    player = Player(name=player_name, gold=100)
    print(f"\nHallo {player.name}! Du startest mit {player.gold} Gold.")
    
    merchant = Merchant(name="Händler Alrik", inventory=[
        Item(name="Heiltrank", value=25, weight=1.0),
        Item(name="Eisernes Schwert", value=60, weight=3.5)
    ])
    
    while True:
        print("\n--- HAUPTMENÜ ---")
        print("1. Status anzeigen")
        print("2. Zum Händler gehen")
        print("3. Spiel beenden")
        
        choice = input("Wähle eine Option (1-3): ").strip()
        
        if choice == "1":
            print(f"\n--- SPIELERSTATUS ---")
            print(f"Name: {player.name}")
            print(f"Gold: {player.gold}")
            print("Inventar:")
            if player.inventory:
                for item in player.inventory:
                    print(f" - {item.name} (Wert: {item.value} Gold)")
            else:
                print(" (Dein Inventar ist aktuell leer)")
                
        elif choice == "2":
            print(f"\n--- {merchant.name.upper()} ---")
            print("Angebote:")
            for idx, item in enumerate(merchant.inventory):
                print(f" [{idx+1}] {item.name} - {item.value} Gold")
            
            buy_choice = input("Möchtest du etwas kaufen? (Nummer eingeben oder Enter zum Zurück): ").strip()
            if buy_choice.isdigit():
                idx = int(buy_choice) - 1
                if 0 <= idx < len(merchant.inventory):
                    item = merchant.inventory[idx]
                    if player.gold >= item.value:
                        player.gold -= item.value
                        merchant.inventory.pop(idx)
                        player.inventory.append(item)
                        print(f"Erfolgreich gekauft: {item.name}!")
                    else:
                        print("Du hast nicht genug Gold!")
                else:
                    print("Ungültige Auswahl.")
                    
        elif choice == "3":
            print("\nDanke fürs Spielen! Bis zum nächsten Mal.")
            break
        else:
            print("Bitte wähle eine Option zwischen 1 und 3.")

if __name__ == "__main__":
    main()
  
