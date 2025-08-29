# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 11:43:50 2025

@author: Victor.Bontemps
"""

# import re
# from playwright.sync_api import sync_playwright
# # from urllib.request import urlretrieve

# base_url = "https://registers.esma.europa.eu/publication/details?core=esma_registers_priii_documents&docId="
# links = {
#     "BNP" : "https://registers.esma.europa.eu/publication/details?core=esma_registers_priii_documents&docId=38244945"
#     }

# for bank, link in links.items() :
#     pw = sync_playwright().start()
#     browser = pw.firefox.launch(
#         headless=False 
#         ,slow_mo=6000
#         )
#     page = browser.new_page()
#     page.goto(link)
#     page.get_by_role("tab").get_by_text(
#         "Related Final Terms"
#         ).click()
    
#     # récupérer tous les href qui contiennent "docId="
#     anchors = page.locator("a[href*='docId=']").all()

#     doc_ids = []
#     for a in anchors:
#         href = a.get_attribute("href")
#         if href:
#             match = re.search(r"docId=(\d+)", href)
#             if match:
#                 doc_ids.append(match.group(1))
#     urls = [base_url + id_doc for id_doc in doc_ids]

#     # with page.expect_download() as download_info:
#     #     page.locator("xpath=//a[contains(@href, 'downloadFile')]").first.click()
#     # download = download_info.value  # objet Download
#     # save_path = download.suggested_filename  # nom du fichier par défaut
#     # download.save_as(save_path)
#     # print(f"Fichier téléchargé et sauvegardé sous: {save_path}")

#     browser.close()
    
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

# ---- Paramètres ----
links = {
    # "Nom Banque": "URL ESMA de la banque",
    "Ma Banque Exemple": "https://registers.esma.europa.eu/publication/details?core=esma_registers_priii_documents&docId=38244945"
    # Ajoute d'autres banques ici
}

BASE_DIR = Path("downloads_esma")  # répertoire racine pour tout stocker
DOWNLOAD_XPATH = "//a[contains(@href, 'downloadFile')]"  # sélecteur de liens de téléchargement

# ---- Utilitaires ----
def sanitize_dirname(name: str) -> str:
    """Rend le nom de dossier compatible avec le système de fichiers."""
    return re.sub(r'[\\/:*?"<>|]+', "_", name).strip()

def unique_path(base_dir: Path, filename: str) -> Path:
    """Retourne un chemin unique (évite l'écrasement)."""
    candidate = base_dir / filename
    if not candidate.exists():
        return candidate
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    i = 1
    while True:
        cand = base_dir / f"{stem}_({i}){suffix}"
        if not cand.exists():
            return cand
        i += 1

# ---- Script ----
with sync_playwright() as pw:
    browser = pw.firefox.launch(headless=False, slow_mo=800)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    for bank_name, bank_url in links.items():
        # 1) Préparer le dossier de la banque
        bank_dir = BASE_DIR / sanitize_dirname(bank_name)
        bank_dir.mkdir(parents=True, exist_ok=True)

        # 2) Ouvrir la page ESMA
        page.goto(bank_url, wait_until="domcontentloaded")

        # 3) Cliquer l'icône principale (si présente) et sauvegarder
        try:
            page.wait_for_selector(f"xpath={DOWNLOAD_XPATH}", timeout=8000)
            with page.expect_download() as d1:
                page.locator(f"xpath={DOWNLOAD_XPATH}").first.click()
            dl1 = d1.value
            fname1 = dl1.suggested_filename or "fichier.pdf"
            path1 = unique_path(bank_dir, fname1)
            dl1.save_as(str(path1))
            print(f"[{bank_name}] Téléchargé (principal) → {path1}")
        except Exception as e:
            print(f"[{bank_name}] Pas d'icône principale ou échec du 1er téléchargement : {e}")

        # 4) Récupérer TOUS les liens de type downloadFile et les télécharger
        #    Astuce : on clique par index (snapshot du count) pour éviter les soucis de sélecteur.
        try:
            links_locator = page.locator(f"xpath={DOWNLOAD_XPATH}")
            total = links_locator.count()
            # Optionnel : on peut dédupliquer par href pour éviter de retélécharger le même
            seen_hrefs = set()

            for i in range(total):
                try:
                    a = links_locator.nth(i)
                    href = a.get_attribute("href")
                    # Dédupliquer par URL
                    if href and href in seen_hrefs:
                        continue
                    if href:
                        seen_hrefs.add(href)

                    with page.expect_download() as dfile:
                        a.click()
                    dlf = dfile.value
                    fname = dlf.suggested_filename or "fichier.pdf"
                    path = unique_path(bank_dir, fname)
                    dlf.save_as(str(path))
                    print(f"[{bank_name}] Téléchargé → {path}")
                except Exception as inner_e:
                    print(f"[{bank_name}] Échec sur un lien (index {i}) : {inner_e}")
        except Exception as e:
            print(f"[{bank_name}] Impossible de lister les liens : {e}")

    browser.close()
