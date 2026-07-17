# Account Taxonomy for Receipt Tracking

## Full Account Hierarchy

```
expenses
├── food
│   ├── groceries
│   │   ├── fish              ; Lachs, Sardinen, Garnelen, Sardellen
│   │   ├── dairy             ; Eier, Käse, Butter, Milch, Sahne
│   │   ├── produce:fruit     ; Äpfel, Bananen, Beeren, Orangen
│   │   ├── produce:vegetables; Gurken, Tomaten, Spinat, Salat
│   │   ├── bakery            ; Brot, Brötchen, Croissants
│   │   ├── meat              ; Salami, Wurst, Hähnchen, Rind
│   │   ├── beverages:soft    ; Limo, Cola, Smoothies, Saft
│   │   ├── beverages:energy  ; Red Bull, Monster, Energydrinks
│   │   ├── coffee            ; Espresso, Kaffeebohnen, gemahlener Kaffee
│   │   ├── chocolate         ; Schokolade, Pralinen, Süßigkeiten
│   │   ├── spread            ; Samba Dark, Nutella, Marmelade
│   │   ├── snacks            ; Chips, Nüsse, Knabberzeug
│   │   ├── alcohol           ; Wein, Bier, Sekt, Spirituosen
│   │   └── other             ; Olivenöl, Kichererbsen, Nudeln, Reis
│   └── eating-out            ; Restaurant, Kiosk, Imbiss, Café
├── household
│   ├── decor                 ; Giftbags, Vasen, Kerzen, Deko
│   ├── personal-care         ; Deospray, Zahnpasta, Shampoo, Haarlack
│   ├── cleaning              ; Spülmittel, Spülschwämme, Putzmittel
│   └── (default)             ; IKEA, Hornbach, Möbel, Elektrogeräte
├── leisure
│   ├── books                 ; Bücher, eBooks, Magazine
│   └── (default)             ; Kino, Eventim, Konzerte, Streaming
├── tech
│   ├── subscriptions         ; Notion, Disney+, Prime, Apple, Netflix
│   └── hardware              ; Laptop, Handy, Zubehör
├── transport
│   ├── shared                ; Bolt, Voi, Bahn, Bus, Uber
│   └── (default)             ; Tanken, Auto-Wartung, Fahrrad
├── health
│   ├── insurance             ; Krankenversicherung, Zusatzleistungen
│   └── other                 ; DM, Müller, Apotheke, Arzt
├── investment:fees           ; Trade Republic, Broker-Gebühren
└── tax:kapitalertragsteuer   ; Steuer auf Dividenden/Zinsen
```

## Item-to-Account Quick Reference

| Keyword | Account |
|---------|---------|
| Lachs, Salmon, Forelle, Fisch | `expenses:food:groceries:fish` |
| Sardine, Sardelle, Anchovis | `expenses:food:groceries:fish` |
| Garnelen, Shrimps, Prawns | `expenses:food:groceries:fish` |
| Eier, Ei, Eier | `expenses:food:groceries:dairy` |
| Käse, Cheese, Parmesan, Reggiano | `expenses:food:groceries:dairy` |
| Butter, Margarine | `expenses:food:groceries:dairy` |
| Milch, Sahne, Joghurt | `expenses:food:groceries:dairy` |
| Apfel, Banane, Orange, Beere | `expenses:food:groceries:produce:fruit` |
| Gurke, Tomate, Spinat, Salat | `expenses:food:groceries:produce:vegetables` |
| Brot, Brötchen, Baguette, Croissant | `expenses:food:groceries:bakery` |
| Salami, Wurst, Schinken, Hähnchen | `expenses:food:groceries:meat` |
| Kaffee, Espresso, Bohnen, gemahlen | `expenses:food:groceries:coffee` |
| Schokolade, Bitter, Vollmilch | `expenses:food:groceries:chocolate` |
| Samba, Nuss-Nougat, Creme | `expenses:food:groceries:spread` |
| Wein, Bier, Sekt, Champagner | `expenses:food:groceries:alcohol` |
| Limo, Cola, Sprite, Smoothie | `expenses:food:groceries:beverages:soft` |
| Red Bull, Monster, Energy | `expenses:food:groceries:beverages:energy` |
| Chips, Nüsse, Knabber, Popcorn | `expenses:food:groceries:snacks` |
| Olivenöl, Öl, Nudeln, Reis | `expenses:food:groceries:other` |
| Deo, Spray, Zahnpasta, Shampoo | `expenses:household:personal-care` |
| Spülmittel, Putzmittel, Schwamm | `expenses:household:cleaning` |
| Giftbag, Giftwrap, Vase, Deko | `expenses:household:decor` |
| Buch, Roman, Taschenbuch | `expenses:leisure:books` |
| Kino, Ticket, Konzert, Event | `expenses:leisure` |
| Notion, Disney, Prime, Netflix | `expenses:tech:subscriptions` |
| Bolt, Voi, Bahn, Uber | `expenses:transport:shared` |
| Tanken, Aral, Shell, Avia | `expenses:transport:shared` |
| DM, Müller, Apotheke | `expenses:health:other` |
| Versicherung, Beitrag | `expenses:health:insurance` |

## Adding New Accounts

When a receipt contains an item that doesn't fit existing categories:

1. Check if a sub-account under an existing parent makes sense
2. Add to `declarations/accounts.journal` in the finance repo
3. Use the new account in the receipt entry
4. Update this taxonomy file if the pattern repeats

## Naming Conventions

- English account names (lowercase, hyphenated)
- German item descriptions in comments (`;`)
- Quantity notation: `(2×)` or `(3× 0.5L)`
- Weight notation: `; Apfel 1.482 kg`
