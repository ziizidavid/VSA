#!/usr/bin/env python3
"""
IPTV Auto Link Generator
Generates shareable URLs and QR codes for IPTV playlist whenever the IPtv file is updated.
"""

import os
import json
import hashlib
import qrcode
from datetime import datetime
from pathlib import Path

class IPTVLinkGenerator:
    def __init__(self, repo_owner="ziizidavid", repo_name="VSA", branch="main"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.branch = branch
        self.raw_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}/IPtv"
        self.github_url = f"https://github.com/{repo_owner}/{repo_name}/blob/{branch}/IPtv"
        
    def generate_hash(self):
        """Generate hash untuk unique identifier"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{self.raw_url}{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:8]
    
    def create_links(self):
        """Create berbagai format link"""
        unique_id = self.generate_hash()
        
        links = {
            "raw_url": self.raw_url,
            "github_url": self.github_url,
            "unique_id": unique_id,
            "generated_at": datetime.now().isoformat(),
            "formats": {
                "raw": self.raw_url,
                "github_web": self.github_url,
                "vlc_friendly": f"http://localhost:8000/iptv/{unique_id}.m3u8",  # untuk local server
                "direct_copy": f"{self.raw_url}?t={unique_id}",  # dengan cache busting
            }
        }
        
        return links
    
    def generate_qr_code(self, url, output_path):
        """Generate QR code untuk link"""
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
    
    def save_links_json(self, output_path="links_generated.json"):
        """Save generated links ke JSON file"""
        links = self.create_links()
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(links, f, indent=2)
        
        print(f"✓ Links saved to {output_path}")
        return links
    
    def display_links(self):
        """Display semua links ke console"""
        links = self.create_links()
        
        print("\n" + "="*70)
        print("🎬 IPTV PLAYLIST - AUTO GENERATED LINKS")
        print("="*70)
        print(f"\n📅 Generated: {links['generated_at']}")
        print(f"🆔 Unique ID: {links['unique_id']}\n")
        
        print("📋 AVAILABLE LINKS:")
        print("-" * 70)
        for format_name, url in links['formats'].items():
            print(f"\n{format_name.upper()}:")
            print(f"  {url}")
        
        print("\n" + "="*70)
        print("💡 INSTRUCTIONS:")
        print("-" * 70)
        print("1. RAW_URL: Copy-paste langsung ke VLC, Kodi, atau aplikasi IPTV")
        print("2. GITHUB_WEB: Lihat file di GitHub web interface")
        print("3. VLC_FRIENDLY: Untuk local server (jika ada)")
        print("4. DIRECT_COPY: Link dengan cache busting (untuk refresh otomatis)")
        print("="*70 + "\n")
        
        return links


def main():
    """Main function"""
    generator = IPTVLinkGenerator(
        repo_owner="ziizidavid",
        repo_name="VSA",
        branch="main"
    )
    
    # Generate dan save links
    links = generator.save_links_json("links_generated.json")
    
    # Generate QR code
    qr_path = "qrcodes/iptv_playlist_qr.png"
    generator.generate_qr_code(links['formats']['raw'], qr_path)
    
    # Display di console
    generator.display_links()
    
    print("✅ IPTV Link generation complete!\n")


if __name__ == "__main__":
    main()
