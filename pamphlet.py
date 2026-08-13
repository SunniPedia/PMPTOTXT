import requests
from bs4 import BeautifulSoup
import html
import time
import re

BASE_URL = "https://www.dawateislami.net/pamphlets/8969/page/{}"
START_PAGE = 1
END_PAGE = 50
SAVE_PATH = "/storage/emulated/0/Download/pamphlet_8969.txt"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

def final_clean(text):
    # ১. HTML এনটিটি ডিকোড
    text = html.unescape(text)
    
    # ২. অতিরিক্ত স্পেস বা নিউলাইনকে একটি স্পেসে রূপান্তর
    text = re.sub(r'\s+', ' ', text)
    
    # ৩. ব্র্যাকেটের ভেতরের স্পেস ঠিক করা: ( অর্থাৎ ) -> (অর্থাৎ)
    text = re.sub(r'\(\s+', '(', text)
    text = re.sub(r'\s+\)', ')', text)
    
    # ৪. দাঁড়ি, কমা বা কোলনের আগের স্পেস মুছে ফেলা
    text = re.sub(r'\s+([।,:!])', r'\1', text)
    
    # ৫. অনেক সময় শব্দের মাঝে ভুল করে ডাবল স্পেস থাকে, সেটা কমানো
    text = re.sub(r' +', ' ', text)
    
    return text.strip()

all_text = ""

for page in range(START_PAGE, END_PAGE + 1):
    url = BASE_URL.format(page)
    print(f"Scraping Page {page}...")

    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200:
            break

        soup = BeautifulSoup(res.text, "html.parser")
        div = soup.find("div", class_="WordSection1")

        if not div:
            break

        paragraphs = div.find_all("p")

        for p in paragraphs:
            # separator=' ' ব্যবহার করছি যাতে শব্দগুলো জোড়া লেগে না যায়
            raw_text = p.get_text(separator=' ', strip=True)
            
            # ক্লিনআপ ফাংশন কল
            cleaned_text = final_clean(raw_text)

            if cleaned_text:
                all_text += cleaned_text + "\n\n"

        time.sleep(0.5)

    except Exception as e:
        print(f"Error: {e}")
        break

# সেভ করা
try:
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        f.write(all_text)
    print(f"✅ মাশা-আল্লাহ! এবার আউটপুট ইনশাআল্লাহ ঠিক আসবে।")
except Exception as e:
    print(f"সেভ এরর: {e}")
