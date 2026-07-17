---
name: receipt-tracker
description: Scan physical receipts and convert them into item-level hledger journal entries. Use when the user sends receipt photos (images) and wants granular expense tracking per item instead of aggregated totals. Triggers on phrases like "scan receipt", "track items", "split receipt", "item-level tracking", or when receipt images are sent for finance tracking. Works with hledger-based finance systems.
---

# Receipt Tracker

## Overview

Convert physical receipts into item-level hledger journal entries. Enables queries like "How much for Lachs?" or "How much for coffee?" by splitting each receipt into categorized line items.

## Workflow

### 1. Receipt Intake
- User sends one or more receipt photos
- Extract items, prices, quantities, store name, date using vision model
- Note: Dates on receipts may differ from bank transaction dates (receipt date vs. booking date)

### 2. Categorization Rules

Map each item to the appropriate hledger expense account. Use the account taxonomy in `references/account-taxonomy.md`.

**Default mapping rules:**

| Item Type | Account | Examples |
|---|---|---|
| Fresh fish / seafood | `expenses:food:groceries:fish` | Lachs, Sardinen, Garnelen |
| Eggs, cheese, butter | `expenses:food:groceries:dairy` | Eier, Parmigiano, Alpenbutter |
| Fruit | `expenses:food:groceries:produce:fruit` | Äpfel, Bananen, Himbeeren |
| Vegetables | `expenses:food:groceries:produce:vegetables` | Gurken, Tomaten, Spinat |
| Bread / baked goods | `expenses:food:groceries:bakery` | Brot, Brötchen, Kamps |
| Meat / sausages | `expenses:food:groceries:meat` | Salami, Haussalami, Wurst |
| Coffee beans / ground | `expenses:food:groceries:coffee` | Espresso, Kaffee |
| Chocolate / sweets | `expenses:food:groceries:chocolate` | Schokolade, Himbeer-Splitter |
| Spreads | `expenses:food:groceries:spread` | Samba Dark, Nuss-Nougat |
| Alcoholic beverages | `expenses:food:groceries:alcohol` | Wein, Bier, Sekt |
| Soft drinks | `expenses:food:groceries:beverages:soft` | Limo, Cola, Smoothies |
| Energy drinks | `expenses:food:groceries:beverages:energy` | Red Bull, Monster |
| Snacks / chips | `expenses:food:groceries:snacks` | Chips, Nüsse, Knabberzeug |
| Other groceries | `expenses:food:groceries:other` | Olivenöl, Kichererbsen, Tomaten-Dosen |
| Eating out | `expenses:food:eating-out` | Restaurant, Kiosk, Bäckerei (Konsum) |
| Books | `expenses:leisure:books` | Bücher, eBooks, Magazine |
| Personal care | `expenses:household:personal-care` | Deospray, Zahnpasta, Haarlack |
| Cleaning supplies | `expenses:household:cleaning` | Spülmittel, Spülschwämme |
| Decor / gifts | `expenses:household:decor` | Giftbags, Vasen, Giftwrap |
| Other household | `expenses:household` | IKEA, Hornbach, Möbel |
| Health / pharmacy | `expenses:health:other` | DM, Müller, Apotheke |
| Transport | `expenses:transport:shared` | Bolt, Bahn, Voi, Tanken |
| Tech subscriptions | `expenses:tech:subscriptions` | Notion, Disney+, Prime |
| Leisure / entertainment | `expenses:leisure` | Kino, Eventim, VIVINO |
| Investment fees | `expenses:investment:fees` | Trade Republic, Broker |

### 3. Journal Entry Format

Replace aggregated bank transaction entries with item-level splits in the yearly journal:

**File location:** `journal/YYYY/bank.journal` (where YYYY is the transaction year)

**Never create separate files like `ledger.journal` — always append to the appropriate yearly bank journal.**

```hledger
2026-05-19 * Fuellhorn Karlsruhe eG  ; Bon 18.05.2026 14:33
    assets:bank:traderepublic:cash    -95.57 EUR
    expenses:food:groceries:fish      15.98 EUR  ; Nordatlantik Lachs mild geräuchert (2×)
    expenses:food:groceries:dairy      8.98 EUR  ; Bruderhahn Eier 10er (2×)
    expenses:food:groceries:dairy      8.62 EUR  ; Parmigiano Reggiano DOP
    expenses:food:groceries:produce:fruit   5.91 EUR  ; Apfel 1.482 kg
    expenses:food:groceries:produce:vegetables  4.59 EUR  ; Gurken Mini 0.464 kg
    expenses:food:groceries:coffee      14.99 EUR  ; Espresso ganze Bohne
    expenses:food:groceries:spread      11.98 EUR  ; Samba Dark (2×)
    expenses:food:groceries:chocolate   8.98 EUR  ; Edel Bitter Blutorange (2×)
    expenses:household                  6.99 EUR  ; 2in1 Duschgel
    expenses:household                  5.98 EUR  ; Spülschwämme kratzfrei (2×)
```

**Rules:**
- Add `; Bon DD.MM.YYYY HH:MM` comment with receipt date/time
- Add `; Description` comment for each item line
- Match total exactly (hledger check must pass)
- Include Pfand (deposit) in beverage prices if shown separately
- If receipt has discounts/cashback, adjust line items to match total

### 4. Belegbild ablegen

Store the receipt photo itself in the finance repo so the dashboard can display it ("Beleg öffnen" in the transaction modal):

- **Folder:** `receipts/` (repo root)
- **Filename:** `JJJJ-MM-TT_BETRAG[_haendler].jpg` — full convention in `receipts/README.md`
  - Date = journal booking date (not the receipt date, if different)
  - Amount = absolute total with `-` as decimal separator, two digits: `95-57` = 95,57 €
  - Optional lowercase merchant slug (`rewe`, `thalia`) disambiguates same-day same-amount bookings
- Convert HEIC photos to jpg first (browsers can't render HEIC)
- Commit to the **private** repo: `fin-data add -f receipts/ && fin-data commit` (`-f` is required because the images are gitignored in the public repo)

### 5. Account Creation

If a needed account doesn't exist in `declarations/accounts.journal`, add it before posting. New accounts go under existing top-level accounts.

### 6. Validation & Commit

After editing:
1. **Verify file location:** Must be in `journal/YYYY/bank.journal`, not a new file
2. Run `hledger check`
3. If unbalanced, debug line items (usually Pfand or discounts)
4. Fix and re-check until clean
5. Git commit with descriptive message

## Handling Edge Cases

**Receipt date ≠ Bank date:** Use receipt date in comment, bank date as transaction date
**Pfand (deposit):** Add to beverage line item, don't create separate posting
**Discounts:** Distribute across items or adjust affected item to match total
**Unreadable items:** Mark as `expenses:food:groceries:other` with `; unclear`
**Multiple receipts:** Process all, then batch-commit

## Resources

### references/account-taxonomy.md
Full account hierarchy with all existing and planned sub-accounts. Load when adding new accounts or uncertain about categorization.
