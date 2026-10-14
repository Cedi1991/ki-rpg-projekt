import tkinter as tk
from tkinter import messagebox
from src.core import Player, Item
from src.consumables import use_item

class InventoryGUI:
    def __init__(self, player: Player):
        self.player = player
        self.root = tk.Tk()
        self.root.title(f"Inventar von {self.player.name}")
        self.listbox = tk.Listbox(self.root, width=40)
        self.listbox.pack(padx=10, pady=5)
        self.use_button = tk.Button(self.root, text="Benutzen", command=self.use_selected)
        self.use_button.pack(pady=5)
        self.refresh_button = tk.Button(self.root, text="Aktualisieren", command=self.refresh)
        self.refresh_button.pack(pady=5)
        self.refresh()

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for item in self.player.inventory.values():
            self.listbox.insert(tk.END, f"{item.name} (x{item.quantity})")
        self.root.update_idletasks()

    def use_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Bitte ein Item auswählen.")
            return
        item_line = self.listbox.get(selection[0])
        item_name = item_line.split(" (x")[0]
        if use_item(self.player, item_name):
            messagebox.showinfo("Erfolg", f"{item_name} wurde verwendet.")
        else:
            messagebox.showwarning("Fehler", f"{item_name} konnte nicht verwendet werden.")
        self.refresh()

def launch_gui(player: Player):
    gui = InventoryGUI(player)
    gui.root.mainloop()

if __name__ == "__main__":
    # Demo-Setup für direkte Ausführung
    demo_player = Player(name="Demo")
    demo_player.add_item(Item(name="Heiltrank", category="consumable", base_value=20, quantity=3))
    demo_player.add_item(Item(name="Eisenerz", category="material", base_value=5, quantity=5))
    launch_gui(demo_player)
