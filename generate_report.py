import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg
import os

def generate_pdf():
    # Use visualizations folder relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    vis_dir = os.path.join(current_dir, "visualizations")
    pdf_path = os.path.join(vis_dir, "raport_wywodu.pdf")
    
    # Ensure visualizations dir exists
    if not os.path.exists(vis_dir):
        print(f"Error: Directory {vis_dir} does not exist.")
        return

    with PdfPages(pdf_path) as pdf:
        # --- Title Page ---
        plt.figure(figsize=(8.27, 11.69)) # A4 size
        plt.axis('off')
        
        plt.text(0.5, 0.7, "Raport Projektowy\nPoly-DPG", 
                 ha='center', va='center', fontsize=24, fontweight='bold')
        
        plt.text(0.5, 0.6, "Temat: Wizualizacja Wywodu i Opis Sterownika", 
                 ha='center', va='center', fontsize=16)
        
        plt.text(0.5, 0.5, "Data: 22.01.2026", 
                 ha='center', va='center', fontsize=12)
                 
        pdf.savefig()
        plt.close()

        # --- Image Steps ---
        # List of tuples: (filename, title, description)
        steps = [
            ("iter_0_start.png", 
             "Stan Początkowy", 
             "Hipergraf inicjalny. Widoczne elementy czworokątne (Q, środek/góra/dół)\noraz sześciokątne (S, lewa/prawa). Grubymi liniami zaznaczono krawędzie (E)."),
             
            ("iter_1.png", 
             "Krok 1: Złamanie dołu", 
             "Zastosowanie produkcji podziału na dolnym elemencie prostokątnym (Q3).\nPowstają nowe mniejsze czworokąty."),
             
            ("iter_2.png", 
             "Krok 2: Złamanie prawej strony", 
             "Zastosowanie produkcji podziału na prawym elemencie sześciokątnym (S2).\nElement zostaje podzielony na pod-czworokąty z zachowaniem ciągłości krawędzi."),
             
            ("iter_3.png", 
             "Krok 3: Złamanie środka", 
             "Podział centralnego kwadratu (Q1). Zauważalne zagęszczenie siatki\nw centrum układu."),
             
            ("iter_4.png", 
             "Krok 4: Lokalne zagęszczenie", 
             "Kolejna iteracja refinacji zastosowana tylko do jednego,\ndolnego-prawego podobszaru (dziecka Q1).")
        ]
        
        for filename, title, desc in steps:
            img_path = os.path.join(vis_dir, filename)
            
            if not os.path.exists(img_path):
                print(f"Warning: Image {filename} not found, skipping.")
                continue
                
            img = mpimg.imread(img_path)
            
            # Setup A4 page layout
            fig = plt.figure(figsize=(8.27, 11.69))
            
            # Add Title
            fig.text(0.5, 0.92, title, ha='center', fontsize=18, fontweight='bold')
            
            # Add Image (centered, taking up mostly middle)
            # axes: [left, bottom, width, height]
            ax = fig.add_axes([0.1, 0.3, 0.8, 0.55]) 
            ax.axis('off')
            ax.imshow(img)
            
            # Add Description
            fig.text(0.5, 0.2, desc, ha='center', fontsize=12, wrap=True)
            
            pdf.savefig(fig)
            plt.close()

        # --- Text Description Page ---
        text_content = """
        Opis Sterownika (Procedury Pilotującej)

        Zadaniem sterownika (drivera) w systemie gramatyk grafowych jest deterministyczne zarządzanie procesem adaptacji siatki. W przedstawionym wywodzie procedura pilotująca realizuje następującą logikę zapewniającą poprawność kolejności i lokalizacji produkcji:

        1. Selekcja Deterministyczna (Adresowanie):
           W początkowych fazach (Kroki 1-3), sterownik wybiera elementy do podziału na podstawie ich unikalnych identyfikatorów (UID) nadanych w fazie inicjalizacji (np. "Q3", "S2"). Dzięki temu mamy gwarancję, że produkcja zostanie zaaplikowana dokładnie w tym miejscu struktury, które zaplanowaliśmy, niezależnie od stanu sąsiednich elementów.

        2. Zapytania Topologiczno-Geometryczne:
           W Kroku 4 sterownik demonstruje bardziej zaawansowany mechanizm. Element docelowy (dolny-prawy fragment środka) nie istniał na początku symulacji – powstał w wyniku działań z Kroku 3.
           Sterownik identyfikuje go dynamicznie poprzez:
           a) Pobranie listy potomków elementu Q1 po podziale.
           b) Analizę współrzędnych geometrycznych (centroidów) tych potomków.
           c) Wybór tego elementu, który spełnia warunek geometryczny (znajduje się w czwartej ćwiartce lokalnego układu).
           Taki mechanizm symuluje działanie rzeczywistych algorytmów adaptacyjnych (AMR), które sterują gęstością siatki na podstawie lokalnych estymatorów błędu.

        3. Sekwencyjność i Spójność:
           Każda produkcja jest transakcją atomową. Sterownik oczekuje na pełne zakończenie aktualizacji grafu (włącznie z "połataniem" sąsiednich krawędzi tzw. problemem wiszących węzłów) przed przejściem do kolejnego kroku. Dzięki temu każda kolejna produkcja operuje na spójnym, poprawnym topologicznie hipergrafie.

        4. Polimorfizm Produkcji:
           Sterownik automatycznie rozpoznaje typ elementu (Czworokąt vs Sześciokąt) i aplikuje odpowiedni wariant algorytmu podziału (Split), zapewniając generalizację procesu dla różnych kształtów elementów skończonych.
        """
        
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.text(0.5, 0.9, "Opis Sterownika", ha='center', fontsize=18, fontweight='bold')
        fig.text(0.12, 0.85, text_content, ha='left', va='top', fontsize=11, wrap=True)
        # Hack to force left alignment wrapping usually requires manual handling or TextWrapper, 
        # but matplotlib's text wrapping is basic. 
        # For this purpose, the layout above is sufficient given standard margins.
        
        pdf.savefig(fig)
        plt.close()

    print(f"Pomyślnie wygenerowano raport: {pdf_path}")

if __name__ == "__main__":
    generate_pdf()
