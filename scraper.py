import os
import time
import requests
from bs4 import BeautifulSoup
import html
import re

# ১০০০ থেকে ১০০০০ পর্যন্ত আইডি রেঞ্জ
START_ID = 1000
END_ID = 10000

# ফাইল সেভ করার ফোল্ডার নির্দেশ করা
OUTPUT_DIR = "pamphlets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_URL = "https://www.dawateislami.net/pamphlets/{}/page/{}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

def final_clean(text):
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\(\s+', '(', text)
    text = re.sub(r'\s+\)', ')', text)
    text = re.sub(r'\s+([।,:!])', r'\1', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()

def run_git_command(cmd):
    """গিট কমান্ড চালানোর জন্য সহায়িকা ফাংশন"""
    return os.system(cmd)

# গিট কনফিগারেশন সেটআপ (GitHub Actions-এ প্রয়োজনীয়)
run_git_command('git config --global user.name "github-actions[bot]"')
run_git_command('git config --global user.email "github-actions[bot]@users.noreply.github.com"')

for p_id in range(START_ID, END_ID + 1):
    file_name = f"pamphlet_{p_id}.txt"
    file_path = os.path.join(OUTPUT_DIR, file_name)
    
    # ফাইল আগেই থাকলে স্ক্র্যাপ না করে পরেরটিতে চলে যাবে
    if os.path.exists(file_path):
        print(f"Skipping {file_name}, already exists.")
        continue

    pamphlet_text = ""
    has_data = False
    page = 1

    # পেজ লিমিট তুলে দেওয়া হয়েছে, যতক্ষণ টেক্সট পাওয়া যাবে লুপ চলবে
    while True:
        url = BASE_URL.format(p_id, page)
        print(f"Scraping Pamphlet {p_id} - Page {page}...")

        try:
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code != 200:
                print(f"Page {page} returned status code {res.status_code}. Stopping pamphlet {p_id}.")
                break

            soup = BeautifulSoup(res.text, "html.parser")
            div = soup.find("div", class_="WordSection1")

            # যদি কন্টেন্ট ডিভ না থাকে বা খালি থাকে তবে পরের পেজে যাবে না
            if not div:
                print(f"No WordSection1 div found on page {page}. Stopping pamphlet {p_id}.")
                break

            paragraphs = div.find_all("p")
            page_text = ""

            for p in paragraphs:
                raw_text = p.get_text(separator=' ', strip=True)
                cleaned_text = final_clean(raw_text)

                if cleaned_text:
                    page_text += cleaned_text + "\n\n"

            # পেজে কোনো টেক্সট না পাওয়া গেলে লুপ থামিয়ে দেওয়া হবে
            if page_text.strip():
                pamphlet_text += page_text
                has_data = True
                page += 1
            else:
                print(f"No valid text on page {page}. Stopping pamphlet {p_id}.")
                break

            time.sleep(0.5)

        except Exception as e:
            print(f"Error on Pamphlet {p_id}, Page {page}: {e}")
            break

    # ডেটা থাকলে ফাইল সেভ করা এবং আলাদা আলাদা Commit ও Push করা
    if has_data and pamphlet_text.strip():
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(pamphlet_text)
            print(f"Saved: {file_path}")

            # গিটহাব রিপোজিটরিতে একটি করে ফাইল Commit এবং Push করা
            run_git_command(f'git add "{file_path}"')
            run_git_command(f'git commit -m "Add pamphlet {p_id}"')
            run_git_command('git push')
            
            print(f"Pushed Pamphlet {p_id} to GitHub successfully.")

        except Exception as e:
            print(f"Save/Push error for Pamphlet {p_id}: {e}")
