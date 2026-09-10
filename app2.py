#!/usr/bin/env python3
# أداة البحث عن حسابات بوبجي المتروكة
# تجمع الحسابات المربوطة بـ Google, Twitter, Facebook وغيرها
# التشغيل: python3 pubg_account_finder.py

import requests
import time
import re
import json
import os
import sys
from datetime import datetime
from urllib.parse import quote

# ============================================================
# الإعدادات
# ============================================================
class Config:
    TIMEOUT = 15
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    OUTPUT_DIR = os.path.expanduser("~/pubg_accounts")
    PROXIES = []
    
    @classmethod
    def setup(cls):
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)

# ============================================================
# المحرك الأساسي
# ============================================================
class PUBGAccountFinder:
    """أداة البحث عن حسابات بوبجي المتروكة"""
    
    def __init__(self, query=None):
        self.query = query
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": Config.USER_AGENT})
        self.results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "accounts": [],
            "inactive": [],
            "linked_accounts": {}
        }
    
    # ========================================================
    # 1. البحث عن حسابات بوبجي في منصات بيع الحسابات
    # ========================================================
    def search_marketplaces(self):
        """البحث في منصات بيع الحسابات عن حسابات متروكة"""
        print(f"\n[1] البحث في منصات بيع الحسابات...")
        
        marketplaces = [
            {
                "name": "PlayerAuctions",
                "url": "https://www.playerauctions.com/pubg-mobile-account/",
                "search_url": "https://www.playerauctions.com/search/?q={}"
            },
            {
                "name": "G2G",
                "url": "https://www.g2g.com/categories/pubg-mobile-account",
                "search_url": "https://www.g2g.com/search?q={}"
            },
            {
                "name": "EpicNPC",
                "url": "https://www.epicnpc.com/forums/pubg-mobile-accounts.310/",
                "search_url": "https://www.epicnpc.com/search/?q={}"
            }
        ]
        
        for market in marketplaces:
            try:
                # البحث بكلمة "inactive" أو "OG"
                search_url = market["search_url"].format(quote(self.query or "inactive pubg account"))
                response = self.session.get(search_url, timeout=Config.TIMEOUT)
                
                if response.status_code == 200:
                    # البحث عن إشارات الحسابات المتروكة
                    inactive_keywords = ["inactive", "og", "old", "abandoned", "8 years", "7 years"]
                    found = []
                    
                    for keyword in inactive_keywords:
                        if keyword.lower() in response.text.lower():
                            found.append(keyword)
                    
                    if found:
                        print(f"   ✅ {market['name']}: تم العثور على {len(found)} إشارة")
                        self.results["inactive"].append({
                            "source": market["name"],
                            "url": search_url,
                            "keywords": found
                        })
                    else:
                        print(f"   ⚠️ {market['name']}: لا توجد إشارات")
            except Exception as e:
                print(f"   ❌ {market['name']}: خطأ - {e}")
            
            time.sleep(1)
    
    # ========================================================
    # 2. البحث عن الحسابات المربوطة بـ Google
    # ========================================================
    def search_google_linked(self):
        """البحث عن حسابات بوبجي المربوطة بـ Google"""
        print(f"\n[2] البحث عن حسابات Google المربوطة...")
        
        try:
            # البحث في Google عن حسابات بوبجي قديمة
            search_query = f"site:pubgmobile.com OR site:krafton.com {self.query or 'inactive'} account"
            google_url = f"https://www.google.com/search?q={quote(search_query)}"
            
            response = self.session.get(google_url, timeout=Config.TIMEOUT)
            
            if response.status_code == 200:
                # استخراج النتائج
                links = re.findall(r'href="/url\?q=([^&]+)', response.text)
                for link in links[:5]:
                    if "pubg" in link.lower() or "krafton" in link.lower():
                        self.results["linked_accounts"].setdefault("google", []).append({
                            "url": link,
                            "found_at": datetime.now().isoformat()
                        })
                
                print(f"   ✅ تم العثور على {len(self.results['linked_accounts'].get('google', []))} نتيجة")
            else:
                print(f"   ⚠️ لم يتم العثور على نتائج")
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
    
    # ========================================================
    # 3. البحث عن الحسابات المربوطة بـ Twitter
    # ========================================================
    def search_twitter_linked(self):
        """البحث عن حسابات بوبجي المربوطة بـ Twitter"""
        print(f"\n[3] البحث عن حسابات Twitter المربوطة...")
        
        try:
            # استخدام Nitter للبحث
            nitter_instances = ["https://nitter.net", "https://nitter.cz"]
            
            for instance in nitter_instances:
                search_url = f"{instance}/search?f=tweets&q=PUBG%20account%20inactive"
                response = self.session.get(search_url, timeout=Config.TIMEOUT)
                
                if response.status_code == 200:
                    # البحث عن تغريدات تتعلق بحسابات بوبجي
                    tweets = re.findall(r'tweet-content[^>]*>([^<]+)', response.text)
                    for tweet in tweets[:5]:
                        if "pubg" in tweet.lower() or "account" in tweet.lower():
                            self.results["linked_accounts"].setdefault("twitter", []).append({
                                "tweet": tweet.strip()[:200],
                                "found_at": datetime.now().isoformat()
                            })
                    
                    print(f"   ✅ تم العثور على {len(self.results['linked_accounts'].get('twitter', []))} تغريدة")
                    break
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
    
    # ========================================================
    # 4. البحث عن الحسابات المربوطة بـ Facebook
    # ========================================================
    def search_facebook_linked(self):
        """البحث عن حسابات بوبجي المربوطة بـ Facebook"""
        print(f"\n[4] البحث عن حسابات Facebook المربوطة...")
        
        try:
            # البحث في Facebook
            search_url = f"https://www.facebook.com/search/top?q=PUBG%20account%20inactive"
            response = self.session.get(search_url, timeout=Config.TIMEOUT)
            
            if response.status_code == 200:
                # البحث عن منشورات
                posts = re.findall(r'"message":"([^"]+)"', response.text)
                for post in posts[:5]:
                    if "pubg" in post.lower() or "account" in post.lower():
                        self.results["linked_accounts"].setdefault("facebook", []).append({
                            "post": post[:200],
                            "found_at": datetime.now().isoformat()
                        })
                
                print(f"   ✅ تم العثور على {len(self.results['linked_accounts'].get('facebook', []))} منشور")
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
    
    # ========================================================
    # 5. البحث في قواعد البيانات المسربة
    # ========================================================
    def search_breaches(self):
        """البحث في قواعد البيانات المسربة عن حسابات بوبجي"""
        print(f"\n[5] البحث في قواعد البيانات المسربة...")
        
        if not self.query:
            print("   ⚠️ لا يوجد بريد للبحث")
            return
        
        try:
            # استخدام HIBP API
            hibp_url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{quote(self.query)}"
            response = self.session.get(hibp_url, timeout=Config.TIMEOUT)
            
            if response.status_code == 200:
                breaches = response.json()
                for breach in breaches:
                    if "pubg" in breach.get("Name", "").lower() or "krafton" in breach.get("Name", "").lower():
                        self.results["inactive"].append({
                            "source": "HIBP",
                            "breach": breach.get("Name"),
                            "date": breach.get("BreachDate"),
                            "accounts_affected": breach.get("PwnCount")
                        })
                        print(f"   ⚠️ تم العثور على اختراق: {breach.get('Name')}")
            elif response.status_code == 404:
                print(f"   ✅ لا توجد اختراقات مرتبطة")
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
    
    # ========================================================
    # 6. البحث عن الحسابات المهجورة في منصات التواصل
    # ========================================================
    def search_abandoned_social(self):
        """البحث عن حسابات بوبجي المهجورة في منصات التواصل"""
        print(f"\n[6] البحث عن الحسابات المهجورة...")
        
        # البحث عن حسابات قديمة في Twitter
        try:
            # استخدام Twitter Search API (بديل)
            search_terms = [
                "PUBG account for sale old",
                "PUBG account inactive",
                "PUBG OG account abandoned"
            ]
            
            for term in search_terms:
                search_url = f"https://nitter.net/search?f=tweets&q={quote(term)}"
                response = self.session.get(search_url, timeout=Config.TIMEOUT)
                
                if response.status_code == 200:
                    tweets = re.findall(r'tweet-content[^>]*>([^<]+)', response.text)
                    for tweet in tweets[:3]:
                        if "account" in tweet.lower():
                            self.results["inactive"].append({
                                "source": "Twitter",
                                "term": term,
                                "content": tweet.strip()[:200]
                            })
                time.sleep(1)
            
            print(f"   ✅ تم العثور على {len(self.results['inactive'])} إشارة")
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
    
    # ========================================================
    # 7. البحث في منتديات بوبجي
    # ========================================================
    def search_forums(self):
        """البحث في منتديات بوبجي عن حسابات متروكة"""
        print(f"\n[7] البحث في المنتديات...")
        
        forums = [
            "https://www.reddit.com/r/PUBGMobile/search.json?q=inactive+account&restrict_sr=1",
            "https://www.reddit.com/r/PUBG/search.json?q=old+account&restrict_sr=1"
        ]
        
        for forum_url in forums:
            try:
                response = self.session.get(forum_url, timeout=Config.TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("data", {}).get("children", [])
                    
                    for post in posts[:5]:
                        post_data = post.get("data", {})
                        title = post_data.get("title", "")
                        if "account" in title.lower() or "inactive" in title.lower():
                            self.results["inactive"].append({
                                "source": "Reddit",
                                "title": title,
                                "url": f"https://reddit.com{post_data.get('permalink', '')}",
                                "created": post_data.get("created_utc")
                            })
                    
                    print(f"   ✅ Reddit: تم العثور على {len(posts)} منشور")
            except Exception as e:
                print(f"   ❌ خطأ: {e}")
    
    # ========================================================
    # 8. توليد التقرير
    # ========================================================
    def generate_report(self):
        """توليد تقرير كامل"""
        print("\n" + "=" * 60)
        print("📊 تقرير البحث عن حسابات بوبجي المتروكة")
        print("=" * 60)
        
        print(f"\n📅 التاريخ: {self.results['timestamp']}")
        print(f"🔍 البحث عن: {self.query or 'حسابات متروكة'}")
        
        print(f"\n📱 الحسابات المتروكة المكتشفة: {len(self.results['inactive'])}")
        for item in self.results["inactive"]:
            print(f"   📌 {item.get('source')}: {item.get('title', item.get('content', item.get('breach', '')))[:80]}")
        
        print(f"\n🔗 الحسابات المربوطة:")
        for platform, accounts in self.results["linked_accounts"].items():
            print(f"   {platform}: {len(accounts)}")
        
        # حفظ التقرير
        report_file = os.path.join(Config.OUTPUT_DIR, f"pubg_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 تم حفظ التقرير في: {report_file}")
        print("=" * 60)
        
        return self.results

# ============================================================
# الدالة الرئيسية
# ============================================================
def main():
    print("=" * 60)
    print("🔥 منارة نونو - أداة جمع حسابات بوبجي المتروكة")
    print("=" * 60)
    
    Config.setup()
    
    # قراءة المدخلات
    if len(sys.argv) >= 2:
        query = sys.argv[1]
    else:
        query = input("🔍 أدخل بريد إلكتروني أو اسم مستخدم للبحث (اختياري): ").strip() or None
    
    finder = PUBGAccountFinder(query=query)
    
    # تنفيذ جميع الفحوصات
    finder.search_marketplaces()
    finder.search_google_linked()
    finder.search_twitter_linked()
    finder.search_facebook_linked()
    finder.search_breaches()
    finder.search_abandoned_social()
    finder.search_forums()
    finder.generate_report()

if __name__ == "__main__":
    main()#