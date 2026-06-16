#!/usr/bin/env python3
"""
IPTV Auto Content Updater & Link Generator
- Fetch konten terbaru dari external IPTV source
- Append ke file IPtv (keep existing content)
- Auto-generate shareable links dengan cache busting
"""

import os
import json
import hashlib
import requests
import qrcode
from datetime import datetime
from pathlib import Path

class IPTVAutoUpdater:
    def __init__(self, repo_owner="ziizidavid", repo_name="VSA", branch="main"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.branch = branch
        self.iptv_file = "IPtv"
        self.raw_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}/{self.iptv_file}"
        self.github_url = f"https://github.com/{repo_owner}/{repo_name}/blob/{branch}/{self.iptv_file}"
        
        # External IPTV source to fetch from
        self.external_source = "https://raw.githubusercontent.com/doms9/iptv/refs/heads/default/M3U8/events.m3u8"
        
    def fetch_external_content(self):
        """Fetch konten dari external IPTV source"""
        try:
            response = requests.get(self.external_source, timeout=10)
            response.raise_for_status()
            print(f"✓ Fetched external content from: {self.external_source}")
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"⚠ Warning: Failed to fetch external content: {e}")
            return None
    
    def read_existing_content(self):
        """Baca konten existing dari file IPtv"""
        if os.path.exists(self.iptv_file):
            with open(self.iptv_file, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    def find_insertion_point(self, content):
        """Find dimana untuk insert konten external (setelah TVRI Sport)"""
        marker = 'http://103.148.44.38:8000/play/a05u/index.m3u8'
        if marker in content:
            pos = content.find(marker) + len(marker)
            return pos
        return len(content)
    
    def update_iptv_file(self, external_content):
        """Update IPtv file dengan konten external"""
        existing = self.read_existing_content()
        
        if not existing:
            print("⚠ Warning: IPtv file not found")
            return False
        
        if not external_content:
            print("⚠ Warning: External content is empty")
            return False
        
        # Find insertion point (after TVRI Sport entry)
        insert_pos = self.find_insertion_point(existing)
        
        # Combine: keep existing + add external content
        updated_content = existing[:insert_pos] + "\n" + external_content
        
        # Write back
        with open(self.iptv_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✓ IPtv file updated successfully")
        print(f"  - Kept existing content up to TVRI Sport")
        print(f"  - Appended {len(external_content)} bytes of new content")
        return True
    
    def generate_hash(self):
        """Generate hash untuk unique identifier"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{self.raw_url}{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:8]
    
    def create_links(self):
        """Create berbagai format link dengan cache busting"""
        unique_id = self.generate_hash()
        
        links = {
            "raw_url": self.raw_url,
            "github_url": self.github_url,
            "unique_id": unique_id,
            "timestamp": datetime.now().isoformat(),
            "external_source": self.external_source,
            "formats": {
                "raw_direct": self.raw_url,
                "raw_with_cache_bust": f"{self.raw_url}?t={unique_id}",
                "github_web": self.github_url,
                "github_raw": f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/{self.branch}/{self.iptv_file}?cache={unique_id}",
            }
        }
        
        return links
    
    def generate_qr_code(self, url, output_path="qrcodes/iptv_playlist_qr.png"):
        """Generate QR code untuk link"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path)
            print(f"✓ QR code generated: {output_path}")
            return output_path
        except Exception as e:
            print(f"⚠ Warning: Could not generate QR code: {e}")
            return None
    
    def save_links_json(self, output_path="links_generated.json"):
        """Save generated links ke JSON file"""
        links = self.create_links()
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(links, f, indent=2)
        
        print(f"✓ Links saved to {output_path}")
        return links
    
    def display_links(self, links):
        """Display semua links ke console"""
        print("\n" + "="*80)
        print("🎬 IPTV PLAYLIST - AUTO UPDATED & GENERATED LINKS")
        print("="*80)
        print(f"\n📅 Generated: {links['timestamp']}")
        print(f"🆔 Unique ID: {links['unique_id']}")
        print(f"📡 External Source: {links['external_source']}\n")
        
        print("📋 AVAILABLE LINKS:")
        print("-" * 80)
        for format_name, url in links['formats'].items():
            print(f"\n{format_name.upper()}:")
            print(f"  {url}")
        
        print("\n" + "="*80)
        print("💡 HOW TO USE:")
        print("-" * 80)
        print("1. RAW_DIRECT: Copy-paste ke VLC, Kodi, TiviMate, atau IPTV Player")
        print("2. RAW_WITH_CACHE_BUST: Gunakan ini untuk refresh otomatis (app akan selalu load terbaru)")
        print("3. GITHUB_WEB: Lihat file di GitHub interface")
        print("4. GITHUB_RAW: Alternative raw link dengan cache parameter")
        print("\n⚡ TIPS:")
        print("  • Gunakan RAW_WITH_CACHE_BUST link untuk menghindari caching")
        print("  • Unique ID berubah setiap kali script dijalankan")
        print("  • Konten external di-append otomatis setiap update")
        print("="*80 + "\n")
    
    def run(self):
        """Main execution"""
        print("\n🚀 Starting IPTV Auto Updater...\n")
        
        # Step 1: Fetch external content
        print("📥 Step 1: Fetching external IPTV content...")
        external_content = self.fetch_external_content()
        
        # Step 2: Update IPtv file
        print("\n📝 Step 2: Updating IPtv file...")
        if external_content:
            self.update_iptv_file(external_content)
        else:
            print("⚠ Skipping file update (no external content)")
        
        # Step 3: Generate links
        print("\n🔗 Step 3: Generating shareable links...")
        links = self.save_links_json("links_generated.json")
        
        # Step 4: Generate QR code
        print("\n📱 Step 4: Generating QR code...")
        self.generate_qr_code(links['formats']['raw_with_cache_bust'])
        
        # Step 5: Display results
        print("\n✅ STEP 5: Results")
        self.display_links(links)
        
        return links


def main():
    """Main function"""
    updater = IPTVAutoUpdater(
        repo_owner="ziizidavid",
        repo_name="VSA",
        branch="main"
    )
    
    updater.run()


if __name__ == "__main__":
    main()
